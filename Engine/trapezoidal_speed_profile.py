
from Util.geometry import clamp
from Engine.robot import Robot, MAX_LINEAR_ACCELERATION

MIN_DISTANCE_TO_REACH_TARGET_SPEED = 0


def get_next_velocity(robot: Robot, dt):
    """Return the next velocity according to a constant acceleration model of a point mass.
       It try to produce a trapezoidal velocity path with the required cruising and target speed.
       The target speed is the speed that the robot need to reach at the target point."""
    current_speed = robot.velocity.position.norm
    target_speed = robot.path.speeds[1]
    next_speed = current_speed

    offset = 10
    if target_speed > current_speed:
        next_speed += MAX_LINEAR_ACCELERATION * dt * offset
    else:
        if reach_acceleration_dist(robot, target_speed, current_speed):  # We need to accelerate
            next_speed += MAX_LINEAR_ACCELERATION * dt * offset
        elif reach_break_distance(robot, target_speed, current_speed):  # We need to go to break
            next_speed -= MAX_LINEAR_ACCELERATION * dt * offset
        else:  # This is never reach.
            next_speed += MAX_LINEAR_ACCELERATION * dt * offset

    return clamp(next_speed, 0, robot.cruise_speed)


def reach_acceleration_dist(robot: Robot, target_speed, current_speed, offset=2) -> bool:
    acc = MAX_LINEAR_ACCELERATION
    distance = 0.5 * abs(current_speed ** 2 - target_speed ** 2) / acc
    position_error = robot.path.points[1] - robot.pose.position
    return position_error.norm >= distance * offset


def reach_break_distance(robot: Robot, target_speed, current_speed, offset=2) -> bool:
    acc = MAX_LINEAR_ACCELERATION
    distance = 0.5 * abs(current_speed ** 2 - target_speed ** 2) / acc
    position_error = robot.path.points[1] - robot.pose.position
    return position_error.norm <= distance * offset
