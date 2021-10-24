#!/usr/bin/env python3

class Robot:
    def __init__(self, location):
        self.location = location
        self.kwh_max = 100
        self.kwh_used = 0

    def kwh_available(self):
        return min(self.kwh_max, max(0, self.kwh_max - self.kwh_used))
