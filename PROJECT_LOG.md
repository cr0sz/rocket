# Project Log — AeroRL Bench backend

Versions (venv): Python 3.12.10, gymnasium 1.4.0, numpy 2.5.4, stable-baselines3 2.9.0, torch 2.14.1+cpu

## Phase A — make the data
Commit: `feat: evaluate all controllers and write results.json`

- Rewrote `evaluate.py`: evaluates `ppo` (basic & extended, seeds 0-4), `hand_rule` (`make_autopilot(5, -20)`), `random` (seeded coin flip), all on the same 2000 start altitudes (`env.reset(seed=123)` once, then replayed). Writes `results.json` with counts + 10 altitude bands (20 m each, 400-600 m). Asserts band game/landing sums equal the totals.
- PPO extended landings (MEASURED): 1291, 1335, 1335, 1325, 1335 — matches the brief exactly.
- PPO basic landings (MEASURED): 1106, 1114, 1114, 1053, 1114 (55.30 / 55.70 / 55.70 / 52.65 / 55.70 %).
- `hand_rule`: 875/2000 (43.75 %), `random`: 1/2000 (0.05 %). Both seeded & reproducible; supersede the unverified 44.18 % / 0.1 % that came from the non-reproducible unseeded `win_rate()`.
- Removed the swear comment from `rocket.py` line 1.
- `plots.py` now reads `results.json` instead of hand-typed numbers (ceiling/best_by_band remain theoretical constants from ceiling.py).

Next: Phase B — FastAPI skeleton in a new folder with its own venv and pinned requirements.txt.
