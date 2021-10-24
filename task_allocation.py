#!/usr/bin/env python3

class SubTaskDriving:
    def __init__(self, destination):
        self.destination = destination

    def is_done(self, robot):
        return robot.location == self.destination


class SubTaskCharging:
    def is_done(self, robot):
        return robot.kwh_used <= 0


class SubTaskAttaching:
    def is_done(self, robot):
        return True


class SubTaskDetaching:
    def is_done(self, robot):
        return True


class Robot:
    def __init__(self, location):
        self.location = location
        self.kwh_max = 100
        self.kwh_used = 0

    def kwh_available(self):
        return min(self.kwh_max, max(0, self.kwh_max - self.kwh_used))
