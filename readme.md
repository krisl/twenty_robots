# Twenty Robots

* To run tests: `python3 tests.py`
* To run sample allocation: `python3 task_allocation.py`

>In each store we have around 20 robots, some of which will be charging batteries and others doing actual work moving trolleys around the store.
Each robot notifies the store server their current battery level, in kilowatt-hour (one kilowatt for one hour).
Our task manager needs to know, for each task, which robot to pick.
Each task is divided in subtasks, and for each subtask the task manager knows both the robot’s power consumption (in Watts) and the maximum amount of time the subtask is supposed to take.

Task A – Recharging
  1. Identifying a robot with low charge.
  2. Selecting one of the available charging stations.
  3. Driving the robot to the chosen charging station.
  4. Recharging (this is the only subtask where the robot charges instead of consuming power)

Task B – Trolley Manipulation
  1. Receiving a request to reposition a trolley.
  2. Selecting one of the available robots.
  3. Driving the robot to the trolley.
  4. Attaching to the trolley.
  5. Driving the trolley to the destination.
  6. Detaching from the trolley.

The system should be able to provide to the task manager the best suitable robot to perform a manipulation task, if any, as well as sending the robots to recharge the battery if necessary.
