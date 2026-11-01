# plots.py - makes the pictures for your report.   Run:  python plots.py
# Needs matplotlib:   pip install matplotlib
import json
import os
import matplotlib
matplotlib.use("Agg")                      # draw to files, no window needed
import matplotlib.pyplot as plt

RESULTS_FILE = "results.json"

# ------------------------------------------------------------------
# 1) YOUR NUMBERS. Read from results.json (written by evaluate.py).
#    ceiling and best_by_band are theoretical (from ceiling.py),
#    not evaluation results, so they stay as constants.
# ------------------------------------------------------------------
with open(RESULTS_FILE) as f:
    _data = json.load(f)


def _find(controller, obs_mode=None, seed=None):
    for r in _data:
        if r["controller"] != controller:
            continue
        if obs_mode is not None and r["obs_mode"] != obs_mode:
            continue
        if seed is not None and r["seed"] != seed:
            continue
        return r


def _rate(controller, obs_mode=None, seed=None):
    r = _find(controller, obs_mode, seed)
    return r["landings"] / r["games"] * 100


random_rate = _rate("random")
hand_rule = _rate("hand_rule")
ceiling = 74.2                                 # theoretical, from ceiling.py
basic_seeds = [_rate("ppo", "basic", s) for s in range(5)]
ext_seeds = [_rate("ppo", "extended", s) for s in range(5)]

bands = [f"{b['alt_min']}-{b['alt_max']}" for b in _find("ppo", "extended", 0)["bands"]]
basic_by_band = [b["landings"] / b["games"] * 100 for b in _find("ppo", "basic", 0)["bands"]]
ext_by_band = [b["landings"] / b["games"] * 100 for b in _find("ppo", "extended", 0)["bands"]]
best_by_band = [88.0, 88.0, 88.0, 88.0, 65.0, 65.0, 65.0, 65.0, 65.0, 65.0]  # theoretical


def average(values):
    return sum(values) / len(values)


# ------------------------------------------------------------------
# 2) Picture 1: the comparison (the main result)
# ------------------------------------------------------------------
names = ["random", "hand rule", "PPO\nbasic inputs", "PPO + forecast\ninputs", "best\npossible"]
heights = [random_rate, hand_rule, average(basic_seeds), average(ext_seeds), ceiling]
low_err = [0, 0, average(basic_seeds) - min(basic_seeds), average(ext_seeds) - min(ext_seeds), 0]
high_err = [0, 0, max(basic_seeds) - average(basic_seeds), max(ext_seeds) - average(ext_seeds), 0]

plt.figure(figsize=(8, 5))
plt.bar(names, heights, yerr=[low_err, high_err], capsize=6,
        color=["#999999", "#c9a227", "#4c78a8", "#2e8b57", "#555555"])
for i, h in enumerate(heights):
    plt.text(i, h + 2, f"{h:.1f}%", ha="center")
plt.ylabel("landing rate (%)")
plt.ylim(0, 90)
plt.title("Rocket landing: who lands the most?\n(bars = average over seeds, lines = worst to best seed)")
plt.tight_layout()
plt.savefig("comparison.png", dpi=150)
plt.close()
print("saved comparison.png")

# ------------------------------------------------------------------
# 3) Picture 2: landing rate per start altitude
# ------------------------------------------------------------------
x = range(len(bands))
width = 0.27
plt.figure(figsize=(10, 5))
plt.bar([i - width for i in x], basic_by_band, width, label="PPO basic inputs", color="#4c78a8")
plt.bar([i for i in x], ext_by_band, width, label="PPO + forecast inputs", color="#2e8b57")
plt.bar([i + width for i in x], best_by_band, width, label="best possible", color="#555555")
plt.xticks(list(x), bands, rotation=30)
plt.xlabel("start altitude (m)")
plt.ylabel("landing rate (%)")
plt.title("Where does the AI fail? (seed 0)")
plt.legend()
plt.tight_layout()
plt.savefig("by_altitude.png", dpi=150)
plt.close()
print("saved by_altitude.png")


# ------------------------------------------------------------------
# 4) Picture 3: learning curve (only if train.py saved logs in the logs/ folder)
# ------------------------------------------------------------------
def load_games(folder):
    # every environment writes "<number>.monitor.csv": one comment line, one header line,
    # then one line per finished game: reward, length, time
    games = []
    for name in os.listdir(folder):
        if name.endswith(".monitor.csv"):
            with open(os.path.join(folder, name)) as f:
                f.readline()                               # comment line
                for line in f.readlines()[1:]:             # skip the header "r,l,t"
                    r, l, t = line.strip().split(",")
                    games.append((float(t), float(r), int(float(l))))
    games.sort()                                           # oldest game first
    return games


if os.path.isdir("logs"):
    plt.figure(figsize=(8, 5))
    drew_something = False
    for folder in sorted(os.listdir("logs")):
        games = load_games(os.path.join("logs", folder))
        if len(games) < 500:
            continue
        steps = []
        rewards = []
        total = 0
        for t, r, l in games:
            total = total + l
            steps.append(total)
            rewards.append(r)
        window = 1000
        smooth_x = []
        smooth_y = []
        for i in range(window, len(rewards), 200):
            smooth_x.append(steps[i])
            smooth_y.append(sum(rewards[i - window:i]) / window)
        plt.plot(smooth_x, smooth_y, label=folder)
        drew_something = True
    if drew_something:
        plt.xlabel("training steps")
        plt.ylabel("average reward per game")
        plt.title("Learning curve (training games, smoothed)")
        plt.legend()
        plt.tight_layout()
        plt.savefig("learning_curve.png", dpi=150)
        print("saved learning_curve.png")
    plt.close()
else:
    print("no logs/ folder yet - train seeds 3 and 4 with the new train.py to get a learning curve")