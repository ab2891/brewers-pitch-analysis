"""Finite count/previous-pitch planning with explicit terminal-reward assumptions."""
import numpy as np

RESULTS = ('ball', 'strike', 'whiff', 'foul')


def states_for(actions):
    previous = [('START', 'START')] + [(a, r) for a in actions for r in RESULTS]
    return [(b, s, a, r) for b in range(4) for s in range(3) for a, r in previous]


def continuation(state, action, result):
    balls, strikes, _, _ = state
    if result == 'ball':
        return None if balls == 3 else (balls + 1, strikes, action, result)
    if result in ('strike', 'whiff'):
        return None if strikes == 2 else (balls, strikes + 1, action, result)
    if result == 'foul':
        return (balls, min(2, strikes + 1), action, result)
    return None


def solve(states, actions, probabilities, rewards, allowed=None, pitch_cost=.0001):
    """Minimize approximate terminal wOBA plus a declared tiny pitch-usage cost.

    probabilities maps (state, action) to named pitch-outcome probabilities.
    Rewards include walk, hbp, out, single, extra_base, home_run.
    This is a model-implied association policy, not a causal optimum.
    """
    values = {state: 0.0 for state in states}
    for key, distribution in probabilities.items():
        if any(p < 0 or not np.isfinite(p) for p in distribution.values()) or not np.isclose(sum(distribution.values()), 1, atol=1e-5):
            raise ValueError(f'Invalid outcome distribution for {key}')
    action_values = {}
    for _ in range(2000):
        updated = {}
        for state in states:
            available = actions if allowed is None else allowed[(state[0], state[1])]
            scores = {}
            for action in available:
                q = pitch_cost
                for result, probability in probabilities[(state, action)].items():
                    next_state = continuation(state, action, result)
                    if next_state is not None:
                        reward = values[next_state]
                    elif result == 'ball':
                        reward = rewards['walk']
                    elif result in ('strike', 'whiff'):
                        reward = 0
                    else:
                        reward = rewards[result]
                    q += probability * reward
                scores[action] = q
            action_values[state] = scores
            updated[state] = min(scores.values())
        error = max(abs(updated[s] - values[s]) for s in states)
        values = updated
        if error < 1e-9:
            break
    else:
        raise ValueError('Non-absorbing or nonconvergent count policy')
    policy = {s: min(action_values[s], key=action_values[s].get) for s in states}
    return policy, action_values
