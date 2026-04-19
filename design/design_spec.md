# Design Specification: Integrated Theory Experimental Test

**Status:** Draft v0.2. Revised to cover three-experiment arc.
**Author:** David J. Cox
**Version:** 0.2 (2026-04-17)
**Relationship to other work:**
- Target framework: Cox (2026), *Toward a Dynamical Systems Account of Behavior
  Networks* (preprint: https://www.researchgate.net/publication/403079477 ;
  code: https://github.com/david-j-cox/integrating-behavioral-processes).
- Prior experiment: Cox (under review), *Testing Behavior Dynamic Models to
  Predict Choice in a Non-Stationary Two-Choice Foraging Environment*
  (2-choice task, 60 humans, 22 models fit, HMM-dominant result).
- Engagement reference: Young, Hancock, Watson, Howatt, Southern, & Payne
  (2026), *Video game engines as the new "virtual" Skinner box*, JEAB.

---

## Overview: Three-experiment structure

This manuscript tests the Cox (2026) unified dynamical systems framework for
behavior networks through three experiments with increasing ecological
complexity:

- **Experiment 1** fits the unified model to existing 2-choice data from the
  prior paper. This is a gate check: if the framework cannot compete with the
  best continuous-dynamics models on 2D data, it needs revision before
  proceeding.
- **Experiment 2** is a purpose-built 5-option concurrent schedule task that
  tests the framework's three unique predictions (coupling propagation, mass
  accumulation, oscillatory return) in the simplest possible preparation.
- **Experiment 3** is a resource harvesting game that tests whether the
  framework's predictions generalize to a richer, ecologically motivated
  environment with energy budgets, variable reward magnitudes, and visible
  coupling.

---

# EXPERIMENT 1: Model Fit to Existing Data

## 1.1 Purpose

Establish baseline performance of the unified Eq. (14) on the existing
2-choice foraging dataset before committing to new data collection. This is
a necessary gate: if the framework's 2D reduction cannot compete with
existing continuous-dynamics models, the theory needs revision.

## 1.2 Data source

The existing dataset from Cox (under review):
- 60 human participants (Prolific), browser-based 2-choice foraging task
- 360 s per session, ~924 clicks per session average, 200 ms cooldown
- Four unsignaled phases: symmetric baseline, A advantage, B advantage
  (reversal), scarcity with alternating bonus pulses
- 55,455 click events with ground-truth latent values logged per click
- Dynamic RR schedules with patch depletion (per-click depletion `d`,
  per-second recovery `r` on latent value)
- 22 models already fit: matching/melioration/kinetic/momentum/
  hill-climbing/ratio-invariance, Q-learning variants, HMMs (2-4 state),
  foraging models, EDM, baselines

Data location: `../real_data/`

## 1.3 What we fit

The unified Eq. (14) from the preprint, reduced to the 2D case (n = 2):

    m_i * ddot(B_i) = omega_i^2 * F_DE,i(B) - zeta * dot(B_i)
                      + sum_j w_{ij} * (B_j - B_j^0)

With n = 2, the coupling term `sum_j w_{ij}(B_j - B_j^0)` is absorbed
into the disequilibrium term (since B_1 + B_2 = 1). The fitted model is
therefore the 2D reduction with free parameters: `k_field`, `zeta`,
`omega_base`, `m0`, `gain`, `a_sensitivity`.

Fitting via maximum likelihood on next-choice prediction, same objective
as the 22-model comparison.

## 1.4 Pass criterion

The unified fit's next-choice negative log-likelihood must be competitive
with the best continuous-dynamics model in the existing leaderboard
(expected to be the kinetic model or melioration). "Competitive" means
within 5% of their NLL, or better. The unified fit does NOT need to beat
HMM (which dominates by thousands of AIC points using discrete latent
states, a fundamentally different modeling strategy).

If the unified fit loses to kinetic/melioration/momentum on AIC, the
framework's 2D reduction adds complexity without payoff and needs
theoretical revision before Exp 2.

## 1.5 Secondary analyses

- Compare the unified fit's parameter estimates (omega, zeta, mass
  trajectory) to the preprint's simulation predictions. Do the fitted values
  fall in plausible ranges?
- Qualitative comparison of fitted trajectories to observed allocation
  time series for representative participants.
- Report AIC, BIC, and next-choice accuracy alongside all 22 existing models
  for transparency.

---

# EXPERIMENT 2: Five-Option Concurrent Schedule Task

## 2.1 Motivation and relationship to Exp 1

Exp 1 establishes that the unified equation's 2D reduction is at least
competitive on existing data. But the 2-choice structure cannot test the
framework's three most distinctive predictions:

1. **Coupling propagation** (Eq. 11, 13): With n = 2, the coupling term is
   absorbed into the disequilibrium term. Coupling requires n >= 3.
2. **Mass accumulation** (Eq. 6-7): With only 3 transitions per session in
   Exp 1, the prediction that adaptation progressively slows with cumulative
   reinforcement cannot be tested cleanly.
3. **Damped oscillatory return** (Eq. 8-9, the BV piece): Exp 1 has no
   quiescence probes, so free-oscillation dynamics are never observable.

Exp 2 uses 5 response options and a purpose-built phase structure to make
all three predictions testable in a clean, minimal preparation.

## 2.2 What the framework uniquely predicts

From the preprint's unified dynamical equation:

    m_i * ddot(B_i) = omega_i^2 * F_DE,i(B) - zeta * dot(B_i)
                      + sum_j w_{ij} * (B_j - B_j^0)           (14)

Three predictions distinguish this from every model in the Exp 1 set:

**P1. Coupling propagation.** Displacing one response from its baseline
should propagate measurable displacement to coupled responses, in
proportion to `w_{ij}`, even when the coupled response's own schedule is
unchanged. With an experimenter-imposed W_true matrix, the framework
predicts that fitted `W_hat` recovers the imposed structure.

**P2. Mass accumulation as progressive slowing.** Eq. (6) treats mass as
`m_i ~ sum_t R_i(t)`, so behaviors with longer reinforcement histories
should be progressively harder to disrupt. Phases preceded by long blocks
(more cumulative reinforcement) should produce slower adaptation than
phases preceded by short blocks.

**P3. Damped oscillatory return.** Eqs. (8)-(9) predict that behavior
displaced from equilibrium returns via an underdamped oscillation with
frequency `omega_i` (scaling with local reinforcement rate) and damping
`zeta`. In a standard task, this oscillation is masked by continuous
contingency contact. A quiescence probe inserted after the participant has
contacted the new contingency (responded through the first ~25 clicks of a
phase transition) creates a window where the system is briefly unforced.
When the probe lifts, the post-release trajectory should reveal the
system's free response: a damped sinusoidal return, distinguishable from
a pure exponential decay. This is the single most unique prediction of the
BV piece.

## 2.3 Specific falsifiable hypotheses

All hypotheses are framed as formal contrasts. Alpha = .05, Bonferroni
correction across the five primary hypotheses (alpha_adj ~ .01 per test).

**H1 (coupling recovery).** Under the Coupled condition, per-participant
fitted `W_hat` from the unified-equation integrator recovers the
experimenter-imposed W_true above chance. Three metrics, all reported
without pre-committed thresholds:

- **Distance correlation (dCor; Szekely 2007)** between vectorized
  off-diagonal entries of `W_hat` and W_true. Zero iff independent;
  captures any dependence including nonlinear.
- **Mantel-style permutation test** comparing observed dCor to a null
  distribution from row/column-shuffled W_true (1000 permutations).
- **Topology recovery**: do the largest off-diagonal entries of W_hat
  correspond to the largest entries of W_true? Reported as a binary
  match rate across participants.

Falsified if group-level dCor is not significantly above the permutation
null. Supported if dCor is significant and topology recovery exceeds
chance (>20% for a 5x5 matrix).

**H2 (mass accumulation drives progressive slowing).** Adaptation latency,
operationalized as the number of clicks to reach within 25% of the new
B^0 after a phase boundary, is longer following long phases (200 clicks)
than following short phases (50 clicks). Primary test: paired Wilcoxon
signed-rank test within each participant, aggregated via one-sample
Wilcoxon on per-participant median differences.

Falsified if the long-vs-short difference is not in the predicted
direction. Supported if the difference is significant at p < .01.

**H3 (BV frequency scales with reinforcement rate).** Across participants
and conditions, adaptation speed (1 / adaptation latency) is positively
associated with per-option reinforcement rate, controlling for the
reinforcement ratio. Primary test: mixed-effects regression with rate as
a continuous predictor and ratio as a covariate.

Falsified if the rate coefficient is not significantly > 0 after
controlling for ratio. Supported if rate coefficient > 0 at p < .01.

**H4 (damped oscillatory return).** In quiescence-probe blocks, the
post-release choice-proportion trajectory shows evidence of damped
oscillation. Primary test: fit a damped sinusoid
`A * exp(-zeta * t) * cos(omega * t + phi) + B^0` to the post-release
window (first 15-20 seconds) and compare BIC to a pure exponential
`A * exp(-k * t) + B^0`.

Falsified if fewer than ~20% of probe blocks prefer the damped-sinusoid
model and group-level BIC favors the exponential. Supported if >= 40%
prefer damped-sinusoid and group-level BIC difference > 10.

**H5 (unified fit beats existing dynamic models).** On held-out blocks
(leave-one-phase-out cross-validation), the fitted unified Eq. (14)
integrator produces lower negative log-likelihood on next-choice
prediction than: generalized matching, melioration, kinetic model,
Q-learning (dual-rate), 3-state HMM, and MVT Threshold. Primary test:
paired-sample Wilcoxon signed-rank tests across participants.

Falsified if unified fit is not significantly better than the best
continuous-dynamics baseline. Supported if unified fit significantly
outperforms at least the continuous-dynamics baselines (matching,
melioration, kinetic, Q-learning). HMM may remain competitive on raw
fit; the claim is that the unified fit makes recoverable structural
predictions (H1, H4) that HMM does not.

## 2.4 Participants

- **N:** determined by Tier B power analysis (formal model recovery
  simulation). Placeholder: 80. Tier B will establish the minimum N at
  which H1 (coupling recovery, the highest-variance estimate) reaches
  80% power.
- **Recruitment:** Prolific, matching Exp 1. Compensation at ~$12/hr.
- **Inclusion:** age 18+, fluent English, desktop browser (5-option layout
  requires adequate screen width).
- **Exclusion:** fewer than 80% of expected clicks, zero switches across a
  full block, total inactivity > 60 s within a block.

## 2.5 Apparatus

- **Platform:** Browser-based, vanilla HTML/CSS/JS, mirroring Exp 1
  architecture (see Exp 1 task code at
  `measuring-behavior-trajectories/experiment/` for reference layout).
- **Hosting:** Vercel (static site deploy).
- **Backend:** Supabase (Postgres). Insert-only Row Level Security via
  public anon key. Participants write events; cannot read. Event log
  uploaded at session end.
- **Module layout:**
  - `task/index.html` -- single entry point, screen flow
  - `task/css/style.css` -- layout
  - `task/js/config.js` -- schedule parameters, condition assignment,
    coupling matrices, block-length tables
  - `task/js/state.js` -- task engine (5 RR timers, coupling application,
    reward sampling, phase detection, quiescence probe logic)
  - `task/js/ui.js` -- DOM render, 5-button layout, score display
  - `task/js/logger.js` -- event array, metadata, JSON/CSV export
  - `task/js/main.js` -- flow control, event wiring
  - `task/js/supabase-upload.js` -- Supabase upload

## 2.6 Task structure

### 2.6.1 Response options

Five response buttons arranged horizontally, each labeled with a neutral
symbol (Option 1 through Option 5). One is designated the **target**
(Option 3, the middle button); the other four are **side channels**. All
five are on independent dynamic random-ratio (RR) schedules with patch
depletion matching Exp 1: each option has a latent value `V_i` in [0, 1]
that depletes by `d_i` per click and recovers at rate `r_i` per second.
On each click, reward is delivered with probability equal to `V_i` at that
moment.

### 2.6.2 Baseline schedules

Side channels run on fixed schedules throughout the session:

| Option | Role         | Mean RR | Recovery rate (r) | Expected rate |
|--------|--------------|---------|--------------------|---------------|
| 1      | Side channel | RR-20   | 0.050/s            | ~0.050 rein/s |
| 2      | Side channel | RR-40   | 0.025/s            | ~0.025 rein/s |
| 3      | **Target**   | varies  | varies by phase    | varies        |
| 4      | Side channel | RR-60   | 0.017/s            | ~0.017 rein/s |
| 5      | Side channel | RR-80   | 0.012/s            | ~0.012 rein/s |

The target alternates between RR-10 (rich, ~0.100 rein/s) and RR-100
(lean, ~0.010 rein/s) across phases. This matches the preprint simulations
(Figures 7-9) for direct comparability.

### 2.6.3 Phase structure (ABABABAB reversal with uneven lengths)

Each block contains **8 phases** alternating A (target rich) / B (target
lean). Phase boundaries are **completely unsignaled** (no cue, no screen
change, no announcement). This matches Exp 1's convention.

Phase lengths alternate between long (200 clicks) and short (50 clicks)
within each block: {200, 200, 50, 50, 200, 200, 50, 50} clicks per
phase. A counterbalanced mirror {50, 50, 200, 200, 50, 50, 200, 200} is
assigned to half the participants. This provides the within-subject
contrast for H2 (mass accumulation): adaptation following long phases
(more cumulative reinforcement) vs. adaptation following short phases.

### 2.6.4 Coupling manipulation (within-subject)

Each participant completes two blocks in a single session, order
counterbalanced:

- **Independent block:** The five RR timers advance independently. Each
  option's latent value depends only on its own clicks and recovery rate.
  This replicates the standard concurrent-schedule preparation.

- **Coupled block:** An experimenter-imposed coupling matrix W_true
  governs cross-option influence. Clicking option i adds
  `w_{ij} * delta_V` to the latent value of coupled options j, where
  `delta_V` is the depletion caused by the click on i. The coupling is
  **invisible** to the participant: no visual cue, no animation, no
  instruction about coupling. W_true is unique per participant, drawn
  from a distribution (details in Section 2.8), and recorded in the data
  for post-hoc recovery analysis.

The analysis (H1) asks whether fitted `W_hat` recovers the imposed
W_true above chance. The specific topology of W_true is treated as
exploratory, not constrained to canonical forms.

### 2.6.5 Quiescence probes

Four of the seven phase transitions within each block are followed by a
**quiescence probe**. The probe is NOT placed at the phase boundary
itself. Instead:

1. The phase transition occurs silently (schedule rates change).
2. The participant responds normally for ~25 clicks, contacting the new
   contingency and beginning to adjust.
3. All buttons are disabled (visibly grayed out) for ~10 seconds.
4. Buttons re-enable without warning.
5. The first 15-20 seconds of post-release responding are recorded as the
   **free-response window** for H4.

The rationale for the post-contact placement: the participant must have
experienced the new contingency (been displaced from the old B^0) before
the probe creates a meaningful free-response test. Placing the probe at
the boundary itself would test exploratory sampling, not dynamical return.

No point loss occurs during the probe in Exp 2. Point loss is reserved
for Exp 3 (energy budget design).

Probe placement is counterbalanced: odd transitions vs even transitions,
alternated across participants.

### 2.6.6 Session structure

Each participant completes a **single session** with two blocks:

1. Consent (identical to Exp 1)
2. Prolific ID capture
3. Instructions (5-option layout, depleting patches; no mention of phases,
   coupling, or probes)
4. Practice block (30 s, not logged)
5. Countdown (5 s)
6. **Block 1:** 8 phases at uneven lengths + 4 quiescence probes
   (~6-7 minutes)
7. Mid-session 30-s break (score displayed)
8. **Block 2:** 8 phases at uneven lengths + 4 quiescence probes
   (~6-7 minutes)
9. Post-task demographics (1 minute)
10. Debrief + Prolific completion code

**Total session time: approximately 18 minutes.**

## 2.7 Data collected

The event log mirrors Exp 1's CSV format with Exp 2 additions.

**Core columns (same as Exp 1):**
- `participant_id`, `session_id`, `timestamp_ms`, `absolute_timestamp`,
  `click_index`, `chosen_option` (1 through 5), `reward_outcome`,
  `points_earned`, `cumulative_score`, `time_since_prev_click_ms`
- `phase_id`, `phase_label`, `latent_value_{1..5}_pre`,
  `latent_value_{1..5}_post`, `reward_probability_used`
- `run_length`, `switch_flag`, `total_clicks_so_far`,
  `total_rewards_so_far`

**Exp 2 additions:**
- `block_id` (1 or 2)
- `coupling_condition` ("independent" | "coupled")
- `coupling_condition_order` ("indep_first" | "coupled_first")
- `phase_length_condition` ("long" | "short"; 200 or 50 clicks)
- `phase_length_sequence` ("long_first" | "short_first")
- `w_true_matrix` (JSON-serialized 5x5 matrix, stored once per session)
- `quiescence_probe_flag` (true if this click falls within 15 s after a
  probe release)
- `quiescence_probe_id` (which probe this is, 1-4 within block)
- `clicks_since_phase_transition` (for the post-contact probe placement)
- `phase_transition_flag` (true on first click after a boundary)
- `cum_R_{1..5}` (cumulative per-option reinforcement for mass analysis)

## 2.8 Coupling matrix generation

Each Coupled-block participant receives a unique W_true. Generation:

1. Start with a 5x5 zero matrix.
2. Randomly select k edges (off-diagonal pairs (i,j) with i != j),
   where k is drawn uniformly from {3, 4, 5, 6}.
3. For each selected edge, assign a coupling weight drawn uniformly from
   [0.1, 0.4].
4. Symmetrize: W_true[i,j] = W_true[j,i] = max(W_true[i,j], W_true[j,i]).
5. Set diagonal to 0.
6. Record the full matrix in the session metadata.

This produces a variety of sparse, symmetric coupling structures without
constraining to canonical topologies. The analysis fits W_hat as a free
5x5 matrix and tests recovery against the known W_true.

## 2.9 Analysis plan

### 2.9.1 Data preparation

Same pipeline as Exp 1: raw `events.csv` -> `events_processed.csv` via
`analysis/transform.py`. Validates, computes rolling statistics, produces
session-level summary in `session_metrics.csv`.

### 2.9.2 Model fitting

**Primary model:** Unified Eq. (14) integrator from `model.py` in the
preprint repo. Per-participant, per-block fit via maximum likelihood on
next-choice prediction. Free parameters:

- `k_field`, `zeta`, `omega_base` (global per block)
- `W_hat` (5x5 off-diagonal, 20 free parameters in unconstrained fit)
- `a_sensitivity` (matching exponent)
- `m0`, `gain` (mass: `m = m0 + gain * cum_R`)

**Baselines for H5:**
- 3-state HMM (Exp 1 winner)
- MVT Threshold (top foraging model from Exp 1)
- Generalized matching (continuous update)
- Melioration
- Kinetic model
- Q-learning (dual learning rates)

Implementations carried over from Exp 1 codebase.

### 2.9.3 Primary statistical tests

Each hypothesis in Section 2.3 maps to one pre-registered test. Five
tests, Bonferroni corrected (alpha_adj ~ .01).

### 2.9.4 Secondary / exploratory analyses

- Parameter comparisons (k, omega, zeta, mass) between Independent and
  Coupled blocks. Coupling should affect W_hat; other parameters should
  be stable.
- Quiescence-probe trajectory visualization, group-averaged.
- HMM comparison: refit 3-state HMM to Exp 2 data and report AIC
  alongside unified fit. The claim is not that the unified fit dominates
  HMM on fit quality, but that it makes recoverable structural predictions
  (coupling, mass, oscillation) that HMM cannot represent.
- Adaptation latency distributions, visualized per phase position.

---

# EXPERIMENT 3: Resource Harvesting Game (Outline)

## 3.1 Purpose

Test whether the framework's predictions generalize from a minimal
concurrent-schedule preparation (Exp 2) to a richer, ecologically
motivated environment. Exp 3 introduces:

- **Energy budgets (constant point loss):** Points decay continuously,
  creating a foraging pressure analogous to metabolic costs in behavioral
  ecology. This changes the choice dynamic: participants must maintain a
  positive energy balance, not just accumulate points.
- **Variable reward magnitudes:** Each harvest yields variable points
  (small/medium/large), not binary reinforcement. Variable magnitudes
  sustain responding better than variable timing alone (Hancock, in
  Young et al., 2026).
- **Visible coupling (optional condition):** In one condition, harvesting
  from a patch visibly accelerates regeneration of connected patches,
  allowing participants to learn the coupling structure.
- **Richer visual and mechanical engagement:** Thematic resource patches,
  harvest animations, goal/level structure, score progression. Informed
  by Young et al. (2026) on game engines as experimental platforms.

## 3.2 Key design features (preliminary)

- Browser-based game (Phaser.js, PixiJS, or vanilla canvas). Deployable
  to Vercel.
- Five resource patches visible simultaneously (no avatar movement; keeps
  discrete-choice structure comparable to Exp 2).
- Dynamic RR schedules with patch depletion (matching Exp 2 mechanics at
  the engine level).
- "Storm" events as quiescence probes: screen dims, patches gray out,
  points decay at a visible rate. When the storm lifts, free-response
  window is recorded. Point loss during storms creates salience for the
  wait duration.
- Goal structure: reach point thresholds per "level" (= phase). Level
  transitions are thematically marked but rate changes are unsignaled.
- Prolific bonus tied to final score for consequential outcomes.
- Session length: ~25 minutes if engagement features sustain quality
  responding.

## 3.3 Relationship to Exp 2

Exp 3 replicates Exp 2's hypothesis tests (H1-H5) in the richer
environment. If the framework's predictions hold in both Exp 2's minimal
preparation and Exp 3's ecologically motivated game, that is strong
evidence for generalizability. If they hold only in Exp 2, the framework
may be specific to simple concurrent schedules and limited in applied
utility.

The energy budget (constant point loss) is a deliberate Exp 3 addition
because point loss has been shown to differentially influence choice
distinct from gains. This cannot be introduced in Exp 2 without
confounding the clean test of the framework's predictions.

## 3.4 Status

Exp 3 design is deferred until Exp 2 data are collected and analyzed.
Full design spec, power analysis, and task code will be developed after
Exp 2 results are known. If Exp 2 fails to support the framework's
predictions, Exp 3 design will be revised accordingly.

---

## Open questions for Tier B (power analysis)

The following decisions are deferred until the Tier B model-recovery
simulations are complete:

1. **Final sample size.** Placeholder: 80. Tier B should establish the
   minimum N at which H1 (coupling recovery) is detectable at 80% power.
2. **Final quiescence window duration.** Current guess: 10 s. Tier B
   should sweep [5, 10, 15, 20] seconds on synthetic trajectories and
   pick the shortest duration at which H4's damped-sinusoid fit is
   reliably distinguishable from a pure exponential.
3. **Final block-length contrast.** Current guess: 200 vs 50. Tier B
   should confirm the short-phase condition still produces detectable
   mass-driven slowing.
4. **Coupling matrix sparsity.** Current guess: 3-6 edges per W_true.
   Tier B should test recovery rates at different sparsity levels.

## Pre-registration and timeline

- **v0.2 (this document):** three-experiment spec, all design decisions
  locked for Exp 2.
- **Stage 0 (Exp 1 model fit):** fit unified equation to existing data.
  Gate check before proceeding.
- **Tier B (power analysis):** model-recovery simulation using `model.py`.
  Locks final N, quiescence duration, block-length contrast, sparsity.
- **Pre-registration:** after Tier B, register Exp 2 on OSF using this
  document plus the power-analysis report.
- **Tier C (task code):** build Exp 2 browser task. Mirrors Exp 1 module
  architecture.
- **Pilot:** 5-10 participants for QA.
- **Data collection:** single Prolific batch.
- **Analysis and writeup:** using preprint `model.py` for fitting.
- **Exp 3:** design, build, collect, analyze after Exp 2 is complete.

## Known limitations and honest caveats

- **The HMM result from Exp 1 is a structural challenge.** If
  participants genuinely switch between discrete regimes, continuous
  dynamics describes fine structure within regimes, not the whole picture.
  The claim is that coupling recovery (H1), mass accumulation (H2), and
  oscillatory return (H4) are interpretable in continuous terms that HMMs
  cannot parsimoniously represent.
- **Humans strategize.** The quiescence probe assumes post-release
  behavior reveals the dynamical system's free response. Participants may
  reason explicitly about the blackout. Mitigation: the probe is placed
  post-contact (after ~25 clicks into the new contingency), so the
  displacement is real, not inferred. Analyze the first 2-3 post-release
  clicks separately from later clicks.
- **Patch depletion complicates the matching baseline.** Depletion is not
  part of the unified equation's matching-equilibrium definition. Compute
  B^0 two ways: from instantaneous latent values (matching Exp 1) and
  from steady-state equilibrium assuming constant depletion. Report both.
- **Coupling operationalization is one of many.** Implementing coupling as
  latent-value flow between options is an experimenter-imposed choice.
  Other operationalizations (punishment coupling, timer acceleration) are
  equally valid. Report this prominently in the methods.
- **Single-session within-subject coupling risks order effects.** The
  counterbalancing (Independent-first vs Coupled-first) should control
  for this, but if an order effect is detected, the analysis will include
  order as a covariate.
- **Point loss excluded from Exp 2.** Point loss differentially
  influences choice distinct from gains. Including it in Exp 2 would
  confound the clean test of the framework. Exp 3 addresses this
  limitation by introducing energy budgets as a deliberate manipulation.

---

*End of design spec v0.2. Next: Stage 0 (Exp 1 model fit), then Tier B
power analysis.*
