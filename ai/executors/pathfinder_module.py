import time
from functools import partial
from typing import List

from ai.Algorithm.path_partitionner import PathPartitionner, CollisionBody
from Util.path import Path
from ai.states.game_state import GameState
from config.config_service import ConfigService
from RULEngine.robot import Robot, MAX_LINEAR_ACCELERATION

INTERMEDIATE_DISTANCE_THRESHOLD = 540


def create_pathfinder():

    return PathPartitionner()


def generate_path(game_state, ai_command):
    last_path = None
    if ai_command.target is None:
        return None
    player = game_state.get_player(ai_command.robot_id)
    if ai_command is None or not player.pathfinder_on:
        return None
    if player.pathfinder_history.last_pose_goal is not None:
        MIN_CHANGE_IN_GOAL = 200
        if (player.pathfinder_history.last_pose_goal - ai_command.target.position).norm() < MIN_CHANGE_IN_GOAL:
            last_path = player.pathfinder_history.last_path
    pathfinder = create_pathfinder()

    # ai_command.pose_goal.position = \
    #     field.respect_field_rules(Position(ai_command.pose_goal.position[0],
    #                                        ai_command.pose_goal.position[1]))
    #optionnal_collision_bodies = field.field_collision_body
    collision_bodies = get_pertinent_collision_objects(player, game_state, ai_command)
    player_collision_object = CollisionBody(player.pose.position, player.velocity.position, 150, body_pose=player.pose,
                                            max_acc=MAX_LINEAR_ACCELERATION/1000, ident_num=player.id)
    target = CollisionBody(body_position=ai_command.target.position,
                           body_pose=ai_command.target,
                           body_avoid_radius=1)
    path = pathfinder.get_path(player_collision_object,
                               target,
                               ai_command.cruise_speed,
                               last_path,
                               end_speed=ai_command.end_speed,
                               collidable_objects=collision_bodies)
    MIN_CHANGE_FOR_RECALCULATE = 100
    if path.get_path_length() < MIN_CHANGE_FOR_RECALCULATE:
        player.pathfinder_history.last_path = None
        player.pathfinder_history.last_pose_goal = path.goal
    else:
        player.pathfinder_history.last_path = path
        player.pathfinder_history.last_pose_goal = path.goal

    return path


def get_pertinent_collision_objects(commanded_player, game_state, ai_command, optionnal_collision_bodies=None):
    factor = 1.1
    collision_bodies = []
    gap_proxy = 250
    # FIXME: Find better name that is less confusing between self.player and player
    for player in game_state.our_team.available_players.values():
        if player.id != commanded_player.id:
            if (commanded_player.pose.position - player.pose.position).norm() + \
                    (ai_command.target.position - player.pose.position).norm() < \
                    (ai_command.target.position - commanded_player.pose.position).norm() * factor:
                collision_bodies.append(
                    CollisionBody(player.pose.position, player.velocity.position, gap_proxy))
    for player in game_state.enemy_team.available_players.values():
        if (commanded_player.pose.position - player.pose.position).norm() + \
                (ai_command.target.position - player.pose.position).norm() < \
                (ai_command.target.position - commanded_player.pose.position).norm() * factor:
            collision_bodies.append(
                CollisionBody(player.pose.position, player.velocity.position, gap_proxy))
    if commanded_player.ball_collision:
        ball_colision_body = [
            CollisionBody(game_state.get_ball_position(), game_state.get_ball_velocity(), gap_proxy)]
        return collision_bodies + ball_colision_body
    return collision_bodies


