import time
from functools import partial
from typing import List

from Util.ai_command_shit import AICommand
from ai.Algorithm.path_partitionner import PathPartitionner, CollisionBody
from Util.path import Path
from ai.states.game_state import GameState
from config.config_service import ConfigService
from RULEngine.robot import Robot

INTERMEDIATE_DISTANCE_THRESHOLD = 540
AIcommands = List[AICommand]


def create_pathfinder():

    return PathPartitionner()


def pathfind_ai_commands(game_state, ai_commands):
    last_path = None
    last_raw_path = None
    field = game_state.game.field
    for ai_command in ai_commands:
        player = game_state.get_player(ai_command.robot_id)
        if ai_command is None or not player.pathfinder_on:
            return None
        if player.pathfinder_history.last_pose_goal is not None:
            MIN_CHANGE_IN_GOAL = 200
            if (player.pathfinder_history.last_pose_goal - player.ai_command.pose_goal.position).norm() < MIN_CHANGE_IN_GOAL:
                last_path = player.pathfinder_history.last_path
                last_raw_path = player.pathfinder_history.last_raw_path
        pathfinder = create_pathfinder()

        # player.ai_command.pose_goal.position = \
        #     field.respect_field_rules(Position(player.ai_command.pose_goal.position[0],
        #                                        player.ai_command.pose_goal.position[1]))
        optionnal_collision_bodies = field.field_collision_body
        collision_bodies = get_pertinent_collision_objects(player, game_state, optionnal_collision_bodies)
        player_collision_object = CollisionBody(player.pose.position, player.velocity.position, 150, body_pose=player.pose,
                                                max_acc=Robot.max_linear_acceleration/1000, ident_num=player.id)
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

        ai_command.path = path
    return ai_commands


def get_pertinent_collision_objects(commanded_player, game_state, optionnal_collision_bodies=None):
    factor = 1.1
    collision_bodies = []
    gap_proxy = 250
    # FIXME: Find better name that is less confusing between self.player and player
    for player in game_state.my_team.available_players.values():
        if player.id != commanded_player.id:
            if (commanded_player.pose.position - player.pose.position).norm() + \
                    (commanded_player.ai_command.pose_goal.position - player.pose.position).norm() < \
                    (commanded_player.ai_command.pose_goal.position - commanded_player.pose.position).norm() * factor:
                collision_bodies.append(
                    CollisionBody(player.pose.position, player.velocity.position, gap_proxy))
    for player in game_state.other_team.available_players.values():
        if (commanded_player.pose.position - player.pose.position).norm() + \
                (commanded_player.ai_command.pose_goal.position - player.pose.position).norm() < \
                (commanded_player.ai_command.pose_goal.position - commanded_player.pose.position).norm() * factor:
            collision_bodies.append(
                CollisionBody(player.pose.position, player.velocity.position, gap_proxy))

    if optionnal_collision_bodies is None:

        return collision_bodies
    else:
        if commanded_player.ai_command.collision_ball:
            ball_colision_body = [
                CollisionBody(game_state.field.ball.position, game_state.field.ball.velocity, gap_proxy)]
            return collision_bodies + optionnal_collision_bodies + ball_colision_body
        return collision_bodies + optionnal_collision_bodies


class PathfinderModule:

    def __init__(self):
        super().__init__()
        self.type_of_pathfinder = ConfigService().config_dict["STRATEGY"]["pathfinder"]
        self.last_time_pathfinding_for_robot = {}
        self.last_frame = time.time()
        self.game_state = GameState()

    def exec(self):

        callback = partial(pathfind_ai_commands, self.type_of_pathfinder.lower(), self.game_state)
        paths = [callback(player) for player in list(self.ws.game_state.my_team.available_players.values())]

        for path in paths:
            if path is not None:
                self.draw_path(path)

    def draw_path(self, path, pid=0):

        points = []
        for idx, path_element in enumerate(path.points):
            x = path_element.x
            y = path_element.y
            points.append((x, y))

        #    print(points)
        # self.ws.debug_interface.add_multi_line(points)
