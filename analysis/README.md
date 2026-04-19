# Analysis Pipeline

Complete data processing and modeling pipeline for all three experiments.

## Structure

```
analysis/
├── shared/              # Shared utilities
│   ├── model_wrapper.py # Unified integrator wrapper + scoring
│   └── __init__.py
├── exp1_model_fit/      # Stage 0: Fit unified model to Exp 1 baseline
│   └── fit_unified_to_exp1.py
├── exp2_analysis/       # Exp 2: 5-option task analysis
│   └── fit_unified_to_exp2.py
├── design/              # Exp design utilities
│   ├── power_analysis.py       # Tier B: model recovery simulation
│   └── design_spec.md
├── transform.py         # Data pipeline: raw CSV → processed
└── README.md            # This file
```

## Data Flow

### Exp 2 Complete Pipeline

1. **Collect data** via browser task (task/)
   - Outputs: `exp2_<PROLIFIC_ID>.csv` (click-level events)

2. **Transform** raw CSV → processed metrics
   ```bash
   python transform.py exp2_P123.csv output/
   ```
   - Inputs: Raw click-level CSV from task
   - Outputs:
     - `exp2_P123_processed.csv` — click-level with rolling stats
     - `exp2_P123_phase_metrics.csv` — phase-level aggregates
     - `exp2_P123_session_metrics.csv` — session-level summary

3. **Fit unified model** per-participant, per-block
   ```bash
   python exp2_analysis/fit_unified_to_exp2.py
   ```
   - Inputs: Processed CSV files
   - Outputs:
     - `results/fitted_params.csv` — per-block parameters (k, ω, ζ, m₀, gain, a, W)
     - `results/fit_summary.csv` — NLL, AIC, BIC, accuracy
     - `results/fit_report.txt` — summary statistics

4. **Compare models** (H5: hypothesis test)
   ```bash
   python exp2_analysis/compare_baselines.py
   ```
   - Baseline models: 3-state HMM, MVT Threshold, Kinetic, Melioration, Q-learning
   - Output: Model comparison table (AIC/BIC, Δ from unified)

5. **Analyze results** per hypotheses (H1-H5)
   - H1: Coupling recovery (Pearson/dCor of W_hat vs W_true)
   - H2: Mass accumulation (correlation of m with phase duration)
   - H3: Oscillatory return (damped oscillation detection)
   - H4: Unsignaled phase detection (change-point analysis)
   - H5: Unified vs baselines (model comparison)

## Key Scripts

### transform.py
Processes raw click-level CSV from browser task into analysis-ready data.

**Input schema:** (from `js/logger.js`)
- participantId, sessionId, timestamp_ms, chosen_option
- reward_outcome, points_earned, cumulative_score
- phase_id, phase_label, block_id, coupling_condition
- latent_value_*_pre, latent_value_*_post
- quiescence_probe_flag, switch_flag, run_length, elapsed_time_s

**Outputs:**
- Phase-level metrics: n_clicks, n_rewards, reward_rate, avg_run_length, phase_duration_sec
- Session-level: validity flags, overall engagement stats
- Rolling windows: inter-click intervals, reward rates per option (10-click window)

**Usage:**
```bash
python transform.py data/exp2_P123.csv output_dir/
```

### exp2_analysis/fit_unified_to_exp2.py
Maximum likelihood parameter estimation per participant per block.

**Free parameters (7 + 20 for Block 2):**
- Block 1: k_field, omega_base, zeta, m0, gain, a_sensitivity, temperature
- Block 2: same 7 + 20 off-diagonal W elements (5×5 coupling matrix)

**Optimization:** Differential evolution, 200 iterations (default)

**Next-choice prediction task:** At each click, compute probability of observed choice given current latent state and integrated dynamics.

**Output columns:**
- NLL (negative log likelihood)
- AIC, BIC (information criteria)
- Accuracy (next-choice prediction: % correct)
- Converged (boolean: DE reached tolerance)

**Usage:**
```bash
python exp2_analysis/fit_unified_to_exp2.py                    # All sessions
python exp2_analysis/fit_unified_to_exp2.py --participant P123 # One participant
python exp2_analysis/fit_unified_to_exp2.py --maxiter 500      # Higher precision
python exp2_analysis/fit_unified_to_exp2.py --block 1          # Block 1 only
python exp2_analysis/fit_unified_to_exp2.py --test             # Quick test
```

### exp1_model_fit/fit_unified_to_exp1.py (Stage 0)
Gate check: Fit unified 2D reduction (Eq. 14) to existing Exp 1 data.

Must demonstrate that unified model is competitive (within 5% NLL) with best
continuous-dynamics baselines (kinetic, melioration, momentum) before proceeding
to Exp 2 commitment.

**Output:** Determines go/no-go for Exp 2 launch.

### design/power_analysis.py (Tier B)
Model recovery simulation to determine sample size for Exp 2.

**Sweep:** N ∈ {20, 40, 60, 80, 100, 120} × 5 reps each

**Outputs:**
- Recovery rates per parameter at each N
- Recommendation: minimum N for 80% power on all parameters
- Timing estimates per N

## Analysis Workflow for Publication

### Before Experiment Launch
1. **Stage 0:** Run `fit_unified_to_exp1.py` → confirm unified model passes gate check
2. **Tier B:** Run `power_analysis.py` full sweep → determine N for pre-registration
3. **Pre-register:** OSF with final design + sample size + analysis plan

### After Data Collection
1. **QA:** Run `transform.py` on all sessions → flag invalid data (low engagement, timing issues)
2. **Model fitting:** Run `fit_unified_to_exp2.py` on all valid sessions
3. **Hypothesis tests:** For each H1-H5:
   - H1: Distance correlation of W_hat vs W_true (coupling recovery)
   - H2: Linear/spline regression of m vs phase length (mass accumulation)
   - H3: Frequency analysis on post-quiescence latent trajectories (Brunt-Väisälä frequency)
   - H4: Change-point detection on choice probability vs phase transitions
   - H5: Model comparison (AIC/BIC relative to unified)
4. **Robustness:** Sensitivity analysis on parameter bounds, initialization, solver tolerance
5. **Plotting:** Trajectory overlays, phase-averaged latent values, parameter recovery scatter

## Testing Locally

### Test mode (quick validation)
```bash
# Stage 0 gate check (1 participant, quick)
cd exp1_model_fit && python fit_unified_to_exp1.py --test

# Power analysis (N=20, 2 reps, timing estimate)
cd ../design && python power_analysis.py --test

# Exp 2 fitting (awaiting real data)
cd ../exp2_analysis && python fit_unified_to_exp2.py --test
```

## Dependencies

- pandas, numpy, scipy (optimization)
- scikit-learn (change-point detection for H4)
- matplotlib, seaborn (plotting)
- statsmodels (time-series analysis)

Install via:
```bash
~/.venvs/matching-diseq/bin/pip install -r requirements.txt
```

## Performance Notes

- **Exp 1 fit:** ~3-4 min per participant (60 participants → ~5 hours)
- **Power analysis full sweep:** ~30-40 hours (6 N values × 5 reps × ~1.5 hours per rep)
- **Exp 2 fit:** ~2-3 min per participant per block (typical N=80 → ~5 hours)

All computations should use `~/.venvs/matching-diseq/bin/python` (outside Dropbox venv).

## Troubleshooting

### Missing data file
If Stage 0 fit complains about missing Exp 1 CSV:
```bash
# Verify path in fit_unified_to_exp1.py DATA_PATH
# Should point to: /Users/davidjcox/Dropbox/Projects/.../real_data/01_raw_data/events.csv
```

### Power analysis takes too long
- Reduce N sweep range (e.g., just [40, 60, 80])
- Reduce reps (default 5, can lower to 3)
- Increase maxiter tolerance (currently 200, can reduce to 100)

### Model fitting not converging
- Check parameter bounds (in fit_unified_to_exp2.py)
- Increase maxiter (e.g., --maxiter 500)
- Verify data has sufficient variation (check transform.py output)
- Check coupling_matrix is correctly parsed from session metadata
