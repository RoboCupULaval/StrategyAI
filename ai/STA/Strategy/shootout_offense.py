# Under MIT license, see LICENSE.txt
from Util.constant import KickForce, BALL_RADIUS
from Util.pose import Pose
from Util.role import Role

from ai.STA.Strategy.team_go_to_position import TeamGoToPosition
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.STA.Tactic.leeroy_jenkins import LeeroyJenkins
from ai.states.game_state import GameState
from Util.area import Area



class ShootoutOffense(TeamGoToPosition):
    def __init__(self, game_state):
        super().__init__(game_state)

        field = self.game_state.field
        our_goal = field.our_goal_pose
        their_goal = field.their_goal_pose

        role_to_positions = {Role.GOALKEEPER:   Pose.from_values(our_goal.position.x * 1 / 8, field.top * 4 / 5),
                             Role.SECOND_ATTACK:  Pose.from_values(our_goal.position.x * 2 / 8, field.top * 4 / 5),
                             Role.FIRST_DEFENCE:  Pose.from_values(our_goal.position.x * 4 / 8, field.top * 4 / 5),
                             Role.SECOND_DEFENCE: Pose.from_values(our_goal.position.x * 6 / 8, field.top * 4 / 5),
                             Role.FIRST_ATTACK: Pose.from_values(our_goal.position.x * 7 / 8, field.top * 4 / 5)
                             }

        kicker = self.assigned_roles[Role.MIDDLE]
        self.create_node(Role.MIDDLE, LeeroyJenkins(game_state, kicker, their_goal))

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
