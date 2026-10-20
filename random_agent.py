import gymnasium as gym

env = gym.make("LunarLander-v3")
obs, info = env.reset(seed=42)

env.action_space.seed(42)
results = []

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

for i in range(100):
    results.append(run_episode(env))

print(sum(results) / len(results) , max(results), min(results))

env.close()