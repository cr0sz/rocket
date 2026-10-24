import gymnasium as gym
import numpy as np
from gymnasium import spaces
import rocket


class RocketEnv(gym.Env):
    # extended=False: the AI sees 3 numbers (altitude, speed, fuel)
    # extended=True : the AI also sees 4 "forecast" numbers (see _forecast)
    def __init__(self, extended=False):
        super().__init__()
        self.extended = extended
        self.action_space = spaces.Discrete(2)
        size = 7 if extended else 3
        self.observation_space = spaces.Box(low=-2.0, high=2.0, shape=(size,), dtype=np.float32)

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

    def _forecast(self, burn_first):
        # Imagine: I (maybe) burn this second, then NEVER burn again.
        # How many seconds until the ground, and how fast do I hit it?
        # This only uses the same physics the game already has.
        alt, speed, fuel = self.altitude, self.speed, self.fuel
        burn = burn_first
        seconds = 0
        while alt > 0:
            alt, speed, fuel = rocket.step(alt, speed, fuel, burn)
            burn = False
            seconds = seconds + 1
        return seconds, speed

    def _obs(self):
        values = [self.altitude / 1000, self.speed / 100, self.fuel / 45]
        if self.extended:
            s1, v1 = self._forecast(False)     # forecast if I coast now
            s2, v2 = self._forecast(True)      # forecast if I burn now
            values = values + [s1 / 20, v1 / 100, s2 / 20, v2 / 100]
        return np.array(values, dtype=np.float32)