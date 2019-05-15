# Under MIT licence, see LICENCE.txt

from typing import Optional

from Util import Pose
from Util.ai_command import CmdBuilder, Idle, MoveTo
from Util.constant import ROBOT_RADIUS
from Util.geometry import normalize, Line, closest_point_on_segment
from ai.Algorithm.evaluation_module import ball_not_going_toward_player
from ai.GameDomainObjects import Player, Ball
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState

SAFE_DISTANCE_TO_SWITCH_TO_GO_KICK = ROBOT_RADIUS + 200


class ReceivePass(Tactic):

    def __init__(self, game_state: GameState, player: Player, target: Optional[Pose]=None):
      
        super().__init__(game_state, player, target)
        self.current_state = self.initialize
        self.next_state = self.initialize

        self.passing_robot_pose = None  # passing_robot_pose != None => Align with passing robot

    def initialize(self):
        self.status_flag = Flags.WIP
        self.next_state = self.intercept
        return Idle

    def halt(self):
        self.status_flag = Flags.SUCCESS
        return Idle

    def intercept(self):
        ball = self.game_state.ball

        if self._must_change_state(ball):
            return Idle

        ball_trajectory = Line(ball.position, ball.position + ball.velocity)
        target_pose = self._find_target_pose(ball, ball_trajectory)

        return MoveTo(target_pose, cruise_speed=2, end_speed=0, ball_collision=False)

    def align_with_passing_robot(self):
        ball = self.game_state.ball

        if self._must_change_state(ball):
            return Idle

        # pass_trajectory = Line(self.passing_robot_pose.position, ball.position)
        # target_pose = self._find_target_pose(ball, pass_trajectory)
        # move_command = MoveTo(target_pose, cruise_speed=2, end_speed=0, ball_collision=False)

        target_pose = Pose(self.player.position, -self.passing_robot_pose.orientation)

        return MoveTo(target_pose, cruise_speed=2, end_speed=0, ball_collision=False)

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
                                      ball_collision=True)\
                           .addChargeKicker().build()

    def _must_change_state(self, ball: Ball):
        if self.game_state.field.is_outside_wall_limit(ball.position):
            self.logger.info("The ball has left the field")
            self.next_state = self.go_away_from_ball
            return True

        if ball.is_immobile():
            self.logger.info("The ball is not moving, success?")
            self.next_state = self.go_away_from_ball
            return True

        if (ball.position - self.player.position).norm < ROBOT_RADIUS + 50:
            self.logger.info("The ball about to touch us, success?")
            self.next_state = self.go_away_from_ball
            return True

        # TODO si le go kicker a reussi sa passe, changer de align_with_passing_robot à intercept, afin de suivre la trajectoire
        # TODO de la balle
        if self.passing_robot_pose is None:
            self.next_state = self.intercept
            return self.current_state != self.intercept
        elif ball_not_going_toward_player(self.game_state, self.player) or self._passing_robot_has_ball():
            self.next_state = self.align_with_passing_robot
            return self.current_state != self.align_with_passing_robot

        return False

    def _find_target_pose(self, ball, ball_trajectory):
        # Find the point where the ball will leave the field
        where_ball_leaves_field = self._find_where_ball_leaves_field(ball, ball_trajectory)

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
            raise RuntimeError("The ball is somehow inside and outside the field")

        return where_ball_leaves_field
