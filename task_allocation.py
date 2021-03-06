#!/usr/bin/env python3

from copy import copy
import random


# robot, [tasks] -> (task, (start cost, max power cost))
def min_cost_task(robot, tasks):
    tasks_costs = map(lambda t: (t, t.calc_costs(robot)), tasks)
    # choose task with minimum start cost

    # filter out those that we dont have enough power to perform
    feasible = filter(lambda c: robot.kwh_available() >= c[1][1],
                      tasks_costs)

    return min(feasible, key=lambda tc: tc[1], default=(None, None))


# [robot], [task] -> [(robot, task)]
def match_robots_to_tasks(robots_, tasks):
    # copy arguments, we will mutate them
    robots = robots_.copy()
    results = []

    while (len(robots) > 0 and len(tasks) > 0):
        # calc lowest cost task for each robot
        # [(r, (t, c)),...]
        # [(r, None)...]
        task_costs = map(lambda r: (r, min_cost_task(r, tasks)),
                         robots)

        # choose pair with highest cost of set of lowest costs
        robot, (task, _) = max(task_costs, key=lambda z: z[1][1])

        # a task is returned if its feasible
        if task is not None:
            # add chosen pair to result set
            results.append((robot, task))
            tasks.remove(task)

        robots.remove(robot)

    return results


class SubTaskDriving:
    # all robots use the same power to drive
    kwh_per_tick = 0.2

    def __init__(self, destination):
        self.destination = destination

    def tick(self, robot):
        robot.kwh_used += self.kwh_per_tick
        robot.location += 1 if robot.location < self.destination else -1

    # robot -> (time_cost, power_cost)
    def calc_cost(self, mutable_robot):
        # conveniently, all robots move 1 unit distance / 1 unit time
        time = abs(mutable_robot.location - self.destination)
        power = time * self.kwh_per_tick

        # update robot with resouce usage
        mutable_robot.kwh_used += power
        mutable_robot.location = self.destination

        return (time, power)

    def is_done(self, robot):
        return robot.location == self.destination


class SubTaskCharging:
    # all robots charge 1kwh / 1 unit time
    kwh_per_tick = -1

    def tick(self, robot):
        # lets not overcharge
        if (robot.kwh_used + self.kwh_per_tick < 0):
            robot.kwh_used = 0
        else:
            robot.kwh_used += self.kwh_per_tick

    # robot -> (time_cost, power_cost)
    def calc_cost(self, mutable_robot):
        # conveniently, all robots charge at same rate
        time = max(0, mutable_robot.kwh_used)
        power = time * self.kwh_per_tick

        # update robot with resouce usage
        mutable_robot.kwh_used = 0  # recharged

        return (time, power)

    def is_done(self, robot):
        return robot.kwh_used <= 0


class SubTaskAttaching:
    kwh_per_tick = 0.3

    def tick(self, robot):
        robot.kwh_used += self.kwh_per_tick

    # robot -> (time_cost, power_cost)
    def calc_cost(self, mutable_robot):
        mutable_robot.kwh_used += self.kwh_per_tick
        return (1, self.kwh_per_tick)

    def is_done(self, robot):
        return True


class SubTaskDetaching:
    kwh_per_tick = 0.1

    def tick(self, robot):
        robot.kwh_used += self.kwh_per_tick

    # robot -> (time_cost, power_cost)
    def calc_cost(self, mutable_robot):
        mutable_robot.kwh_used += self.kwh_per_tick
        return (1, self.kwh_per_tick)

    def is_done(self, robot):
        return True


class TaskBase:
    def __init__(self):
        self.subtasks = []
        self.subtask_index = 0

    def tick(self, robot):
        if len(self.subtasks) > self.subtask_index:
            subtask = self.subtasks[self.subtask_index]
            subtask.tick(robot)

            if subtask.is_done(robot):
                self.subtask_index += 1

            return subtask
        return None

    # robot -> (start_time_cost, max_power_cost)
    def calc_costs(self, robot_):
        robot = copy(robot_)  # robot is mutatated during calculation
        costs = [st.calc_cost(robot) for st in self.subtasks]

        # we want the robot specific independant cost (start cost)
        time_to_first_subtask = costs[0][0]

        # and the max power consumption (assume charging is last)
        max_kwh_used = sum([c[1] for c in costs if c[1] > 0])

        return (time_to_first_subtask, max_kwh_used)

    def is_standby(self):
        return False


class TaskCharge(TaskBase):
    def __init__(self, station):
        super().__init__()
        self.subtasks = [
                SubTaskDriving(station),
                SubTaskCharging()]

    def get_station(self):
        return self.subtasks[0].destination

    def __str__(self):
        return "TaskCharge loc: %s" % (
            self.get_station()
        )

    def __repr__(self):
        return self.__str__()


class TaskTrolly(TaskBase):
    def __init__(self, source, destination):
        super().__init__()
        self.subtasks = [
                SubTaskDriving(source),
                SubTaskAttaching(),
                SubTaskDriving(destination),
                SubTaskDetaching()]

    def __str__(self):
        return "TaskTrolly %s from %s to %s" % (
            id(self),
            self.subtasks[0].destination,
            self.subtasks[2].destination
        )

    def __repr__(self):
        return self.__str__()


class TaskStandby(TaskBase):
    def __init__(self):
        super().__init__()

    def is_standby(self):
        return True

    def __str__(self):
        return "TaskStandby"

    def __repr__(self):
        return self.__str__()


class Robot:
    def __init__(self, location):
        self.location = location
        self.kwh_max = 100
        self.kwh_used = 0
        self.current_task = TaskStandby()

    def tick(self):
        subtask = self.current_task.tick(self)

        if subtask is None:
            self.current_task = TaskStandby()

        # prevent overcharging
        if (self.kwh_used < 0):
            self.kwh_used = 0

        # battery protection
        if (self.kwh_used > self.kwh_max):
            self.assign_task(TaskStandby())

        return subtask

    def assign_task(self, task):
        if not self.is_idle():
            print("interrupting current task")

        self.current_task = task

    def kwh_available(self):
        return min(self.kwh_max, max(0, self.kwh_max - self.kwh_used))

    def is_idle(self):
        return self.current_task.is_standby()

    def needs_charge(self):
        return self.kwh_available() < 50.5  # we charge when half flat

    def __str__(self):
        return "Robot %s loc: %s chrg: %skwh %s" % (
            id(self),
            "{: <2}".format(self.location),
            "{:3.2f}".format(self.kwh_available()).rjust(6),
            self.current_task
        )

    def __repr__(self):
        return self.__str__()


class TaskManager:
    def __init__(self, charging_stations):
        self.charging_stations = charging_stations
        self.robots = []
        self.tasks = set()

    def add_robot(self, robot):
        self.robots.append(robot)

    def add_task(self, task):
        self.tasks.add(task)

    def get_idle_robots(self):
        flat_robots, work_robots = [], []
        for robot in self.robots:
            if robot.is_idle():
                if robot.needs_charge():
                    flat_robots.append(robot)
                else:
                    work_robots.append(robot)

        return flat_robots, work_robots

    def get_free_charge_tasks(self):
        return [TaskCharge(station)
                for station, robot in self.charging_stations.items()
                if robot is None]

    def tick(self):
        flat_robots, work_robots = self.get_idle_robots()
        charge_tasks = self.get_free_charge_tasks()

        for robot, task in match_robots_to_tasks(flat_robots, charge_tasks):
            robot.assign_task(task)
            self.charging_stations[task.get_station()] = robot

        for robot, task in match_robots_to_tasks(work_robots, self.tasks):
            robot.assign_task(task)

        # march time forward
        ticks = []
        for robot in self.robots:
            subtask = robot.tick()
            ticks.append((robot, subtask))

            # finished charging, free up the station
            if isinstance(subtask, SubTaskCharging):
                if subtask.is_done(robot):
                    station = robot.current_task.get_station()
                    self.charging_stations[station] = None

        return ticks

    def show_robots(self):
        print("==== Robots ====")
        for robot in self.robots:
            print(robot)


if __name__ == '__main__':

    # five charging stations
    QTY_STATIONS = 5
    charging_stations = {
        k: None for k in random.sample(range(0, 99), QTY_STATIONS)
    }
    print(charging_stations)

    tm = TaskManager(charging_stations)

    # some number of robots robots
    QTY_ROBOTS = 20
    for location in random.sample(range(0, 99), QTY_ROBOTS):
        tm.add_robot(Robot(location))

    # a few hundred tasks
    QTY_TASKS = 900
    for _ in range(QTY_TASKS):
        src, dst = random.sample(range(0, 99), 2)
        tm.add_task(TaskTrolly(src, dst))

    tm.show_robots()

    tick_count = 0
    while True:
        step = tm.tick()
        tick_count += 1
        tm.show_robots()
        if len(tm.tasks) == 0:
            if all(isinstance(robot.current_task, TaskStandby)
                    for (robot, _) in step):
                break

    print("Completed %s tasks with %s robots in %s ticks"
          % (QTY_TASKS, QTY_ROBOTS, tick_count))
