from hub import light_matrix
from hub import port
import color_sensor
import color
import motor_pair
import runloop

PHI = -300
RED = (275, 150,175 , 450)
YELLOW = (350,320,250, 707)
BLUE = (260, 120, 140, 411)
TOLERATE_RANGE = 250

motor_pair.pair(motor_pair.PAIR_1, port.C, port.D)

def same_color(input_:tuple[int,int,int,int], compare:tuple[int,int,int,int]):
    total_err = 0
    for i in input_:
        total_err += abs(input_[i] - compare[i])
    if(total_err < TOLERATE_RANGE):
        return True
    else:
        return False

def go_straight(vel : int):
    light_matrix.write('F')
    motor_pair.move_tank(motor_pair.PAIR_1, vel, vel)

async def turn_right(turn : float, dir : int):
    if(dir == 1):
        print('R')
        await light_matrix.write('R')
        await motor_pair.move_tank_for_degrees(motor_pair.PAIR_1, int(turn * 360), 0, PHI * dir)
    elif(dir == -1):
        print('L')
        await light_matrix.write('L')
        await motor_pair.move_tank_for_degrees(motor_pair.PAIR_1, int(turn * 360),-PHI* dir, 0)

async def rotate(turn : float):
    await motor_pair.move_tank_for_degrees(motor_pair.PAIR_1, int(turn * 360), -PHI , PHI )

async def main():
    turn_flag = 1
    while(True):
        co = color_sensor.color(port.A)
        rgbi = color_sensor.rgbi(port.A)
            #rotate
        #if(co == color.RED):
        if(same_color(rgbi, RED)):
            # -dir => left
            print(rgbi)
            await turn_right(1.2 , -turn_flag)
        #elif(co == color.YELLOW):
        elif(same_color(rgbi,YELLOW)):
            print(rgbi)
            await turn_right(1.2 , turn_flag)
        #elif(co == color.BLUE):
        elif(same_color(rgbi, BLUE)):
            # reuse the turn function to make rotation
            print(rgbi)
            await rotate(1.15)
            turn_flag = -1
        # Stop
        #elif(co == color.BLACK):
        elif(rgbi[3] < 300):
            go_straight(0)
            #reset_color = False
            await light_matrix.write('S')
        else:
            go_straight(PHI)

runloop.run(main())
