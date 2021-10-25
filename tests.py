#!/usr/bin/env python3

import unittest
from task_allocation import Robot, TaskManager
from task_allocation import TaskTrolly, TaskCharge, TaskStandby
from task_allocation import SubTaskDriving, SubTaskCharging
from task_allocation import SubTaskAttaching, SubTaskDetaching


class TestSubTaskCostCalculation(unittest.TestCase):
    def test_driving_cost(self):
        robot = Robot(6)

        driving = SubTaskDriving(7)
        self.assertEqual(driving.calc_cost(robot), (1, 0.2))

        driving = SubTaskDriving(5)
        self.assertEqual(driving.calc_cost(robot), (1, 0.2))

        driving = SubTaskDriving(4)
        self.assertEqual(driving.calc_cost(robot), (2, 0.4))

        driving = SubTaskDriving(8)
        self.assertEqual(driving.calc_cost(robot), (2, 0.4))

    def test_charging_cost(self):
        robot = Robot(6)
        charging = SubTaskCharging()

        # robots start fully charged
        self.assertEqual(charging.calc_cost(robot), (0, 0))

        # drain the battery a little
        robot.kwh_used = 1
        self.assertEqual(charging.calc_cost(robot), (1, -1))

        # drain the battery a lot
        robot.kwh_used = 100
        self.assertEqual(charging.calc_cost(robot), (100, -100))

    def test_attaching_detaching_cost(self):
        robot = Robot(6)
        attaching = SubTaskAttaching()
        detaching = SubTaskDetaching()

        self.assertEqual(attaching.calc_cost(robot), (1, 0.3))
        self.assertEqual(detaching.calc_cost(robot), (1, 0.1))


class TestSubTaskDone(unittest.TestCase):
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


class TestTaskStandby(unittest.TestCase):
    def test_task_standby(self):
        task = TaskStandby()
        self.assertTrue(task.is_standby())


class TestTaskCharge(unittest.TestCase):
    def test_task_charge(self):
        task = TaskCharge(7)
        self.assertFalse(task.is_standby())
        self.assertIsInstance(task.subtasks[0], SubTaskDriving)
        self.assertIsInstance(task.subtasks[1], SubTaskCharging)

        self.assertEqual(task.subtasks[0].destination, 7)


class TestTaskTrolly(unittest.TestCase):
    def test_task_charge(self):
        task = TaskTrolly(7, 9)
        self.assertFalse(task.is_standby())
        self.assertIsInstance(task.subtasks[0], SubTaskDriving)
        self.assertIsInstance(task.subtasks[1], SubTaskAttaching)
        self.assertIsInstance(task.subtasks[2], SubTaskDriving)
        self.assertIsInstance(task.subtasks[3], SubTaskDetaching)

        self.assertEqual(task.subtasks[0].destination, 7)
        self.assertEqual(task.subtasks[2].destination, 9)


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

    def test_is_idle(self):
        robot = Robot(6)
        # new robots are idle
        self.assertTrue(robot.is_idle())


class TestTaskManager(unittest.TestCase):
    def test_basic_functions(self):
        task_manager = TaskManager({5: None})
        self.assertEqual(task_manager.charging_stations, {5: None})
        self.assertEqual(task_manager.robots, [])
        self.assertEqual(task_manager.tasks, set())

        robotAt6 = Robot(6)
        task_manager.add_robot(robotAt6)
        self.assertEqual(task_manager.robots, [robotAt6])

        robotAt16 = Robot(16)
        task_manager.add_robot(robotAt16)
        self.assertEqual(task_manager.robots, [robotAt6, robotAt16])

        task_chargeAt7 = TaskCharge(7)
        task_manager.add_task(task_chargeAt7)
        self.assertEqual(task_manager.tasks, set([task_chargeAt7]))

        task_chargeAt17 = TaskCharge(17)
        task_manager.add_task(task_chargeAt17)
        self.assertEqual(task_manager.tasks, set([task_chargeAt7,
                                                  task_chargeAt17]))

    def test_get_idle_robots(self):
        task_manager = TaskManager({5: None})

        robotAt6 = Robot(6)
        robotAt6.kwh_used = 55  # drain the battry of this robot
        task_manager.add_robot(robotAt6)

        robotAt16 = Robot(16)
        task_manager.add_robot(robotAt16)

        flat_robots, work_robots = task_manager.get_idle_robots()
        self.assertEqual(flat_robots, [robotAt6])
        self.assertEqual(work_robots, [robotAt16])

    def test_get_free_charging_tasks(self):
        task_manager = TaskManager({5: None, 6: 'some robot', 7: None})

        charge_tasks = task_manager.get_free_charge_tasks()
        self.assertEqual(len(charge_tasks), 2)

        taskA, taskB = charge_tasks
        self.assertIsInstance(taskA, TaskCharge)
        self.assertIsInstance(taskB, TaskCharge)

        # order of tasks unimportant
        self.assertEqual(set([taskA.subtasks[0].destination,
                              taskB.subtasks[0].destination]),
                         set([5, 7]))


if __name__ == '__main__':
    unittest.main()
