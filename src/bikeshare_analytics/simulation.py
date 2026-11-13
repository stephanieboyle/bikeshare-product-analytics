"""SYNTHETIC demonstration. No operator experiment or empirically calibrated effect."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize


def difference_interval(success_t, n_t, success_c, n_c, alpha=.05):
    if min(n_t, n_c) <= 1 or not (0 <= success_t <= n_t and 0 <= success_c <= n_c):
        raise ValueError('Valid counts with at least two observations per arm required')
    pt, pc = success_t / n_t, success_c / n_c
    estimate = pt - pc
    se = np.sqrt(pt * (1 - pt) / n_t + pc * (1 - pc) / n_c)
    half = norm.ppf(1 - alpha / 2) * se
    return estimate, estimate - half, estimate + half


def planned_n(p0=.70, effect=.02, power=.8):
    return int(np.ceil(NormalIndPower().solve_power(
        effect_size=abs(proportion_effectsize(p0 + effect, p0)), power=power,
        alpha=.05, ratio=1, alternative='two-sided')))


def diagnostics(estimates, lows, highs, target):
    estimates, lows, highs = map(np.asarray, (estimates, lows, highs))
    reps = len(estimates)
    coverage = np.mean((lows <= target) & (highs >= target))
    rejection = np.mean((lows > 0) | (highs < 0))
    return {'target_risk_difference': target, 'mean_estimate': float(estimates.mean()),
        'bias': float(estimates.mean() - target),
        'bias_mc_se': float(estimates.std(ddof=1) / np.sqrt(reps)),
        'coverage': float(coverage), 'coverage_mc_se': float(np.sqrt(coverage * (1 - coverage) / reps)),
        'rejection_rate': float(rejection),
        'rejection_mc_se': float(np.sqrt(rejection * (1 - rejection) / reps))}


def simulate(repetitions=2000, users=4000, seed=20261113):
    if repetitions < 100 or users < 100:
        raise ValueError('Use >=100 repetitions and >=100 users per arm')
    rng = np.random.default_rng(seed)
    scenarios = [
        ('null', .70, .70, 'complete', 0),
        ('plausible_effect', .70, .72, 'complete', .02),
        ('missing_at_random_complete_case', .70, .72, 'mar', .02),
        ('differential_missing_complete_case_BIASED', .70, .72, 'mnar', .02),
        ('immature_coded_failure_BIASED', .70, .72, 'immature_bad', .02),
        ('mature_cohort_only', .70, .72, 'mature', .02),
        ('spillover_at_half_saturation', .71, .73, 'complete', .02),
    ]
    result = {}
    for name, pc, pt, mode, target in scenarios:
        estimates, lows, highs = [], [], []
        for _ in range(repetitions):
            nc = nt = users
            if mode == 'mature':
                # Enrolment age is independent of allocation and outcomes; freeze cohort before looking.
                nc, nt = rng.binomial(users, .75, 2)
            sc, st = rng.binomial(nc, pc), rng.binomial(nt, pt)
            if mode in ('mar', 'mnar'):
                c_success = rng.binomial(sc, .9)
                c_failure = rng.binomial(nc - sc, .9)
                t_success = rng.binomial(st, .9 if mode == 'mar' else .95)
                t_failure = rng.binomial(nt - st, .9 if mode == 'mar' else .7)
                sc, nc = c_success, c_success + c_failure
                st, nt = t_success, t_success + t_failure
            elif mode == 'immature_bad':
                sc, st = rng.binomial(sc, .75), rng.binomial(st, .75)
            estimate, low, high = difference_interval(st, nt, sc, nc)
            estimates.append(estimate)
            lows.append(low)
            highs.append(high)
        result[name] = diagnostics(estimates, lows, highs, target)
    # Secondary repeated-event null stress test: four correlated intents per user.
    # Random beta propensity gives within-user ICC .2, with marginal p=.7.
    repeated = {'naive_event_independence_NULL': [[], [], []],
                'user_mean_robust_NULL': [[], [], []]}
    for _ in range(repetitions):
        c = rng.binomial(4, rng.beta(2.8, 1.2, users)) / 4
        t = rng.binomial(4, rng.beta(2.8, 1.2, users)) / 4
        estimate, low, high = difference_interval(t.sum() * 4, users * 4, c.sum() * 4, users * 4)
        for values, value in zip(repeated['naive_event_independence_NULL'], [estimate, low, high]):
            values.append(value)
        estimate = t.mean() - c.mean()
        se = np.sqrt(t.var(ddof=1) / users + c.var(ddof=1) / users)
        for values, value in zip(repeated['user_mean_robust_NULL'],
                                 [estimate, estimate - 1.96 * se, estimate + 1.96 * se]):
            values.append(value)
    result.update({key: diagnostics(*value, 0) for key, value in repeated.items()})
    payload = {'evidence_class': 'SYNTHETIC, not an operator experiment', 'seed': seed,
        'repetitions': repetitions, 'users_per_arm': users,
        'planned_users_per_arm_80pct': planned_n(), 'scenarios': result}
    Path('reports/figures').mkdir(parents=True, exist_ok=True)
    Path('reports/simulation.json').write_text(json.dumps(payload, indent=2))
    fig, axes = plt.subplots(1, 2, figsize=(11, 5), layout='constrained')
    names = list(result)
    labels = ['Null', '+2 pp', 'MAR outcomes', 'Differential missing*', 'Immature as failure*',
              'Mature cohort', 'Spillover (50%)', 'Naive repeat events*', 'User means (repeat)']
    y = np.arange(len(names))
    for ax, field, target in zip(axes, ['coverage', 'rejection_rate'], [.95, .05]):
        ax.barh(y, [result[n][field] for n in names], color='#23676f')
        ax.errorbar([result[n][field] for n in names], y,
                    xerr=[1.96 * result[n][field.replace('rate', 'mc_se') if field == 'rejection_rate'
                          else 'coverage_mc_se'] for n in names], fmt='none', color='black', capsize=2)
        ax.axvline(target, color='#b35534', linestyle='--', linewidth=1)
        ax.set(yticks=y, yticklabels=labels if ax is axes[0] else [], xlim=(0, 1),
               xlabel='95% interval coverage' if field == 'coverage' else 'Reject zero effect')
        ax.invert_yaxis()
    fig.suptitle(f'SYNTHETIC • {repetitions:,} repetitions, {users:,} users per arm')
    fig.text(.01, -.025, '*Deliberately flawed analyses. Whiskers: ±1.96 Monte Carlo SE. '
             'Rejection under +2 pp is power; under null it is false positives.', fontsize=9)
    fig.savefig('reports/figures/05_synthetic_diagnostics.png', dpi=170, bbox_inches='tight')
    plt.close(fig)
    return payload
