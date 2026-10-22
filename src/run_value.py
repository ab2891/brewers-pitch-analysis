"""Expected next-pitch run value and explicit runs-prevented comparisons.

ERPA is project-defined: expected runs prevented above the supported usual mix.
The batting-side run-value target is Statcast delta_run_exp, in runs per pitch.
"""
from collections import deque
import numpy as np
import pandas as pd
from matchup_model import LABELS
from sequence import continuation

COUNTS = [(b, s) for b in range(4) for s in range(3)]


def add_base_outs(frame):
    result = frame.copy()
    result['outs'] = pd.to_numeric(result['outs_when_up'], errors='raise').astype(int)
    if not result.outs.between(0, 2).all():
        raise ValueError('A pitch must start with zero, one, or two outs')
    result['base_mask'] = 0
    for base, bit in [('1b', 1), ('2b', 2), ('3b', 4)]:
        occupied = pd.to_numeric(result['on_' + base], errors='coerce').fillna(0).ne(0)
        result['base_mask'] += occupied.astype(int) * bit
    return result


def fit_run_weights(frame, strength=20):
    """Hierarchically pool sparse count/base/out/outcome cells in run units.

    This estimates outcome-associated delta_RE, not a new inning RE24 matrix.
    Parent is an additive count + base/out correction, shrunk to outcome means.
    Pseudo-count strength is fixed, not optimized on the known postseason test.
    """
    if strength <= 0:
        raise ValueError('Smoothing strength must be positive')
    data = add_base_outs(frame)
    data['rv'] = pd.to_numeric(data.delta_run_exp, errors='coerce')
    data = data[np.isfinite(data.rv) & data.outcome.isin(LABELS)].copy()
    if not set(LABELS).issubset(set(data.outcome)):
        raise ValueError('Run-value sample must include every modeled outcome')
    global_means = data.groupby('outcome').rv.mean()
    count = data.groupby(['balls', 'strikes', 'outcome']).rv.agg(['sum', 'count'])
    base = data.groupby(['outs', 'base_mask', 'outcome']).rv.agg(['sum', 'count'])
    full = data.groupby(['balls', 'strikes', 'outs', 'base_mask', 'outcome']).rv.agg(['sum', 'count'])
    records = []
    for b, s in COUNTS:
        for outs in range(3):
            for mask in range(8):
                for label in LABELS:
                    mean = float(global_means[label])
                    c = count.loc[(b, s, label)] if (b, s, label) in count.index else {'sum': 0, 'count': 0}
                    bo = base.loc[(outs, mask, label)] if (outs, mask, label) in base.index else {'sum': 0, 'count': 0}
                    count_mean = (c['sum'] + strength * mean) / (c['count'] + strength)
                    base_mean = (bo['sum'] + strength * mean) / (bo['count'] + strength)
                    parent = count_mean + base_mean - mean
                    cell = full.loc[(b, s, outs, mask, label)] if (b, s, outs, mask, label) in full.index else {'sum': 0, 'count': 0}
                    estimate = (cell['sum'] + strength * parent) / (cell['count'] + strength)
                    records.append(dict(balls=b, strikes=s, outs=outs, base_mask=mask,
                        outcome=label, expected_batting_run_delta=float(estimate), full_cell_n=int(cell['count']),
                        count_outcome_n=int(c['count']), base_outcome_n=int(bo['count']),
                        observed_cell_mean=float(cell['sum']/cell['count']) if cell['count'] else None))
    return pd.DataFrame(records)


def reachable_states(candidate_rows):
    """Legal histories, even if the previous action is too rare to propose now."""
    choices = {key: group.candidate_pitch.tolist() for key, group in candidate_rows.groupby(
        ['balls', 'strikes', 'previous_pitch', 'previous_result'])}
    root = (0, 0, 'START', 'START')
    repertoire = sorted(set(candidate_rows.previous_pitch) - {'START'})
    seen, queue = {root}, deque([root])
    while queue:
        state = queue.popleft()
        # Next-action pruning must not erase a possible past pitch.
        for action in repertoire:
            for result in ('ball', 'strike', 'whiff', 'foul'):
                next_state = continuation(state, action, result)
                if next_state is not None and next_state not in seen:
                    if next_state not in choices:
                        raise ValueError('Missing continuation context in forecast inventory')
                    seen.add(next_state)
                    queue.append(next_state)
    if {(x[0], x[1]) for x in seen} != set(COUNTS):
        raise ValueError('Forecast inventory does not cover every legal count')
    return seen


def run_values(probabilities, weights):
    probability = np.asarray(probabilities, dtype=float)
    weight = np.asarray(weights, dtype=float)
    if not np.isfinite(probability).all() or not np.isfinite(weight).all():
        raise ValueError('Non-finite probabilities or run weights')
    if (probability < 0).any() or not np.allclose(probability.sum(axis=-1), 1, atol=1e-5):
        raise ValueError('Outcome probabilities must sum to one')
    return (probability * weight).sum(axis=-1)


def relative_value(values, mix):
    values, mix = np.asarray(values, dtype=float), np.asarray(mix, dtype=float)
    if not np.isfinite(values).all() or not np.isfinite(mix).all() or (mix < 0).any() or mix.sum() <= 0:
        raise ValueError('Invalid candidate values or reference mix')
    mix = mix / mix.sum()
    reference = float(values @ mix)
    return reference, reference - values


def base_label(mask):
    return 'empty' if mask == 0 else '+'.join(str(base) for base, bit in [(1, 1), (2, 2), (3, 4)] if mask & bit)
