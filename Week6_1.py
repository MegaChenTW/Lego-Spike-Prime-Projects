from hub import light_matrix, port
import color
import color_sensor
import runloop
import motor_pair

PHI = 80
# measure
REAL_WHITE = 65
REAL_BLACK = 25
REAL_AVG = (REAL_WHITE + REAL_BLACK) / 2
# constant 
dt = 50

def display_intensty(num):
    for i in range (num // 20):
        light_matrix.set_pixel(i , 0, 100)

async def main():
    motor_pair.pair(motor_pair.PAIR_1, port.C, port.D)
    while True:
        ref = color_sensor.reflection(port.A)
        display_intensty(ref)
        print("ref:", ref)
        # turn left
        if ref > REAL_AVG:
            await motor_pair.move_tank_for_time(motor_pair.PAIR_1, int(PHI * 0.2), PHI, dt)
        else:
            await motor_pair.move_tank_for_time(motor_pair.PAIR_1, int(PHI * 1.2), int(PHI * 0.2), dt)

    # write your code here
    await light_matrix.write("Hi!")

runloop.run(main())

