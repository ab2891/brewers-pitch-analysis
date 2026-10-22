import csv
import io
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from download_statcast import date_chunks, fetch_window, reconcile, validate_rows


def pitch(number=1, description="ball"):
    return dict(game_pk="42", at_bat_number="1", pitch_number=str(number),
                pitcher="7", game_date="2026-04-06", game_type="R", pitch_type="FF",
                description=description, delta_run_exp=".03")


class DownloadTests(unittest.TestCase):
    def test_windows_cover_both_endpoints_without_overlap(self):
        self.assertEqual(list(date_chunks(date(2026, 4, 1), date(2026, 4, 8), 7)),
                         [(date(2026, 4, 1), date(2026, 4, 7)), (date(2026, 4, 8), date(2026, 4, 8))])
        with self.assertRaises(ValueError):
            list(date_chunks(date(2026, 4, 1), date(2026, 4, 8), 0))

    def test_wrong_pitcher_dates_and_conflicts_are_rejected(self):
        day = date(2026, 4, 6)
        for bad in [{**pitch(), "pitcher": "8"}, {**pitch(), "game_date": "2026-04-07"},
                    {**pitch(), "game_pk": ""}]:
            with self.assertRaises(ValueError):
                validate_rows([bad], 7, day, day)
        with self.assertRaisesRegex(ValueError, "Conflicting"):
            validate_rows([pitch(), {**pitch(), "description": "called_strike"}], 7, day, day)

    def test_correct_query_and_verified_checkpoint_resume(self):
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=list(pitch()))
        writer.writeheader()
        writer.writerow(pitch())

        class Response:
            content = ("\ufeff" + buffer.getvalue()).encode("utf-8")

        with tempfile.TemporaryDirectory() as temp, patch("download_statcast.request", return_value=Response()) as call:
            cache = Path(temp)
            day = date(2026, 4, 6)
            self.assertEqual(fetch_window(7, day, day, cache), [pitch()])
            params = call.call_args.args[1]
            self.assertEqual(params["pitchers_lookup[]"], 7)
            self.assertEqual(params["type"], "details")
            self.assertEqual(params["game_date_gt"], "2026-04-06")
            self.assertEqual(params["game_date_lt"], "2026-04-06")
            fetch_window(7, day, day, cache)
            self.assertEqual(call.call_count, 1)
            path = next(cache.glob("*.json"))
            saved = json.loads(path.read_text())
            saved["rows"][0]["pitcher"] = "8"
            path.write_text(json.dumps(saved))
            with self.assertRaisesRegex(ValueError, "Invalid checkpoint"):
                fetch_window(7, day, day, cache)

    def test_http_success_with_error_body_is_not_an_empty_window(self):
        class Response:
            content = b"<html>Service unavailable</html>"
        with tempfile.TemporaryDirectory() as temp, patch("download_statcast.request", return_value=Response()):
            with self.assertRaisesRegex(ValueError, "valid pitch CSV"):
                fetch_window(7, date(2026, 4, 6), date(2026, 4, 6), Path(temp))
            self.assertFalse(list(Path(temp).glob("*.json")))

    def test_automatic_events_do_not_count_as_physical_pitches(self):
        logs = [{"date": "2026-04-06", "game": {"gamePk": 42}, "stat": {"numberOfPitches": 1}}]
        result = reconcile([pitch(), pitch(2, "automatic_ball"), pitch(3, "automatic_strike")], logs)
        self.assertEqual(result["pitch_count_differences"], [])
        self.assertEqual(result["physical_pitch_rows"], 1)
        self.assertEqual(result["automatic_event_rows"], 2)
        self.assertEqual(reconcile([], logs)["missing_games"], ["42"])


if __name__ == "__main__":
    unittest.main()
