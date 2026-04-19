"""
Thin wrapper around the preprint's model.py for use in fitting scripts.

Adds the preprint repo to sys.path so `import model` resolves to
integrating-behavioral-processes/model.py without copying files.
Also provides fitting-specific helpers (likelihood, softmax choice rule).
"""

import sys
import os

# Add the preprint repo to the path
_REPO_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..',
                 'integrating-behavioral-processes')
)
if _REPO_DIR not in sys.path:
    sys.path.insert(0, _REPO_DIR)

import model as m  # noqa: E402 — the preprint's equation library
import numpy as np

# Re-export everything from model.py for convenience
from model import (
    matching_ratio,
    concatenated_value,
    baseline_allocation,
    project_simplex,
    nonlinear_potential,
    disequilibrium_force,
    disequilibrium_force_magnitude,
    behavioral_mass,
    newton_acceleration,
    brunt_vaisala_squared,
    bv_frequency_from_rates,
    oscillatory_return,
    reinforcer_density,
    coupling_force,
    uniform_coupling_matrix,
    association_weight,
    unified_acceleration,
    integrator_step,
    vi_to_rate,
    matching_equilibrium_from_rates,
)


# =========================================================================
# Fitting-specific helpers
# =========================================================================

def softmax_choice_prob(B, temperature=0.1, n_options=2):
    """
    Softmax choice rule: P(choose_i) = exp(B_i / tau) / sum_j exp(B_j / tau).

    For the 2-choice case, B is [B_A, B_B] on the simplex (B_A + B_B = 1).
    Temperature tau controls how deterministic the mapping is:
      tau -> 0: deterministic (choose whichever B_i is largest)
      tau -> inf: random (P = 1/n regardless of B)
    """
    B = np.asarray(B, dtype=float)
    # Numerical stability: subtract max before exp
    logits = B / temperature
    logits -= logits.max()
    exp_logits = np.exp(logits)
    return exp_logits / exp_logits.sum()


def choice_nll(choice_index, B, temperature=0.1):
    """
    Negative log-likelihood of a single observed choice given allocation B.

    choice_index: 0-based index of the chosen option
    B: current allocation vector on the simplex
    temperature: softmax temperature

    Returns scalar NLL (clipped to avoid log(0)).
    """
    probs = softmax_choice_prob(B, temperature=temperature)
    p = np.clip(probs[choice_index], 1e-12, 1.0)
    return -np.log(p)


def simulate_and_score(params, click_times, choices, phase_ids,
                       latent_values_a, latent_values_b,
                       n_options=2, dt_resolution=0.01):
    """
    Run the unified integrator forward through a participant's click
    sequence and return total negative log-likelihood.

    This is the objective function for parameter optimization.

    Parameters
    ----------
    params : dict with keys:
        k_field, zeta, omega_base, m0, gain, a_sensitivity, temperature
    click_times : array of shape (n_clicks,), elapsed time in seconds
    choices : array of shape (n_clicks,), 0-based choice indices
    phase_ids : array of shape (n_clicks,), 1-based phase identifiers
    latent_values_a : array of shape (n_clicks,), pre-click latent value for A
    latent_values_b : array of shape (n_clicks,), pre-click latent value for B
    n_options : int, number of response options (2 for Exp 1)
    dt_resolution : float, integrator time step in seconds

    Returns
    -------
    total_nll : float
    """
    k_field = params['k_field']
    zeta = params['zeta']
    omega_base = params['omega_base']
    m0 = params['m0']
    gain = params['gain']
    a_sensitivity = params['a_sensitivity']
    temperature = params['temperature']
    inv_temp = 1.0 / temperature

    n_clicks = len(click_times)

    # Initialize state as plain floats for speed (n=2 case)
    B = np.array([0.5, 0.5])
    Vel = np.array([0.0, 0.0])
    cum_R = np.array([0.0, 0.0])

    total_nll = 0.0
    current_time = 0.0

    # Pre-extract arrays for speed (avoid pandas overhead in loop)
    lat_a = latent_values_a
    lat_b = latent_values_b

    for i in range(n_clicks):
        click_t = click_times[i]

        # Compute B0 from instantaneous latent values
        la, lb = lat_a[i], lat_b[i]
        va = la ** a_sensitivity
        vb = lb ** a_sensitivity
        v_sum = va + vb
        if v_sum > 0:
            B0_0 = va / v_sum
            B0_1 = vb / v_sum
        else:
            B0_0 = B0_1 = 0.5

        # BV frequency from rates (inline bv_frequency_from_rates for n=2)
        ra = max(la, 1e-6)
        rb = max(lb, 1e-6)
        rate_mean = (ra + rb) * 0.5
        inv_rate_mean = omega_base / rate_mean
        om_0 = ra * inv_rate_mean
        om_1 = rb * inv_rate_mean

        # Masses (inline behavioral_mass for n=2)
        mass_0 = m0 + gain * cum_R[0]
        mass_1 = m0 + gain * cum_R[1]

        # Integrate forward from current_time to click_t
        # Inlined integrator: no function call overhead, no coupling (W=0)
        time_to_advance = click_t - current_time
        if time_to_advance > 0:
            n_steps = max(1, int(time_to_advance / dt_resolution))
            dt = time_to_advance / n_steps

            b0, b1 = B[0], B[1]
            v0, v1 = Vel[0], Vel[1]

            for _ in range(n_steps):
                # F_DE = k_field * (B0 - B), linear restoring (p=2, W=0)
                f0 = k_field * (B0_0 - b0)
                f1 = k_field * (B0_1 - b1)

                # Acceleration: (omega^2 * F_DE - zeta * V) / mass
                a0 = (om_0 * om_0 * f0 - zeta * v0) / mass_0
                a1 = (om_1 * om_1 * f1 - zeta * v1) / mass_1

                # Semi-implicit Euler
                v0 += a0 * dt
                v1 += a1 * dt
                b0 += v0 * dt
                b1 += v1 * dt

                # Project onto simplex (clamp + normalize)
                if b0 < 0: b0 = 0.0
                if b1 < 0: b1 = 0.0
                s = b0 + b1
                if s == 0:
                    b0 = b1 = 0.5
                else:
                    b0 /= s
                    b1 /= s

            B[0], B[1] = b0, b1
            Vel[0], Vel[1] = v0, v1

        # Softmax choice probability (inlined for speed)
        logit_0 = B[0] * inv_temp
        logit_1 = B[1] * inv_temp
        max_logit = max(logit_0, logit_1)
        e0 = np.exp(logit_0 - max_logit)
        e1 = np.exp(logit_1 - max_logit)
        p_sum = e0 + e1
        p_chosen = (e0 if choices[i] == 0 else e1) / p_sum
        if p_chosen < 1e-12:
            p_chosen = 1e-12
        total_nll -= np.log(p_chosen)

        # Update cumulative reinforcement
        if choices[i] == 0:
            cum_R[0] += la
        else:
            cum_R[1] += lb

        current_time = click_t

    return total_nll
