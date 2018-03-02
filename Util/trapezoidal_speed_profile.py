import numpy as np

from RULEngine.robot import Robot, MAX_LINEAR_ACCELERATION, MAX_LINEAR_SPEED
from Util import Position, Pose

MIN_DISTANCE_TO_REACH_TARGET_SPEED = 0


def get_next_velocity(robot: Robot, dt):
    """Return the next velocity according to a constant acceleration model of a point mass.
       It try to produce a trapezoidal velocity path with the required cruising and target speed.
       The target speed is the speed that the robot need to reach at the target point."""
    next_speed = robot.velocity.position.norm
    target_speed = robot.path.speeds[1]
    # cruise_speed = robot.cruise_speed
    #print(target_speed)
    #print(next_speed)
    target_direction = robot.path.points[1] - (robot.pose.position / robot.pose.position.norm)
    offset = 10
    if target_speed > next_speed:
        #print('go')
        next_speed += MAX_LINEAR_ACCELERATION * dt * offset
    else:
        if dist_accelerate(robot, target_speed, next_speed):  # We need to accelerate
            #print('go')
            next_speed += MAX_LINEAR_ACCELERATION * dt * offset
        elif dist_break(robot, target_speed, next_speed):  # We need to go to break
            #print('break')
            next_speed -= MAX_LINEAR_ACCELERATION * dt * offset
        else: #accelerate until dist_break:
            #print('go2')
            next_speed += MAX_LINEAR_ACCELERATION * dt * offset

    next_speed = np.clip(next_speed, 0, robot.cruise_speed)
    return next_speed


def dist_accelerate(robot: Robot, target_speed, current_speed) -> bool:  # distance_to_reach_target_speed
    offset = 1
    distance = abs(0.5 * (current_speed ** 2 - target_speed ** 2)) / MAX_LINEAR_ACCELERATION * offset
    # distance = max(distance, MIN_DISTANCE_TO_REACH_TARGET_SPEED)
    position_error = robot.path.points[1] - robot.pose.position
    return position_error.norm >= 2 * distance

def dist_break(robot: Robot, target_speed, current_speed) -> bool:  # distance_to_reach_target_speed
    offset = 2
    distance = abs(0.5 * (current_speed ** 2 - target_speed ** 2)) / MAX_LINEAR_ACCELERATION * offset
    # distance = max(distance, MIN_DISTANCE_TO_REACH_TARGET_SPEED)
    position_error = robot.path.points[1] - robot.pose.position
    return position_error.norm <= distance
