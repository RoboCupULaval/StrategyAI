# Under MIT licence, see LICENCE.txt
from typing import List
import numpy as np
import time

from RULEngine.Game.Team import Team
from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.constant import BALL_RADIUS, ROBOT_RADIUS, TeamColor
from ai.Algorithm.evaluation_module import closest_players_to_point
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.go_to_position_pathfinder import GoToPositionPathfinder
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState
from ai.STA.Action.Idle import Idle

__author__ = 'RoboCupULaval'

ORIENTATION_DEADZONE = 0.2
DISTANCE_TO_KICK_REAL = ROBOT_RADIUS * 3.4
DISTANCE_TO_KICK_SIM = ROBOT_RADIUS + BALL_RADIUS
COMMAND_DELAY = 1.0


class AlignToLineUp(Tactic):
    def __init__(self, game_state: GameState, player: OurPlayer, robots_in_formation: List[OurPlayer], auto_pick=False,
                 args: List[str]=None):
        assert isinstance(robots_in_formation[0], OurPlayer)
        super().__init__(game_state, player, args=args)
        #self.current_state = self.define_center_of_formation
        self.next_state = self.get_players_in_formation
        self.game_state = game_state
        self.last_time = time.time()
        self.robots_in_formation = robots_in_formation
        self.robots = robots_in_formation

        self.temp_robots = robots_in_formation
        self.temp_position_in_formation = (0, 0)
        self.position_offset = (0, 0)

        self.auto_pick = auto_pick
        self.player = player
        #self.field_goal_radius = self.game_state.const["FIELD_GOAL_RADIUS"]
        #self.field_goal_segment = self.game_state.const["FIELD_GOAL_SEGMENT"]
        #self.keep_out_distance = self.field_goal_radius + np.divide(self.field_goal_segment, 2.)
        #self.goal_width = self.game_state.const["FIELD_GOAL_WIDTH"]
        #self.goal_middle = Position(self.game_state.field.constant["FIELD_OUR_GOAL_X_EXTERNAL"], 0)
        #self.position_middle_formation = Position(0, 0)
        self.target_position = (0, 0)
        self.positions_in_formations = []
        self.vec_ball_2_goal = Position(1, 0)
        self.vec_perp_of_ball_2_goal = Position(0, 1)
        self.player_number_in_formation = None
        self.number_of_robots = 0
        self.get_players_in_formation()

    def oldget_players_in_formation(self):
        self.player_number_in_formation = None
        self.robots_in_formation = self.robots
        for idx, player in enumerate(self.robots):
            if not player.check_if_on_field():
                del self.robots_in_formation[idx]
        for idx, player in enumerate(self.robots_in_formation):
            if self.player == player:
                self.player_number_in_formation = idx
                break
        if len(self.game_state.my_team.available_players) == 0:
            self.next_state = self.halt
            self.number_of_robots = 0
        else:
            self.number_of_robots = len(self.game_state.my_team.available_players)
        if self.player_number_in_formation is None:
            self.player_number_in_formation = 0
            self.next_state = self.halt
        else:
            self.next_state = self.define_center_of_formation

    def get_players_in_formation(self):
        self.player_number_in_formation = None
        self.robots = closest_players_to_point(self.target_position, True, self.robots)
        self.temp_robots = self.robots
        #self.robots_in_formation = self.robots
        for idx, player in enumerate(self.robots):
            if not player.check_if_on_field():
                del self.temp_robots[idx]
        for idx, player in enumerate(self.temp_robots):
            if self.player == player:
                self.player_number_in_formation = idx
                break
        if len(self.game_state.my_team.available_players) == 0:
            self.next_state = self.halt
            self.number_of_robots = 0
        else:
            self.number_of_robots = len(self.game_state.my_team.available_players)
        if self.player_number_in_formation is None:
            self.player_number_in_formation = 0
            self.next_state = self.halt









    def compute_positions_in_formation(self):
        self.positions_in_formations = []


        if self.number_of_robots == 1:
            self.positions_in_formations = [self.position_middle_formation]
        elif self.number_of_robots == 2:
            position_0 = self.position_middle_formation + self.vec_perp_of_ball_2_goal * ROBOT_RADIUS * 1.1
            position_1 = self.position_middle_formation - self.vec_perp_of_ball_2_goal * ROBOT_RADIUS * 1.1

            self.positions_in_formations = [position_0, position_1]

        elif self.number_of_robots == 3:
            position_0 = self.position_middle_formation + self.vec_perp_of_ball_2_goal * 2. * ROBOT_RADIUS * 1.1 + \
                         self.vec_ball_2_goal.normalized() * ROBOT_RADIUS * 0.9
            position_1 = self.position_middle_formation - self.vec_ball_2_goal.normalized() * ROBOT_RADIUS * 1.1
            position_2 = self.position_middle_formation - self.vec_perp_of_ball_2_goal * 2. * ROBOT_RADIUS * 1.1 + \
                         self.vec_ball_2_goal.normalized() * ROBOT_RADIUS * 0.9

            self.positions_in_formations = [position_0, position_1, position_2]

        elif self.number_of_robots == 4:
            local_middle_of_formation = self.position_middle_formation + self.vec_perp_of_ball_2_goal * ROBOT_RADIUS /2.
            position_0 = local_middle_of_formation + self.vec_perp_of_ball_2_goal * 3. * ROBOT_RADIUS * 1.1
            position_1 = local_middle_of_formation + self.vec_perp_of_ball_2_goal * ROBOT_RADIUS * 1.1
            position_2 = local_middle_of_formation - self.vec_perp_of_ball_2_goal * ROBOT_RADIUS * 1.1
            position_3 = local_middle_of_formation - self.vec_perp_of_ball_2_goal * 3. * ROBOT_RADIUS * 1.1

            self.positions_in_formations = [position_0, position_1, position_2, position_3]

        elif self.number_of_robots == 5:
            position_0 = self.position_middle_formation + self.vec_perp_of_ball_2_goal * 3. * ROBOT_RADIUS * 1.1 + \
                         self.vec_ball_2_goal.normalized() * 3. * ROBOT_RADIUS * 0.9
            position_1 = self.position_middle_formation + self.vec_perp_of_ball_2_goal * ROBOT_RADIUS * 1.1 + \
                         self.vec_ball_2_goal.normalized() * ROBOT_RADIUS * 0.9
            position_2 = self.position_middle_formation - self.vec_ball_2_goal.normalized() * ROBOT_RADIUS * 1.1
            position_3 = self.position_middle_formation - self.vec_perp_of_ball_2_goal * ROBOT_RADIUS * 1.1 + \
                         self.vec_ball_2_goal.normalized() * ROBOT_RADIUS * 0.9
            position_4 = self.position_middle_formation - self.vec_perp_of_ball_2_goal * 3 * ROBOT_RADIUS * 1.1 + \
                         self.vec_ball_2_goal.normalized() * 3. * ROBOT_RADIUS * 0.9

            self.positions_in_formations = [position_0, position_1, position_2, position_3, position_4]
        # print(self.positions_in_formations)

    def exec(self):
        self.compute_positions_in_formation()
        for idx, player in enumerate(self.robots_in_formation):
            if not self.is_not_one_of_the_closests(player):
                self.get_players_in_formation()
                self.define_center_of_formation()
                self.compute_positions_in_formation()
                break
        # print(self.robots_in_formation)
        # print(self.player_number_in_formation)
        if self.check_success():
            return self.halt
        else:
            destination_orientation = (self.ball_position -
                                       self.positions_in_formations[self.player_number_in_formation]).angle()
            return GoToPositionPathfinder(self.game_state, self.player,
                                          Pose(self.positions_in_formations[self.player_number_in_formation],
                                               destination_orientation)).exec()

    def test(self):
        self.get_players_in_formation()  # avant iter?
        # self.compute_positions_in_formation()
        for idx, player in enumerate(self.robots_in_formation):
            continue
        # print(self.robots_in_formation)
        # print(self.player_number_in_formation)
        if self.check_success():
            return self.halt
        else:
            destination_orientation = 0
            self.position_offset = (self.player_number_in_formation * ROBOT_RADIUS * 1.1, 0)
            self.positions_in_formations = self.target_position + self.position_offset
            return GoToPositionPathfinder(self.game_state, self.player,
                                          Pose(self.positions_in_formations, destination_orientation)).exec()

    def halt(self):
        self.status_flag = Flags.SUCCESS
        return Idle(self.game_state, self.player)

    def check_success(self):
        player_position = self.player.pose.position
        distance = (player_position - self.target.position).norm()
        if distance < self.game_state.const["POSITION_DEADZONE"]:
            return True
        return False

    # @staticmethod
    # def is_closest(player):
    #     if player == closest_players_to_point(GameState().get_ball_position(), True)[0].player:
    #         return True
    #     return False
    #
    # @staticmethod
    # def is_second_closest(player):
    #     if player == closest_players_to_point(GameState().get_ball_position(), True)[1].player:
    #         return True
    #     return False
    #
    # def is_not_closest(self, player):
    #     return not(self.is_closest(player))
    #
    # def is_not_one_of_the_closests(self, player):
    #     return not(self.is_closest(player) or self.is_second_closest(player))