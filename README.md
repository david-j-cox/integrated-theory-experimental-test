# integrated_theory_experimental_test

Testing the Cox (2026) unified dynamical systems framework for behavior
networks through three experiments.

## Three-experiment structure

**Experiment 1: Model fit to existing data.**
Fit the unified Eq. (14) to the existing 2-choice foraging dataset from
Cox (under review). Gate check: the framework's 2D reduction must be
competitive with existing continuous-dynamics models before new data
collection begins.

**Experiment 2: Five-option concurrent schedule task.**
Simple 5-button browser task. Dynamic RR schedules with patch depletion,
unsignaled phase transitions, within-subject coupling (invisible),
quiescence probes. Tests the three unique predictions: coupling
propagation (n=5), mass accumulation (uneven phase lengths), and damped
oscillatory return (post-contact probes). ~18 min session, Prolific.

**Experiment 3: Resource harvesting game.**
Richer environment with energy budgets (constant point loss), variable
reward magnitudes, visible coupling. Tests generalizability. Design
informed by Young et al. (2026, JEAB). Deferred until Exp 2 is complete.

## Directory layout

    integrated_theory_experimental_test/
    |-- README.md              <- this file
    |-- design/
    |   |-- design_spec.md     <- full spec, all three experiments (v0.2)
    |   `-- power_analysis.py  <- Tier B, pending
    |-- task/                  <- Exp 2 browser task (Tier C, pending)
    |-- 01_raw_data/           <- collected data
    |-- 02_transformed_data/   <- processed data
    |-- analysis/              <- fitting + hypothesis tests
    `-- manuscript/            <- writeup

## Related directories

- `../real_data/` -- Exp 1 dataset (2-choice, 60 participants, 22 models)
- `../BP_submission/` -- submitted preprint files
- Preprint code repo: https://github.com/david-j-cox/integrating-behavioral-processes

## Current status

- [x] Tier A: design spec v0.2 complete
- [ ] Stage 0: fit unified model to Exp 1 data (gate check)
- [ ] Tier B: power analysis via model recovery
- [ ] Pre-registration on OSF
- [ ] Tier C: build Exp 2 task (Vercel + Supabase)
- [ ] Pilot (5-10 participants)
- [ ] Exp 2 data collection
- [ ] Exp 2 analysis
- [ ] Exp 3 design, build, collect, analyze
- [ ] Manuscript

## Deployment

- **Exp 2:** Vercel (static site) + Supabase (Postgres, insert-only RLS)
- **Exp 3:** Same hosting, richer frontend (Phaser.js or similar)

## License

Same as the preprint code repo: MIT for code, CC-BY for data and
manuscript once those exist.
