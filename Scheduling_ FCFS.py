"""
Name: Joshua Gardner
Content: Scheduling Program
Description: FCFS scheduling
Date: 10/25/2021
"""

from enum import Enum


class State(Enum):
    # enum consists of process states - life cycle
    New = 0
    Ready = 1
    Running = 2
    Waiting = 3
    Terminated = 4


def evaluate_utilization(os):  # evaluates cpu utilization
    return (os.cpu_time_used / os.cpu_time_total) * 100


def evaluate_tw(p):  # evaluates process waiting time (Tw)
    burst_total = 0
    for burst in p.burst_nums:
        burst_total += burst
    return abs(evaluate_ttr(p) - burst_total)


def evaluate_ttr(p):  # evaluates process turn around time (Ttr)
    return abs(p.terminated_time - p.arrival_time)


def evaluate_tr(p):  # evaluates process response time Tr
    return abs(p.started_time - p.arrival_time)


class PLC(object):  # process and state control (Process Life Cycle)
    def __init__(self, all_p, schedule_method_str):
        self.processes = all_p
        self.const_p = all_p
        self.current_p = None
        self.terminated_p = []
        self.shortest_p = None
        self.wait_q = []
        self.p_running = None
        self.rdy_q = []
        self.time = 0
        self.finished = False
        self.cpu_time_used = 0
        self.cpu_time_total = 0
        self.schedule_method = schedule_method_str
        self.q1 = []
        self.q2 = []
        self.q3 = []
        self.info_string = ""
        self.display_info = True
        for item in all_p:  # modifies ready queue
            self.new(item)
            for i in range(0, len(item.burst_nums)):
                if i % 2 == 0:
                    self.cpu_time_used += item.burst_nums[i]

    def new(self, p):  # sets new process
        self.rdy_q.append(p)
        p.state = State.Ready

    def rdy(self, p):  # Scheduling
        self.first_come_first_serve(self.rdy_q[0])  # FCFS

    def waiting(self, p):  # directs waiting queue
        if p == self.current_p:
            self.info_string += "I/O Burst Remaining: " + str(p.name) + " " + str(p.burst) + "\n"
            if p.burst == 0 and p.index == p.final_index:  # when final process completes
                p.state = State.Terminated
                self.wait_q.remove(p)
                self.terminated(p)

            elif p.burst == 0:   # when a process completes
                p.state = State.Ready
                p.index += 1
                p.burst = p.burst_nums[p.index]
                p.is_cpu_burst = True
                self.wait_q.remove(p)
                self.rdy_q.append(p)
                self.rdy(p)

            elif p.burst > 0:  # when process still running
                p.burst -= 1

    def running(self, p):  # directs process currently running

        if p == self.current_p:
            self.p_running = p

            if p.burst == 0 and p.index == p.final_index:  # when all processes complete
                self.display_info = True
                p.state = State.Terminated
                self.p_running = None
                if p == self.shortest_p:
                    self.shortest_p = None
                self.terminated(p)

            elif p.burst == 0:  # when a process completes
                self.display_info = True
                self.info_string += str(p.name) + " Cpu Burst Completed" + "\n"
                p.state = State.Waiting
                p.index += 1
                p.burst = p.burst_nums[p.index]
                p.is_cpu_burst = False
                self.p_running = None
                if p == self.shortest_p:
                    self.shortest_p = None
                self.wait_q.append(p)
                self.waiting(p)

            elif p.counter == 0 and p.q_number != 3:   # preempt process
                self.display_info = True
                self.info_string += str(p.name) + " PREEMPTED" + "\n"
                self.p_running = None
                p.state = State.Ready
                self.rdy_q.append(p)

                # downgrade process when cpu burst not complete and not preempted by higher queue process
                if p.q_number != 3:
                    p.q_number += 1
                    self.info_string += str(p.name) + " Moved to Queue " + str(p.q_number) + "\n"
                if len(self.rdy_q) == 1:  # round robin resets the process counter
                    p.counter = -1
                    self.rdy(p)

            elif p.burst > 0:
                if not p.started:
                    self.display_info = True
                    p.started = True
                    p.started_time = self.time - 1
                    self.info_string += str(p.name) + " Started at " + str(p.started_time) + "\n"
                p.burst -= 1
                p.counter -= 1

    def terminated(self, p):  # directs terminated processes
        self.info_string += str(p.name) + " TERMINATED" + "\n"
        p.terminated_time = self.time - 1
        self.info_string += str(p.name) + " Terminated at " + str(p.terminated_time) + "\n"
        self.terminated_p.append(p)

    def time_clock(self):  # clock
        self.info_string = ""  # directs text display

        if len(self.processes) != len(self.terminated_p):   # directs end times
            self.info_string += "Time: " + str(self.time) + "\n"
            self.time += 1

            for p in self.processes:   # directs processes to functions depending on their states
                self.current_p = p
                if p.state == State.Ready:
                    self.rdy(p)
                elif p.state == State.Waiting:
                    self.waiting(p)
                elif p.state == State.Running:
                    self.running(p)

            self.info_string += "Ready Queue:" + "\n"  # prepares text display info
            for element in self.rdy_q:
                self.info_string += str(element.name) + ": "
                self.info_string += "Queue " + str(element.q_number) + ": Burst = " + str(element.burst) + "\n"

            if self.p_running is not None:   # Reorganizes processes
                temp = [self.p_running]
                for item in self.processes:
                    if item.state == State.Waiting:
                        temp.append(item)
                for items in self.rdy_q:
                    temp.append(items)
                for more_items in self.terminated_p:
                    temp.append(more_items)
                self.processes = temp

            self.info_string += "\n"
            if self.display_info:   # displays info
                print(self.info_string)
                self.display_info = False
        else:
            self.cpu_time_total = self.time - 1

    def first_come_first_serve(self, p):  # scheduling for FCFS
        if self.p_running is None:  # distributes to running from ready
            self.rdy_q.remove(p)
            p.state = State.Running
            self.running(p)


class Process(object):  # process class

    def __init__(self, data_array, name):
        self.name = name
        self.state = State.Ready
        self.burst = data_array[0]
        self.burst_nums = data_array
        self.index = 0
        self.final_index = len(data_array) - 1
        self.started = False
        self.started_time = 0
        self.arrival_time = 0
        self.terminated_time = 0
        self.is_cpu_burst = True
        self.q_number = 1
        self.counter = -1


def main():  # main function

    units_time = 1000
    p1 = Process([5, 27, 3, 31, 5, 43, 4, 18, 6, 22, 4, 26, 3, 24, 5], "P1")
    p2 = Process([4, 48, 5, 44, 7, 42, 12, 37, 9, 76, 4, 41, 9, 31, 7, 43, 8], "P2")
    p3 = Process([8, 33, 12, 41, 18, 65, 14, 21, 4, 61, 15, 18, 14, 26, 5, 31, 6], "P3")
    p4 = Process([3, 35, 4, 41, 5, 45, 3, 51, 4, 61, 5, 54, 6, 82, 5, 77, 3], "P4")
    p5 = Process([16, 24, 17, 21, 5, 36, 16, 26, 7, 31, 13, 28, 11, 21, 6, 3, 13, 11, 4], "P5")
    p6 = Process([11, 22, 4, 8, 5, 10, 6, 12, 7, 14, 9, 18, 12, 24, 15, 30, 8], "P6")
    p7 = Process([14, 46, 17, 41, 11, 42, 15, 21, 4, 32, 7, 19, 16, 33, 10], "P7")
    p8 = Process([4, 14, 5, 33, 6, 51, 14, 73, 16, 87, 6], "P8")
    os = PLC([p1, p2, p3, p4, p5, p6, p7, p8], "FCFS")

    for i in range(0, units_time + 1):  # starts simulator
        os.time_clock()

    print("Total Time: ", os.cpu_time_total)  # result evaluation
    print()

    print("Turn Around Time: ")
    avg_ttr = 0
    for p0 in os.const_p:
        print("{}:".format(p0.name), evaluate_ttr(p0))
        avg_ttr += evaluate_ttr(p0)
    value = avg_ttr / len(os.const_p)
    print("Turn Around Time Average: ", round(value, 2), "ms\n")

    print("Waiting Time: ")
    avg_wt = 0
    for p1 in os.const_p:
        print("{}:".format(p1.name), evaluate_tw(p1))
        avg_wt += evaluate_tw(p1)
    value = avg_wt / len(os.const_p)
    print("Waiting Time Average: ", round(value, 2), "ms\n")

    print("Response Time: ")
    avg_tr = 0
    for p2 in os.const_p:
        print("{}:".format(p2.name), evaluate_tr(p2))
        avg_tr += evaluate_tr(p2)
    value = avg_tr / len(os.const_p)
    print("Response Time Average: ", round(value, 2), "ms\n")

    print("CPU Utilization: ")
    utilization = evaluate_utilization(os)
    print(round(utilization, 2), "%")


if __name__ == "__main__":
    main()
