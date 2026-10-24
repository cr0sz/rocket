# analysis.py - WHERE does the AI fail?
from stable_baselines3 import PPO
from rocket_env import RocketEnv
from ceiling import landable_ranges


def analyze(model, games=4000):
    ranges = landable_ranges()
    env = RocketEnv()
    env.reset(seed=7)

    games_in_band = {}      # start-altitude band -> how many games
    wins_in_band = {}       # start-altitude band -> how many landings
    crash_speeds = []       # impact speed of every crash

    for i in range(games):
        obs, info = env.reset()
        start = env.altitude
        done = False
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(int(action))
            done = terminated or truncated

        band = 400 + int((start - 400) // 20) * 20      # 400, 420, 440, ... 580
        games_in_band[band] = games_in_band.get(band, 0) + 1
        if reward > 0:
            wins_in_band[band] = wins_in_band.get(band, 0) + 1
        else:
            crash_speeds.append(env.speed)

    print("start altitude     AI lands    best possible")
    for band in sorted(games_in_band):
        ai = wins_in_band.get(band, 0) / games_in_band[band] * 100
        best = 0.0
        for start, end in ranges:
            best = best + max(0.0, min(end, band + 20) - max(start, band))
        best = best / 20 * 100
        print(f"{band}-{band + 20} m        {ai:5.1f} %      {best:5.1f} %")

    near = 0
    medium = 0
    hard = 0
    for s in crash_speeds:
        if s <= 20:
            near = near + 1
        elif s <= 40:
            medium = medium + 1
        else:
            hard = hard + 1
    print()
    print("how the failures look (share of ALL games):")
    print(f"  near-miss crash  (10-20 m/s): {near / games * 100:5.1f} %")
    print(f"  medium crash     (20-40 m/s): {medium / games * 100:5.1f} %")
    print(f"  hard crash       (over 40 m/s): {hard / games * 100:5.1f} %")


if __name__ == "__main__":
    model = PPO.load("ppo_rocket_seed0")
    analyze(model)