from hub import light_matrix, motion_sensor,port
import runloop
import motor_pair

TARGET = 0
PHI = 1000
KP = 5
KD = 2
KI = 0.0
dt = 0.1
last_err = 0
accum = 0

def PD_control(err):
    global last_err, accum
    accum += err * dt
    c = err * KP + accum * KI - (err - last_err) / dt * KD
    last_err = err
    return int(c * PHI)

async def main():    
    motor_pair.pair(motor_pair.PAIR_1, port.C, port.D)
    motion_sensor.set_yaw_face(motion_sensor.TOP)
    # write your code here
    while True:
        #print("y,p,r: ", motion_sensor.tilt_angles())
        err = (motion_sensor.tilt_angles()[1] - TARGET)/900
        control = PD_control(err)
        #print("err :", err)
        #print("con:", control)
        motor_pair.move_tank(motor_pair.PAIR_1, control, control)
        #await runloop.sleep_ms(1)
        last_err = err
    await light_matrix.write("Hi!")

runloop.run(main())

