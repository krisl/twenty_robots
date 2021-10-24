#!/usr/bin/env python3

class SubTaskDriving:
    # all robots use the same power to drive
    power_per_tick = 0.2

    def __init__(self, destination):
        self.destination = destination

    # robot -> (time_cost, power_cost)
    def calc_cost(self, robot):
        # conveniently, all robots move 1 unit distance / 1 unit time
        time = abs(robot.location - self.destination)
        power = time * self.power_per_tick
        return (time, power)

    def is_done(self, robot):
        return robot.location == self.destination


class SubTaskCharging:
    # all robots charge 1kwh / 1 unit time
    power_per_tick = -1

    # robot -> (time_cost, power_cost)
    def calc_cost(self, robot):
        # conveniently, all robots charge at same rate
        time = max(0, robot.kwh_used)
        power = time * self.power_per_tick
        return (time, power)

    def is_done(self, robot):
        return robot.kwh_used <= 0


class SubTaskAttaching:
    power_per_tick = 0.3

    # robot -> (time_cost, power_cost)
    def calc_cost(self, robot):
        return (1, self.power_per_tick)

    def is_done(self, robot):
        return True


class SubTaskDetaching:
    power_per_tick = 0.1

    # robot -> (time_cost, power_cost)
    def calc_cost(self, robot):
        return (1, self.power_per_tick)

    def is_done(self, robot):
        return True


class Robot:
    def __init__(self, location):
        self.location = location
        self.kwh_max = 100
        self.kwh_used = 0

    def kwh_available(self):
        return min(self.kwh_max, max(0, self.kwh_max - self.kwh_used))
