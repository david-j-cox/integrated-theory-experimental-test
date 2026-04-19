// ============================================================
// ui.js — UI rendering for Exp 2 (5 buttons, score, phase info)
// ============================================================

class UIManager {
  constructor(config) {
    this.config = config;
    this.activeScreen = null;
  }

  // ---- Screen visibility ----

  showScreen(screenId) {
    document.querySelectorAll(".screen").forEach(s => s.classList.add("hidden"));
    const screen = document.getElementById(screenId);
    if (screen) {
      screen.classList.remove("hidden");
      this.activeScreen = screenId;
    }
  }

  // ---- Button state management ----

  setButtonStates(enabled = true) {
    const buttons = document.querySelectorAll(".option-button");
    buttons.forEach(btn => {
      btn.disabled = !enabled;
      btn.style.opacity = enabled ? "1" : "0.5";
    });
  }

  highlightButton(optionIdx, highlight = true) {
    const btn = document.querySelector(`[data-option="${optionIdx}"]`);
    if (btn) {
      if (highlight) {
        btn.classList.add("clicked");
      } else {
        btn.classList.remove("clicked");
      }
      setTimeout(() => btn.classList.remove("clicked"), 100);
    }
  }

  // ---- Score and progress ----

  updateScore(score) {
    const scoreDisplay = document.getElementById("score-display");
    if (scoreDisplay) scoreDisplay.textContent = score;
  }

  updatePhaseInfo(phaseId, phaseLabel) {
    const phaseDisplay = document.getElementById("phase-display");
    if (phaseDisplay) phaseDisplay.textContent = `Phase ${phaseId}: ${phaseLabel}`;
  }

  updateTimer(elapsedSec, totalSec) {
    const timerDisplay = document.getElementById("timer-display");
    if (timerDisplay) {
      const remainingSec = Math.max(0, totalSec - elapsedSec);
      timerDisplay.textContent = `${Math.floor(remainingSec / 60)}:${String(Math.floor(remainingSec % 60)).padStart(2, "0")}`;
    }
  }

  updateLatentValueDisplay(latentValues) {
    // 5 small displays for each option's latent value (optional)
    for (let i = 0; i < 5; i++) {
      const display = document.getElementById(`latent-display-${i + 1}`);
      if (display) {
        const pct = Math.round(latentValues[i] * 100);
        display.textContent = `${pct}%`;
        // Optional: bar visualization
        display.style.backgroundColor = `rgba(50, 150, 200, ${latentValues[i]})`;
      }
    }
  }

  updateLeaderboard(leaderboard) {
    const table = document.getElementById("leaderboard-table");
    if (!table) return;
    table.innerHTML = "";
    leaderboard.forEach((entry, idx) => {
      const row = document.createElement("tr");
      row.innerHTML = `<td>${idx + 1}</td><td>${entry.name}</td><td>${entry.score}</td>`;
      table.appendChild(row);
    });
  }

  // ---- Quiescence probe ----

  showQuiescenceProbe(durationMs) {
    // Overlay blocking all interaction + countdown
    const overlay = document.getElementById("quiescence-overlay");
    if (!overlay) return;
    overlay.classList.remove("hidden");
    overlay.style.display = "flex";

    const countdown = document.getElementById("quiescence-countdown");
    if (countdown) {
      let remainingMs = durationMs;
      // Display initial countdown value
      countdown.textContent = `${(remainingMs / 1000).toFixed(1)}s`;

      const interval = setInterval(() => {
        remainingMs -= 100;
        const sec = Math.max(0, remainingMs / 1000).toFixed(1);
        countdown.textContent = `${sec}s`;
        if (remainingMs <= 0) {
          clearInterval(interval);
          this.hideQuiescenceProbe();
        }
      }, 100);
    }
  }

  hideQuiescenceProbe() {
    const overlay = document.getElementById("quiescence-overlay");
    if (overlay) overlay.classList.add("hidden");
  }

  // ---- Countdown screen ----

  showCountdown(seconds) {
    const countdown = document.getElementById("countdown-display");
    if (!countdown) return;

    let remaining = seconds;
    countdown.textContent = remaining;

    const interval = setInterval(() => {
      remaining--;
      countdown.textContent = remaining;
      if (remaining <= 0) {
        clearInterval(interval);
        countdown.parentElement.classList.add("hidden");
      }
    }, 1000);
  }

  // ---- Messaging ----

  showMessage(text, durationMs = 3000) {
    const msgBox = document.getElementById("message-box");
    if (msgBox) {
      msgBox.textContent = text;
      msgBox.classList.remove("hidden");
      if (durationMs > 0) {
        setTimeout(() => msgBox.classList.add("hidden"), durationMs);
      }
    }
  }

  showError(text) {
    const errorBox = document.getElementById("error-box");
    if (errorBox) {
      errorBox.textContent = text;
      errorBox.classList.remove("hidden");
    }
  }

  clearError() {
    const errorBox = document.getElementById("error-box");
    if (errorBox) errorBox.classList.add("hidden");
  }
}
