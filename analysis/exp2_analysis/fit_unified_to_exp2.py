#!/usr/bin/env python3
"""
fit_unified_to_exp2.py — Fit unified Eq. (14) to Exp 2 five-option data

Primary model fitting for Exp 2: per-participant, per-block maximum likelihood
estimation of the unified integrator on next-choice prediction task.

Free parameters (per block):
  - k_field (0.1-10): field strength
  - omega_base (0.05-2): oscillation frequency
  - zeta (0.1-5): damping ratio
  - m0 (0.5-10): baseline mass
  - gain (0-50): mass gain per reward
  - a_sensitivity (0.3-3): matching exponent (softmax temperature)
  - W_hat (5×5 off-diagonal, 20 free params): coupling matrix (Block 2 only)

Block 1 (Independent): W fixed to 0
Block 2 (Coupled): W estimated as free parameters (per design spec)

Usage:
    python fit_unified_to_exp2.py                      # fit all sessions
    python fit_unified_to_exp2.py --participant PID    # fit one participant
    python fit_unified_to_exp2.py --block 1 --test     # test mode: Block 1 only
    python fit_unified_to_exp2.py --maxiter 200        # override optimizer iters

Output:
    results/fitted_params.csv       — per-participant-block parameters
    results/fit_summary.csv         — NLL, AIC, BIC, next-choice accuracy
    results/fit_report.txt          — summary and diagnostics
"""

import sys
import os
import argparse
import warnings
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
from scipy.optimize import differential_evolution

# Add shared module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))


# =========================================================================
# Configuration
# =========================================================================

DATA_DIR = Path(__file__).parent.parent.parent / "task_data"  # Where CSV downloads land
RESULTS_DIR = Path(__file__).parent.parent / "exp2_results"

# Parameter bounds per design spec
PARAM_BOUNDS = {
    'k_field': (0.1, 10.0),
    'omega_base': (0.05, 2.0),
    'zeta': (0.1, 5.0),
    'm0': (0.5, 10.0),
    'gain': (0.0, 50.0),
    'a_sensitivity': (0.3, 3.0),
    'temperature': (0.01, 1.0),
}

# Block-specific configs
BLOCK_CONFIGS = {
    1: {'coupling': 'independent', 'n_phases': 8, 'w_free': False},
    2: {'coupling': 'coupled', 'n_phases': 8, 'w_free': True},  # W has 20 free params
}


# =========================================================================
# Data Loading
# =========================================================================

def load_session_data(csv_path):
    """
    Load and validate Exp 2 CSV from browser task.

    Returns:
        dict: {
            'participant_id': str,
            'session_id': str,
            'block_1': df (click-level),
            'block_2': df (click-level),
            'coupling_matrix': array (Block 2 only),
        }
    """
    df = pd.read_csv(csv_path)

    # Validate required columns
    required = [
        'chosen_option', 'reward_outcome', 'timestamp_ms', 'phase_id',
        'latent_value_1_pre', 'latent_value_2_pre', 'latent_value_3_pre',
        'latent_value_4_pre', 'latent_value_5_pre',
        'block_id', 'coupling_condition'
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in {csv_path}: {missing}")

    pid = df['participantId'].iloc[0]
    sid = df['sessionId'].iloc[0]

    # Extract coupling matrix from metadata if present
    coupling_matrix = None
    if 'couplingMatrix' in df.columns:
        coupling_matrix = df['couplingMatrix'].iloc[0]

    return {
        'participant_id': pid,
        'session_id': sid,
        'block_1': df[df['block_id'] == 1].reset_index(drop=True),
        'block_2': df[df['block_id'] == 2].reset_index(drop=True),
        'coupling_matrix': coupling_matrix,
    }


# =========================================================================
# Model Fitting (placeholder for actual integrator call)
# =========================================================================

def fit_block(block_df, block_id, maxiter=200, seed=42):
    """
    Fit unified model to one block of data via maximum likelihood.

    Args:
        block_df: Click-level dataframe for this block
        block_id: 1 or 2
        maxiter: DE population iterations
        seed: Random seed for reproducibility

    Returns:
        dict: {
            'params': fitted parameter array,
            'nll': negative log likelihood,
            'aic': Akaike info criterion,
            'bic': Bayesian info criterion,
            'accuracy': next-choice prediction accuracy,
        }
    """
    if len(block_df) == 0:
        return None

    # TODO: Integrate with model_wrapper.simulate_and_score for 5-option case
    # For now, placeholder that returns dummy results
    n_clicks = len(block_df)
    n_params = 7  # k, omega, zeta, m0, gain, a_sens, temp (+ W if Block 2)
    if block_id == 2:
        n_params += 20  # Off-diagonal W matrix

    # Dummy results
    fitted_params = np.random.uniform(0, 1, n_params)
    nll = np.random.uniform(500, 1000)
    aic = 2 * n_params + 2 * nll
    bic = np.log(n_clicks) * n_params + 2 * nll
    accuracy = np.random.uniform(0.4, 0.6)

    return {
        'block_id': block_id,
        'n_clicks': n_clicks,
        'params': fitted_params,
        'nll': nll,
        'aic': aic,
        'bic': bic,
        'accuracy': accuracy,
        'converged': True,
    }


# =========================================================================
# Main Pipeline
# =========================================================================

def main():
    parser = argparse.ArgumentParser(description='Fit unified model to Exp 2 data')
    parser.add_argument('--participant', type=str, help='Fit one participant only')
    parser.add_argument('--block', type=int, choices=[1, 2], help='Fit one block only')
    parser.add_argument('--maxiter', type=int, default=200, help='DE iterations')
    parser.add_argument('--test', action='store_true', help='Test mode (1 session, limited iters)')
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Collect CSV files to fit
    if args.test:
        print("TEST MODE: fitting 1 session with limited iterations")
        csv_files = sorted(DATA_DIR.glob('exp2_*.csv'))[:1]
        maxiter = 50
    else:
        csv_files = sorted(DATA_DIR.glob('exp2_*.csv'))
        maxiter = args.maxiter

    if not csv_files:
        print(f"No CSV files found in {DATA_DIR}")
        print("Awaiting Exp 2 data collection...")
        sys.exit(0)

    print(f"Found {len(csv_files)} session(s)")
    print(f"Optimizer: differential_evolution, maxiter={maxiter}")

    # Results accumulation
    all_params = []
    all_summaries = []

    for csv_path in csv_files:
        try:
            print(f"\nLoading {csv_path.name}...")
            session = load_session_data(csv_path)

            pid = session['participant_id']
            print(f"  Participant: {pid}")

            # Fit each block
            for block_id in [1, 2] if not args.block else [args.block]:
                block_df = session[f'block_{block_id}']
                if len(block_df) == 0:
                    continue

                print(f"  Block {block_id}: {len(block_df)} clicks...", end='', flush=True)
                result = fit_block(block_df, block_id, maxiter=maxiter)

                if result:
                    all_params.append({
                        'participantId': pid,
                        'sessionId': session['session_id'],
                        'blockId': block_id,
                        **{f'param_{i}': v for i, v in enumerate(result['params'])}
                    })

                    all_summaries.append({
                        'participantId': pid,
                        'sessionId': session['session_id'],
                        'blockId': block_id,
                        'n_clicks': result['n_clicks'],
                        'nll': result['nll'],
                        'aic': result['aic'],
                        'bic': result['bic'],
                        'accuracy': result['accuracy'],
                        'converged': result['converged'],
                    })

                    print(f" NLL={result['nll']:.1f}, Acc={result['accuracy']:.3f}")

        except Exception as e:
            print(f"  ERROR: {e}")
            continue

    # Save results
    if all_params:
        df_params = pd.DataFrame(all_params)
        params_file = RESULTS_DIR / 'fitted_params.csv'
        df_params.to_csv(params_file, index=False)
        print(f"\nSaved: {params_file}")

    if all_summaries:
        df_summary = pd.DataFrame(all_summaries)
        summary_file = RESULTS_DIR / 'fit_summary.csv'
        df_summary.to_csv(summary_file, index=False)
        print(f"Saved: {summary_file}")

        # Human-readable report
        report_file = RESULTS_DIR / 'fit_report.txt'
        with open(report_file, 'w') as f:
            f.write("Exp 2 Model Fitting Report\n")
            f.write("=" * 60 + "\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            f.write(f"Sessions: {len(df_summary.groupby('sessionId'))}\n")
            f.write(f"Total blocks: {len(df_summary)}\n")
            f.write(f"Mean NLL: {df_summary['nll'].mean():.1f}\n")
            f.write(f"Mean accuracy: {df_summary['accuracy'].mean():.3f}\n")

        print(f"Saved: {report_file}")

    print("\nFitting complete.")


if __name__ == "__main__":
    main()
