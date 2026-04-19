#!/usr/bin/env python3
"""
transform.py — Exp 2 data pipeline

Processes raw click-level CSV from browser task:
1. Validates schema and data integrity
2. Computes rolling statistics (run length, inter-click intervals)
3. Aggregates to phase-level and session-level summaries
4. Outputs processed CSV and session metrics

Usage:
  python transform.py <raw_csv_path> <output_dir>
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime


def validate_schema(df):
    """Verify CSV has all required columns from task logger."""
    required_cols = [
        'participantId', 'sessionId', 'timestamp_ms', 'chosen_option',
        'reward_outcome', 'points_earned', 'cumulative_score',
        'phase_id', 'phase_label', 'block_id',
        'latent_value_1_pre', 'latent_value_2_pre', 'latent_value_3_pre',
        'latent_value_4_pre', 'latent_value_5_pre',
        'latent_value_1_post', 'latent_value_2_post', 'latent_value_3_post',
        'latent_value_4_post', 'latent_value_5_post',
        'coupling_condition', 'quiescence_probe_flag', 'switch_flag',
        'run_length', 'elapsed_time_s'
    ]

    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    return df


def compute_rolling_stats(df):
    """Add rolling window statistics."""
    df = df.sort_values(['participantId', 'sessionId', 'timestamp_ms']).reset_index(drop=True)

    # Inter-click interval (ICI) in seconds
    df['ici_sec'] = df.groupby(['participantId', 'sessionId'])['timestamp_ms'].diff() / 1000

    # Reward rate per option (recent 10 clicks)
    for opt in range(1, 6):
        opt_mask = df['chosen_option'] == opt
        df[f'reward_rate_opt{opt}_win10'] = (
            df.groupby(['participantId', 'sessionId'])['reward_outcome'].rolling(
                window=10, min_periods=1
            ).apply(lambda x: x[-1] if len(x) > 0 else 0, raw=False).reset_index(drop=True)
        )

    # Phase switches (0 if same as previous, 1 if different)
    df['phase_switch'] = df.groupby(['participantId', 'sessionId'])['phase_id'].diff().fillna(0) != 0

    # Quiescence window (flag entries within 5s post-quiescence-end)
    quiescence_events = df[df['quiescence_probe_flag'] == 1][['participantId', 'sessionId', 'timestamp_ms']].copy()
    quiescence_events['quiescence_end_ms'] = quiescence_events['timestamp_ms'] + 10000  # 10s probe duration

    df['post_quiescence'] = False
    for _, event in quiescence_events.iterrows():
        pid = event['participantId']
        sid = event['sessionId']
        end_time = event['quiescence_end_ms']
        mask = (df['participantId'] == pid) & (df['sessionId'] == sid) & \
               (df['timestamp_ms'] > end_time) & (df['timestamp_ms'] <= end_time + 5000)
        df.loc[mask, 'post_quiescence'] = True

    return df


def compute_phase_summary(df):
    """Aggregate to phase-level metrics."""
    phase_groups = df.groupby(['participantId', 'sessionId', 'phase_id', 'phase_label', 'block_id'])

    phase_summary = phase_groups.agg({
        'chosen_option': 'count',  # Total clicks
        'reward_outcome': 'sum',  # Total rewards
        'cumulative_score': 'last',  # Final score in phase
        'run_length': 'mean',  # Avg run length
        'switch_flag': 'sum',  # Total switches
        'ici_sec': 'mean',  # Avg inter-click interval
        'coupling_condition': 'first',
    }).rename(columns={'chosen_option': 'n_clicks', 'reward_outcome': 'n_rewards'})

    phase_summary['reward_rate'] = phase_summary['n_rewards'] / phase_summary['n_clicks']
    phase_summary['phase_duration_sec'] = phase_summary['ici_sec'] * phase_summary['n_clicks']

    return phase_summary.reset_index()


def compute_session_summary(df, phase_summary):
    """Aggregate to session-level metrics."""
    session_groups = df.groupby(['participantId', 'sessionId'])

    session_summary = pd.DataFrame({
        'participantId': session_groups['participantId'].first(),
        'sessionId': session_groups['sessionId'].first(),
        'n_clicks_total': session_groups.size(),
        'n_rewards_total': session_groups['reward_outcome'].sum(),
        'final_score': session_groups['cumulative_score'].last(),
        'n_switches_total': session_groups['switch_flag'].sum(),
        'avg_ici_sec': session_groups['ici_sec'].mean(),
        'coupling_condition_block1': session_groups[session_groups['block_id'] == 1]['coupling_condition'].first(),
        'coupling_condition_block2': session_groups[session_groups['block_id'] == 2]['coupling_condition'].first(),
    }).reset_index(drop=True)

    # Validity checks
    session_summary['is_valid'] = (
        (session_summary['n_clicks_total'] >= 100) &  # Minimum engagement
        (session_summary['n_switches_total'] > 0) &   # Evidence of switching
        (session_summary['avg_ici_sec'] > 0.3) &      # Not too fast (likely errors)
        (session_summary['avg_ici_sec'] < 10)         # Not too slow (disengaged)
    )

    return session_summary


def main():
    if len(sys.argv) < 2:
        print("Usage: python transform.py <raw_csv_path> [output_dir]")
        print("\nProcesses raw click-level CSV from Exp 2 task.")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else input_path.parent / "processed"
    output_dir.mkdir(exist_ok=True)

    print(f"Loading {input_path.name}...")
    df = pd.read_csv(input_path)

    print(f"Validating schema... ({len(df)} clicks)")
    df = validate_schema(df)

    print("Computing rolling statistics...")
    df = compute_rolling_stats(df)

    print("Aggregating to phase level...")
    phase_summary = compute_phase_summary(df)

    print("Aggregating to session level...")
    session_summary = compute_session_summary(df, phase_summary)

    # Output files
    processed_events = output_dir / f"{input_path.stem}_processed.csv"
    phase_output = output_dir / f"{input_path.stem}_phase_metrics.csv"
    session_output = output_dir / f"{input_path.stem}_session_metrics.csv"

    df.to_csv(processed_events, index=False)
    phase_summary.to_csv(phase_output, index=False)
    session_summary.to_csv(session_output, index=False)

    print(f"\nOutput files:")
    print(f"  {processed_events.name}")
    print(f"  {phase_output.name}")
    print(f"  {session_output.name}")

    print(f"\nSession summary:")
    print(f"  Valid sessions: {session_summary['is_valid'].sum()} / {len(session_summary)}")
    print(f"  Avg clicks per session: {session_summary['n_clicks_total'].mean():.0f}")
    print(f"  Avg final score: {session_summary['final_score'].mean():.0f}")
    print(f"  Avg switches: {session_summary['n_switches_total'].mean():.1f}")


if __name__ == "__main__":
    main()
