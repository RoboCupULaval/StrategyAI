# Under MIT license, see LICENSE.txt
import time

import math

from Util.constant import KickForce, BALL_RADIUS, ROBOT_RADIUS, ROBOT_DIAMETER
from Util.pose import Pose
from Util.role import Role
from ai.Algorithm.evaluation_module import closest_players_to_point

from ai.STA.Strategy.team_go_to_position import TeamGoToPosition
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.go_to_position import GoToPosition
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.states.game_state import GameState
from Util.area import Area



class PenaltyOffense(TeamGoToPosition):
    def __init__(self, game_state):
        super().__init__(game_state)

        # We change the forbidden zone so the kicker can kick the ball, even if it's on the goal area line
        their_goal_forbidden_area = self.game_state.field.their_goal_forbidden_area
        new_goal = Area.from_limits(their_goal_forbidden_area.top,
                                    their_goal_forbidden_area.bottom,
                                    their_goal_forbidden_area.right - BALL_RADIUS * 6,
                                    their_goal_forbidden_area.left)

        field = self.game_state.field
        our_goal = field.our_goal_pose
        their_goal = field.their_goal_pose

        role_to_positions = {Role.FIRST_ATTACK:   Pose.from_values(our_goal.position.x / 8, field.top * 2 / 3),
                             Role.SECOND_ATTACK:  Pose.from_values(our_goal.position.x / 8, field.top / 3),
                             Role.FIRST_DEFENCE:  Pose.from_values(our_goal.position.x / 8, field.bottom / 3),
                             Role.SECOND_DEFENCE: Pose.from_values(our_goal.position.x / 8, field.bottom * 2 / 3)}

        kicker = self.assigned_roles[Role.MIDDLE]
        top_hole = self.game_state.field.their_goal.copy()
        top_hole.y += self.game_state.field.goal_width / 2 - 2 * ROBOT_RADIUS
        bot_hole = self.game_state.field.their_goal.copy()
        bot_hole.y -= self.game_state.field.goal_width / 2

        their_goal_to_ball = self.game_state.ball_position - bot_hole
        go_behind_position = self.game_state.ball_position + their_goal_to_ball.unit * ROBOT_RADIUS * 2.0
        go_behind_orientation = their_goal_to_ball.angle + math.pi

        go_behind = self.create_node(Role.MIDDLE, GoToPosition(self.game_state,
                                                               kicker,
                                                               target=Pose(go_behind_position, go_behind_orientation),
                                                               cruise_speed=1,
                                                               ball_collision=False))
        go_kick = self.create_node(Role.MIDDLE, GoKick(game_state,
                                                 kicker,
                                                 target=Pose(top_hole),
                                                 kick_force=KickForce.HIGH,
                                                 forbidden_areas=[new_goal]))

        go_behind.connect_to(go_kick, when=self.goalkeeper_is_top_or_timeout)
        go_kick.connect_to(go_behind, when=self.not_goalkeeper_is_top_or_timeout)
        self.start_time = time.time()

        goalkeeper = self.assigned_roles[Role.GOALKEEPER]
        self.create_node(Role.GOALKEEPER, GoalKeeper(game_state, goalkeeper, penalty_kick=True))

        self.assign_tactics(role_to_positions)

    def not_goalkeeper_is_top_or_timeout(self):
        return not self.goalkeeper_is_top_or_timeout()

    def goalkeeper_is_top_or_timeout(self):
        MAX_WAIT_TIME = 5

        if time.time() - self.start_time > MAX_WAIT_TIME:
            return True
        closest_enemy = closest_players_to_point(self.game_state.field.their_goal, our_team=False)
        if len(closest_enemy) == 0:
            return False

        goalkeeper = closest_enemy[0].player
        if goalkeeper.position not in self.game_state.field.their_goal_area:
            return False

        return goalkeeper.position.y < -self.game_state.field.goal_width / 2 + ROBOT_DIAMETER


    @classmethod
    def required_roles(cls):
        return [Role.GOALKEEPER,
                Role.MIDDLE]

    @classmethod
    def optional_roles(cls):
        return [Role.FIRST_ATTACK,
                Role.SECOND_ATTACK,
                Role.FIRST_DEFENCE,
                Role.SECOND_DEFENCE]
