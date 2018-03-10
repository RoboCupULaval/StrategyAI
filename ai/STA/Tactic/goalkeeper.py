# Under MIT licence, see LICENCE.txt

__author__ = 'RoboCupULaval'

import time
from math import tan, pi
from typing import List

from Util import Pose, Position, AICommand
from Util.constant import ROBOT_RADIUS
from Util.constant import TeamColor
from Util.geometry import clamp, compare_angle, wrap_to_pi
from ai.Algorithm.evaluation_module import closest_player_to_point, best_passing_option, player_with_ball
from ai.GameDomainObjects.Shitty_Field import FieldSide
from ai.GameDomainObjects import Player
from ai.STA.Action.GoBehind import GoBehind
from ai.STA.Action.Kick import Kick
from ai.STA.Action.MoveToPosition import MoveToPosition
from ai.STA.Action.ProtectGoal import ProtectGoal
from ai.STA.Action.grab import Grab
from ai.STA.Tactic.go_kick import GRAB_BALL_SPACING, KICK_DISTANCE, VALIDATE_KICK_DELAY, KICK_SUCCEED_THRESHOLD
from ai.STA.Tactic.go_to_position_pathfinder import GoToPositionPathfinder
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState

TARGET_ASSIGNATION_DELAY = 1


class GoalKeeper(Tactic):
    """
    Tactique du gardien de but standard. Le gardien doit se placer entre la balle et le but, tout en restant à
    l'intérieur de son demi-cercle. Si la balle entre dans son demi-cercle, le gardien tente d'aller en prendre
    possession.
    """

    def __init__(self, game_state: GameState, player: Player, target: Pose=Pose(),
                 penalty_kick=False, args: List[str]=None,):
        super().__init__(game_state, player, target, args)

        if len(self.args) > 0:
            print("Active secret mode")
            role_mapping = {Role.GOALKEEPER: player.id}
            self.game_state.map_players_to_roles_by_player_id(role_mapping)

        self.is_yellow = self.player.team.team_color == TeamColor.YELLOW
        self.current_state = self.protect_goal
        self.next_state = self.protect_goal
        self.status_flag = Flags.WIP
        self.target_assignation_last_time = None
        self.target = target
        self._find_best_passing_option()
        self.kick_force = 5
        self.penalty_kick = penalty_kick

        self.tries_flag = 0
        self.grab_ball_tries = 0
        self.kick_last_time = time.time()

    def kick_charge(self):
        self.next_state = self.protect_goal

        return AICommand(self.player.id,  kick_type=1)

    def protect_goal(self):
        if not self.penalty_kick:
            if not self._is_ball_too_far and \
                    self.player == closest_player_to_point(self.game_state.ball_position).player and\
                    self._get_distance_from_ball() < ROBOT_RADIUS *3:
                self.next_state = self.go_behind_ball
            else:
                self.next_state = self.protect_goal
            return ProtectGoal(self.game_state, self.player, self.is_yellow,
                               minimum_distance=300,
                               maximum_distance=self.game_state.game.field.constant["FIELD_GOAL_RADIUS"]/2)
        else:
            our_goal = Position(self.game_state.const["FIELD_OUR_GOAL_X_EXTERNAL"], 0)
            opponent_kicker = player_with_ball(2*ROBOT_RADIUS)
            ball_position = self.game_state.ball_position
            if opponent_kicker is not None:
                ball_to_goal = our_goal.x - ball_position.x

                if self.game_state.field.our_side is FieldSide.POSITIVE:
                    opponent_kicker_orientation = clamp(opponent_kicker.pose.orientation, -pi/5, pi/5)
                    goalkeeper_orientation = wrap_to_pi(opponent_kicker_orientation - pi)
                else:
                    opponent_kicker_orientation = clamp(wrap_to_pi(opponent_kicker.pose.orientation - pi), -pi/5, pi/5)
                    goalkeeper_orientation = opponent_kicker_orientation

                y_position_on_line = ball_to_goal * tan(opponent_kicker_orientation)
                width = self.game_state.const["FIELD_GOAL_WIDTH"]
                y_position_on_line = clamp(y_position_on_line, -width, width)

                destination = Pose(our_goal.x, y_position_on_line, goalkeeper_orientation)

            else:
                destination = Pose(our_goal)
            return MoveToPosition(self.game_state, self.player, destination, pathfinder_on=True, cruise_speed=2)

    def go_behind_ball(self):
        if self._is_ball_too_far():
            self.next_state = self.protect_goal

        self.ball_spacing = GRAB_BALL_SPACING
        self.status_flag = Flags.WIP
        ball_position = self.game_state.ball_position
        orientation = (self.target.position - ball_position).angle()
        distance_behind = self.get_destination_behind_ball(GRAB_BALL_SPACING * 3)
        if (self.player.pose.position - distance_behind).norm() < 100 and abs(orientation - self.player.pose.orientation) < 0.1:
            self.next_state = self.grab_ball
        else:
            self.next_state = self.go_behind_ball
            self._find_best_passing_option()
        collision_ball = self.tries_flag == 0
        return GoToPositionPathfinder(self.game_state, self.player, Pose(distance_behind, orientation),
                                      collision_ball=collision_ball, cruise_speed=2, end_speed=0.2)

    def grab_ball(self):
        if self._is_ball_too_far():
            self.next_state = self.protect_goal

        if self.grab_ball_tries == 0:
            if self._get_distance_from_ball() < KICK_DISTANCE:
                self.next_state = self.kick
        else:
            if self._get_distance_from_ball() < (KICK_DISTANCE + self.grab_ball_tries * 10):
                self.next_state = self.kick
        ball_position = self.game_state.ball_position
        orientation = (self.target.position - ball_position).angle()
        distance_behind = self.get_destination_behind_ball(GRAB_BALL_SPACING)
        return GoToPositionPathfinder(self.game_state, self.player, Pose(distance_behind, orientation),
                                     cruise_speed=2, charge_kick=True, end_speed=0.3, collision_ball=False)

    def kick(self):
        self.ball_spacing = GRAB_BALL_SPACING
        self.next_state = self.validate_kick
        self.tries_flag += 1
        ball_position = self.game_state.ball_position
        orientation = (self.target.position - ball_position).angle()
        return Kick(self.game_state, self.player, self.kick_force, Pose(ball_position, orientation), cruise_speed=2, end_speed=0)

    def validate_kick(self):
        self.ball_spacing = GRAB_BALL_SPACING
        ball_position = self.game_state.ball_position
        orientation = (self.target.position - ball_position).angle()
        if self.game_state.ball_velocity.norm() > 1000 or self._get_distance_from_ball() > KICK_SUCCEED_THRESHOLD:
            self.next_state = self.protect_goal
        elif self.kick_last_time - time.time() < VALIDATE_KICK_DELAY:
            self.next_state = self.kick
        else:
            self.status_flag = Flags.INIT
            self.next_state = self.go_behind_ball

        return Kick(self.game_state, self.player, self.kick_force, Pose(ball_position, orientation), cruise_speed=2, end_speed=0.2)

    def _get_distance_from_ball(self):
        return (self.player.pose.position - self.game_state.ball_position).norm

    def _is_ball_too_far(self):
        our_goal = Position(self.game_state.const["FIELD_OUR_GOAL_X_EXTERNAL"], 0)
        return (our_goal - self.game_state.ball_position).norm() > self.game_state.const["FIELD_GOAL_WIDTH"]

    def _is_player_towards_ball_and_target(self, abs_tol=pi/30):
        ball_position = self.game_state.ball_position
        target_to_ball = ball_position - self.target.position
        ball_to_player = self.player.pose.position - ball_position
        return compare_angle(target_to_ball.angle, ball_to_player.angle, abs_tol=abs_tol)

    def _find_best_passing_option(self):
        if (self.target_assignation_last_time is None
                or time.time() - self.target_assignation_last_time > TARGET_ASSIGNATION_DELAY):

            tentative_target_id = best_passing_option(self.player)
            if tentative_target_id is None:
                self.target = Pose(Position(self.game_state.const["FIELD_THEIR_GOAL_X_EXTERNAL"], 0), 0)
            else:
                self.target = Pose(self.game_state.get_player_position(tentative_target_id))

            self.target_assignation_last_time = time.time()

    def get_destination_behind_ball(self, ball_spacing):
        """
            Calcule le point situé à  x pixels derrière la position 1 par rapport à la position 2
            :return: Un tuple (Pose, kick) où Pose est la destination du joueur et kick est nul (on ne botte pas)
            """

        delta_x = self.target.position.x - self.game_state.ball_position.x
        delta_y = self.target.position.y - self.game_state.ball_position.y
        theta = np.math.atan2(delta_y, delta_x)

        x = self.game_state.ball_position.x - ball_spacing * np.math.cos(theta)
        y = self.game_state.ball_position.y - ball_spacing * np.math.sin(theta)

        player_x = self.player.pose.position.x
        player_y = self.player.pose.position.y

        if np.sqrt((player_x - x) ** 2 + (player_y - y) ** 2) < 50:
            x -= np.math.cos(theta) * 2
            y -= np.math.sin(theta) * 2
        destination_position = Position(x, y)

        return destination_position
