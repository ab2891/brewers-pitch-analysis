"""Development-fold improvement of a pitch-transition model for matchup planning."""
import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import log_loss, brier_score_loss
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBClassifier

from download_statcast import ROOT, KEY, AUTOMATIC, atomic_json, now
from history import WHIFFS

MIZ = '694819'
LABELS = ['ball', 'strike', 'whiff', 'foul', 'out', 'single', 'extra_base', 'home_run', 'hbp']
CAT = ['pitch_type', 'stand', 'p_throws', 'batter']
SEQ = ['previous_pitch_type', 'previous_result']
MEASURE = ['release_speed', 'release_spin_rate', 'release_extension', 'pfx_x', 'pfx_z']
PRIOR = [f'prior_{x}' for x in MEASURE] + ['prior_pair_n', 'prior_pair_whiff', 'prior_pair_ball', 'prior_pair_damage']
NUM = ['balls', 'strikes'] + PRIOR
CONTEXT = ['balls', 'strikes', 'pitch_type', 'stand', 'p_throws']
RUN = ROOT / 'artifacts/miz_rays_20261023'


def outcome(row):
    description, event = row['description'], row['events']
    if description in WHIFFS:
        return 'whiff'
    if description in {'called_strike', 'foul_tip', 'bunt_foul_tip', 'foul_bunt'}:
        return 'strike'
    if description in {'foul', 'foul_pitchout'}:
        return 'foul'
    if description in {'ball', 'blocked_ball', 'pitchout', 'intent_ball'}:
        return 'ball'
    if description == 'hit_by_pitch':
        return 'hbp'
    if description == 'hit_into_play':
        return {'single': 'single', 'field_error': 'single', 'double': 'extra_base',
                'triple': 'extra_base', 'home_run': 'home_run'}.get(event, 'out')
    return None


def load_matchup(manifest_path=None):
    path = Path(manifest_path) if manifest_path is not None else ROOT / 'data/processed/matchup/manifest.json'
    manifest = json.loads(path.read_text())
    if manifest['status'] != 'complete':
        raise ValueError('Matchup acquisition has not reconciled')
    frames = []
    for player in manifest['players']:
        source = ROOT / player['file']
        if hashlib.sha256(source.read_bytes()).hexdigest() != player['sha256']:
            raise ValueError('Matchup data changed after audit')
        frames.append(pd.DataFrame(json.loads(source.read_text())['rows']))
    data = pd.concat(frames, ignore_index=True)
    before = len(data)
    crucial = list(KEY) + ['pitcher', 'batter', 'pitch_type', 'description', 'events', 'balls', 'strikes']
    unique_versions = data[crucial].drop_duplicates()
    if unique_versions.duplicated(list(KEY)).any():
        raise ValueError('Conflicting overlapping pitcher/batter download records')
    data = data.drop_duplicates(list(KEY)).copy()
    data['game_date'] = pd.to_datetime(data['game_date']).dt.normalize()
    if data.game_date.max() > pd.Timestamp(manifest['as_of']):
        raise ValueError('Future observations in matchup dataset')
    data['outcome'] = data.apply(outcome, axis=1)
    omitted = int(data.outcome.isna().sum())
    data = data.loc[data.outcome.notna() & data.pitch_type.notna() & data.pitch_type.ne('')].copy()
    for col in list(KEY)[1:] + ['balls', 'strikes'] + MEASURE + ['woba_value']:
        data[col] = pd.to_numeric(data[col], errors='coerce')
    if data[list(KEY) + ['balls', 'strikes']].isna().any().any():
        raise ValueError('Missing key/count fields in matchup dataset')
    data = data.sort_values(['game_date'] + list(KEY)).reset_index(drop=True)
    groups = data.groupby(['game_pk', 'at_bat_number', 'pitcher'], sort=False)
    consecutive = data.pitch_number.sub(groups.pitch_number.shift()).eq(1)
    data['previous_pitch_type'] = groups.pitch_type.shift().where(consecutive, 'START')
    data['previous_result'] = groups.outcome.shift().where(consecutive, 'START')
    data['label'] = data.outcome.map({x: i for i, x in enumerate(LABELS)}).astype(int)
    return data, manifest, {'download_rows': before, 'unique_usable_rows': len(data),
        'unmapped_or_automatic_rows': omitted, 'manifest_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def with_priors(data):
    """Also accepts future query rows with outcome=None and missing measurements."""
    result = data.copy()
    group = ['pitcher', 'pitch_type']
    temp = data[group + ['game_date'] + MEASURE].copy()
    for col in MEASURE:
        temp[col] = pd.to_numeric(temp[col], errors='coerce')
    daily = temp.groupby(group + ['game_date'])[MEASURE].mean().reset_index().sort_values(group + ['game_date'])
    for col in MEASURE:
        # An outing-level EWMA provides recent shape; shift excludes the current date.
        smooth = daily.groupby(group)[col].transform(lambda s: s.ewm(span=5, adjust=False).mean())
        daily[f'prior_{col}'] = smooth.groupby([daily[x] for x in group]).shift()
    names = [f'prior_{x}' for x in MEASURE]
    joined = data[group + ['game_date']].merge(daily[group + ['game_date'] + names], on=group + ['game_date'], how='left', sort=False)
    for name in names:
        result[name] = joined[name].to_numpy()
    group = ['batter', 'pitch_type', 'p_throws']
    temp = data[group + ['game_date']].copy()
    observed = data.outcome.notna()
    temp['n'] = observed.astype(int)
    temp['whiff'] = data.outcome.eq('whiff').astype(int)
    temp['ball'] = data.outcome.eq('ball').astype(int)
    temp['contact'] = data.outcome.isin(['out', 'single', 'extra_base', 'home_run']).astype(int)
    temp['damage'] = pd.to_numeric(data.woba_value, errors='coerce').fillna(0).where(temp.contact.eq(1), 0)
    columns = ['n', 'whiff', 'ball', 'contact', 'damage']
    daily = temp.groupby(group + ['game_date'])[columns].sum().reset_index().sort_values(group + ['game_date'])
    prior = daily.groupby(group)[columns].cumsum() - daily[columns]
    daily['prior_pair_n'] = prior.n
    daily['prior_pair_whiff'] = (prior.whiff + 5) / (prior.n + 50)
    daily['prior_pair_ball'] = (prior.ball + 17.5) / (prior.n + 50)
    daily['prior_pair_damage'] = (prior.damage + 9.6) / (prior.contact + 30)
    names = ['prior_pair_n', 'prior_pair_whiff', 'prior_pair_ball', 'prior_pair_damage']
    joined = data[group + ['game_date']].merge(daily[group + ['game_date'] + names], on=group + ['game_date'], how='left', sort=False)
    for name in names:
        result[name] = joined[name].to_numpy()
    for col in CAT + SEQ:
        result[col] = result[col].fillna('START').astype(str)
    return result


def baseline_fit(train):
    counts = np.bincount(train.label, minlength=len(LABELS)) + 1
    global_rate = counts / counts.sum()
    counts = pd.crosstab([train[c] for c in CONTEXT], train.label).reindex(columns=range(len(LABELS)), fill_value=0)
    estimates = (counts.to_numpy() + 50 * global_rate) / (counts.sum(axis=1).to_numpy()[:, None] + 50)
    table = counts.index.to_frame(index=False)
    for i, name in enumerate(LABELS):
        table['p_' + name] = estimates[:, i]
    return {'global': global_rate, 'table': table}


def baseline_predict(fitted, frame):
    names = ['p_' + x for x in LABELS]
    joined = frame[CONTEXT].merge(fitted['table'], on=CONTEXT, how='left', sort=False)
    values = joined[names].to_numpy(dtype=float)
    missing = np.isnan(values).any(axis=1)
    values[missing] = fitted['global']
    return values


def encoder_fit(frame, sequence, extra_numeric=(), extra_categorical=()):
    cat = CAT + (SEQ if sequence else []) + list(extra_categorical)
    numeric = NUM + list(extra_numeric)
    encoder = ColumnTransformer([('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False, dtype=np.float32), cat), ('num', 'passthrough', numeric)])
    features = cat + numeric
    return encoder.fit(frame[features]), features


def fit_model(train, validation, sequence, depth, rounds=700, extra_numeric=(), extra_categorical=()):
    encoder, features = encoder_fit(train, sequence, extra_numeric, extra_categorical)
    settings = dict(n_estimators=rounds, learning_rate=.04, max_depth=depth,
        min_child_weight=20, reg_lambda=20, subsample=.8, colsample_bytree=.8,
        tree_method='hist', n_jobs=4, random_state=42, eval_metric='mlogloss')
    if validation is not None:
        settings['early_stopping_rounds'] = 40
    model = XGBClassifier(**settings)
    kwargs = {} if validation is None else {'eval_set': [(encoder.transform(validation[features]), validation.label)]}
    model.fit(encoder.transform(train[features]), train.label, verbose=False, **kwargs)
    return model, encoder, features


def predict(bundle, frame):
    if bundle['scorer'] == 'xgboost':
        return bundle['model'].predict_proba(bundle['encoder'].transform(frame[bundle['features']]))
    return baseline_predict(bundle['baseline'], frame)


def main():
    if RUN.exists():
        raise SystemExit('The locked matchup run already exists; do not repeatedly tune on its test')
    data, manifest, info = load_matchup()
    data = with_priors(data)
    RUN.mkdir(parents=True)
    atomic_json(RUN / 'protocol.json', {'frozen_at_utc': now(), 'labels': LABELS,
        'folds': [['2026-06-01', '2026-07-16'], ['2026-07-16', '2026-09-28']],
        'test_start': '2026-10-01', 'candidates': [{'sequence': s, 'depth': d} for s in (False, True) for d in (2, 3)]})
    scores = []
    for sequence in (False, True):
        for depth in (2, 3):
            results = []
            for begin, end in [('2026-06-01', '2026-07-16'), ('2026-07-16', '2026-09-28')]:
                train = data[data.game_date < begin]
                validation = data[data.game_date.between(begin, end, inclusive='left')]
                model, encoder, features = fit_model(train, validation, sequence, depth)
                p = model.predict_proba(encoder.transform(validation[features]))
                baseline = baseline_fit(train)
                results.append({'validation_loss': float(log_loss(validation.label, p, labels=range(len(LABELS)))),
                    'context_loss': float(log_loss(validation.label, baseline_predict(baseline, validation), labels=range(len(LABELS)))),
                    'best_rounds': model.best_iteration + 1, 'rows': len(validation)})
            record = {'sequence': sequence, 'depth': depth, 'folds': results,
                'mean_validation_loss': float(np.mean([r['validation_loss'] for r in results]))}
            scores.append(record)
            print(json.dumps(record), flush=True)
    selected = min(scores, key=lambda x: x['mean_validation_loss'])
    rounds = int(np.median([x['best_rounds'] for x in selected['folds']]))
    atomic_json(RUN / 'selection.json', {'selected_before_test': now(), 'candidates': scores,
        'selected': selected, 'rounds': rounds})
    train, test = data[data.game_date < '2026-10-01'], data[data.game_date >= '2026-10-01']
    model, encoder, features = fit_model(train, None, selected['sequence'], selected['depth'], rounds)
    baseline = baseline_fit(train)
    p = model.predict_proba(encoder.transform(test[features]))
    context = baseline_predict(baseline, test)
    global_p = np.tile(baseline['global'], (len(test), 1))
    test_metrics = {}
    roster_ids = {str(x['id']) for x in manifest['batters']}
    for name, mask in [('overall', np.ones(len(test), dtype=bool)), ('miz', test.pitcher.eq(MIZ).to_numpy()), ('rays_hitters', test.batter.isin(roster_ids).to_numpy())]:
        part = test.loc[mask]
        test_metrics[name] = {'rows': len(part), 'games': part.game_pk.nunique(),
            'xgboost_log_loss': float(log_loss(part.label, p[mask], labels=range(len(LABELS)))),
            'context_log_loss': float(log_loss(part.label, context[mask], labels=range(len(LABELS)))),
            'global_log_loss': float(log_loss(part.label, global_p[mask], labels=range(len(LABELS)))),
            'whiff_brier': float(brier_score_loss(part.outcome.eq('whiff'), p[mask, LABELS.index('whiff')]))}
    y = test.label.to_numpy()
    losses = -np.log(np.clip(p[np.arange(len(test)), y], 1e-9, 1))
    ref_losses = -np.log(np.clip(context[np.arange(len(test)), y], 1e-9, 1))
    errors = pd.DataFrame({'game_pk': test.game_pk.to_numpy(), 'delta': ref_losses - losses, 'n': 1})
    sums = errors.groupby('game_pk')[['delta', 'n']].sum().to_numpy()
    rng = np.random.default_rng(42)
    samples = sums[rng.integers(0, len(sums), size=(1000, len(sums)))].sum(axis=1)
    interval = np.quantile(samples[:, 0] / samples[:, 1], [.025, .975]).tolist()
    overall = test_metrics['overall']
    accepted = interval[0] > 0 and overall['xgboost_log_loss'] < min(overall['context_log_loss'], overall['global_log_loss'])
    scorer = 'xgboost' if accepted else 'context_baseline'
    scored = test[list(KEY) + ['game_date', 'pitcher', 'batter', 'outcome']].copy()
    for i, name in enumerate(LABELS):
        scored['p_' + name] = p[:, i]
    scored.to_csv(RUN / 'postseason_predictions.csv', index=False)
    joblib.dump({'model': model, 'encoder': encoder, 'features': features, 'baseline': baseline, 'scorer': scorer}, RUN / 'evaluation.joblib')
    # Forecast refit is explicitly subsequent to the locked evaluation, not a test.
    model, encoder, features = fit_model(data, None, selected['sequence'], selected['depth'], rounds)
    joblib.dump({'model': model, 'encoder': encoder, 'features': features,
        'baseline': baseline_fit(data), 'scorer': scorer}, RUN / 'forecast.joblib')
    report = {'data': info, 'test_start': '2026-10-01', 'as_of': manifest['as_of'],
        'selected': selected, 'rounds': rounds, 'test': test_metrics, 'scorer': scorer,
        'game_bootstrap_95_percent_log_loss_improvement': interval,
        'test_independence': 'new pitch-level predictions; aggregate postseason results previously public',
        'forecast_refit': 'all pregame data; not an additional evaluation',
        'policy_caveat': 'Predictive accuracy does not validate causal pitch or sequence rankings'}
    data.to_pickle(ROOT / 'data/processed/matchup/model_frame.pkl')
    report['processed_frame_sha256'] = hashlib.sha256((ROOT / 'data/processed/matchup/model_frame.pkl').read_bytes()).hexdigest()
    atomic_json(RUN / 'metrics.json', report)
    atomic_json(RUN / 'manifest.json', manifest)
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    main()
