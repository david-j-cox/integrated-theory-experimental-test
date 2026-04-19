# Exp 2: Five-Option Foraging Task

## Overview

Browser-based task implementation for Experiment 2 of the integrated theory of behavior networks study. Participants click among 5 options to earn points under concurrent variable-interval schedules, with dynamic coupling in Block 2.

## Files

- **index.html** — Main entry point; all screen markup (consent, task, break, debrief)
- **css/style.css** — Professional responsive styling; grid layouts for 5 buttons
- **js/config.js** — Task configuration (phase schedule, latent values, quiescence probes, coupling matrix generator)
- **js/state.js** — Task engine: latent value dynamics, reward/depletion, coupling propagation
- **js/logger.js** — Event logging and data export (CSV/JSON)
- **js/ui.js** — UI rendering: screens, button state, score/timer/latent value display
- **js/main.js** — Orchestration: session flow, click handling, timer loop, condition assignment

## Session Flow

1. **Consent** — Informed consent form with checkbox
2. **Prolific ID** — Enter participant ID (required for data linking)
3. **Instructions** — Task overview (~5 seconds auto-advance)
4. **Countdown** — 5-second countdown before Block 1
5. **Block 1 (7 min)** — Independent condition: 5 buttons, 8 unsignaled phases, uneven phase lengths
6. **Break** — 30 seconds rest with manual continue button
7. **Countdown** — 5-second countdown before Block 2
8. **Block 2 (7 min)** — Coupled condition: random sparse coupling matrix applied
9. **Debrief** — Completion code for Prolific

Total duration: ~18 minutes

## Experimental Design

### Options (Base Schedules)
- Option 1: VI-20 (0.050/s recovery)
- Option 2: VI-40 (0.025/s recovery)
- Option 3: TARGET (0.100/s rich, 0.010/s lean, alternates per phase)
- Option 4: VI-60 (0.017/s recovery)
- Option 5: VI-80 (0.012/s recovery)

### Phases
- 16 total (2 blocks × 8 phases each)
- ABABABAB pattern per block (A=rich, B=lean)
- Uneven lengths: [200, 200, 50, 50, 200, 200, 50, 50] clicks (counterbalanced)

### Quiescence Probes
- 10-second blackout overlay
- Triggered after ~25 post-transition clicks
- Applied to phase transitions 1, 3, 5, 7 within each block

### Coupling (Block 2)
- Random sparse 5×5 matrix W with:
  - k ∈ {3, 4, 5, 6} edges
  - Weights ∈ [0.1, 0.4]
  - Symmetric structure
  - Unique per participant
- Coupling effect: depletion of option i propagates to j via W[i][j]

## Data Output

### CSV Export
Click-level event log with columns:
- `participantId`, `sessionId`, `timestamp_ms`, `chosen_option` (1-5)
- `reward_outcome` (0/1), `points_earned`, `cumulative_score`
- `phase_id`, `phase_label`, `block_id`
- `latent_value_1..5_pre` and `_post`
- `coupling_condition` (independent|coupled), `coupling_structure`
- `quiescence_probe_flag` (0/1)
- `run_length`, `switch_flag`, `time_since_prev_click_ms`
- Plus session metadata (blockOrder, phaseLengthOrder)

### JSON Export
Full session object including metadata and all events.

## Development

### Local Testing

```bash
cd task/
python3 -m http.server 8000
# Open http://localhost:8000/index.html in browser
```

### Deployment (Vercel)

1. Push to GitHub repo
2. Connect to Vercel
3. Set root directory to `task/`
4. Deploy

No build step required (static HTML/CSS/JS).

### Backend Integration (Supabase)

Currently, data is downloaded as CSV. To enable server-side upload:

1. Configure Supabase project and get URL + key
2. Update `main.js` uploadData() method with credentials
3. Uncomment logger.uploadToSupabase() call
4. Ensure Supabase table `exp2_events` has matching schema

## Browser Requirements

- Modern browser with ES6 support (Chrome, Firefox, Safari, Edge)
- JavaScript enabled
- ~50 MB memory for session data
- Stable connection (data loss if browser closes mid-session)

## Notes

- Prolific ID is required; session will not advance without it
- Participant must complete entire session for valid data
- Timer auto-ends blocks at 7 minutes; early termination possible via browser close
- Latent value displays update in real-time (cosmetic, not used in reward logic)
- Leaderboard is simulated (not real across sessions)
