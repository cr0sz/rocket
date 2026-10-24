# ceiling.py - what is the BEST any player could ever do in this game?
#
# Idea: the speed you hit the ground with depends ONLY on two things:
#   T = how many seconds the fall lasted, b = how many burns you used.
#       speed_at_ground = 9.8 * T - 20 * b
# So we only look at (T, b) pairs that end with a safe speed, try every way of
# choosing WHEN to burn, and see which start altitudes each schedule can land.
#
# Now wrapped in a function so other files (analysis.py) can reuse it.

from itertools import combinations
import rocket

LOW, HIGH = 400.0, 600.0       # the start altitudes your game uses


def landable_ranges():
    """List of (from_altitude, to_altitude): start heights that SOME burn schedule can land."""
    ranges = []
    for T in range(1, 26):                         # fall lasts T seconds
        for b in range(0, 10):                     # 0 to 9 burns (45 fuel / 5 per burn)
            landing_speed = rocket.gravity * T - rocket.thrust * b
            if not (0 < landing_speed <= rocket.max_safe_speed):
                continue                           # this (T, b) can never land safely, skip it
            for burn_seconds in combinations(range(1, T + 1), b):   # every way to pick burn moments
                alt, speed, fuel = 0.0, 0.0, 45    # pretend we start at altitude 0 and measure the drop
                deepest = 0.0                      # farthest drop reached BEFORE the last second
                for t in range(1, T + 1):
                    alt, speed, fuel = rocket.step(alt, speed, fuel, t in burn_seconds)
                    if t < T:
                        deepest = max(deepest, -alt)
                drop = -alt                        # total drop at second T
                # this schedule lands exactly the start altitudes in (deepest, drop]
                if drop > LOW and deepest < HIGH and drop > deepest:
                    ranges.append((max(deepest, LOW), min(drop, HIGH)))

    # merge overlapping ranges
    ranges.sort()
    merged = []
    for start, end in ranges:
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged


if __name__ == "__main__":
    merged = landable_ranges()
    landable = 0.0
    for start, end in merged:
        landable = landable + (end - start)
    print("best possible landing rate: %.1f %%" % (landable / (HIGH - LOW) * 100))