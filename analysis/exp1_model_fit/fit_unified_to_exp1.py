#!/usr/bin/env python3
"""
Stage 0: Fit the unified Eq. (14) to the existing 2-choice Exp 1 dataset.

Gate check: the framework's 2D reduction must be competitive with the best
continuous-dynamics models before committing to new data collection (Exp 2).

Usage:
    python fit_unified_to_exp1.py                   # fit all 60 participants
    python fit_unified_to_exp1.py --participant P1   # fit one participant
    python fit_unified_to_exp1.py --test             # quick sanity check on 1 participant

Output:
    results/fitted_params.csv       — per-participant fitted parameters
    results/fit_summary.csv         — per-participant NLL, AIC, BIC, accuracy
    results/fit_report.txt          — human-readable summary
"""

import sys
import os
import argparse
import time
import warnings

import numpy as np
import pandas as pd
from scipy.optimize import differential_evolution

# Add shared module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))
from model_wrapper import simulate_and_score


# =========================================================================
# Data loading
# =========================================================================

DATA_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..',
                 'real_data', '01_raw_data', 'events.csv')
)

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')


def load_participant_data(df, pid):
    """Extract arrays needed for fitting from one participant's data."""
    sub = df[df['participant_id'] == pid].sort_values('click_index').copy()

    click_times = sub['elapsed_time_s'].values
    # Convert A/B choices to 0/1 indices
    choices = (sub['chosen_option'] == 'B').astype(int).values
    phase_ids = sub['phase_id'].values
    latent_a = sub['latent_value_a_pre'].values
    latent_b = sub['latent_value_b_pre'].values
    rewards = sub['reward_outcome'].values

    return {
        'click_times': click_times,
        'choices': choices,
        'phase_ids': phase_ids,
        'latent_values_a': latent_a,
        'latent_values_b': latent_b,
        'rewards': rewards,
        'n_clicks': len(click_times),
    }


# =========================================================================
# Parameter bounds and objective
# =========================================================================

# Parameter names and their bounds for differential_evolution
PARAM_BOUNDS = {
    'k_field':       (0.1, 10.0),
    'omega_base':    (0.05, 2.0),
    'zeta':          (0.1, 5.0),
    'm0':            (0.5, 10.0),
    'gain':          (0.0, 50.0),
    'a_sensitivity': (0.3, 3.0),
    'temperature':   (0.01, 1.0),
}

PARAM_NAMES = list(PARAM_BOUNDS.keys())
BOUNDS_LIST = [PARAM_BOUNDS[k] for k in PARAM_NAMES]
N_PARAMS = len(PARAM_NAMES)


def objective(x, data):
    """Objective function for scipy.optimize: returns total NLL."""
    params = dict(zip(PARAM_NAMES, x))
    try:
        nll = simulate_and_score(
            params,
            click_times=data['click_times'],
            choices=data['choices'],
            phase_ids=data['phase_ids'],
            latent_values_a=data['latent_values_a'],
            latent_values_b=data['latent_values_b'],
            n_options=2,
            dt_resolution=0.05,  # 50ms steps; balance speed vs accuracy
        )
    except (FloatingPointError, ValueError, OverflowError):
        return 1e12  # penalty for numerical failure
    if np.isnan(nll) or np.isinf(nll):
        return 1e12
    return nll


# =========================================================================
# Fit one participant
# =========================================================================

def fit_one_participant(data, pid, maxiter=200, seed=42, verbose=True):
    """
    Fit the unified model to one participant via differential evolution.

    Returns dict with fitted params, NLL, AIC, BIC, accuracy.
    """
    t0 = time.time()
    n = data['n_clicks']

    if verbose:
        print(f"  Fitting {pid} ({n} clicks)...", end=' ', flush=True)

    result = differential_evolution(
        objective,
        bounds=BOUNDS_LIST,
        args=(data,),
        maxiter=maxiter,
        seed=seed,
        tol=1e-6,
        atol=1e-8,
        polish=True,
        workers=1,  # safe for Dropbox filesystem
    )

    elapsed = time.time() - t0
    nll = result.fun
    fitted = dict(zip(PARAM_NAMES, result.x))

    # AIC and BIC
    aic = 2 * N_PARAMS + 2 * nll
    bic = N_PARAMS * np.log(n) + 2 * nll

    # Compute choice accuracy: for each click, does the model predict
    # the correct option more than 50%?
    accuracy = compute_accuracy(fitted, data)

    if verbose:
        print(f"NLL={nll:.1f}, AIC={aic:.1f}, acc={accuracy:.3f}, "
              f"time={elapsed:.1f}s")

    return {
        'participant_id': pid,
        'n_clicks': n,
        'nll': nll,
        'aic': aic,
        'bic': bic,
        'accuracy': accuracy,
        'converged': result.success,
        'fit_time_s': elapsed,
        **fitted,
    }


def compute_accuracy(params, data):
    """
    Compute next-choice prediction accuracy by running the integrator
    forward and checking whether P(observed_choice) > 0.5 at each step.
    """
    from model_wrapper import (
        integrator_step, bv_frequency_from_rates,
        behavioral_mass, softmax_choice_prob
    )

    n = data['n_clicks']
    n_options = 2
    B = np.ones(n_options) / n_options
    V = np.zeros(n_options)
    cum_R = np.zeros(n_options)
    W = np.zeros((n_options, n_options))

    correct = 0
    current_time = 0.0

    for i in range(n):
        click_t = data['click_times'][i]
        latent_vals = np.array([data['latent_values_a'][i],
                                data['latent_values_b'][i]])
        values = latent_vals ** params['a_sensitivity']
        v_sum = values.sum()
        B0 = values / v_sum if v_sum > 0 else np.ones(n_options) / n_options

        rates = np.maximum(latent_vals, 1e-6)
        omega = bv_frequency_from_rates(rates, params['omega_base'])
        masses = behavioral_mass(cum_R, m0=params['m0'], gain=params['gain'])

        time_to_advance = click_t - current_time
        if time_to_advance > 0:
            n_steps = max(1, int(time_to_advance / 0.05))
            dt_actual = time_to_advance / n_steps
            for _ in range(n_steps):
                B, V = integrator_step(B, V, B0, masses, omega,
                                       params['zeta'], params['k_field'],
                                       W, dt_actual)

        probs = softmax_choice_prob(B, temperature=params['temperature'])
        predicted = np.argmax(probs)
        if predicted == data['choices'][i]:
            correct += 1

        cum_R[data['choices'][i]] += latent_vals[data['choices'][i]]
        current_time = click_t

    return correct / n


# =========================================================================
# Main
# =========================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Fit unified Eq. (14) to Exp 1 data (Stage 0 gate check)')
    parser.add_argument('--participant', type=str, default=None,
                        help='Fit a single participant ID')
    parser.add_argument('--test', action='store_true',
                        help='Quick test: fit first participant only')
    parser.add_argument('--maxiter', type=int, default=200,
                        help='Max iterations for differential evolution')
    args = parser.parse_args()

    os.makedirs(RESULTS_DIR, exist_ok=True)

    print(f"Loading data from {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    pids = sorted(df['participant_id'].unique())
    print(f"Found {len(pids)} participants, {len(df)} total clicks")

    if args.participant:
        pids = [args.participant]
    elif args.test:
        pids = pids[:1]

    print(f"\nFitting {len(pids)} participant(s), maxiter={args.maxiter}")
    print(f"Parameters: {PARAM_NAMES}")
    print(f"Bounds: {BOUNDS_LIST}\n")

    results = []
    for pid in pids:
        data = load_participant_data(df, pid)
        result = fit_one_participant(data, pid, maxiter=args.maxiter)
        results.append(result)

    # Save results
    results_df = pd.DataFrame(results)

    params_path = os.path.join(RESULTS_DIR, 'fitted_params.csv')
    results_df.to_csv(params_path, index=False)
    print(f"\nSaved fitted parameters to {params_path}")

    summary_path = os.path.join(RESULTS_DIR, 'fit_summary.csv')
    summary_cols = ['participant_id', 'n_clicks', 'nll', 'aic', 'bic',
                    'accuracy', 'converged', 'fit_time_s']
    results_df[summary_cols].to_csv(summary_path, index=False)
    print(f"Saved fit summary to {summary_path}")

    # Print summary
    print(f"\n{'='*60}")
    print("FIT SUMMARY")
    print(f"{'='*60}")
    print(f"Participants fit: {len(results)}")
    print(f"Mean NLL:      {results_df['nll'].mean():.1f} "
          f"(SD {results_df['nll'].std():.1f})")
    print(f"Mean AIC:      {results_df['aic'].mean():.1f} "
          f"(SD {results_df['aic'].std():.1f})")
    print(f"Mean accuracy: {results_df['accuracy'].mean():.3f} "
          f"(SD {results_df['accuracy'].std():.3f})")
    print(f"Converged:     {results_df['converged'].sum()}/{len(results)}")
    print(f"Total time:    {results_df['fit_time_s'].sum():.0f}s")

    # Parameter summary
    print(f"\nFitted parameter means (SD):")
    for p in PARAM_NAMES:
        print(f"  {p:15s}: {results_df[p].mean():.4f} ({results_df[p].std():.4f})")

    # Write report
    report_path = os.path.join(RESULTS_DIR, 'fit_report.txt')
    with open(report_path, 'w') as f:
        f.write("Stage 0: Unified Eq. (14) Fit to Exp 1 Data\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Participants: {len(results)}\n")
        f.write(f"Model: unified Eq. (14), 2D reduction (n=2)\n")
        f.write(f"Free parameters ({N_PARAMS}): {', '.join(PARAM_NAMES)}\n")
        f.write(f"Optimizer: differential_evolution, maxiter={args.maxiter}\n\n")
        f.write(f"Mean NLL:      {results_df['nll'].mean():.2f} "
                f"(SD {results_df['nll'].std():.2f})\n")
        f.write(f"Mean AIC:      {results_df['aic'].mean():.2f} "
                f"(SD {results_df['aic'].std():.2f})\n")
        f.write(f"Mean BIC:      {results_df['bic'].mean():.2f} "
                f"(SD {results_df['bic'].std():.2f})\n")
        f.write(f"Mean accuracy: {results_df['accuracy'].mean():.4f} "
                f"(SD {results_df['accuracy'].std():.4f})\n")
        f.write(f"Converged:     {results_df['converged'].sum()}/{len(results)}\n\n")
        f.write("Parameter means (SD):\n")
        for p in PARAM_NAMES:
            f.write(f"  {p:15s}: {results_df[p].mean():.4f} "
                    f"({results_df[p].std():.4f})\n")
        f.write(f"\nGate check criterion: unified fit NLL must be within 5% of\n")
        f.write(f"the best continuous-dynamics model from Exp 1's leaderboard.\n")
        f.write(f"Compare these results against the 22-model comparison.\n")
    print(f"Saved report to {report_path}")


if __name__ == '__main__':
    main()
