// ============================================================
// admin-debug.js — Admin panel for real-time verification
// Displays hidden task state: phases, coupling matrix, quiescence,
// latent values, phase transitions, etc.
// ============================================================

class AdminDebugPanel {
  constructor() {
    this.panelEl = document.getElementById('admin-panel');
    this.toggleBtn = document.getElementById('admin-toggle');
    this.contentEl = document.getElementById('admin-content');
    this.isExpanded = true;

    this.manager = null; // Will be set by main.js after ExperimentManager instantiation

    // Toggle button
    if (this.toggleBtn) {
      this.toggleBtn.addEventListener('click', () => this.toggle());
    }

    // Start update loop
    this.updateInterval = setInterval(() => this.update(), 200);
  }

  toggle() {
    this.isExpanded = !this.isExpanded;
    if (this.isExpanded) {
      this.contentEl.classList.remove('hidden');
      this.toggleBtn.textContent = 'Collapse';
    } else {
      this.contentEl.classList.add('hidden');
      this.toggleBtn.textContent = 'Expand';
    }
  }

  setManager(manager) {
    this.manager = manager;
  }

  update() {
    if (!this.manager) return;

    const state = this.manager.state;
    const config = this.manager.config;
    const logger = this.manager.logger;

    // Session info
    document.getElementById('debug-session').textContent =
      `Participant: ${logger.sessionMeta.participantId || 'unknown'}\n` +
      `Session: ${logger.sessionMeta.sessionId || 'not started'}\n` +
      `Block: ${state.currentBlockId}\n` +
      `Coupling: ${state.wMatrix ? 'COUPLED' : 'INDEPENDENT'}\n` +
      `Block Order: ${config.blockOrder || 'not assigned'}\n` +
      `Phase Length Order: ${config.phaseLengthOrder || 'not assigned'}`;

    // Current phase
    const phase = state.getCurrentPhase();
    document.getElementById('debug-phase').textContent =
      `Phase ID: ${state.currentPhaseId}\n` +
      `Label: ${phase ? phase.label : 'none'}\n` +
      `Type: ${phase ? phase.phaseType : 'none'}\n` +
      `Target Rate: ${phase ? phase.targetRate : 'N/A'} /s\n` +
      `Block: ${phase ? phase.blockId : 'N/A'}`;

    // Phase progress (click count within current phase)
    const phaseLengths = state.currentBlockId === 1
      ? config.phaseLengths
      : config.phaseLengthsMirror;
    const currentPhaseIdx = state.currentPhaseId - (state.currentBlockId === 1 ? 1 : 9);
    const expectedPhaseLength = phaseLengths[currentPhaseIdx] || '?';

    document.getElementById('debug-progress').textContent =
      `Clicks in current phase: ${this.manager.currentPhaseClickCount}\n` +
      `Expected phase length: ${expectedPhaseLength} clicks\n` +
      `Total block clicks: ${state.clickIndex}\n` +
      `Total rewards earned: ${state.totalRewards}`;

    // Latent values (current state, visible pre-click)
    const latentStr = state.latentValues
      .map((v, i) => `Option ${i+1}: ${(v * 100).toFixed(1)}%`)
      .join('\n');
    document.getElementById('debug-latent').textContent = latentStr || 'No latent values';

    // Coupling matrix
    if (state.wMatrix) {
      let couplingStr = 'Coupling Matrix W:\n';
      state.wMatrix.forEach((row, i) => {
        const rowStr = row.map(v => v.toFixed(3)).join(' ');
        couplingStr += `Row ${i}: [${rowStr}]\n`;
      });
      document.getElementById('debug-coupling').textContent = couplingStr;
    } else {
      document.getElementById('debug-coupling').textContent = 'No coupling matrix (Block 1 or not set)';
    }

    // Last click details
    if (state.clickIndex > 0) {
      document.getElementById('debug-click').textContent =
        `Last choice: Option ${state.previousChoice + 1}\n` +
        `Run length: ${state.runLength}\n` +
        `Cumulative switches: ${state.totalSwitches}\n` +
        `Current score: ${state.cumulativeScore}\n` +
        `Time since last click: ${(performance.now() - state.lastClickTimeMs).toFixed(0)} ms`;
    } else {
      document.getElementById('debug-click').textContent = 'No clicks yet';
    }

    // Quiescence state
    const quiescenceActive = this.manager.quiescenceActive;
    document.getElementById('debug-quiescence').textContent =
      `Active: ${quiescenceActive ? 'YES' : 'No'}\n` +
      `Duration: ${config.quiescenceProbes.durationMs} ms\n` +
      `Clicks before probe: ${config.quiescenceProbes.clicksBeforeProbe}\n` +
      `Probe transitions (per block): ${config.quiescenceProbes.transitionsWithProbe.join(', ')}\n` +
      `Post-release latency recorded: ${this.manager.quiescencePostReleaseStartTime ? 'pending' : 'none'}`;
  }

  log(msg) {
    // Optional: log to console as well
    console.log('[ADMIN]', msg);
  }
}

// Instantiate and attach to window for access by main.js
document.addEventListener("DOMContentLoaded", () => {
  window.adminDebugPanel = new AdminDebugPanel();
});
