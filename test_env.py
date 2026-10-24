from rocket_env import RocketEnv
from stable_baselines3.common.env_checker import check_env

env = RocketEnv()
obs, info = env.reset(seed=42)
print(obs)
print(env.observation_space)
print(env.action_space)

check_env(env)
print("env OK")