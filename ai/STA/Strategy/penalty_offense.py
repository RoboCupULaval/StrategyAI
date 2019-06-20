# Under MIT license, see LICENSE.txt
from Util.constant import KickForce, BALL_RADIUS
from Util.pose import Pose
from Util.role import Role

from ai.STA.Strategy.team_go_to_position import TeamGoToPosition
from ai.STA.Tactic.go_kick import GoKick
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
        self.create_node(Role.MIDDLE, GoKick(game_state, kicker, their_goal, kick_force=KickForce.HIGH,
                                                   forbidden_areas=[new_goal]))

        goalkeeper = self.assigned_roles[Role.GOALKEEPER]
        self.create_node(Role.GOALKEEPER, GoalKeeper(game_state, goalkeeper, penalty_kick=True))

        self.assign_tactics(role_to_positions)

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
