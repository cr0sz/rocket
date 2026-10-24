from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from rocket_env import RocketEnv

SEEDS = [1, 2, 3, 4]                      # later: [0, 1, 2, 3, 4]
STEPS = 1_000_000                  # first a short test, then change to 1_000_000

for seed in SEEDS:
    env = make_vec_env(RocketEnv, n_envs=8, seed=seed)
    model = PPO(
        "MlpPolicy",
        env,
        n_steps=256,             # each of the 8 games plays 256 steps per round (8 x 256 = 2048)
        batch_size=256,          # the network studies that data in chunks of 256
        n_epochs=10,             # ... going through all of it 10 times
        gamma=0.99,              # how much future reward counts
        ent_coef=0.01,           # small bonus for trying different things
        learning_rate=3e-4,      # how big each nudge is
        seed=seed,
        device="cpu",
        verbose=1,
    )
    model.learn(total_timesteps=STEPS)
    model.save(f"ppo_rocket_seed{seed}")
    print("saved ppo_rocket_seed" + str(seed))
    