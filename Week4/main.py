from hub import light_matrix
import motor_pair
from hub import port
import runloop
from time import sleep
import force_sensor
import distance_sensor


#phi : angular velocity of wheel
phi = 250

motor_pair.pair(motor_pair.PAIR_1, port.A,port.B)

def go_straight():
    #print("straight")
    motor_pair.move_tank(motor_pair.PAIR_1, phi, phi)

async def turn_left(turn:float):
    print("back")
    await motor_pair.move_tank_for_degrees(motor_pair.PAIR_1, int(0.1 * 360), -phi, -phi)
    print("left")
    await motor_pair.move_tank_for_degrees(motor_pair.PAIR_1, int(turn * 360), -phi, phi)
    print("left done")

async def turn_right(turn:float):
    print("back")
    await motor_pair.move_tank_for_degrees(motor_pair.PAIR_1, int(0.1 * 360), -phi, -phi)
    print("right")
    await motor_pair.move_tank_for_degrees(motor_pair.PAIR_1, int(turn * 360), phi, -phi)
    print("right done")

#motor_pair.move_tank(motor_pair.PAIR_1, 100,100)
#sleep(3)
async def task():
    while(True):
        go_straight()
        if(force_sensor.pressed(port.E)):
            dis2r = distance_sensor.distance(port.C)
            print(str(dis2r))
            if(dis2r < 500 and dis2r != -1): #右邊有牆
                await turn_left(0.35)
            else:
                await turn_right(0.35)

runloop.run(task())
