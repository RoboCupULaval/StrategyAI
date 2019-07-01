# Under MIT license, see LICENSE.txt

from Util.role import Role
from ai.STA.Strategy.prepare_kickoff_offense import PrepareKickOffOffense

from ai.STA.Tactic.go_kick import GoKick


class OffenseKickOff(PrepareKickOffOffense):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        middle_player = self.assigned_roles[Role.MIDDLE]
        self.clear_graph_of_role(Role.MIDDLE)
        self.create_node(Role.MIDDLE, GoKick(self.game_state,
                                             middle_player,
                                             auto_update_target=True))

