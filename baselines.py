from rocket_env import RocketEnv

env = RocketEnv()
env.reset(seed=42)
env.action_space.seed(42)

def run_episode(env):
    total_reward = 0.0
    obs, info = env.reset()
    while True:
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        if terminated or truncated:
            break
    return total_reward

results = []
for i in range(1000):
    results.append(run_episode(env))

wins = 0
for r in results:
    if r > 0:
        wins = wins + 1

print("random agent: average reward", sum(results) / len(results))
print("random agent: landing rate", wins / len(results) * 100, "%")