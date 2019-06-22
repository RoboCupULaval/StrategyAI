# Under MIT licence, see LICENCE.txt

import time
from typing import List

import numpy as np

from Debug.debug_command_factory import DebugCommandFactory, CYAN, RED, GREEN
from Util import Pose, Position
from Util.ai_command import Idle
from Util.constant import KickForce
from Util.geometry import normalize
from ai.Algorithm.evaluation_module import best_passing_option, player_covered_from_goal
from ai.GameDomainObjects import Player
from ai.STA.Tactic.tactic import Tactic
from ai.states.game_state import GameState

TARGET_ASSIGNATION_DELAY = 1.0
KICK_DISTANCE = 90


class TestBestPassingOption(Tactic):
    def __init__(self, game_state: GameState, player: Player,
                 target: Pose = Pose(),
                 args: List[str] = None,
                 kick_force: KickForce = KickForce.HIGH,
                 forbidden_areas=None,
                 can_kick_in_goal=False):

        super().__init__(game_state, player, target, args=args, forbidden_areas=forbidden_areas)
        self.current_state = self.find_best_passing_option
        self.next_state = self.find_best_passing_option
        self.kick_last_time = time.time()
        self.can_kick_in_goal = can_kick_in_goal
        self.target_assignation_last_time = 0
        self.target = target
        self.kick_force = kick_force

    def find_best_passing_option(self):
        assignation_delay = (time.time() - self.target_assignation_last_time)
        if assignation_delay > TARGET_ASSIGNATION_DELAY:

            # TODO Tester ces 2 fonctions
            scoring_target = player_covered_from_goal(self.player)
            tentative_target = best_passing_option(self.player, passer_can_kick_in_goal=self.can_kick_in_goal)

            # Kick in the goal where it's the easiest
            if self.can_kick_in_goal and scoring_target is not None:
                self.logger.debug("======== Kick in the goal where it's the easiest")

                self.target = Pose(scoring_target, 0)
                self.kick_force = KickForce.HIGH

            # Kick in the goal center
            elif tentative_target is None:
                if self.can_kick_in_goal:
                    self.logger.debug("======== Kick in the goal center")
                else:
                    self.logger.debug("======== Kick in the goal center, even if can_kick_in_goal is None")
                self.target = Pose(self.game_state.field.their_goal, 0)
                self.kick_force = KickForce.HIGH

            # Pass the ball to another player
            else:
                self.logger.debug("======== Pass the ball to another player")
                self.target = Pose(tentative_target.position)
                self.kick_force = KickForce.for_dist((self.target.position - self.game_state.ball.position).norm)

            self.target_assignation_last_time = time.time()

        return Idle

    def debug_cmd(self):
        angle = 10
        additional_dbg = [DebugCommandFactory.circle(self.game_state.ball_position, KICK_DISTANCE, color=RED),
                          DebugCommandFactory.circle(self.target.position, KICK_DISTANCE * 2)]
        if angle is not None:
            angle *= np.pi / 180.0
            base_angle = (self.game_state.ball.position - self.target.position).angle
            magnitude = 3000
            ori = self.game_state.ball.position
            upper = ori - Position.from_angle(base_angle + angle, magnitude)
            lower = ori - Position.from_angle(base_angle - angle, magnitude)
            ball_to_player = self.player.position - self.game_state.ball_position
            behind_player = (ball_to_player.norm + 1000) * normalize(ball_to_player) + self.game_state.ball_position
            return [DebugCommandFactory.line(ori, upper),
                    DebugCommandFactory.line(ori, lower),
                    DebugCommandFactory.line(self.game_state.ball_position, behind_player, color=CYAN)] + additional_dbg
        return []
