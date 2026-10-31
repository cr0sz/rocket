from stable_baselines3 import PPO
from rocket_env import RocketEnv

EXTENDED = True                  # must match the setting you trained with
SEEDS = [0, 1, 2, 3, 4]
GAMES = 2000
NAME = "ppo_rocket_ext_seed" if EXTENDED else "ppo_rocket_seed"


def landing_rate(model, extended=False):
    env = RocketEnv(extended=extended)
    env.reset(seed=123)
    wins = 0
    for i in range(GAMES):
        obs, info = env.reset()
        done = False
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(int(action))
            done = terminated or truncated
        if reward > 0:
            wins = wins + 1
    return wins


def watch_one(model, start_altitude=500.0, extended=False):
    env = RocketEnv(extended=extended)
    env.reset()
    env.altitude = start_altitude
    obs = env._obs()
    done = False
    t = 0
    while not done:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(int(action))
        done = terminated or truncated
        t = t + 1
        print(f"t={t}s  burn={int(action)}  alt={env.altitude:.1f} m  speed={env.speed:.1f} m/s  fuel={env.fuel}")
    print("LANDED" if reward > 0 else "CRASHED")


if __name__ == "__main__":
    rates = []
    for seed in SEEDS:
        model = PPO.load(f"{NAME}{seed}")
        wins = landing_rate(model, extended=EXTENDED)
        rate = wins / GAMES * 100
        print("seed", seed, "landing rate:", rate, "%")
        rates.append(rate)
    print("average:", sum(rates) / len(rates), "%  best:", max(rates), "%  worst:", min(rates), "%")