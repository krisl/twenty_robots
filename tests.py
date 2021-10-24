#!/usr/bin/env python3

import unittest
from task_allocation import Robot
from task_allocation import SubTaskDriving, SubTaskCharging
from task_allocation import SubTaskAttaching, SubTaskDetaching


class TestSubTask(unittest.TestCase):
    def test_driving_done(self):
        robot = Robot(6)
        driving = SubTaskDriving(7)

        self.assertFalse(driving.is_done(robot))

        # drive to the location
        robot.location = 7
        self.assertTrue(driving.is_done(robot))

    def test_charging_done(self):
        robot = Robot(6)
        charging = SubTaskCharging()

        # robots start fully charged
        self.assertTrue(charging.is_done(robot))

        # drain the battery a bit
        robot.kwh_used = 0.001
        self.assertFalse(charging.is_done(robot))

        # recharge the battery
        robot.kwh_used = 0
        self.assertTrue(charging.is_done(robot))

    def test_attaching_done(self):
        robot = Robot(6)
        attaching = SubTaskAttaching()

        # attaching is always done, we dont keep state about it
        self.assertTrue(attaching.is_done(robot))

    def test_detaching_done(self):
        robot = Robot(6)
        detaching = SubTaskDetaching()

        # detaching is always done, we dont keep state about it
        self.assertTrue(detaching.is_done(robot))


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
