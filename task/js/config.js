// ============================================================
// config.js — Exp 2 task parameters (5-option foraging)
// ============================================================

const CONFIG = Object.freeze({

  // --- General ---
  taskVersion: "2.0.0",
  pointsPerReward: 1,
  cooldownMs: 200,          // minimum ms between clicks
  practiceDurationMs: 30000, // 30-second practice block

  // --- Block structure (two blocks per session) ---
  // Block 1 and Block 2 differ in coupling condition
  blockDurationMs: 420000,   // 7 minutes per block (~600 clicks at 700ms ICI)
  midSessionBreakMs: 30000,  // 30-second rest between blocks

  // --- 5-option button labels and base schedules ---
  options: {
    1: { label: "Option 1", baseRRate: 0.050, baseD: 0.10 },  // VI-20
    2: { label: "Option 2", baseRRate: 0.025, baseD: 0.10 },  // VI-40
    3: { label: "Option 3", baseRRate: 0.100, baseD: 0.10 },  // TARGET, VI-10 (alternating)
    4: { label: "Option 4", baseRRate: 0.017, baseD: 0.10 },  // VI-60
    5: { label: "Option 5", baseRRate: 0.012, baseD: 0.10 },  // VI-80
  },

  // --- Starting latent values (all 0.7 for uniform start) ---
  startingLatentValues: [0.7, 0.7, 0.7, 0.7, 0.7],

  // --- Phase schedule (8 phases per block, ABABABAB) ---
  // A = target rich (VI-10 = 0.100/s), B = target lean (VI-100 = 0.010/s)
  // Unsignaled transitions
  phases: [
    // Block 1
    { id: 1, label: "Phase 1 (A)",  targetRate: 0.100, blockId: 1, phaseType: "A" },
    { id: 2, label: "Phase 2 (B)",  targetRate: 0.010, blockId: 1, phaseType: "B" },
    { id: 3, label: "Phase 3 (A)",  targetRate: 0.100, blockId: 1, phaseType: "A" },
    { id: 4, label: "Phase 4 (B)",  targetRate: 0.010, blockId: 1, phaseType: "B" },
    { id: 5, label: "Phase 5 (A)",  targetRate: 0.100, blockId: 1, phaseType: "A" },
    { id: 6, label: "Phase 6 (B)",  targetRate: 0.010, blockId: 1, phaseType: "B" },
    { id: 7, label: "Phase 7 (A)",  targetRate: 0.100, blockId: 1, phaseType: "A" },
    { id: 8, label: "Phase 8 (B)",  targetRate: 0.010, blockId: 1, phaseType: "B" },

    // Block 2
    { id: 9,  label: "Phase 9 (A)",  targetRate: 0.100, blockId: 2, phaseType: "A" },
    { id: 10, label: "Phase 10 (B)", targetRate: 0.010, blockId: 2, phaseType: "B" },
    { id: 11, label: "Phase 11 (A)", targetRate: 0.100, blockId: 2, phaseType: "A" },
    { id: 12, label: "Phase 12 (B)", targetRate: 0.010, blockId: 2, phaseType: "B" },
    { id: 13, label: "Phase 13 (A)", targetRate: 0.100, blockId: 2, phaseType: "A" },
    { id: 14, label: "Phase 14 (B)", targetRate: 0.010, blockId: 2, phaseType: "B" },
    { id: 15, label: "Phase 15 (A)", targetRate: 0.100, blockId: 2, phaseType: "A" },
    { id: 16, label: "Phase 16 (B)", targetRate: 0.010, blockId: 2, phaseType: "B" },
  ],

  // --- Uneven phase lengths for mass accumulation test ---
  // Pattern: [200, 200, 50, 50, 200, 200, 50, 50] clicks per phase
  // Counterbalanced: half of participants get mirror [50, 50, 200, 200, ...]
  phaseLengths: [200, 200, 50, 50, 200, 200, 50, 50],
  phaseLengthsMirror: [50, 50, 200, 200, 50, 50, 200, 200],

  // --- Quiescence probes ---
  // Placement: after ~25 post-transition clicks
  // Duration: 10 seconds
  quiescenceProbes: {
    durationMs: 10000,
    clicksBeforeProbe: 25,
    transitionsWithProbe: [1, 3, 5, 7],  // probe after phase transitions 1, 3, 5, 7 (per block)
  },

  // --- Coupling condition assignment ---
  // Block 1 = Independent (W = 0)
  // Block 2 = Coupled (random sparse W, or could be fixed per condition)
  couplingStructure: "independent", // or "sparse" or "chain" etc
  couplingCoefficient: 0.0, // Block 1 (Independent)

  // --- Condition counterbalancing ---
  // Determined at session start via random assignment
  blockOrder: null, // will be set at runtime
  phaseLengthOrder: null, // will be set at runtime

  // --- Session management ---
  countdownSec: 5,
  prolificCompletionCode: "EXP2TEST",

  // --- Validity checks ---
  validity: {
    inactivityThresholdMs: 10000,  // gaps > this = inactive
    maxTotalInactivityMs: 60000,   // flag if total inactivity exceeds
    minTotalClicks: 100,           // flag if fewer clicks
    zeroSwitchesFlag: true         // flag if never switched
  },

  // --- Leaderboard (simulated) ---
  leaderboard: [
    { name: "Player 3",  score: 5327 },
    { name: "Player 12", score: 4890 },
    { name: "Player 7",  score: 4510 },
    { name: "Player 15", score: 4180 },
    { name: "Player 9",  score: 3820 },
    { name: "Player 1",  score: 3470 },
    { name: "Player 11", score: 3150 },
    { name: "Player 5",  score: 2880 },
    { name: "Player 8",  score: 2590 },
    { name: "Player 14", score: 2340 },
  ]
});

// ============================================================
// Helper: Generate sparse coupling matrix for Block 2
// ============================================================

function generateCouplingMatrix() {
  // Returns a 5x5 sparse symmetric coupling matrix W_true
  // per design spec Section 2.8:
  // 1. Zero matrix
  // 2. Select k edges (k uniform from {3,4,5,6})
  // 3. Assign weights uniform [0.1, 0.4]
  // 4. Symmetrize
  // 5. Set diagonal to 0

  const size = 5;
  const W = Array(size).fill().map(() => Array(size).fill(0));

  // Step 1: Random number of edges
  const k = Math.floor(Math.random() * 4) + 3; // {3, 4, 5, 6}

  // Step 2-3: Select k random edges and assign weights
  const edges = [];
  const selectedPairs = new Set();

  while (edges.length < k) {
    const i = Math.floor(Math.random() * size);
    const j = Math.floor(Math.random() * size);

    if (i !== j) {
      const pairKey = i < j ? `${i}-${j}` : `${j}-${i}`;
      if (!selectedPairs.has(pairKey)) {
        selectedPairs.add(pairKey);
        const weight = Math.random() * 0.3 + 0.1; // [0.1, 0.4]
        edges.push({ i, j, weight });
      }
    }
  }

  // Step 4: Apply weights and symmetrize
  edges.forEach(({ i, j, weight }) => {
    W[i][j] = Math.max(W[i][j], weight);
    W[j][i] = Math.max(W[j][i], weight);
  });

  // Step 5: Diagonal is already 0

  return W;
}
