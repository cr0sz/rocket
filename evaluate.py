"""Evaluate every controller and write results.json.

Controllers:
  ppo            - PPO model, deterministic predict.
                   seed   = training seed (0..4); obs_mode = basic | extended.
                   Randomness: only the env start-altitude stream (eval_seed).
  hand_rule      - hand-written autopilot rocket.make_autopilot(5, -20).
                   seed   = null (deterministic, no RNG); obs_mode = null.
  random         - coin-flip burn decision.
                   seed   = RANDOM_SEED (action RNG); obs_mode = null.
                   Randomness: random.Random(RANDOM_SEED) for actions.

Every controller flies the SAME 2000 start altitudes, generated once from
env.reset(seed=EVAL_SEED) followed by 2000 unseeded resets, so results are
directly comparable. A landing is reward > 0. Counts are stored, not
percentages. Band sums are asserted to equal the totals.
"""
import json
import random

from stable_baselines3 import PPO

from rocket_env import RocketEnv
import rocket

EXTENDED = True
SEEDS = [0, 1, 2, 3, 4]
GAMES = 2000
EVAL_SEED = 123          # env seed that generates the shared start altitudes
RANDOM_SEED = 123        # action-RNG seed for the random controller
BAND_WIDTH = 20
ALT_MIN, ALT_MAX = 400, 600
BANDS = [
    (ALT_MIN + i * BAND_WIDTH, ALT_MIN + (i + 1) * BAND_WIDTH)
    for i in range((ALT_MAX - ALT_MIN) // BAND_WIDTH)
]
HAND_RULE = rocket.make_autopilot(5, -20)   # c=5, d=-20
RESULTS_FILE = "results.json"

NAME_EXT = "ppo_rocket_ext_seed"
NAME_BASIC = "ppo_rocket_seed"


def start_altitudes(env, n, seed):
    """Generate n start altitudes from one seeded env stream (reused by all controllers)."""
    env.reset(seed=seed)
    altitudes = []
    for _ in range(n):
        _, _ = env.reset()
        altitudes.append(env.altitude)
    return altitudes


def band_index(start):
    idx = int((start - ALT_MIN) // BAND_WIDTH)
    return max(0, min(len(BANDS) - 1, idx))


def new_bands():
    return [{"alt_min": lo, "alt_max": hi, "games": 0, "landings": 0} for lo, hi in BANDS]


def run_game(env, start_altitude, controller, rng=None):
    env.altitude = start_altitude
    env.speed = 0.0
    env.fuel = 45
    obs = env._obs()
    done = False
    while not done:
        action = controller(obs, env, rng)
        obs, reward, terminated, truncated, _ = env.step(int(action))
        done = terminated or truncated
    return reward


def evaluate(env, altitudes, controller, rng=None):
    landings = 0
    bands = new_bands()
    for start in altitudes:
        bands[band_index(start)]["games"] += 1
        if run_game(env, start, controller, rng) > 0:
            landings += 1
            bands[band_index(start)]["landings"] += 1
    assert sum(b["games"] for b in bands) == len(altitudes), "band game counts don't add up"
    assert sum(b["landings"] for b in bands) == landings, "band landing counts don't add up"
    return landings, bands


def ppo_controller(model):
    def act(obs, env, rng=None):
        action, _ = model.predict(obs, deterministic=True)
        return int(action)
    return act


def hand_rule_controller(_obs, env, rng=None):
    return int(HAND_RULE(env.altitude, env.speed, env.fuel))


def random_controller(_obs, env, rng):
    return int(rng.random() < 0.5)


def main():
    env = RocketEnv(extended=EXTENDED)
    altitudes = start_altitudes(env, GAMES, EVAL_SEED)

    records = []

    # PPO, both observation modes, one record per seed.
    for extended, name in ((True, NAME_EXT), (False, NAME_BASIC)):
        env_mode = RocketEnv(extended=extended)
        for seed in SEEDS:
            model = PPO.load(f"{name}{seed}")
            landings, bands = evaluate(env_mode, altitudes, ppo_controller(model))
            records.append({
                "controller": "ppo",
                "obs_mode": "extended" if extended else "basic",
                "seed": seed,
                "eval_seed": EVAL_SEED,
                "games": GAMES,
                "landings": landings,
                "bands": bands,
            })

    # Hand rule: deterministic autopilot, no observation mode, no seed.
    landings, bands = evaluate(env, altitudes, hand_rule_controller)
    records.append({
        "controller": "hand_rule",
        "obs_mode": None,
        "seed": None,
        "eval_seed": EVAL_SEED,
        "games": GAMES,
        "landings": landings,
        "bands": bands,
    })

    # Random: coin-flip burn, seeded action RNG.
    rng = random.Random(RANDOM_SEED)
    landings, bands = evaluate(env, altitudes, random_controller, rng)
    records.append({
        "controller": "random",
        "obs_mode": None,
        "seed": RANDOM_SEED,
        "eval_seed": EVAL_SEED,
        "games": GAMES,
        "landings": landings,
        "bands": bands,
    })

    with open(RESULTS_FILE, "w") as f:
        json.dump(records, f, indent=2)

    for r in records:
        rate = r["landings"] / r["games"] * 100
        print(f"{r['controller']:10s} {str(r['obs_mode']):10s} seed={str(r['seed']):5s}  "
              f"landings={r['landings']}/{r['games']}  {rate:.2f}%")
    print(f"wrote {RESULTS_FILE}")


if __name__ == "__main__":
    main()
