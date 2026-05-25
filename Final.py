from hub import light_matrix, motion_sensor, port, sound
import motor_pair
import time
import math
import heapq

# sould be 0, but add offset for better performance
TARGET = 12
PHI = 900

class PID_controller():
    def __init__(self, now_time, kp=1, ki=0, kd=0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.dt = 0
        self.last_time = now_time
        self.last_err = 0
        self.accum = 0

    def PID_calculate(self, err: float):
        current_time = time.ticks_ms()
        self.dt = current_time - self.last_time

        # avoid divided by 0
        if self.dt <= 0:
            self.dt = 1

        self.accum += err * self.dt
        c = err * self.kp + self.accum * self.ki + ((err - self.last_err) / self.dt) * self.kd

        self.last_time = current_time
        self.last_err = err

        return c

class Node:
    def __init__(self, r, c, parent=None):
        self.r = r        # Row (0-4)
        self.c = c        # Column (0-4)
        self.parent = parent
        self.g = 0
        self.h = 0
        self.f = 0

    # To compare with '=' sign
    def __eq__(self, other):
        return self.r == other.r and self.c == other.c
    # To compare in heapq
    def __lt__(self, other):
        return self.f < other.f

# Dummy class
class Task:
    def __init__(self, period_ms):
        self.period = period_ms
        self.last_time = time.ticks_ms()

    def run(self):
        # To be override by child
        pass

class Song_Task(Task):
    def __init__(self):
        BPM = 114
        beat_ms = round(60000 / BPM) # 每拍(四分音符)的毫秒數: ~526ms

        # 根據 BPM 定義精確的音符持續時間 (毫秒)
        VS = round(beat_ms / 4)# 十六分音符
        S = round(beat_ms / 2)    # 八分音符
        L = beat_ms            # 四分音符
        EL = round(beat_ms * 1.5) # 附點四分音符
        H = round(beat_ms * 2)    # 二分音符

        # 2. 定義精確的音符頻率 (Hz)
        REST = 0# ⭐️ 定義休止符頻率為 0
        A4 = 440
        B4 = 494
        CS5 = 554
        D5 = 587
        E5 = 659
        FS5 = 740
        A5 = 880

        # 3. 建立 2D Array 旋律 (在每個樂句後加上適當的休止符)
        self.melody = [
            # We're no strangers to love + 休止符
            [B4, S], [CS5, S], [D5, S], [D5, L], [E5, S], [CS5, S], [B4, S], [A4, EL], [REST, L],

            # You know the rules and so do I + 休止符
            [B4, S], [B4, S], [CS5, S], [D5, S], [B4, S], [A4, L], [A5, S], [A5, S], [E5, EL], [REST, L],

            # A full commitment's what I'm thinking of + 短休止符
            [B4, S], [B4, S], [CS5, S], [D5, S], [B4, S], [D5, S], [E5, S], [CS5, S], [B4, S], [CS5, S], [B4, S], [A4, L], [REST, S],

            # You wouldn't get this from any other guy + 長休止符
            [B4, S], [B4, S], [CS5, S], [D5, S], [B4, S], [A4, L], [E5, S], [E5, S], [E5, S], [FS5, S], [E5, EL], [REST, H],

            # I just wanna tell you how I'm feeling
            [D5, VS], [E5, VS], [FS5, VS], [D5, VS], [E5, S], [E5, L], [E5, S], [FS5, S], [E5, S], [A4, EL], [REST, S],

            # Gotta make you understand... + 準備進入副歌的停頓
            [B4, VS], [CS5, VS], [D5, L], [B4, S], [E5, S], [FS5, S], [E5, EL], [REST, L],

            # Never gonna give you up
            [A4, S], [B4, S], [D5, S], [B4, S], [FS5, L], [FS5, L], [E5, EL], [REST, S],

            # Never gonna let you down
            [A4, S], [B4, S], [D5, S], [B4, S], [E5, L], [E5, L], [D5, S], [CS5, S], [B4, EL], [REST, S],

            # Never gonna run around and desert you
            [A4, S], [B4, S], [D5, S], [B4, S], [D5, L], [E5, S], [CS5, S], [A4, S], [A4, S], [E5, L], [D5, EL], [REST, S],

            # Never gonna make you cry
            [A4, S], [B4, S], [D5, S], [B4, S], [FS5, L], [FS5, L], [E5, EL], [REST, S],

            # Never gonna say goodbye
            [A4, S], [B4, S], [D5, S], [B4, S], [A5, L], [CS5, S], [D5, S], [CS5, S], [B4, EL], [REST, S],

            # Never gonna tell a lie and hurt you
            [A4, S], [B4, S], [D5, S], [B4, S], [D5, VS], [E5, VS], [CS5, VS], [A4, S], [A4, S], [E5, L], [D5, EL], [REST, H]
        ]
        super().__init__(100)
        self.index = 0
        self.is_playing = True

    def run(self):
        if not self.is_playing:
            return

        freq, duration = self.melody[self.index]
        sound.beep(freq=freq, duration=duration, volume=100, attack=10 , waveform=sound.WAVEFORM_SAWTOOTH)
        self.period = duration + 50

        self.index += 1
        if self.index >= len(self.melody):
            self.index = 0 # 歸零代表無限循環播放 (也可改為 self.is_playing = False 停播)

class A_Star_Visualization_Task(Task):
    def __init__(self, period_ms=500):
        super().__init__(period_ms)

        self.start_node = Node(0, 0)
        self.goal_node = Node(4, 4)

        # 寫入指定的迷宮地圖 (0: unknown, 1: blocked)
        self.map_grid = [
            [0, 0, 0, 0, 0],
            [1, 1, 0, 1, 1],
            [0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1],
            [0, 0, 0, 0, 0]
        ]

        self.obstacles = []
        for r in range(5):
            for c in range(5):
                if self.map_grid[r][c] == 1:
                    self.obstacles.append((r, c))

        self.open_list = [self.start_node]
        self.closed_list = []
        self.state = "SEARCHING"# SEARCHING, PATH_FOUND, NO_PATH
        self.path = []

    def heuristic(self, node_a, node_b):
        return math.sqrt((node_a.r - node_b.r)**2 + (node_a.c - node_b.c)**2)

    def render(self):
        """
        - explored : 85
        - open_set : 50
        - path_reconstruction : 100
        - obstacles :30
        """
        for r in range(5):
            for c in range(5):
                intensity = 0 #default dark
                pos = (r, c)

                if self.state == "PATH_FOUND" and pos in self.path:
                    intensity = 100

                elif pos in self.obstacles:
                    intensity = 30

                elif self.state == "SEARCHING":
                    in_closed = any(n.r == r and n.c == c for n in self.closed_list)
                    in_open = any(n.r == r and n.c == c for n in self.open_list)

                    if pos == (self.start_node.r, self.start_node.c) or pos == (self.goal_node.r, self.goal_node.c):
                        intensity = 100# 起點終點始終高亮
                    elif in_closed:
                        intensity = 85# explored (已探索)
                    elif in_open:
                        intensity = 50# open_set (待探索)

                light_matrix.set_pixel(r, c, intensity)

    def run(self):
        # found or no path
        if self.state == "PATH_FOUND" or self.state == "NO_PATH":
            return
        # no path
        if len(self.open_list) == 0:
            self.state = "NO_PATH"
            self.render()
            return

        current_node = heapq.heappop(self.open_list)
        self.closed_list.append(current_node)

        # path reconstruct
        if current_node == self.goal_node:
            self.state = "PATH_FOUND"
            current = current_node
            while current is not None:
                self.path.append((current.r, current.c))
                current = current.parent
            self.render()
            return

        # euclidean
        directions = [
            (0, 1), (0, -1), (1, 0), (-1, 0),# 上下左右
            (1, 1), (1, -1), (-1, 1), (-1, -1)# 四個對角
        ]
        for dr, dc in directions:
            new_r, new_c = current_node.r + dr, current_node.c + dc

            # boundary and block
            if not (0 <= new_r <= 4 and 0 <= new_c <= 4):
                continue
            if (new_r, new_c) in self.obstacles:
                continue

            neighbor = Node(new_r, new_c, current_node)
            # skip if explored
            if any(neighbor == closed_node for closed_node in self.closed_list):
                continue

            if dr == 0 or dc == 0:
                step_cost = 1.0
            else:
                step_cost = 1.414

            # cal g, h, f
            neighbor.g = current_node.g + step_cost
            neighbor.h = self.heuristic(neighbor, self.goal_node)
            neighbor.f = neighbor.g + neighbor.h

            # skip if in openset and new g is not smaller
            is_worse = False
            for open_node in self.open_list:
                if neighbor == open_node and neighbor.g >= open_node.g:
                    is_worse = True
                    break

            if not is_worse:
                heapq.heappush(self.open_list, neighbor)

        self.render()

class Balance_Car_Task(Task):
    def __init__(self, period_ms = 5):
        super().__init__(period_ms)
        motor_pair.pair(motor_pair.PAIR_1, port.C, port.D)
        motion_sensor.set_yaw_face(motion_sensor.TOP)

        now = time.ticks_ms()

        # PID for yaw and pitch
        self.pitch_pid = PID_controller(now, kp=5, ki=0.02, kd=2)
        self.yaw_pid = PID_controller(now, kp=0.5, ki=0, kd=0.5)

        self.target_yaw = 0
        self.first_run = True

    def turn(self, angle_deg):

        self.target_yaw = (angle_deg * 10)
        print("goal", {self.target_yaw})

    def run(self):
        current_yaw, current_pitch, r= motion_sensor.tilt_angles()

        # --- PID ---
        pitch_err = (current_pitch - TARGET) / 900
        base_control = int(self.pitch_pid.PID_calculate(pitch_err) * PHI)

        yaw_err = (self.target_yaw - current_yaw) / 900
        #print("yaw now: ", current_yaw)
        #print("goal yaw: ", self.target_yaw)
        #print("yaw diff: " , yaw_err)
        #                                                    smaller balance, bigger turn
        v_dif = int(self.yaw_pid.PID_calculate(yaw_err) * 0.1 * abs(PHI - abs(base_control)))

        # pure balance
        #motor_pair.move_tank(motor_pair.PAIR_1, base_control, base_control)
        # add turn
        motor_pair.move_tank(motor_pair.PAIR_1, base_control - v_dif, base_control + v_dif)


def main():
    car_task = Balance_Car_Task()
    song_task = Song_Task()
    astar_task = A_Star_Visualization_Task()

    tasks = [car_task, song_task, astar_task]

    position = [(5000, 50), (12000, 120), (18000, 180)]

    start_time = time.ticks_ms()
    has_turned = False

    k = 0
    while True:
        current_time = time.ticks_ms()
        
        if not has_turned:
            if(current_time - start_time > position[k][0]):
                car_task.turn(position[k][1])
                has_turned = True
                if (k < len(position) - 1):
                    k += 1
                    has_turned = False

        for i in tasks:
            if(current_time - i.last_time >= i.period):
                i.run()
                i.last_time = current_time


main()