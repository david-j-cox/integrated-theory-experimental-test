// ============================================================
// logger.js — Exp 2 event logging (JSON + CSV export)
// ============================================================

class DataLogger {
  constructor() {
    this.events = [];
    this.sessionMeta = {};
  }

  reset() {
    this.events = [];
    this.sessionMeta = {};
  }

  setSessionMeta(meta) {
    this.sessionMeta = { ...this.sessionMeta, ...meta };
  }

  logEvent(record) {
    // Enriched event record
    const enriched = {
      participantId: this.sessionMeta.participantId || "unknown",
      sessionId: this.sessionMeta.sessionId || "unknown",
      timestamp_ms: record.timestamp_ms,
      absolute_timestamp: new Date().toISOString(),
      click_index: record.click_index,
      chosen_option: record.chosen_option,
      reward_outcome: record.reward_outcome,
      points_earned: record.points_earned,
      cumulative_score: record.cumulative_score,
      time_since_prev_click_ms: record.time_since_prev_click_ms,
      phase_id: record.phase_id,
      phase_label: record.phase_label,
      latent_value_1_pre: record.latent_value_1_pre,
      latent_value_2_pre: record.latent_value_2_pre,
      latent_value_3_pre: record.latent_value_3_pre,
      latent_value_4_pre: record.latent_value_4_pre,
      latent_value_5_pre: record.latent_value_5_pre,
      latent_value_1_post: record.latent_value_1_post,
      latent_value_2_post: record.latent_value_2_post,
      latent_value_3_post: record.latent_value_3_post,
      latent_value_4_post: record.latent_value_4_post,
      latent_value_5_post: record.latent_value_5_post,
      block_id: record.block_id,
      coupling_condition: record.coupling_condition,
      coupling_structure: record.coupling_structure,
      phase_length_condition: record.phase_length_condition,
      quiescence_probe_flag: record.quiescence_probe_flag || false,
      run_length: record.run_length,
      switch_flag: record.switch_flag,
      total_clicks_so_far: record.total_clicks_so_far,
      total_rewards_so_far: record.total_rewards_so_far,
      elapsed_time_s: record.elapsed_time_s,
    };
    this.events.push(enriched);
  }

  getFullDataObject() {
    return {
      metadata: this.sessionMeta,
      events: this.events
    };
  }

  toJSON() {
    return JSON.stringify(this.getFullDataObject(), null, 2);
  }

  downloadJSON(filename) {
    const blob = new Blob([this.toJSON()], { type: "application/json" });
    this._downloadBlob(blob, filename || "exp2_data.json");
  }

  toCSV() {
    if (this.events.length === 0) return "";
    const headers = Object.keys(this.events[0]);
    const rows = this.events.map(e =>
      headers.map(h => {
        const val = e[h];
        if (val === null || val === undefined) return "";
        if (typeof val === "string" && val.includes(",")) return `"${val}"`;
        return val;
      }).join(",")
    );
    return [headers.join(","), ...rows].join("\n");
  }

  downloadCSV(filename) {
    const blob = new Blob([this.toCSV()], { type: "text/csv" });
    this._downloadBlob(blob, filename || "exp2_data.csv");
  }

  _downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  // --- Supabase upload (for Exp 2) ---
  async uploadToSupabase(supabaseUrl, supabaseKey, tableName = "exp2_events") {
    try {
      const response = await fetch(`${supabaseUrl}/rest/v1/${tableName}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "apikey": supabaseKey,
          "Authorization": `Bearer ${supabaseKey}`,
        },
        body: JSON.stringify(this.events),
      });
      if (!response.ok) {
        throw new Error(`Supabase upload failed: ${response.statusText}`);
      }
      return { success: true, message: "Data uploaded to Supabase" };
    } catch (err) {
      console.error("Supabase upload error:", err);
      return { success: false, message: err.message };
    }
  }
}
