# Under MIT licence, see LICENCE.txt
from unittest.suite import _DebugResult

import numpy as np

from Debug.debug_command_factory import DebugCommandFactory

__author__ = 'RoboCupULaval'

import time
from math import tan, pi
from typing import List

from Util import Pose, Position, AICommand
from Util.ai_command import CmdBuilder, MoveTo, Idle
from Util.constant import ROBOT_RADIUS, KickForce
from Util.constant import TeamColor
from Util.geometry import clamp, compare_angle, wrap_to_pi, intersection_line_and_circle
from ai.Algorithm.evaluation_module import closest_player_to_point, best_passing_option, player_with_ball
from ai.GameDomainObjects.field import FieldSide
from ai.GameDomainObjects import Player

from ai.STA.Action.ProtectGoal import ProtectGoal
from ai.STA.Tactic.go_kick import GRAB_BALL_SPACING, KICK_DISTANCE, VALIDATE_KICK_DELAY, KICK_SUCCEED_THRESHOLD, GoKick

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

        self.current_state = self.defense
        self.next_state = self.defense

        self.target = Pose(self.game_state.field.our_goal, np.pi)  # Ignore target argument, always go for our goal


        self.OFFSET_FROM_GOAL_LINE = Position(ROBOT_RADIUS + 10, 0)

        self.go_kick_tactic = None

    def defense_dumb(self):
        dest_y = self.game_state.ball_position.y \
                 * self.game_state.const["FIELD_GOAL_WIDTH"] / 2 / self.game_state.const["FIELD_Y_TOP"]
        position = self.game_state.field.our_goal - Position(ROBOT_RADIUS + 10, -dest_y)
        return MoveTo(Pose(position, np.pi))

    def defense(self):
        if self.game_state.field.is_ball_in_our_goal() and self.game_state.ball.is_immobile():
            self.next_state = self.clear

        circle_radius = self.game_state.const["FIELD_GOAL_WIDTH"] / 2
        circle_center = self.game_state.field.our_goal - self.OFFSET_FROM_GOAL_LINE
        solutions = intersection_line_and_circle(circle_center,
                                                 circle_radius,
                                                 self.game_state.ball_position,
                                                 self._best_target_into_goal())
        # Their is one or two intersection on the circle, take the one on the field
        for solution in solutions:
            if solution.x < self.game_state.field.field_length / 2\
               and self.game_state.ball_position.x < self.game_state.field.field_length / 2:
                orientation_to_ball = (self.game_state.ball_position - self.player.position).angle
                return MoveTo(Pose(solution, orientation_to_ball),
                      cruise_speed=2,
                      end_speed=2)

        return MoveTo(Pose(self.game_state.field.our_goal, np.pi),
                      cruise_speed=2,
                      end_speed=2)


    def clear(self):
        # Move the ball to outside of the penality zone
        if self.go_kick_tactic is None:
            self.go_kick_tactic = GoKick(self.game_state, self.player, auto_update_target=True)
        if not self.game_state.field.is_ball_in_our_goal():
            self.next_state = self.defense
            self.go_kick_tactic = None
            return Idle
        else:
            return self.go_kick_tactic.exec()


    def _best_target_into_goal(self):
        # Find the bisection of the triangle made by the ball (a) and the two goals extremities(b, c)
        a = self.game_state.ball_position
        b = self.game_state.field.our_goal + Position(0, +self.game_state.const["FIELD_GOAL_WIDTH"] / 2)
        c = self.game_state.field.our_goal + Position(0, -self.game_state.const["FIELD_GOAL_WIDTH"] / 2)

        ab = a-b
        ac = a-c

        be = self.game_state.field.goal_width / (1 + ab.norm/ac.norm)

        return b + Position(0, -be)

    def debug_cmd(self):
        return [DebugCommandFactory().line(self.game_state.ball_position,
                                            self.game_state.field.our_goal - self.OFFSET_FROM_GOAL_LINE,  #self._best_target_into_goal(),
                                            timeout=0.1),
                DebugCommandFactory().line(self.game_state.ball_position,
                                            self._best_target_into_goal(),
                                            timeout=0.1)]


