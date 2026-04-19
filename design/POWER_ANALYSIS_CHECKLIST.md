# Power Analysis Results Checklist

**Trigger:** When `power_analysis.py` completes

**Timeline:** Check this file ~04:00-13:00 UTC on 2026-04-18

---

## Expected Output

Power analysis should produce two files in `design/results/power_analysis/`:

1. **`recovery_by_sample_size.csv`**
   - Columns: N, parameter, recovery_rate, n_reps
   - Rows: One per parameter per N value
   - Example:
     ```
     N,parameter,recovery_rate,n_reps
     20,k_field,0.3,5
     20,omega_base,0.4,5
     20,zeta,0.2,5
     ...
     120,k_field,0.95,5
     120,omega_base,0.98,5
     ```

2. **`power_analysis_report.md`**
   - Summary statistics
   - Recommendation for final N
   - Example text: "Recommended N = 80 (all parameters recover >80%)"

---

## Interpretation Guide

### What the numbers mean

**recovery_rate:** Percentage of simulation runs where fitted parameter was within 50% of ground truth

Example:
- If k_field ground truth = 3.0, recovery means fitted k ∈ [1.5, 4.5]
- recovery_rate = 0.80 means 80% of fits recovered k in that range

### Reading the results table

**Healthy results look like:**
```
N        k_field  omega_base  zeta   m0    gain  a_sens  W_hat
20       0.2      0.3         0.1    0.3   0.4   0.8     NaN
40       0.4      0.5         0.2    0.6   0.7   0.95    NaN
60       0.6      0.7         0.4    0.8   0.9   1.0     0.5
80       0.8      0.85        0.6    0.9   0.95  1.0     0.7
100      0.9      0.95        0.8    0.95  1.0   1.0     0.85
120      0.95     1.0         0.95   1.0   1.0   1.0     0.95
```

**Pattern:** Recovery rates generally increase with N (upward trend)

**Success criterion:** All parameters >80% at recommended N

### What if results are concerning?

**Scenario 1: Recovery plateaus before 80%**
- Example: stays at 50% even at N=120
- **Interpretation:** Parameter is unidentifiable or optimization not converging
- **Action:** 
  - Check parameter bounds are reasonable
  - Verify synthetic data generation is correct
  - Consider increasing maxiter (was 200)
  - May need to fix parameter or simplify model

**Scenario 2: One parameter much harder to recover**
- Example: k_field at 60%, others at 90%+
- **Interpretation:** That parameter has less sensitivity to task
- **Action:** May be acceptable; report in appendix
- **Alternative:** Could increase N just for that parameter if feasible

**Scenario 3: W_hat recovery very low**
- Example: W_hat recovery at 0-30% even at N=120
- **Interpretation:** Coupling matrix is hard to fit with current task design
- **Action:** 
  - Expected (20 parameters, 1000 clicks per session = 50:1 data-to-param ratio)
  - Consider relaxing recovery criterion for W (e.g., 50% instead of 80%)
  - Or accept lower power on H1 (coupling recovery hypothesis)

---

## Decision Tree

### Question 1: Are all parameters >80% at some N?

**YES** → Go to Question 2

**NO** → 
- Review results file for which parameters are problematic
- Consider:
  - Increasing task duration (more clicks = more data per session)
  - Increasing maxiter in power_analysis.py (was 200)
  - Relaxing recovery criterion (was 50% of ground truth)
  - Model reformulation before full launch
- Document decision in PREREGISTRATION_TEMPLATE.md
- Proceed to pre-registration with caveats

### Question 2: At what N do all parameters reach 80%?

**N ≤ 60** → Proceed with N = 60 (or recommended N)

**N = 80-100** → Proceed with N = 80 or 100

**N = 120** → 
- Budget check: $1-2/session × 120 = $120-240 for full study
- Feasible? Yes → Use N = 120
- Feasible? No → Use N = 80 and accept slightly lower power
- Document trade-off in pre-registration

### Question 3: Is W_hat (coupling matrix) recovery <50%?

**NO** (W_hat recovery >50%) → Proceed as normal

**YES** (W_hat recovery <50%) →
- Expected (coupling is complex to estimate)
- Options:
  a) Accept lower power on H1; report results anyway
  b) Increase task duration (currently 7 min/block)
  c) Increase N to compensate
  d) Simplify W estimation (e.g., constrain to known structure)
- Document choice in pre-registration Appendix

---

## Actions to Take Upon Completion

### Step 1: Verify Completion (5 min)
```bash
# Check files exist and have content
ls -lah design/results/power_analysis/
wc -l design/results/power_analysis/*.csv design/results/power_analysis/*.md
```

### Step 2: Review Results (15 min)
```bash
# View summary
cat design/results/power_analysis/power_analysis_report.md

# View detailed table
head -20 design/results/power_analysis/recovery_by_sample_size.csv
```

### Step 3: Determine Final N (5 min)
From results, identify minimum N where ALL parameters ≥ 80%:
- Record as `FINAL_N` in your notes

### Step 4: Fill Pre-Registration (30 min)
Edit `design/PREREGISTRATION_TEMPLATE.md`:
1. Search for `[TO BE FILLED` and replace with actual values:
   - `[TO BE FILLED: Power analysis recommendation]` → `N = FINAL_N`
   - `[TO BE FILLED: After power analysis completes]` → Current date
   - `[TO BE FILLED: ~months]` → Reasonable timeline estimate

2. Add summary paragraph under "Sample Size Justification":
   ```
   Power analysis (power_analysis.py) tested N ∈ {20, 40, 60, 80, 100, 120}
   with 5 replications each. Success criterion: all parameters within 50%
   of ground truth. Results: [summary]. Recommended N = [FINAL_N].
   ```

3. Review for completeness; resolve any remaining placeholders

### Step 5: Stage 0 Gate Check (Already Done or Pending)
Check if Stage 0 fit has completed:
- If yes: review results for NLL comparison vs. baselines
- If no: wait for completion, then proceed to Step 6

### Step 6: Register on OSF (15 min)
1. Go to https://osf.io
2. Create new project "Integrated Theory Experiment 2"
3. Create registration under Registrations tab
4. Upload completed PREREGISTRATION_TEMPLATE.md
5. Share registration URL with collaborators

### Step 7: Deploy to Vercel (30 min)
1. If not already: `cd task && git init && git add . && git commit -m "Exp 2 task"`
2. Push to GitHub
3. Connect GitHub to Vercel
4. Set root directory to `task/`
5. Deploy
6. Test live at provided URL

### Step 8: Prolific Setup (30 min)
1. Log into Prolific
2. Create new study
3. Set study requirements, target N = FINAL_N
4. Set completion URL (Vercel deployment)
5. Configure payment rate (~$2-3 for 18-min task)
6. Consider pilot: launch to 5-10 participants first for QA

---

## Success Criteria Checklist

Before launching full data collection, verify:

- [ ] Power analysis completed without errors
- [ ] CSV and report files generated
- [ ] All parameters have recovery_rate metric
- [ ] Final N determined (all params >80% at that N)
- [ ] Stage 0 gate check passed (unified model ≥ baseline)
- [ ] Pre-registration filled and uploaded to OSF
- [ ] OSF registration has DOI/permanent URL
- [ ] Vercel deployment live and tested
- [ ] Prolific study created with correct URL and payment
- [ ] Pilot participants (5-10) have completed and data validated
- [ ] No issues found in pilot data (transform.py and initial QA)

---

## Troubleshooting Common Issues

### "power_analysis.py is still running"
- **Expected:** Sweep of 30 synthetics × 5 = ~40 hours
- **Check:** `ps aux | grep power_analysis`
- **If stuck:** May have crashed; check output file
- **Alternative:** Can pre-register with preliminary N=60 estimate while waiting

### "recovery_by_sample_size.csv is empty or truncated"
- **Cause:** Likely crashed mid-run
- **Check:** Last line of CSV to see last completed N
- **Option 1:** Re-run from that N forward (modify power_analysis.py)
- **Option 2:** Use results from last completed N; note as preliminary

### "W_hat recovery is NaN or missing"
- **Cause:** W matrix only estimated in Block 2; Block 1 has W=0 (no free params)
- **Expected behavior:** W_hat should only appear in Block 2 results
- **Check:** Verify BLOCK_CONFIGS in power_analysis.py

### "Results show no clear recommendation (recovery rate all <60%)"
- **Interpretation:** Model recovery is poor; parameters not well-identified
- **Actions:**
  1. Review task design (1000 clicks × 5 options = sparse per-option data)
  2. Consider increasing task duration
  3. Consider parameter constraints or simplifications
  4. May need Stage 0 results to inform whether unified model needs revision
- **Do not launch:** Until resolved with PI

---

## Questions to Answer

Before proceeding, be able to answer:

1. **What is the recommended N?**
   - Answer: [FINAL_N from results]

2. **At what N do all parameters reach 80% recovery?**
   - Answer: Specific N value

3. **Are there any parameters of concern?**
   - Answer: Which ones, and why (if any)

4. **How does this compare to initial power analysis test results?**
   - Previous (test): N=40, 2 reps (concerning results: mostly 50% or worse)
   - Current (full): N ∈ {20,40,60,80,100,120}, 5 reps (expected improvement)
   - **Expectation:** Recovery rates should improve with N and reps

5. **Is W_hat (coupling matrix) recovery adequate for H1?**
   - If recovery <50%: Plan to report but manage expectations on coupling detection power
   - If recovery 50-80%: Acceptable; adequate statistical power for hypothesis test
   - If recovery >80%: Strong power; coupling effects should be detectable

---

## Contact for Questions

If results are unclear or concerning:
- Review `analysis/power_analysis.py` source code
- Check ground truth parameters (k_field=3.0, omega_base=0.8, etc.)
- Verify synthetic data generation matches task structure
- Consult with PI before finalizing sample size

---

**Expected Timeline:** Check this checklist ~04:00-13:00 UTC on 2026-04-18

**Your action:** Do not launch Prolific until all steps 1-8 complete and success criteria met.
