#fucking rocket will fly at the end of this shit
import random

gravity = 9.8
thrust = 20.0
fuel_per_burn = 5
max_safe_speed = 10.0

def step(altitude, speed, fuel, burn):
    if burn and fuel > 0:
        speed = speed - thrust
        fuel = fuel - fuel_per_burn
    speed = speed + gravity
    altitude = altitude - speed
    return altitude, speed, fuel 

def check_landing(speed):
    if speed > max_safe_speed:
        return "crashed"
    else:
        return "landed"

def never_burn(altitude, speed, fuel):
    return False

def always_burn(altitude, speed, fuel):
    return True

def burn_if_fast(altitude, speed, fuel):
        return speed > 30
    
def burn_if_low(altitude, speed, fuel):
        return altitude < 150


def play(controller=None, start_altitude=500.0, verbose=True):
    altitude = start_altitude
    speed = 0.0
    fuel = 45
    second = 0

    while altitude > 0:
        if controller is None:
            choice = input("Burn the engine y/n: ").lower().strip()
            burn = (choice == "y")
        else:
            burn = controller(altitude, speed, fuel)
        
        altitude, speed, fuel = step(altitude, speed, fuel, burn)
        second = second + 1
        if verbose: 
            print(f"t={second}s  alt={altitude:.1f} m  speed={speed:.1f} m/s  fuel: {fuel}")
    
    result = check_landing(speed)
    if verbose:
        if result == "crashed":
            print(f"Hit the ground at {speed:.1f} m/s")
        else:
            print("Safely Landed")
    return result

def win_rate(controller, games= 1000):
    wins = 0
    for i in range(games):
        start = random.uniform(400, 600)
        result = play(controller, start, False)
        if result != "crashed":
            wins = wins + 1
    return wins / games * 100




print(win_rate(never_burn))
print(win_rate(always_burn))
print(win_rate(burn_if_fast))
print(win_rate(burn_if_low))


