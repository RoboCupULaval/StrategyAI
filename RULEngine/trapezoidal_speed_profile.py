
from Util.geometry import clamp
from RULEngine.robot import Robot, MAX_LINEAR_ACCELERATION


def get_next_velocity(robot: Robot, dt, offset=10):
    """Return the next velocity according to a constant acceleration model of a point mass.
       It try to produce a trapezoidal velocity path with the required cruising and target speed.
       The target speed is the speed that the robot need to reach at the target point."""

    acc = MAX_LINEAR_ACCELERATION

    if robot.target_speed > robot.current_speed:
        next_speed = robot.current_speed + acc * dt * offset
    else:
        if not reach_acceleration_dist(robot, acc):
            next_speed = robot.current_speed + acc * dt * offset
        else:
            next_speed = robot.current_speed - acc * dt * offset

    return clamp(next_speed, 0, robot.cruise_speed)


def reach_acceleration_dist(robot: Robot, acc, offset=2) -> bool:
    distance = 0.5 * abs(robot.current_speed ** 2 - robot.target_speed ** 2) / acc
    return robot.position_error.norm < distance * offset
