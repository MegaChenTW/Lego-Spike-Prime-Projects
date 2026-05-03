from hub import light_matrix, motion_sensor,port
import runloop
import motor_pair
import distance_sensor
import time

TARGET = 0
PHI = 900
KP = 8
KD = 3.5
KI = 0.002

class PID_controller():
    def __init__(self, now_time, kp=KP, ki=KI, kd=KD):
        self.kp = KP
        self.ki = KI
        self.kd = KD
        self.dt = 0
        self.last_time = now_time
        self.last_err = 0
        self.accum = 0

    def PID_calculate(self, err: float):
        current_time = time.ticks_ms()
        self.dt = current_time - self.last_time
        self.accum += err * self.dt
        c = err * self.kp + self.accum * self.ki + (err - self.last_err) / self.dt * self.kd
        #update
        self.last_time = current_time
        self.last_err = err

        return (c * PHI)


async def main():
    motor_pair.pair(motor_pair.PAIR_1, port.C, port.D)
    motion_sensor.set_yaw_face(motion_sensor.TOP)
    wheel_pid = PID_controller(now_time=time.ticks_ms())
    await runloop.sleep_ms(10)
    # write your code here
    while True:
        # Balance
        #print("y,p,r: ", motion_sensor.tilt_angles())
        err = (motion_sensor.tilt_angles()[1] - TARGET)/900
        control = int(wheel_pid.PID_calculate(err))
        #print("err :", err)
        #print("con:", control)
        motor_pair.move_tank(motor_pair.PAIR_1, control, control)
        await runloop.sleep_ms(5)


runloop.run(main())