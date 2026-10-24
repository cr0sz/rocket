from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from rocket_env import RocketEnv

EXTENDED = True                  # False = basic inputs (3 numbers), True = plus 4 forecast inputs
SEEDS = [3, 4]                   # seeds 0, 1, 2 are already trained
STEPS = 1_000_000

NAME = "ppo_rocket_ext_seed" if EXTENDED else "ppo_rocket_seed"

for seed in SEEDS:
    env = make_vec_env(RocketEnv, n_envs=8, seed=seed, env_kwargs=dict(extended=EXTENDED),
                       monitor_dir=f"logs/{NAME}{seed}")   # saves a log of every game, for the learning curve
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
    model.save(f"{NAME}{seed}")
    print("saved " + NAME + str(seed))