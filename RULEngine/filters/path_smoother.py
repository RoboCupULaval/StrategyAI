
from Util import Position
from Util.path import Path
from RULEngine.robot import Robot, MAX_LINEAR_ACCELERATION
from math import sqrt, sin


def path_smoother(robot: Robot, path):
    path = path.copy()
    path = remove_close_points(path, threshold=10)

    point_list = [path.start]
    speed_list = [path.speeds[0]]

    for p1, p2, p3 in zip(path.points[:], path.points[1:], path.points[2:]):
        p4, p5, turn_radius = compute_circle_points(p1, p2, p3, robot.cruise_speed)
        point_list += [p4, p5]
        speed_list += [speed_in_corner(turn_radius), speed_in_corner(turn_radius)]

    speed_list += [path.speeds[-1]]
    point_list += [path.goal]

    point_list, speed_list = filter_points_and_speed(point_list, speed_list, threshold=100)

    return Path().generate_path_from_points(point_list, speed_list, threshold=None)


def filter_points_and_speed(point_list, speed_list, threshold):
    position_list = []
    new_speed_list = []
    
    for i, point in enumerate(point_list[0:-1]):
        if (point_list[i] - point_list[i + 1]).norm < threshold:
            continue
        else:
            position_list += [point_list[i]]
            new_speed_list += [speed_list[i]]

    position_list += [point_list[-1]]
    new_speed_list += [speed_list[-1]]

    return position_list, new_speed_list


def remove_close_points(path, threshold=10):
    points_in_between = path.points[1:-1]
    points_in_between_kept = []
    for point, next_point in zip(points_in_between, points_in_between[1:]):
        if (point - next_point).norm >= threshold:
            points_in_between_kept.append(point)
    path.points = [path.start] + points_in_between_kept + [path.goal]
    return path


def compute_circle_points(p1, p2, p3, speed, acc=MAX_LINEAR_ACCELERATION):
    turn_radius, deviation_from_path = compute_turn_radius(p1, p2, p3, speed, acc)

    distance_on_segment = sqrt((deviation_from_path + turn_radius) ** 2 - turn_radius ** 2)
    p4 = point_on_segment(p2, p1, distance_on_segment)
    p5 = point_on_segment(p2, p3, distance_on_segment)

    return p4, p5, turn_radius


def speed_in_corner(radius, acc=MAX_LINEAR_ACCELERATION):

    speed = sqrt(radius * acc)

    return speed


def compute_turn_radius(p1, p2, p3, speed, max_deviation=50, acc=MAX_LINEAR_ACCELERATION):
    """Assume the raw path is p1->p2->p3.
       Deviation is compute from p2 to the circle with a line passing by the center of the circle."""

    radius_at_const_speed = speed ** 2 / acc
    path_angle = (p3 - p2).angle - (p1 - p2).angle

    const_speed_deviation = deviation(radius_at_const_speed, path_angle)

    if const_speed_deviation < max_deviation:
        deviation_from_path = const_speed_deviation
        turn_radius = radius_at_const_speed
    else:
        deviation_from_path = max_deviation
        turn_radius = deviation_from_path / (1 / sin(path_angle / 2) - 1)

    return turn_radius, deviation_from_path


def deviation(radius: float, theta: float):
    return radius / sin(theta / 2) - radius if sin(theta/2) != 0 else 0


def point_on_segment(start: Position, end: Position, distance: float):
    ratio = distance / (start-end).norm
    return (1-ratio) * start + ratio * end
