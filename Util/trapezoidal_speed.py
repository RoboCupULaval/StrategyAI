import numpy as np

from RULEngine.robot import Robot
from Util import Position, Pose

MIN_DISTANCE_TO_REACH_TARGET_SPEED = 0



def get_next_velocity(robot: Robot, dt):
    """Return the next velocity according to a constant acceleration model of a point mass.
       It try to produce a trapezoidal velocity path with the required cruising and target speed.
       The target speed is the speed that the robot need to reach at the target point."""
    next_speed = Pose.from_dict(robot.velocity).position.norm()
    target_speed = robot.path.speeds[1]
    # cruise_speed = robot.cruise_speed
    #print(target_speed)
    #print(next_speed)
    target_direction = (robot.path.points[1] - Pose.from_dict(robot.pose).position).normalized()
    offset = 1
    if target_speed > next_speed:
        #print('go')
        next_speed += robot.max_linear_acceleration * dt * offset
    else:
        if dist_accelerate(robot, target_speed, next_speed):  # We need to accelerate
            #print('go')
            next_speed += robot.max_linear_acceleration * dt * offset
        elif dist_break(robot, target_speed, next_speed):  # We need to go to break
            #print('break')
            next_speed -= robot.max_linear_acceleration * dt * offset
        else: #accelerate until dist_break:
            #print('go2')
            next_speed += robot.max_linear_acceleration * dt * offset


    next_speed = np.clip(next_speed, 0, robot.cruise_speed)
    print(next_speed)
    next_velocity = Position(target_direction * next_speed)

    return next_velocity


def dist_accelerate(robot: Robot, target_speed, current_speed) -> bool:  # distance_to_reach_target_speed
    offset = 1
    distance = abs(0.5 * (current_speed ** 2 - target_speed ** 2)) / robot.max_linear_acceleration * offset
    # distance = max(distance, MIN_DISTANCE_TO_REACH_TARGET_SPEED)
    position_error = robot.path.points[1] - Pose.from_dict(robot.pose).position
    return position_error.norm() >= 2 * distance

def dist_break(robot: Robot, target_speed, current_speed) -> bool:  # distance_to_reach_target_speed
    offset = 1
    distance = abs(0.5 * (current_speed ** 2 - target_speed ** 2)) / robot.max_linear_acceleration * offset
    # distance = max(distance, MIN_DISTANCE_TO_REACH_TARGET_SPEED)
    position_error = robot.path.points[1] - Pose.from_dict(robot.pose).position
    return position_error.norm() <= distance


