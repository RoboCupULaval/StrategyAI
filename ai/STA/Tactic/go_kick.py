# Under MIT licence, see LICENCE.txt
import math as m
from typing import List, Union
import time

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from RULEngine.Util.geometry import are_collinear, get_position_behind_point

from ai.Algorithm.evaluation_module import best_passing_option, best_goal_score_option
from ai.states.game_state import GameState

from ai.STA.Action.ChargeKick import ChargeKick
from ai.STA.Action.Idle import Idle
from ai.STA.Action.Kick import Kick
from ai.STA.Action.MoveToPosition import MoveToPosition

from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags

__author__ = 'RoboCupULaval'

VALIDATE_KICK_DELAY = 0.5
TARGET_ASSIGNATION_DELAY = 1
MAX_KICK_TRIES = 100000

GO_BEHIND_SPACING = 200
GRAB_BALL_SPACING = 220
APPROACH_SPEED = 100
KICK_DISTANCE = 140
KICK_SUCCEED_DISTANCE_THRESHOLD = 600
KICK_SUCCEED_SPEED_THRESHOLD = 1000
COMMAND_DELAY = 0.5


class GoKick(Tactic):
    def __init__(self, game_state: GameState, player: OurPlayer,
                 target: Pose = Pose(),
                 args: List[str] = None,
                 kick_force: Union[int, float] = 5,
                 auto_update_target=False,
                 consider_goal_as_target=True):

        Tactic.__init__(self, game_state, player, target, args)
        self.kick_force = kick_force
        self.auto_update_target = auto_update_target
        self.consider_goal_as_target = consider_goal_as_target

        self.target_assignation_last_time = 0

        if self.auto_update_target:
            self._find_best_passing_option()

        self.cmd_last_time = time.time()
        self.kick_last_time = time.time()

        self.has_kick = False
        self.kick_tries = 0
        self.kick_succeed = False

        self.next_state = self.kick_charge

    def kick_charge(self):
        self.status_flag = Flags.WIP

        self.next_state = self.go_behind_ball
        return ChargeKick(self.game_state, self.player)

    def go_behind_ball(self):
        self.status_flag = Flags.WIP

        if self.auto_update_target:
            self._find_best_passing_option()

        pose_behind_ball = self._get_pose_behind_ball()

        if self.player.pose.position.is_close(pose_behind_ball.position, abs_tol=40):
            self.next_state = self.grab_ball
        else:
            self.next_state = self.go_behind_ball

        collision_ball_flag = not self.has_kick

        return MoveToPosition(self.game_state,
                              self.player,
                              pose_behind_ball,
                              collision_ball=collision_ball_flag,
                              cruise_speed=1)

    def grab_ball(self):
        self.status_flag = Flags.WIP

        print(self.player.pose.compare_orientation(self._get_aiming(), abs_tol=m.pi/20))
        print(self._get_aiming(), self.player.pose.orientation)
        print(self._get_distance_from_ball())

        if self._get_distance_from_ball() < KICK_DISTANCE and \
                self.player.pose.compare_orientation(self._get_aiming(), abs_tol=m.pi/20):
            self.next_state = self.kick
        else:
            self.next_state = self.grab_ball

        return MoveToPosition(self.game_state,
                              self.player,
                              Pose(self.game_state.get_ball_position(), self._get_aiming()),
                              cruise_speed=1,
                              end_speed=0.1)

    def validate_kick(self):
        self.status_flag = Flags.WIP

        if self.game_state.get_ball_velocity().norm() > KICK_SUCCEED_SPEED_THRESHOLD or \
                self._get_distance_from_ball() > KICK_SUCCEED_DISTANCE_THRESHOLD:

            if self.auto_update_target:
                if self.tentative_target_id:
                    for player in self.game_state.my_team.available_players.values():
                        player.receiver_pass_flag = False

            self.next_state = self.halt
            self.kick_succeed = True

        elif time.time() - self.kick_last_time < VALIDATE_KICK_DELAY:
            self.next_state = self.validate_kick
            self.kick_succeed = False

        else:
            self.next_state = self.go_behind_ball
            self.kick_succeed = False

        return Idle(self.game_state,
                    self.player)

    def kick(self):
        self.status_flag = Flags.WIP

        self.next_state = self.validate_kick
        self.kick_last_time = time.time()
        self.has_kick = True
        self.kick_tries += 1

        if self.kick_tries == MAX_KICK_TRIES:
            self.status_flag = Flags.FAILURE
            self.next_state = self.halt

        return Kick(self.game_state,
                    self.player,
                    self.kick_force,
                    self.target,
                    )

    def halt(self):
        if self.status_flag == Flags.INIT:
            self.status_flag = Flags.WIP
            self.next_state = self.kick_charge
        elif self.kick_succeed:
            self.status_flag = Flags.SUCCESS
            self.next_state = self.halt
        else:
            self.status_flag = Flags.FAILURE
            self.next_state = self.halt
        return Idle(self.game_state, self.player)

    def _get_distance_from_ball(self):
        return (self.player.pose.position - self.game_state.get_ball_position()).norm()

    def _get_aiming(self):
        ball_position = self.game_state.get_ball_position()
        orientation = (self.target.position - ball_position).angle()
        return orientation

    def _is_player_towards_ball_and_target(self):
        player = self.player.pose.position
        ball = self.game_state.get_ball_position()
        target = self.target.position
        return are_collinear(player, ball, target, abs_tol=m.pi / 30)

    def _get_pose_behind_ball(self):
        ball = self.game_state.get_ball_position()
        target = self.target.position
        orientation = self._get_aiming()
        return Pose(get_position_behind_point(ball, target, GRAB_BALL_SPACING), orientation)

    def _find_best_passing_option(self):

        assignation_delay = (time.time() - self.target_assignation_last_time)

        if assignation_delay > TARGET_ASSIGNATION_DELAY:
            self.tentative_target_id = best_passing_option(self.player, self.consider_goal_as_target)
            if self.tentative_target_id is None:
                self.target = Pose(best_goal_score_option(self.player))
            else:
                self.target = Pose(GameState().get_player_position(self.tentative_target_id))
                self.game_state.get_player(self.tentative_target_id).receiver_pass_flag = True

            self.target_assignation_last_time = time.time()
