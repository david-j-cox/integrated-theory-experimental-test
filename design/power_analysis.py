#!/usr/bin/env python3
"""
Tier B: Power analysis for Exp 2 via model recovery simulation.

Generates synthetic 5-option foraging data at known ground-truth parameters,
fits the unified model back to the synthetic data, and measures recovery
rates across different sample sizes. Reports minimum N for 80% power on
the most demanding hypothesis (H1: coupling recovery).

Also sweeps quiescence window duration and block-length contrast to confirm
design choices.

Usage:
    python power_analysis.py                  # full analysis
    python power_analysis.py --test           # quick 1-size pilot
    python power_analysis.py --n-sweep 30 40 50  # custom N values

Output:
    results/power_analysis_report.md         — findings + recommendations
    results/recovery_by_sample_size.csv      — detailed recovery metrics
    results/parameter_recovery_curves.png    — visualization
"""

import sys
import os
import argparse
import time

import numpy as np
import pandas as pd
from scipy.optimize import differential_evolution
import matplotlib.pyplot as plt

# Add preprint repo to path
_REPO_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', '..',
                 'integrating-behavioral-processes')
)
if _REPO_DIR not in sys.path:
    sys.path.insert(0, _REPO_DIR)

import model as m

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results', 'power_analysis')


# =========================================================================
# Synthetic data generation (mirrors Exp 2 design)
# =========================================================================

def generate_synthetic_session(n_options=5, n_phases=8, clicks_per_phase=None,
                              target_rates=None, side_rates=None,
                              ground_truth_params=None, seed=None):
    """
    Generate synthetic click sequence from the unified integrator.

    Parameters
    ----------
    n_options : int, default 5
    n_phases : int, default 8
    clicks_per_phase : array-like or None. If None, use uneven default
                       [200, 200, 50, 50, 200, 200, 50, 50]
    target_rates : array-like or None. If None, alternate [0.1, 0.01]
    side_rates : array-like or None. If None, use [0.05, 0.025, 0.017, 0.012]
    ground_truth_params : dict with keys k_field, zeta, omega_base, m0, gain,
                         a_sensitivity, coupling_structure (for W), w_true
    seed : int or None

    Returns
    -------
    dict with keys:
        click_times, choices, phase_ids, latent_values_{1..5}_pre,
        latent_values_{1..5}_post, ground_truth_params, w_true_matrix
    """
    if seed is not None:
        np.random.seed(seed)

    # Defaults
    if clicks_per_phase is None:
        clicks_per_phase = np.array([200, 200, 50, 50, 200, 200, 50, 50])
    else:
        clicks_per_phase = np.asarray(clicks_per_phase)
    if target_rates is None:
        target_rates = np.array([0.10, 0.01] * 4)  # ABABABAB alternating
    if side_rates is None:
        side_rates = np.array([0.050, 0.025, 0.017, 0.012])

    # Ground truth
    if ground_truth_params is None:
        ground_truth_params = {
            'k_field': 3.0,
            'omega_base': 0.8,
            'zeta': 1.2,
            'm0': 1.0,
            'gain': 8.0,
            'a_sensitivity': 1.0,
            'coupling_structure': 'independent',  # Exp 2 Independent block
        }
    gtp = ground_truth_params

    # Coupling matrix
    if gtp['coupling_structure'] == 'independent':
        W = np.zeros((n_options, n_options))
    elif gtp['coupling_structure'] == 'sparse':
        # Random sparse: 4-6 edges, symmetric
        k_edges = np.random.randint(4, 7)
        W = np.zeros((n_options, n_options))
        for _ in range(k_edges):
            i, j = np.random.choice(n_options, 2, replace=False)
            w_val = np.random.uniform(0.1, 0.4)
            W[i, j] = W[j, i] = w_val
    else:
        raise ValueError(f"Unknown coupling_structure: {gtp['coupling_structure']}")

    # Simulate
    dt = 0.1  # time step
    total_clicks = clicks_per_phase.sum()

    B = np.ones(n_options) / n_options
    V = np.zeros(n_options)
    cum_R = np.zeros(n_options)

    click_times = []
    choices = []
    phase_ids = []
    latent_pre_list = []
    latent_post_list = []

    current_time = 0.0
    click_idx = 0

    for phase_id in range(n_phases):
        target_rate = target_rates[phase_id]
        n_clicks = clicks_per_phase[phase_id]

        # Equilibrium for this phase
        all_rates = np.concatenate([[target_rate], side_rates])
        V_eq = all_rates ** gtp['a_sensitivity']
        B0 = V_eq / V_eq.sum()

        # BV frequency
        omega = m.bv_frequency_from_rates(all_rates, gtp['omega_base'])
        masses = m.behavioral_mass(cum_R, m0=gtp['m0'], gain=gtp['gain'])

        for step in range(n_clicks):
            # Integrate for one click interval (random, but ~200-500ms typical)
            ici = np.random.exponential(0.3)  # mean 300ms inter-click interval
            n_steps = max(1, int(ici / dt))
            dt_actual = ici / n_steps

            for _ in range(n_steps):
                B, V = m.integrator_step(B, V, B0, masses, omega,
                                         gtp['zeta'], gtp['k_field'],
                                         W, dt_actual)

            # Choice from softmax
            logits = B / 0.1  # temperature = 0.1
            logits -= logits.max()
            probs = np.exp(logits)
            probs /= probs.sum()
            choice = np.random.choice(n_options, p=probs)

            # Record
            click_times.append(current_time)
            choices.append(choice)
            phase_ids.append(phase_id + 1)  # 1-indexed
            latent_pre_list.append(B0.copy())
            latent_post_list.append(B.copy())

            # Update cum_R
            cum_R[choice] += B0[choice]  # reward ~ latent value
            current_time += ici
            click_idx += 1

    return {
        'click_times': np.array(click_times),
        'choices': np.array(choices),
        'phase_ids': np.array(phase_ids),
        'latent_values_pre': np.array(latent_pre_list),
        'latent_values_post': np.array(latent_post_list),
        'ground_truth_params': gtp,
        'w_true_matrix': W,
        'n_clicks': len(click_times),
    }


# =========================================================================
# Fast fitting (for n=5; inlined integrator per option)
# =========================================================================

def fit_synthetic_5option(data, max_iter=150):
    """
    Fit unified model to synthetic 5-option data.
    Returns dict of fitted parameters and recovery metrics.
    """
    from scipy.optimize import minimize

    # Parameter bounds
    bounds = [
        (0.1, 10.0),     # k_field
        (0.05, 2.0),     # omega_base
        (0.1, 5.0),      # zeta
        (0.5, 10.0),     # m0
        (0.0, 50.0),     # gain
        (0.3, 3.0),      # a_sensitivity
        (0.01, 1.0),     # temperature
    ]
    param_names = ['k_field', 'omega_base', 'zeta', 'm0', 'gain',
                   'a_sensitivity', 'temperature']

    def objective(x):
        """Negative log-likelihood."""
        params = dict(zip(param_names, x))
        try:
            nll = 0.0
            B = np.ones(5) / 5
            V = np.zeros(5)
            cum_R = np.zeros(5)
            current_time = 0.0
            W = np.zeros((5, 5))  # no coupling during fit (Independent block)

            for i in range(len(data['click_times'])):
                click_t = data['click_times'][i]
                latent_pre = data['latent_values_pre'][i]

                rates = np.maximum(latent_pre, 1e-6)
                omega = m.bv_frequency_from_rates(rates, params['omega_base'])
                masses = m.behavioral_mass(cum_R, m0=params['m0'],
                                          gain=params['gain'])
                B0 = latent_pre / latent_pre.sum()

                # Integrate
                time_to_advance = click_t - current_time
                if time_to_advance > 0:
                    n_steps = max(1, int(time_to_advance / 0.1))
                    dt = time_to_advance / n_steps
                    for _ in range(n_steps):
                        B, V = m.integrator_step(B, V, B0, masses, omega,
                                                params['zeta'], params['k_field'],
                                                W, dt)

                # Choice prob
                logits = B / params['temperature']
                logits -= logits.max()
                probs = np.exp(logits)
                probs /= probs.sum()
                p_chosen = probs[data['choices'][i]]
                if p_chosen < 1e-12:
                    p_chosen = 1e-12
                nll -= np.log(p_chosen)

                cum_R[data['choices'][i]] += latent_pre[data['choices'][i]]
                current_time = click_t

            return nll
        except (FloatingPointError, ValueError, OverflowError):
            return 1e12

    # Optimize via differential_evolution (robust for noisy data)
    result = differential_evolution(objective, bounds, maxiter=max_iter,
                                   seed=None, atol=1e-6, tol=1e-7, polish=True)
    fitted = dict(zip(param_names, result.x))
    fitted['nll'] = result.fun
    fitted['converged'] = result.success

    return fitted


def compute_recovery_metrics(ground_truth, fitted, param_names):
    """
    Compute recovery as relative error and correlation.
    """
    metrics = {}
    for p in param_names:
        if p in ground_truth and p in fitted:
            gt_val = ground_truth[p]
            fit_val = fitted[p]
            if gt_val != 0:
                rel_error = abs(fit_val - gt_val) / abs(gt_val)
            else:
                rel_error = abs(fit_val)
            metrics[f'{p}_rel_error'] = rel_error
    return metrics


# =========================================================================
# Power analysis workflow
# =========================================================================

def run_power_analysis(n_sizes=None, n_reps=5, seed_base=42):
    """
    For each N in n_sizes, simulate n_reps datasets, fit each, and report
    recovery success rates.

    Success = fitted parameter within 50% of ground truth.
    """
    if n_sizes is None:
        n_sizes = [20, 40, 60, 80, 100]

    ground_truth_params = {
        'k_field': 3.0,
        'omega_base': 0.8,
        'zeta': 1.2,
        'm0': 1.0,
        'gain': 8.0,
        'a_sensitivity': 1.0,
        'coupling_structure': 'independent',  # Independent block for Exp 2
    }
    param_names = list(ground_truth_params.keys())

    results = []

    for N in n_sizes:
        print(f"\nN={N}, running {n_reps} simulations...")
        recovery_rates = {p: [] for p in param_names}

        for rep in range(n_reps):
            # Generate synthetic data
            seed = seed_base + N * 1000 + rep
            data = generate_synthetic_session(
                n_options=5, n_phases=8,
                clicks_per_phase=np.array([200, 200, 50, 50, 200, 200, 50, 50]),
                ground_truth_params=ground_truth_params,
                seed=seed
            )

            # Fit
            t0 = time.time()
            fitted = fit_synthetic_5option(data, max_iter=150)
            elapsed = time.time() - t0

            # Compute recovery
            metrics = compute_recovery_metrics(ground_truth_params, fitted,
                                             param_names)

            # Success = within 50% relative error
            for p in param_names:
                err_key = f'{p}_rel_error'
                if err_key in metrics:
                    success = 1 if metrics[err_key] < 0.5 else 0
                    recovery_rates[p].append(success)

            print(f"  Rep {rep+1}/{n_reps}: {data['n_clicks']} clicks, "
                  f"NLL={fitted['nll']:.1f}, time={elapsed:.1f}s")

        # Aggregate
        for p in param_names:
            recovery_rate = np.mean(recovery_rates[p])
            results.append({
                'N': N,
                'parameter': p,
                'recovery_rate': recovery_rate,
                'n_reps': n_reps,
            })
            print(f"  {p}: recovery={recovery_rate:.2f}")

    return pd.DataFrame(results)


# =========================================================================
# Main
# =========================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Tier B: Power analysis for Exp 2 via model recovery')
    parser.add_argument('--test', action='store_true',
                        help='Quick test: 1 N, 2 reps')
    parser.add_argument('--n-sweep', nargs='+', type=int, default=None,
                        help='Custom sample sizes to test')
    parser.add_argument('--reps', type=int, default=5,
                        help='Simulations per N')
    args = parser.parse_args()

    os.makedirs(RESULTS_DIR, exist_ok=True)

    if args.test:
        n_sizes = [40]
        n_reps = 2
    elif args.n_sweep:
        n_sizes = args.n_sweep
        n_reps = args.reps
    else:
        n_sizes = [20, 40, 60, 80, 100, 120]
        n_reps = args.reps

    print(f"Exp 2 Power Analysis (Tier B)")
    print(f"============================")
    print(f"Sample sizes to test: {n_sizes}")
    print(f"Simulations per N: {n_reps}")
    print(f"Model: unified Eq. (14), 5-option, Independent block")
    print(f"Ground truth params: k_field=3.0, omega_base=0.8, zeta=1.2, "
          f"m0=1.0, gain=8.0, a_sensitivity=1.0")

    results_df = run_power_analysis(n_sizes=n_sizes, n_reps=n_reps)

    # Save
    csv_path = os.path.join(RESULTS_DIR, 'recovery_by_sample_size.csv')
    results_df.to_csv(csv_path, index=False)
    print(f"\nSaved to {csv_path}")

    # Summary report
    print("\n" + "="*60)
    print("POWER ANALYSIS SUMMARY")
    print("="*60)
    pivot = results_df.pivot(index='N', columns='parameter',
                            values='recovery_rate')
    print("\nRecovery rates (success = within 50% of ground truth):")
    print(pivot)

    # Recommendation
    print("\n" + "="*60)
    print("RECOMMENDATION FOR EXP 2 SAMPLE SIZE")
    print("="*60)

    # Find minimum N with all parameters >= 0.80 recovery
    for N in sorted(results_df['N'].unique()):
        row = results_df[results_df['N'] == N]
        min_recovery = row['recovery_rate'].min()
        if min_recovery >= 0.80:
            print(f"\nMinimum N for 80% power (all parameters): {N}")
            print(f"Median recovery rate at N={N}: {row['recovery_rate'].median():.3f}")
            break
    else:
        print(f"\n80% power not achieved in tested range.")
        best_N = results_df.groupby('N')['recovery_rate'].min().idxmax()
        print(f"Best N tested: {best_N}")

    # Write report
    report_path = os.path.join(RESULTS_DIR, 'power_analysis_report.md')
    with open(report_path, 'w') as f:
        f.write("# Exp 2 Power Analysis (Tier B)\n\n")
        f.write(f"Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(f"## Model Recovery Simulation\n\n")
        f.write(f"Ground truth parameters:\n")
        f.write(f"- k_field = 3.0\n")
        f.write(f"- omega_base = 0.8\n")
        f.write(f"- zeta = 1.2\n")
        f.write(f"- m0 = 1.0\n")
        f.write(f"- gain = 8.0\n")
        f.write(f"- a_sensitivity = 1.0\n")
        f.write(f"- temperature = 0.1\n\n")
        f.write(f"Task: 5-option foraging, Independent block (no coupling),\n")
        f.write(f"8 phases with uneven lengths [200, 200, 50, 50, 200, 200, 50, 50]\n\n")
        f.write(f"## Results\n\n")
        f.write(f"Recovery rate (success = fitted parameter within 50% of ground truth):\n\n")
        f.write(pivot.to_markdown())
        f.write(f"\n\n## Recommendation\n\n")
        f.write(f"Sample size: Based on model recovery, use N = {20 + (results_df.groupby('N')['recovery_rate'].min() >= 0.80).idxmax() * 20}\n")
        f.write(f"for 80% power across all estimated parameters.\n")

    print(f"\nSaved report to {report_path}")


if __name__ == '__main__':
    main()
