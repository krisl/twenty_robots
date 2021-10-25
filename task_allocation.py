#!/usr/bin/env python3

from copy import copy


# robot, [tasks] -> (task, (start cost, max power cost))
def min_cost_task(robot, tasks):
    tasks_costs = map(lambda t: (t, t.calc_costs(robot)), tasks)
    # choose task with minimum start cost

    # filter out those that we dont have enough power to perform
    feasible = filter(lambda c: robot.kwh_available() >= c[1][1],
                      tasks_costs)

    return min(feasible, key=lambda tc: tc[1], default=(None, None))


class SubTaskDriving:
    # all robots use the same power to drive
    power_per_tick = 0.2

    def __init__(self, destination):
        self.destination = destination

    # robot -> (time_cost, power_cost)
    def calc_cost(self, mutable_robot):
        # conveniently, all robots move 1 unit distance / 1 unit time
        time = abs(mutable_robot.location - self.destination)
        power = time * self.power_per_tick

        # update robot with resouce usage
        mutable_robot.kwh_used += power
        mutable_robot.location = self.destination

        return (time, power)

    def is_done(self, robot):
        return robot.location == self.destination


class SubTaskCharging:
    # all robots charge 1kwh / 1 unit time
    power_per_tick = -1

    # robot -> (time_cost, power_cost)
    def calc_cost(self, mutable_robot):
        # conveniently, all robots charge at same rate
        time = max(0, mutable_robot.kwh_used)
        power = time * self.power_per_tick

        # update robot with resouce usage
        mutable_robot.kwh_used = 0  # recharged

        return (time, power)

    def is_done(self, robot):
        return robot.kwh_used <= 0


class SubTaskAttaching:
    power_per_tick = 0.3

    # robot -> (time_cost, power_cost)
    def calc_cost(self, mutable_robot):
        mutable_robot.kwh_used += self.power_per_tick
        return (1, self.power_per_tick)

    def is_done(self, robot):
        return True


class SubTaskDetaching:
    power_per_tick = 0.1

    # robot -> (time_cost, power_cost)
    def calc_cost(self, mutable_robot):
        mutable_robot.kwh_used += self.power_per_tick
        return (1, self.power_per_tick)

    def is_done(self, robot):
        return True


class TaskBase:
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
        self.subtasks = [
                SubTaskDriving(station),
                SubTaskCharging()]


class TaskTrolly(TaskBase):
    def __init__(self, source, destination):
        self.subtasks = [
                SubTaskDriving(source),
                SubTaskAttaching(),
                SubTaskDriving(destination),
                SubTaskDetaching()]


class TaskStandby(TaskBase):
    def is_standby(self):
        return True


class Robot:
    def __init__(self, location):
        self.location = location
        self.kwh_max = 100
        self.kwh_used = 0
        self.current_task = TaskStandby()

    def kwh_available(self):
        return min(self.kwh_max, max(0, self.kwh_max - self.kwh_used))

    def is_idle(self):
        return self.current_task.is_standby()

    def needs_charge(self):
        return self.kwh_available() < 50.5  # we charge when half flat


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
