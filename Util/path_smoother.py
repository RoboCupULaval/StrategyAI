import numpy as np
import path
import






def path_smoother(path, player: Player, vel_cruise: [int, float]=1000):
    path = path
    player = player
    cmd = player.ai_command
    if cmd.cruise_speed:
        vel_cruise = cmd.cruise_speed * 1000
    positions_list = [path.points[0]]
    for idx, point in enumerate(path.points[1:-1]):
        i = idx + 1
        if (path.points[i] - path.points[i+1]).norm() < 10:
            continue
        positions_list += [path.points[i]]
    positions_list += [path.points[-1]]
    path.points = positions_list
    p1 = path.points[0]
    point_list = [p1]
    speed_list = [path.speeds[0]]

    for idx, point in enumerate(path.points[1:-1]):
        dist_from_path = 50  # mm
        i = idx + 1
        p2 = point
        p3 = path.points[i+1]
        radius_at_const_speed = vel_cruise ** 2 / (Player.max_acc * 1000)
        theta = abs(np.math.atan2(p3[1]-p2[1], p3[0]-p2[0]) - np.math.atan2(p1[1]-p2[1], p1[0]-p2[0]))
        try:
            dist_deviation = (radius_at_const_speed/(np.math.sin(theta/2)))-radius_at_const_speed
        except ZeroDivisionError:
            dist_deviation = 0
        speed = vel_cruise
        radius = radius_at_const_speed
        while dist_deviation > dist_from_path:
            speed *= 0.4
            radius = speed ** 2 / (Player.max_acc * 1000)
            dist_deviation = (radius / (np.math.sin(theta / 2))) - radius
        if (p1-p2).norm() < 0.001 or (p2-p3).norm() < 0.001 or (p1-p3).norm() < 0.001:
            # on traite tout le cas ou le problème dégènere
            point_list += [p2]
            speed_list += [vel_cruise]
        else:
            p4 = p2 + np.sqrt(np.square(dist_deviation + radius) - radius ** 2) *\
                      (p1 - p2) / (p1 - p2).norm()
            p5 = p2 + np.sqrt(np.square(dist_deviation + radius) - radius ** 2) *\
                (p3 - p2) / (p3 - p2).norm()
            if (p4-p5).norm() > (p3-p1).norm():
                point_list += [p2]
                speed_list += [vel_cruise]
            elif (p1 - p2).norm() < (p4 - p2).norm():
                radius *= (p1 - p2).norm() / (p4 - p2).norm()
                dist_deviation = (radius / (np.math.sin(theta / 2))) - radius
                p4 = p2 + np.sqrt(np.square(dist_deviation + radius) - radius ** 2) * (p1 - p2) / (p1 - p2).norm()
                p5 = p2 + np.sqrt(np.square(dist_deviation + radius) - radius ** 2) * (p3 - p2) / (p3 - p2).norm()
                point_list += [p4, p5]
                speed_list += [speed, speed]
            elif (p3 - p2).norm() < (p5 - p2).norm():
                radius *= (p3 - p2).norm() / (p5 - p2).norm()
                dist_deviation = (radius / (np.math.sin(theta / 2))) - radius
                p4 = p2 + np.sqrt(np.square(dist_deviation + radius) - radius ** 2) * (p1 - p2) / (p1 - p2).norm()
                p5 = p2 + np.sqrt(np.square(dist_deviation + radius) - radius ** 2) * (p3 - p2) / (p3 - p2).norm()
                point_list += [p4, p5]
                speed_list += [speed, speed]
            else:
                point_list += [p4, p5]
                speed_list += [speed, speed]
        p1 = point_list[-1]

    speed_list += [path.speeds[-1]]
    point_list += [path.goal]
    # on s'assure que le path est bel et bien réalisable par un robot et on
    # merge les points qui sont trop proches les un des autres.
    position_list = [point_list[0]]
    new_speed_list = [speed_list[0]]
    for idx, point in enumerate(point_list[1:-1]):
        i = idx + 1
        if (point_list[i] - point_list[i+1]).norm() < 10:
            continue
        if False:
            min_dist = abs(0.5 * (np.square(speed_list[i]) - np.square(speed_list[i + 1])) / (Player.max_acc * 1000))
            if min_dist > (point_list[i] - point_list[i+1]).norm():
                if speed_list[i] > speed_list[i + 1]:
                    speed_list[i] *= (point_list[i] - point_list[i+1]).norm() / min_dist

        position_list += [point_list[i]]
        new_speed_list += [speed_list[i]]
    position_list += [point_list[-1]]
    new_speed_list += [speed_list[-1]]
    return Path().generate_path_from_points(position_list, new_speed_list)