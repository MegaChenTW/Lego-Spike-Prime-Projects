from hub import light_matrix, port
import color
import color_sensor
import runloop
import motor_pair

PHI = 200
P = 10
# measure
REAL_WHITE = 60
REAL_BLACK = 30
REAL_AVG = (REAL_WHITE + REAL_BLACK) / 2

def cal_phi(num):
    return abs(num / (REAL_WHITE - REAL_BLACK)) * PHI

def display_intensty(row, num):
    for i in range (num // 20):
        light_matrix.set_pixel(i , row, 100)

async def main():
    motor_pair.pair(motor_pair.PAIR_1, port.C, port.D)
    while True:
        ref_r = color_sensor.reflection(port.A)
        ref_l = color_sensor.reflection(port.B)
        print("r: ", ref_r, "l: ", ref_l)
        display_intensty(0, ref_r)
        display_intensty(1, ref_l)
        err = (ref_r - ref_l) / 100
        # turn left
        if err > 0:
            motor_pair.move_tank(motor_pair.PAIR_1, int(PHI * err * P), PHI)
        else:
            motor_pair.move_tank(motor_pair.PAIR_1, PHI, int(PHI * abs(err) * P))
        runloop.sleep_ms(5)

    # write your code here
    await light_matrix.write("Hi!")

runloop.run(main())

