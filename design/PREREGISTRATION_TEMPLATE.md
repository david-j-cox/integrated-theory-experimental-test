# Exp 2 Pre-Registration (OSF Template)

**Study Title:** Testing the Unified Theory of Behavior Networks: Coupling Propagation, Mass Accumulation, and Brunt-Väisälä Oscillations in Five-Option Foraging

**Authors:** David J. Cox, [co-authors]

**Experiment:** 2 of 3

**Registration Date:** 2026-04-18

---

## Summary

Experiment 2 tests three unique, quantitative predictions from the unified dynamical systems theory of behavior (Cox, 2026):

1. **Coupling propagation** (H1): Depletion of one option propagates to others via behavioral coupling
2. **Mass accumulation** (H2): Behavioral mass increases with cumulative reward exposure
3. **Brunt-Väisälä oscillations** (H3): Free-response trajectories show damped oscillatory return to baseline after perturbations

A single-session, browser-based five-option foraging task with within-subject phase manipulation and between-subjects coupling condition (visible only in data, not feedback) directly tests all three predictions.

---

## Study Design

### Participants
- **Sample size:** N = 60 (pragmatic target balancing statistical power and resource constraints)
- **Population:** Prolific Academic general population (US-based)
- **Exclusion criteria:** None beyond Prolific platform requirements
- **Target demographics:** Adult, English-literate

### Procedure

#### Session Structure
1. **Consent** (~2 min): Informed consent with checkbox
2. **Demographics** (~1 min): Prolific ID entry
3. **Instructions** (~1 min): Task overview (auto-advance after 5s)
4. **Block 1** (~7 min): Five-option concurrent RR task, unsignaled phase transitions
5. **Break** (~1 min): Rest with manual continue button
6. **Block 2** (~7 min): Identical structure, coupling matrix applied (unseen by participant)
7. **Debrief** (~1 min): Completion code display

**Total duration:** ~18 minutes

#### Task Design

**5 Response Options:**
- Option 1 (side): VI-20 (0.050/s recovery)
- Option 2 (side): VI-40 (0.025/s recovery)
- Option 3 (target): VI-10 rich (0.100/s) alternating VI-100 lean (0.010/s)
- Option 4 (side): VI-60 (0.017/s recovery)
- Option 5 (side): VI-80 (0.012/s recovery)

**Phase Schedule:**
- 16 total phases (2 blocks × 8 phases per block)
- ABABABAB pattern per block (A = target rich, B = target lean)
- Unsignaled transitions (participants must detect contingency changes)
- Uneven phase lengths: [200, 200, 50, 50, 200, 200, 50, 50] clicks
  - Counterbalanced: half of participants receive mirror [50, 50, 200, 200, ...]
  - Tests mass accumulation via varying exposure duration

**Block 1 (Independent):** Coupling matrix W = 0 (standard five-option task)

**Block 2 (Coupled):** Random sparse coupling matrix per participant
- Unique 5×5 symmetric W per participant
- k ∈ {3, 4, 5, 6} random edges
- Weights uniform [0.1, 0.4] per spec Section 2.8
- Coupling effect: V[j] -= w_ij × depletion[i] (unseen by participant)

**Quiescence Probes:**
- 10-second blackout overlay (no responses possible)
- Triggered after ~25 post-transition clicks
- Applied to phase transitions 1, 3, 5, 7 within each block
- Tests free-response dynamics and oscillatory return (H3)

#### Randomization
- **Phase length order:** Counterbalanced (normal vs. mirror) via random assignment
- **Block order:** [TO BE CONFIRMED: Within-subject? Between-subject?] Coupling condition
- **Coupling matrix:** Unique random sparse matrix per participant (Block 2 only)
- **Random seed:** Session timestamp used for reproducibility

---

## Hypotheses

### H1: Coupling Recovery
**Prediction:** Under the Coupled condition (Block 2), fitted coupling matrix W̃ significantly recovers the true coupling structure W_true (Pearson r > 0.40, or distance correlation > 0.30).

**Operationalization:** Per-participant, per-block maximum likelihood fit of unified Eq. (14) with W as free parameters (20 off-diagonal elements). Comparison of W̃ to W_true:
- **Primary metric:** Distance correlation (dCor) [robust to nonlinear relations]
- **Reporting:** Distribution of dCor across participants, 95% CI, effect size

**Analysis:** 
- Sample: Block 2 data only (coupled condition)
- Test: Bayesian highest density interval; Report dCor for all parameter pairs
- Baseline: Model with W = 0 has dCor ≈ 0.1 by chance; 0.30+ indicates signal

### H2: Mass Accumulation
**Prediction:** Behavioral mass parameter m increases with cumulative reward exposure, and this relationship is stronger in longer-exposure phases (high-n phases) than short-exposure phases (low-n phases).

**Operationalization:** Extract fitted m parameter per phase via block-level maximum likelihood fit. Regress m on cumulative rewards received by phase end:
- **Primary metric:** Spline regression slope (penalized) or linear regression R²
- **Reporting:** Slope, 95% CI; comparison across phase length groups

**Analysis:**
- Sample: All block × phase combinations (32 data points per participant)
- Test: Mixed-effects regression with random intercept per participant
- Prediction: Slope > 0 and steeper for [200, 200, 50, 50] phases than [50, 50, 200, 200] (phase length order interaction)

### H3: Brunt-Väisälä Oscillations
**Prediction:** Post-quiescence latent value trajectories exhibit damped oscillatory return to equilibrium, with oscillation frequency near the predicted Brunt-Väisälä frequency ω_B = sqrt(k × ζ) / m.

**Operationalization:** 
1. Extract quiescence probe events (10 per participant)
2. Isolate 5-second post-release latent trajectories per option
3. Fit second-order linear system (damped harmonic oscillator) to trajectory
4. Extract fitted frequency, damping ratio (ζ)
5. Compare to ω_B predicted from fitted model parameters

**Analysis:**
- Sample: Quiescence events in both blocks (up to 20 per participant)
- Metric: Distance between observed frequency and predicted ω_B (log scale)
- Test: One-sample t-test that mean |log(ω_obs / ω_B)| < 0.3 (within 35% error)
- Reporting: Mean frequency match, example trajectory plots

### H4: Phase Change Detection (Exploratory)
**Prediction:** Choice probabilities exhibit significant change-point(s) aligned with actual phase transitions, detectable via change-point analysis or HMM-style segmentation.

**Operationalization:** 
- Apply PELT change-point algorithm or rolling window χ² test to choice sequences
- Detect alignment of detected change-points with true phase boundaries
- Report F1 score (precision × recall)

**Analysis:**
- Sample: Phase sequences in both blocks (16 per participant)
- Metric: Proportion of true transitions detected vs. false positives
- Test: Binomial test that detection rate > chance (0.5)

### H5: Model Comparison (Primary Outcome)
**Prediction:** The unified Eq. (14) model provides better explanation of next-choice behavior (lower Δ AIC) than all five baseline models combined.

**Baseline Models:**
- 3-state HMM (Exp 1 winner)
- MVT Threshold (top foraging model)
- Kinetic model (continuous dynamics)
- Melioration (gradient-ascent choice rule)
- Q-learning with dual learning rates

**Operationalization:** 
- Per-participant, per-block fit each model via maximum likelihood
- Compute AIC for each
- Report Δ AIC (AIC_baseline - AIC_unified)

**Analysis:**
- Sample: All valid sessions, both blocks (typically N × 2 fits)
- Primary metric: Σ Δ AIC across all participants/blocks (should be > 0 for unified wins)
- Test: Bayesian model comparison; report Bayes Factor
- Reporting: AIC distribution, win-loss table, per-parameter recovery comparison

---

## Analysis Plan

### Data Preparation
1. **Quality assurance:**
   - Flag low-engagement sessions: <100 clicks, no switches, >60% inactivity
   - Verify coupling matrix correctly parsed from session metadata
   - Verify block durations ~7 min; remove if <4 min or >10 min

2. **Transformation:**
   - Run `analysis/transform.py` on raw CSV per spec Section 2.9.1
   - Outputs: phase-level and session-level metrics
   - Compute rolling statistics (reward rates, inter-click intervals)

3. **Invalid data handling:**
   - Exclude sessions failing QA checks (pre-registered in OSF)
   - Final sample size: _N_valid = [TO BE FILLED after QA]

### Model Fitting
- Per-participant, per-block fit via differential_evolution (200 iterations)
- Parameter estimation: MLE on next-choice prediction
- Output: fitted parameters + NLL/AIC/BIC + next-choice accuracy

### Hypothesis Tests
All tests pre-registered; two-tailed α = 0.05 unless otherwise specified.

**H1:** dCor(W̃, W_true) > 0.30? [Bayesian interval]
**H2:** Regression slope m~cumulative_reward > 0? [Mixed-effects t-test]
**H3:** |log(ω_obs / ω_B)| < 0.3? [One-sample t-test]
**H4:** Phase detection F1 > 0.5? [Binomial test]
**H5:** Σ Δ AIC > 0? [Bayes factor]

### Robustness Checks
- Sensitivity to parameter bounds (±10% on each bound)
- Alternative distance metrics (Kendall τ vs. dCor)
- Cross-validation: 80/20 train/test split on click sequences

---

## Sample Size Justification

Sample size determined via Tier B model recovery simulation (power_analysis.py) completed 2026-04-18 00:21 UTC:

- **Ground truth:** Known parameters (k_field=3.0, ω_base=0.8, ζ=1.2, m0=1.0, gain=8.0, a_sensitivity=1.0)
- **Task:** Synthetic 5-option data, 1000 clicks per synthetic session
- **Success criterion:** Fitted parameters within 50% of ground truth
- **Sweep:** N ∈ {20, 40, 60, 80, 100, 120}, 5 replications each
- **Results:** Recovery rates varied (omega_base 0.6-0.8, other parameters 0.0-0.4); no single N achieved 80% across all parameters
- **Recommendation (extrapolated):** N = 420 for 80% power across all parameters
- **Selected N:** 60 (pragmatic target given resource constraints; tradeoff accepted)

**Note:** Power analysis focused on model recovery (ability to fit and recover parameters). Recovery patterns were noisier than expected, suggesting parameter identifiability challenges within the current task design. N = 60 will provide moderate power; results will be reported with discussion of this tradeoff.

---

## Secondary Outcomes & Exploratory Analyses

- Time-series coherence between target option latent value and coupling-induced oscillations
- Parameter correlation structure (e.g., does ζ correlate with participant engagement?)
- Learning curves: phase-by-phase change in m and a_sensitivity
- Inter-individual differences: correlate fitted parameters with task experience (via Prolific demographics if available)

---

## Deviations from Design

**Expected deviations that warrant explanation (not pre-registered):**
- Coupling matrix not successfully generated for some Block 2 sessions (browser error)
- Participant disengagement (low click counts) on Block 2
- HTTP server timeout / data not uploaded (rare on Vercel)

**Planned handling:** Exclude affected sessions per QA criteria (pre-registered).

---

## Open Science Commitment

- **Pre-registration:** This form registered on OSF before data collection begins
- **Data release:** Anonymized session-level summary (participant ID, session ID, block, n_clicks, n_rewards, final_score, fitting results) released on OSF
- **Code release:** Analysis scripts (transform.py, fit_unified_to_exp2.py, hypothesis test scripts) released on GitHub
- **Materials:** Browser task code (HTML/CSS/JS) released on GitHub for reproducibility
- **Expected timeline:** 
  - Data collection: [TO BE FILLED: months]
  - Analysis: [TO BE FILLED: months]
  - Preprint: [TO BE FILLED: date]

---

## References

Cox, D. J. (2026). A unified dynamical systems theory of behavior networks. [Preprint].

Young, M. E., et al. (2026). Game engines as Skinner boxes: Towards digital behavior modification. Journal of the Experimental Analysis of Behavior.

[Additional references to Exp 1 baseline models and theory]

---

## Sign-Off

**Principal Investigator:** David J. Cox, Endicott College

**Date Registered:** [TO BE FILLED]

**OSF Project:** [TO BE FILLED]

**Data available at:** [GitHub repo URL]
