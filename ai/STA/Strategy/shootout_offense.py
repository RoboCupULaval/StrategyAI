# Under MIT license, see LICENSE.txt
from Util.role import Role
from ai.STA.Strategy.strategy import Strategy

from ai.STA.Tactic.leeroy_jenkins import LeeroyJenkins


class ShootoutOffense(Strategy):
    def __init__(self, game_state):
        super().__init__(game_state)

        field = self.game_state.field
        their_goal = field.their_goal_pose

        kicker = self.assigned_roles[Role.MIDDLE]
        self.create_node(Role.MIDDLE, LeeroyJenkins(game_state, kicker, their_goal))

    @classmethod
    def required_roles(cls):
        return [Role.MIDDLE]

    @classmethod
    def optional_roles(cls):
        return [Role.FIRST_ATTACK,
                Role.SECOND_ATTACK,
                Role.GOALKEEPER,
                Role.FIRST_DEFENCE,
                Role.SECOND_DEFENCE]
