# Admin Test Version of Exp 2 Task

This is a separate version of the task with a real-time debug panel showing all hidden state.

## How to Use

1. Navigate to `task-admin/index.html` during testing (never deploy this to production)
2. The red **ADMIN DEBUG PANEL** appears in the bottom-right corner of the screen
3. It updates every 200ms with:
   - **Session**: Participant ID, session ID, block, coupling condition, counterbalancing
   - **Current Phase**: Phase ID, label (A/B), type, target rate, block
   - **Phase Progress**: Click count in current phase, expected phase length, total block clicks, rewards
   - **Latent Values**: Real-time reward probability (0-100%) for each option
   - **Coupling Matrix**: Full W matrix (Block 2 only) showing interdependencies
   - **Last Click**: Which option, run length, switches, score, time since last click
   - **Quiescence State**: Whether probe is active, duration, clicks-before-probe, recorded latencies

## What to Verify During Testing

### Phase Transitions
- Watch the phase counts in "Phase Progress"
- Click counts should match phase lengths: {200, 200, 50, 50, 200, 200, 50, 50} or mirror
- Phase changes should be **silent** (no announcement)
- Phase ID should increment correctly (1→2→3... or 9→10→11... for block 2)

### Coupling
- Block 1: Coupling Matrix should show "No coupling matrix"
- Block 2: W matrix should appear with sparse non-zero entries
- Check that W is symmetric and diagonal is 0
- Check that weights are in the range [0.1, 0.4]

### Quiescence Probes
- After ~25 clicks post-phase-transition, the screen should blackout for 10 seconds
- "Quiescence State" should show "Active: YES"
- During blackout: latent values should NOT change, no points awarded
- After release: first click latency should be recorded

### Latent Values
- Should start at 0.7 (or whatever config.startingLatentValues sets)
- Should recover gradually between clicks based on base rates
- Should deplete when clicked (always by 0.10 per option)
- Block 2: depletion should propagate via W matrix to coupled options
- Should never go below 0 or above 1

### Score & Rewards
- Should increment only when latent > random() at time of click
- No points during quiescence blackout
- Cumulative score should match the score display

### Button Order Counterbalancing
- Block Order (normal/mirror) shows phase length sequence
- Look for counterbalancing metadata in session info

## CSV Export Validation

After completing a test run, export the CSV data and check:

```
- phase_id changes at correct click counts
- quiescence_latency_ms populated for probe windows
- coupling_matrix JSON logged for Block 2
- reward values (0 or 1) match when latent value >  random threshold
- no points awarded when quiescence_active = true
- run_length and is_switch tracked correctly
```

## Deploying to Production

**CRITICAL: Never deploy task-admin to production.**
- The debug panel exposes hidden state that breaks the design
- Only the regular `/task/` version should go to Prolific
- Vercel deploys the root `task/` directory by default (confirmed in previous config)

## Contact

Questions about implementation details? Check console (F12) for logged errors and timing info.
