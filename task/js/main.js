// ============================================================
// main.js — Exp 2 orchestration (screens, flow, event handling)
// ============================================================

class ExperimentManager {
  constructor(config) {
    this.config = config;
    this.state = new TaskState(config);
    this.logger = new DataLogger();
    this.ui = new UIManager(config);
    this.sessionStartTime = null;
    this.currentBlockStartTime = null;
    this.blockClickCounts = [0, 0]; // clicks per phase in current block
    this.currentPhaseClickCount = 0;
    this.quiescenceActive = false;
    this.quiescencePostReleaseStartTime = null;
    this.timerInterval = null; // Timer update loop
  }

  // ---- Session setup ----

  async initializeSession() {
    // Generate session metadata
    const sessionId = this.generateSessionId();
    const participantId = document.getElementById("prolific-id-input")?.value || "unknown";

    this.logger.setSessionMeta({
      participantId: participantId,
      sessionId: sessionId,
      taskVersion: this.config.taskVersion,
      createdAt: new Date().toISOString(),
    });

    // Randomize condition assignments
    this.assignConditions();

    // Show countdown to block 1
    this.ui.showScreen("screen-countdown");
    this.ui.showCountdown(this.config.countdownSec);

    // Start block 1
    await new Promise(resolve => setTimeout(resolve, (this.config.countdownSec + 1) * 1000));
    this.startBlock(1);
  }

  assignConditions() {
    // Block 1 = Independent, Block 2 = Coupled (fixed for Exp 2)
    // Phase length order = random counterbalance
    const blockLengthOrder = Math.random() < 0.5 ? "normal" : "mirror";
    const couplingOrder = Math.random() < 0.5 ? "indep-then-coupled" : "coupled-then-indep";

    // Store on manager instance, not on frozen CONFIG
    this.blockOrder = couplingOrder;
    this.phaseLengthOrder = blockLengthOrder;

    this.logger.sessionMeta.blockOrder = couplingOrder;
    this.logger.sessionMeta.phaseLengthOrder = blockLengthOrder;
  }

  startBlock(blockId) {
    this.state.setBlockId(blockId);
    this.state.currentPhaseId = blockId === 1 ? 1 : 9; // phases 1-8 are block 1, 9-16 are block 2
    this.currentBlockStartTime = performance.now();
    this.state.reset();
    this.blockClickCounts = [0, 0];
    this.currentPhaseClickCount = 0;

    // Determine coupling condition for this block
    const couplingCondition = blockId === 1 ? "independent" : "coupled";

    // Generate coupling matrix for Block 2
    if (blockId === 2 && couplingCondition === "coupled") {
      this.state.wMatrix = generateCouplingMatrix();
      this.logger.sessionMeta.couplingMatrix = this.state.wMatrix;
    }

    this.logger.sessionMeta.currentBlock = blockId;
    this.logger.sessionMeta.currentCouplingCondition = couplingCondition;

    this.ui.showScreen("screen-task");
    this.ui.setButtonStates(true);
    this.ui.updateLeaderboard(this.config.leaderboard);
    this.ui.showMessage(`Block ${blockId} started`, 2000);

    // Start timer update loop
    if (this.timerInterval) clearInterval(this.timerInterval);
    this.timerInterval = setInterval(() => {
      const elapsedMs = performance.now() - this.currentBlockStartTime;
      const elapsedSec = Math.floor(elapsedMs / 1000);
      const blockDurationSec = this.config.blockDurationMs / 1000;
      this.ui.updateTimer(elapsedSec, blockDurationSec);

      // Auto-end block if time expires
      if (elapsedMs >= this.config.blockDurationMs) {
        clearInterval(this.timerInterval);
        this.endBlock(blockId);
      }
    }, 100); // Update every 100ms for smooth display
  }

  endBlock(blockId) {
    if (this.timerInterval) clearInterval(this.timerInterval);
    this.ui.setButtonStates(false);
    if (blockId === 1) {
      // Show break screen
      this.ui.showScreen("screen-break");
      const breakBtn = document.getElementById("btn-continue-after-break");
      if (breakBtn) {
        breakBtn.onclick = () => {
          this.ui.showScreen("screen-countdown");
          this.ui.showCountdown(this.config.countdownSec);
          setTimeout(() => this.startBlock(2), (this.config.countdownSec + 1) * 1000);
        };
      }
    } else {
      // Block 2 complete - end session
      this.endSession();
    }
  }

  async endSession() {
    this.ui.showScreen("screen-debrief");
    // Upload data to Supabase
    await this.uploadData();
    // Show completion code
    const codeDisplay = document.getElementById("completion-code");
    if (codeDisplay) codeDisplay.textContent = this.config.prolificCompletionCode;
  }

  // ---- Click handling ----

  async handleClick(optionIdx) {
    if (this.quiescenceActive) return; // Ignore clicks during quiescence

    const elapsedMs = performance.now() - this.currentBlockStartTime;
    const blockId = this.state.currentBlockId;

    // Process the click
    const clickData = this.state.processClick(optionIdx, elapsedMs);

    // Check if we should trigger a quiescence probe
    const shouldProbeNow = this.shouldTriggerQuiescenceProbe(blockId);

    // Log the event
    this.logClickEvent(optionIdx, elapsedMs, clickData, shouldProbeNow);

    // Update UI
    this.ui.highlightButton(optionIdx);
    this.ui.updateScore(this.state.cumulativeScore);
    this.ui.updateLeaderboard(this.config.leaderboard, this.state.cumulativeScore);
    this.ui.updatePhaseInfo(this.state.currentPhaseId, this.state.getCurrentPhase().label);
    this.ui.updateLatentValueDisplay(this.state.latentValues);

    // Increment phase click counter
    this.currentPhaseClickCount++;

    // Check phase transition
    const phaseLengths = blockId === 1 ? this.config.phaseLengths : this.config.phaseLengthsMirror;
    const currentPhaseIdxInBlock = (this.state.currentPhaseId - 1) % 8;
    if (this.currentPhaseClickCount >= phaseLengths[currentPhaseIdxInBlock]) {
      this.currentPhaseClickCount = 0;
      this.state.advancePhase();
      this.ui.updateMessage(`New phase: ${this.state.getCurrentPhase().label}`);
    }

    // Check block completion
    const totalClicksThisBlock = this.blockClickCounts[blockId - 1];
    const targetClicks = phaseLengths.reduce((a, b) => a + b, 0);
    if (totalClicksThisBlock >= targetClicks) {
      this.endBlock(blockId);
    }

    // Trigger quiescence probe if needed
    if (shouldProbeNow) {
      await this.triggerQuiescenceProbe();
    }
  }

  shouldTriggerQuiescenceProbe(blockId) {
    // Check if this is a phase transition that should have a probe
    const probeTransitions = this.config.quiescenceProbes.transitionsWithProbe;
    const phaseIdxInBlock = (this.state.currentPhaseId - 1) % 8;
    return probeTransitions.includes(phaseIdxInBlock + 1) && this.currentPhaseClickCount === this.config.quiescenceProbes.clicksBeforeProbe;
  }

  async triggerQuiescenceProbe() {
    this.quiescenceActive = true;
    this.ui.setButtonStates(false);
    this.ui.showQuiescenceProbe(this.config.quiescenceProbes.durationMs);

    await new Promise(resolve => setTimeout(resolve, this.config.quiescenceProbes.durationMs));

    this.quiescenceActive = false;
    this.ui.setButtonStates(true);
    this.quiescencePostReleaseStartTime = performance.now() - this.currentBlockStartTime;
  }

  // ---- Logging ----

  logClickEvent(optionIdx, elapsedMs, clickData, quiescenceFlag) {
    const blockId = this.state.currentBlockId;
    const couplingCondition = blockId === 1 ? "independent" : "coupled";
    const phaseLengthCondition = blockId === 1 ? this.phaseLengthOrder : this.phaseLengthOrder; // same for both blocks in Exp 2

    this.logger.logEvent({
      timestamp_ms: Math.round(elapsedMs),
      click_index: this.state.clickIndex,
      chosen_option: optionIdx + 1, // 1-indexed for output
      reward_outcome: clickData.rewardOutcome,
      points_earned: clickData.pointsEarned,
      cumulative_score: clickData.cumulativeScore,
      time_since_prev_click_ms: clickData.timeSincePrevClick,
      phase_id: this.state.currentPhaseId,
      phase_label: this.state.getCurrentPhase().label,
      latent_value_1_pre: clickData.preClickLatent[0].toFixed(4),
      latent_value_2_pre: clickData.preClickLatent[1].toFixed(4),
      latent_value_3_pre: clickData.preClickLatent[2].toFixed(4),
      latent_value_4_pre: clickData.preClickLatent[3].toFixed(4),
      latent_value_5_pre: clickData.preClickLatent[4].toFixed(4),
      latent_value_1_post: clickData.postClickLatent[0].toFixed(4),
      latent_value_2_post: clickData.postClickLatent[1].toFixed(4),
      latent_value_3_post: clickData.postClickLatent[2].toFixed(4),
      latent_value_4_post: clickData.postClickLatent[3].toFixed(4),
      latent_value_5_post: clickData.postClickLatent[4].toFixed(4),
      block_id: blockId,
      coupling_condition: couplingCondition,
      coupling_structure: "independent", // or random W matrix info
      phase_length_condition: phaseLengthCondition,
      quiescence_probe_flag: quiescenceFlag,
      run_length: clickData.runLength,
      switch_flag: clickData.isSwitch,
      total_clicks_so_far: this.state.clickIndex,
      total_rewards_so_far: this.state.totalRewards,
      elapsed_time_s: (elapsedMs / 1000).toFixed(3),
    });

    this.blockClickCounts[blockId - 1]++;
  }

  // ---- Data upload ----

  async uploadData() {
    // Download locally first
    this.logger.downloadCSV(`exp2_${this.logger.sessionMeta.participantId}.csv`);

    // TODO: Upload to Supabase when backend is configured
    // const result = await this.logger.uploadToSupabase(SUPABASE_URL, SUPABASE_KEY);
  }

  // ---- Utilities ----

  generateSessionId() {
    return `exp2_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

// ---- Global setup ----

let experiment;

document.addEventListener("DOMContentLoaded", () => {
  experiment = new ExperimentManager(CONFIG);

  // Consent screen
  const consentCheckbox = document.getElementById("consent-checkbox");
  const consentBtn = document.getElementById("btn-consent");
  if (consentCheckbox && consentBtn) {
    consentCheckbox.addEventListener("change", () => {
      consentBtn.disabled = !consentCheckbox.checked;
    });
    consentBtn.addEventListener("click", () => {
      experiment.ui.showScreen("screen-prolific");
    });
  }

  // Prolific ID screen
  const prolificInput = document.getElementById("prolific-id-input");
  const prolificBtn = document.getElementById("btn-prolific");
  if (prolificInput && prolificBtn) {
    prolificInput.addEventListener("input", () => {
      prolificBtn.disabled = !prolificInput.value.trim();
    });
    prolificBtn.addEventListener("click", async () => {
      experiment.ui.showScreen("screen-instructions");
      // Show instructions for ~5 seconds then proceed
      setTimeout(() => experiment.initializeSession(), 5000);
    });
  }

  // Instructions screen continue button
  const instructionsBtn = document.getElementById("btn-instructions-continue");
  if (instructionsBtn) {
    instructionsBtn.addEventListener("click", () => {
      experiment.initializeSession();
    });
  }

  // Task buttons (5 options)
  for (let i = 0; i < 5; i++) {
    const btn = document.querySelector(`[data-option="${i}"]`);
    if (btn) {
      btn.addEventListener("click", () => experiment.handleClick(i));
    }
  }

  experiment.ui.showScreen("screen-consent");
});
