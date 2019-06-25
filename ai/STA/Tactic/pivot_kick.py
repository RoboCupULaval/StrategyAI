from typing import List

import numpy as np

from Debug.debug_command_factory import DebugCommandFactory
from Util.ai_command import CmdBuilder
from Util.constant import KickForce, BALL_RADIUS, ROBOT_RADIUS, ROBOT_CENTER_TO_KICKER
from Util.geometry import Pose, normalize_to_zero, compare_angle, Line, Position, intersection_between_line_and_segment, \
    wrap_to_pi, intersection_between_segments
from ai.GameDomainObjects import Player
from ai.STA.Tactic.tactic import Tactic
from ai.states.game_state import GameState
from config.config import Config


class PivotKick(Tactic):
    def __init__(self, game_state: GameState, player: Player,
                 target: Pose = Pose(),
                 args: List[str] = None,
                 kick_force: KickForce = KickForce.HIGH):
        super().__init__(game_state, player, target, args=args)
        self.current_state = self.grab_ball
        self.next_state = self.grab_ball
        self.kick_force = kick_force
        self.player_sniping_line = None

        # Grsim seem to have a kicker closer to the robot_radius
        self.ROBOT_CENTER_TO_KICKER = ROBOT_RADIUS if Config().is_simulation() else ROBOT_CENTER_TO_KICKER

    def grab_ball(self):
        if self._ball_touching_dribbler():
            self.next_state = self.kick
            return self.next_state()

        player_to_ball = self.game_state.ball_position - self.player.position
        behind_ball = self.game_state.ball_position - (self.ROBOT_CENTER_TO_KICKER + BALL_RADIUS) * normalize_to_zero(player_to_ball)
        pose = Pose(behind_ball, player_to_ball.angle)
        return CmdBuilder().addMoveTo(pose, cruise_speed=3, ball_collision=False).addForceDribbler().build()

    def kick(self):
        if not self._ball_touching_dribbler(5 * BALL_RADIUS):
            self.player_sniping_line = None
            self.next_state = self.grab_ball
            return self.next_state()

        ROT_SPEED = 1.5 # rad/s
        radius = self.ROBOT_CENTER_TO_KICKER + BALL_RADIUS

        player_orientation = self.player.orientation
        goal_orientation = (self.game_state.field.their_goal - self.player.position).angle

        turn_clockwise = wrap_to_pi(goal_orientation - player_orientation) > 0
        rot_speed = -ROT_SPEED if turn_clockwise else ROT_SPEED

        cmd = CmdBuilder().addPivotTo(self.game_state.ball_position,
                                      target_angle=0, # not used for the moment
                                      target_radius=radius,
                                      cruise_speed=rot_speed)
        if self._player_is_facing_goal():
            return cmd.addKick(KickForce.HIGH).build()
        else:
            return cmd.build()

    def _ball_touching_dribbler(self, kick_distance_max=1.5 * BALL_RADIUS):
        MAX_ANGLE_FOR_KICK = 30

        ball_position = self.game_state.ball.position
        player_to_ball = ball_position - self.player.position

        return player_to_ball.norm <  self.ROBOT_CENTER_TO_KICKER + kick_distance_max \
               and compare_angle(self.player.orientation, player_to_ball.angle, abs_tol=np.deg2rad(MAX_ANGLE_FOR_KICK))

    def _player_is_facing_goal(self):
        player_far_target = self.player.position + 50000 * Position.from_angle(self.player.orientation)
        self.player_sniping_line = Line(self.player.position, player_far_target)

        goal_line = self.game_state.field.their_goal_line
        intersections = intersection_between_segments(goal_line.p1, goal_line.p2, self.player_sniping_line.p1, self.player_sniping_line.p2)
        return intersections is not None

    def debug_cmd(self):
        if self.player_sniping_line is None:
            return []
        return [DebugCommandFactory.line(self.player_sniping_line.p1, self.player_sniping_line.p2)]