# Under MIT licence, see LICENCE.txt
import time
from typing import Optional, List

from Util import Pose
from Util.ai_command import CmdBuilder, Idle
from Util.constant import ROBOT_RADIUS
from Util.geometry import normalize, Line, closest_point_on_segment
from ai.Algorithm.evaluation_module import ball_going_toward_player
from ai.GameDomainObjects import Player, Ball
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState

SAFE_DISTANCE_TO_SWITCH_TO_GO_KICK = ROBOT_RADIUS + 200
MIN_DELAY_TO_SWITCH_IMMOBILE_BALL = 0.5


class ReceivePass(Tactic):
    def __init__(self, game_state: GameState,
                 player: Player,
                 target: Optional[Pose] = None,
                 args: List[str] = None,
                 passing_robot: Optional[Player] = None):
      
        super().__init__(game_state, player, target, args=args)
        self.passing_robot = passing_robot

        self.status_flag = Flags.WIP
        if passing_robot is not None:
            self.current_state = self.next_state = self.align_with_passing_robot
        else:
            self.current_state = self.next_state = self.intercept

        self.passing_robot_has_kicked = False
        self.ball_is_immobile_since = None

    def halt(self):
        self.status_flag = Flags.SUCCESS
        return Idle

    def intercept(self):
        ball = self.game_state.ball

        if self._must_change_state(ball):
            return Idle

        ball_trajectory = Line(ball.position, ball.position + ball.velocity)
        target_pose = self._find_target_pose(ball, ball_trajectory)

        return CmdBuilder().addMoveTo(target_pose, cruise_speed=2, end_speed=0, ball_collision=False) \
                           .addForceDribbler().build()

    def align_with_passing_robot(self):
        ball = self.game_state.ball

        if self._must_change_state(ball):
            return Idle

        target_orientation = (self.passing_robot.position - self.player.position).angle
        target_pose = Pose(self.player.position, target_orientation)
        return CmdBuilder().addMoveTo(target_pose, cruise_speed=2, end_speed=0, ball_collision=False)\
                           .addForceDribbler().build()

    def go_away_from_ball(self):
        """
        If the ball have been intersect, we should switch directly to go_kick.
        However go_kick does not like been initiated near the ball and will immediately kick it.
        To prevent this we do a simple go_behind_ball with the kicker off BEFORE switching to go_kick
        """
        ball_position = self.game_state.ball.position
        player_to_ball = ball_position - self.player.position
        if player_to_ball.norm > SAFE_DISTANCE_TO_SWITCH_TO_GO_KICK:
            self.next_state = self.halt
            return self.next_state()

        target = self.game_state.field.their_goal  # We want a general orientation, go_kick will do the alignment
        away_position = normalize(ball_position - target) * SAFE_DISTANCE_TO_SWITCH_TO_GO_KICK + ball_position
        orientation = (target - self.game_state.ball.position).angle

        return CmdBuilder().addMoveTo(Pose(away_position, orientation),
                                      cruise_speed=3,
                                      end_speed=0,
                                      ball_collision=True) \
                           .addForceDribbler() \
                           .addChargeKicker().build()

    def _must_change_state(self, ball: Ball):
        if self.game_state.field.is_outside_field_limit(ball.position):
            self.logger.info("The ball has left the field")
            self.next_state = self.go_away_from_ball
            return True

        # We do not wat to switch to go_away_from_ball is the ball has not been already kicked
        if ball.is_immobile() and self.current_state != self.align_with_passing_robot:
            if self.ball_is_immobile_since is None:
                self.ball_is_immobile_since = time.time()
            elif time.time() - self.ball_is_immobile_since > MIN_DELAY_TO_SWITCH_IMMOBILE_BALL:
                self.logger.info("The ball is not moving, success?")
                self.next_state = self.go_away_from_ball
                self.ball_is_immobile_since = None
                return True

        if (ball.position - self.player.position).norm < ROBOT_RADIUS + 50 and ball.is_immobile():
            self.logger.info("The ball just touch us, success?")
            self.next_state = self.go_away_from_ball
            return True

        if self.passing_robot_has_kicked or ball_going_toward_player(self.game_state, self.player):
            self.next_state = self.intercept
            return self.current_state != self.intercept

        return False

    def _find_target_pose(self, ball, ball_trajectory):
        # Find the point where the ball will leave the field
        where_ball_leaves_field = self._find_where_ball_leaves_field(ball, ball_trajectory)
        if where_ball_leaves_field is None:
            return Pose(ball.position, (ball.position - self.player.position).angle)

        ball_to_leave_field = Line(ball.position, where_ball_leaves_field)

        # The robot can intercepts the ball by leaving the field, thus we must add a ROBOT_RADIUS
        intersect_position_limit = where_ball_leaves_field + ball_to_leave_field.direction * ROBOT_RADIUS
        intersect_position = closest_point_on_segment(self.player.position, ball.position, intersect_position_limit)

        if (self.player.position - intersect_position).norm < ROBOT_RADIUS:
            best_orientation = (ball.position - intersect_position_limit).angle
        else:
            best_orientation = self.player.pose.orientation  # We move a bit faster, if we keep our orientation

        return Pose(intersect_position, best_orientation)

    def _find_where_ball_leaves_field(self, ball: Ball, trajectory: Line):
        intersection_with_field = self.game_state.field.area.intersect_with_line(trajectory)
        where_ball_leaves_field = None
        for inter in intersection_with_field:
            # If this is the intersection that have the same direction as trajectory direction
            if (inter - ball.position).dot(trajectory.direction) > 0:
                where_ball_leaves_field = inter
                break

        if where_ball_leaves_field is None:
            self.logger.error(f"_find_where_ball_leaves_field - ball: {ball.position}, trajectory: {trajectory}")
            self.logger.error(f"_find_where_ball_leaves_field - intersections_with_field: {intersection_with_field}")
            raise RuntimeError("The ball is somehow inside and outside the field")

        return where_ball_leaves_field
