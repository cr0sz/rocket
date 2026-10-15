#fucking rocket will fly at the end of this shit


altitude = 500.0
speed = 0.0
gravity = 9.8
thrust = 20.0
fuel = 45
fuel_per_burn = 5
max_safe_speed = 10.0

second = 0 

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


while altitude > 0:
    choice = input("Burn the engine y/n: ").lower().strip()
    burn = (choice == "y")
    altitude, speed, fuel = step(altitude, speed, fuel, burn)
    second = second + 1
    result = check_landing(speed)
    print(f"t={second}s  alt={altitude:.1f} m  speed={speed:.1f} m/s  fuel: {fuel}")

if result == "crashed":
    print(f"Hit the ground at {speed:.1f} m/s")
else:
    print("Safely Landed")