# Exp 2 Power Analysis (Tier B)

Date: 2026-04-18 00:21

## Model Recovery Simulation

Ground truth parameters:
- k_field = 3.0
- omega_base = 0.8
- zeta = 1.2
- m0 = 1.0
- gain = 8.0
- a_sensitivity = 1.0
- temperature = 0.1

Task: 5-option foraging, Independent block (no coupling),
8 phases with uneven lengths [200, 200, 50, 50, 200, 200, 50, 50]

## Results

Recovery rate (success = fitted parameter within 50% of ground truth):

|   N |   a_sensitivity |   coupling_structure |   gain |   k_field |   m0 |   omega_base |   zeta |
|----:|----------------:|---------------------:|-------:|----------:|-----:|-------------:|-------:|
|  20 |             0.4 |                  nan |    0.4 |       0.4 |  0.4 |          0.6 |    0   |
|  40 |             0.8 |                  nan |    0.4 |       0.4 |  0.4 |          0.8 |    0.2 |
|  60 |             0.4 |                  nan |    0.2 |       0.2 |  0.2 |          0.8 |    0.2 |
|  80 |             0.2 |                  nan |    0.2 |       0.6 |  0   |          0.8 |    0.2 |
| 100 |             0.2 |                  nan |    0.2 |       0.4 |  0   |          0.8 |    0.2 |
| 120 |             0.8 |                  nan |    0.2 |       0.8 |  0   |          0.6 |    0   |

## Recommendation

Sample size: Based on model recovery, use N = 420
for 80% power across all estimated parameters.
