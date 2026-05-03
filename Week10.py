from hub import light_matrix, port
import runloop
import motor_pair
import motor
import distance_sensor

THRESHOLD = 500
PHI = 300
ABS_ANGLE = 80

motor_pair.pair(motor_pair.PAIR_1, port.C, port.D)

async def move_forward(turn : float):
    await motor_pair.move_tank_for_degrees(motor_pair.PAIR_1, int(turn * 360), PHI, PHI)

async def pick_ball():
    await motor.run_to_absolute_position(port.B, ABS_ANGLE, 200)

async def place_ball():
    await motor.run_to_absolute_position(port.B, -10, 200)

async def main():
    await place_ball()
    await move_forward(1)
    await pick_ball()
    count_time = 0
    count_time_max  = 15
    while True:
        if(count_time < count_time_max):
            await motor_pair.move_tank_for_degrees(motor_pair.PAIR_1, 10, -50, 50)
        elif( count_time < count_time_max * 2):
            await motor_pair.move_tank_for_degrees(motor_pair.PAIR_1, 10, 50, -50)
        else :
            await motor_pair.move_tank_for_degrees(motor_pair.PAIR_1, 10, 50, -50)
        await runloop.sleep_ms(100)
        count_time += 1
        dis = distance_sensor.distance(port.A)
        print("dis: ", dis)
        if(dis > THRESHOLD or dis == -1):   #detected
            light_matrix.write('D')
            motor_pair.move_tank(motor_pair.PAIR_1, 0, 0)
            break
    await place_ball()

    #await light_matrix.write("Hi!")

runloop.run(main())
