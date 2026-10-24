import gymnasium as gym
import numpy as np
from gymnasium import spaces
import rocket

class RocketEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Box(low=-2.0, high=2.0, shape=(3,), dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.altitude = self.np_random.uniform(400, 600)
        self.speed = 0.0
        self.fuel = 45
        return self._obs(), {}

    def step(self, action):
        burn = (action == 1)
        self.altitude, self.speed, self.fuel = rocket.step(self.altitude, self.speed, self.fuel, burn)

        terminated = bool(self.altitude <= 0)
        reward = 0.0
        if terminated:
            if rocket.check_landing(self.speed) == "landed":
                reward = 1.0
            else:
                reward = -self.speed / 100

        return self._obs(), reward, terminated, False, {}

    def _obs(self):
        return np.array([self.altitude / 1000, self.speed / 100, self.fuel / 45], dtype=np.float32)