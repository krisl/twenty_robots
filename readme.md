Design an algorithm to schedule tasks according to the requirements below.

In each store we have around 20 robots, some of which will be charging batteries and others doing actual work moving trolleys around the store.
Each robot notifies the store server their current battery level, in kilowatt-hour (one kilowatt for one hour).
Our task manager needs to know, for each task, which robot to pick.
Each task is divided in subtasks, and for each subtask the task manager knows both the robot’s power consumption (in Watts) and the maximum amount of time the subtask is supposed to take.

Task A – Recharging
  5. Identifying a robot with low charge.
  6. Selecting one of the available charging stations.
  7. Driving the robot to the chosen charging station.
  8. Recharging (this is the only subtask where the robot charges instead of consuming power)

Task B – Trolley Manipulation
  7. Receiving a request to reposition a trolley.
  8. Selecting one of the available robots.
  9. Driving the robot to the trolley.
  10. Attaching to the trolley.
  11. Driving the trolley to the destination.
  12. Detaching from the trolley.

The system should be able to provide to the task manager the best suitable robot to perform a manipulation task, if any, as well as sending the robots to recharge the battery if necessary.
