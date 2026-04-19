// ============================================================
// state.js — Exp 2 task engine (5-option, coupling, quiescence)
// ============================================================

class TaskState {
  constructor(config) {
    this.config = config;
    this.reset();
  }

  reset() {
    // Latent values (one per option)
    this.latentValues = [...this.config.startingLatentValues];
    this.lastClickTimeMs = 0;
    this.clickIndex = 0;
    this.totalRewards = 0;
    this.cumulativeScore = 0;
    this.previousChoice = null;
    this.runLength = 0;
    this.lastSwitchTimeMs = 0;
    this.totalSwitches = 0;
    this.isPractice = false;
    this.cumulativeRewardsPerOption = [0, 0, 0, 0, 0];
    this.currentBlockId = 1;
    this.currentPhaseId = 1;
    this.wMatrix = null; // Coupling matrix (set for Block 2)
  }

  // ---- Phase helpers ----

  getPhaseAtTime(elapsedMs, blockId) {
    // Calculate which phase we're in based on cumulative click counts
    // For now, simple approach: derive from elapsed time
    // In practice, we track by click count per phase
    const phaseLengths = blockId === 1 ? this.config.phaseLengths : this.config.phaseLengthsMirror;

    let clicksSoFar = 0;
    for (let i = 0; i < phaseLengths.length; i++) {
      clicksSoFar += phaseLengths[i];
      // Note: we'll actually track this by click count, not elapsed time
    }

    return this.config.phases.find(p => p.blockId === blockId && p.id === this.currentPhaseId) || this.config.phases[0];
  }

  getCurrentPhase() {
    return this.config.phases.find(p => p.id === this.currentPhaseId);
  }

  // ---- Recovery + depletion ----

  updateLatentValues(dtSec, targetRate, sideRates) {
    // All options recover at their base rate
    const rates = [sideRates[0], sideRates[1], targetRate, sideRates[2], sideRates[3]];
    const depletionRate = 0.10; // shared depletion parameter

    for (let i = 0; i < 5; i++) {
      this.latentValues[i] = Math.min(1.0, this.latentValues[i] + rates[i] * dtSec);
    }
  }

  depleteOption(optionIdx) {
    // Depletion is constant across options in this design
    const depletionRate = 0.10;
    this.latentValues[optionIdx] = Math.max(0, this.latentValues[optionIdx] - depletionRate);
  }

  // ---- Coupling (optional, used in Block 2) ----

  applyCoupling(optionIdx) {
    // Apply coupling effect on latent values after depletion of chosen option
    // The depletion of option i propagates to j via coupling: delta_V_j = w_ij * delta_V_i
    if (!this.wMatrix) return; // No coupling matrix set

    const depletionRate = 0.10; // Standard depletion amount
    const depletedAmount = depletionRate;

    // Propagate depletion to other options via W matrix
    for (let j = 0; j < 5; j++) {
      if (j !== optionIdx && this.wMatrix[optionIdx][j] > 0) {
        const coupledDepletion = this.wMatrix[optionIdx][j] * depletedAmount;
        this.latentValues[j] = Math.max(0, this.latentValues[j] - coupledDepletion);
      }
    }
  }

  // ---- Core click processing ----

  processClick(optionIdx, elapsedMs) {
    const dtSec = (elapsedMs - this.lastClickTimeMs) / 1000;
    const phase = this.getCurrentPhase();

    // Build rates array: [side1, side2, target, side3, side4]
    const targetRate = phase.targetRate;
    const sideRates = [
      this.config.options[1].baseRRate,
      this.config.options[2].baseRRate,
      this.config.options[4].baseRRate,
      this.config.options[5].baseRRate,
    ];

    // Recovery
    this.updateLatentValues(dtSec, targetRate, sideRates);

    // Pre-click latent values
    const preClickLatent = [...this.latentValues];

    // Reward probability = latent value before depletion
    const rewardProb = this.latentValues[optionIdx];
    const rewarded = Math.random() < rewardProb;
    const pointsEarned = rewarded ? this.config.pointsPerReward : 0;

    // Depletion
    this.depleteOption(optionIdx);

    // Coupling propagation (Block 2)
    this.applyCoupling(optionIdx);

    // Post-click latent values
    const postClickLatent = [...this.latentValues];

    // Switching metrics
    const isSwitch = this.previousChoice !== null && this.previousChoice !== optionIdx;
    if (isSwitch) {
      this.runLength = 1;
      this.lastSwitchTimeMs = elapsedMs;
      this.totalSwitches++;
    } else {
      this.runLength = this.previousChoice === null ? 1 : this.runLength + 1;
    }

    const timeSinceSwitch = this.previousChoice === null ? 0 : elapsedMs - this.lastSwitchTimeMs;
    const timeSincePrevClick = this.clickIndex === 0 ? 0 : elapsedMs - this.lastClickTimeMs;

    // Update state
    this.previousChoice = optionIdx;
    this.lastClickTimeMs = elapsedMs;
    this.clickIndex++;
    this.totalRewards += rewarded ? 1 : 0;
    this.cumulativeScore += pointsEarned;
    this.cumulativeRewardsPerOption[optionIdx] += rewarded ? 1 : 0;

    return {
      chosenOption: optionIdx,
      rewardOutcome: rewarded ? 1 : 0,
      pointsEarned: pointsEarned,
      cumulativeScore: this.cumulativeScore,
      preClickLatent: preClickLatent,
      postClickLatent: postClickLatent,
      runLength: this.runLength,
      isSwitch: isSwitch,
      timeSincePrevClick: timeSincePrevClick,
      timeSinceSwitch: timeSinceSwitch,
      currentPhaseId: this.currentPhaseId,
    };
  }

  advancePhase() {
    // Called when we've reached the click count for the current phase
    if (this.currentPhaseId < this.config.phases.length) {
      this.currentPhaseId++;
    }
  }

  setBlockId(blockId) {
    this.currentBlockId = blockId;
  }

  getLatentValueEquilibrium(targetRate, sideRates) {
    // B^0 = normalized rates raised to a_sensitivity (default a=1)
    const rates = [sideRates[0], sideRates[1], targetRate, sideRates[2], sideRates[3]];
    const sum = rates.reduce((a, b) => a + b, 0);
    return rates.map(r => r / sum);
  }
}
