#!/usr/bin/env python3

import unittest
from task_allocation import Robot


class TestRobot(unittest.TestCase):
    def test_kwh_available(self):
        robot = Robot(6)

        # start fully charged
        self.assertEqual(robot.kwh_available(), 100)

        # if we use ~half, half remaining
        robot.kwh_used = 51
        self.assertEqual(robot.kwh_available(), 49)

        # if we use more, less remaining
        robot.kwh_used = 75.75
        self.assertEqual(robot.kwh_available(), 24.25)

        # we cant use more than capacity
        robot.kwh_used = 120  # > 100 capacity
        self.assertEqual(robot.kwh_available(), 0)

        # we cant use negative amounts
        robot.kwh_used = -10
        self.assertEqual(robot.kwh_available(), 100)


if __name__ == '__main__':
    unittest.main()
