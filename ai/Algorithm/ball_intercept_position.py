from Util import Position
from Util.geometry import compare_angle
from ai.GameDomainObjects import Player, Ball
import numpy as np


def BallInterceptPosition(player: Player, ball: Ball, target):
    # Calcule ittérativement la position d'interception de la ball en fonction de sa vitesse et de la vitesse maximale du robot
    max_robot_speed = 1.5
    ball_decelration = -50        # m/s³
    ball_spacing = 100
    projected_ball_position = ball.position
    projected_ball_velocity = ball.velocity
    position_behind_ball = get_destination_behind_ball(player, target, ball.position, ball_spacing * 3)
    time_to_reach = 0
    player_pos_time_2_reach = player.pose.position + time_to_reach * max_robot_speed * position_behind_ball / position_behind_ball.norm
    dt = 0.02
    while (player_pos_time_2_reach - position_behind_ball).norm > 50:
        time_to_reach += dt
        projected_ball_position += projected_ball_velocity * dt + \
                                   ball_decelration * projected_ball_velocity / projected_ball_velocity.norm * dt ** 2
        projected_ball_velocity += ball_decelration * projected_ball_velocity / projected_ball_velocity.norm * dt
        position_behind_ball = get_destination_behind_ball(player, target, projected_ball_position, ball_spacing * 3)
        player_pos_time_2_reach = player.pose.position + \
                                  time_to_reach * max_robot_speed * (position_behind_ball - player.pose.position) / \
                                  (position_behind_ball - player.pose.position).norm
        if time_to_reach > 2:
            player_pos_time_2_reach = get_destination_behind_ball(player, target, ball.position, ball_spacing * 3)
            break
    return player_pos_time_2_reach





def get_destination_behind_ball(player, target, ball_position, ball_spacing):
    """
        Calcule le point situé à  x pixels derrière la position 1 par rapport à la position 2
        :return: Un tuple (Pose, kick) où Pose est la destination du joueur et kick est nul (on ne botte pas)
        """

    delta_x = target.position.x - ball_position.x
    delta_y = target.position.y - ball_position.y
    theta = np.math.atan2(delta_y, delta_x)

    x = ball_position.x - ball_spacing * np.math.cos(theta)
    y = ball_position.y - ball_spacing * np.math.sin(theta)

    player_x = player.pose.position.x
    player_y = player.pose.position.y

    if np.sqrt((player_x - x) ** 2 + (player_y - y) ** 2) < 50:
        x -= np.math.cos(theta) * 2
        y -= np.math.sin(theta) * 2
    destination_position = Position(x, y)

    return destination_position