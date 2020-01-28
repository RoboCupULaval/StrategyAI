# Under MIT license, see LICENSE.txt
from Util.area import Area
from Util.constant import ROBOT_RADIUS
from Util.role import Role
from ai.STA.Strategy.prepare_kickoff_offense import PrepareKickOffOffense

from ai.STA.Tactic.go_kick import GoKick


class OffenseKickOffWithPass(PrepareKickOffOffense):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        middle_player = self.assigned_roles[Role.MIDDLE]
        self.clear_graph_of_role(Role.MIDDLE)
        no_pass = self.create_node(Role.MIDDLE, GoKick(self.game_state,
                                                       middle_player,
                                                       auto_update_target=True))
        force_pass = self.create_node(Role.MIDDLE, GoKick(self.game_state,
                                                          middle_player,
                                                          can_kick_in_goal=False,
                                                          auto_update_target=True))
        no_pass.connect_to(force_pass, when=self.their_is_a_pass_receiver)
        force_pass.connect_to(no_pass, when=self.their_is_no_pass_receiver)

        self.attackers = [r for r in [Role.FIRST_ATTACK, Role.SECOND_ATTACK] if r in self.assigned_roles]

    def their_is_a_pass_receiver(self):
        right_limit = self.game_state.field.our_goal_x * 4 / 15 + ROBOT_RADIUS
        field = self.game_state.field
        top_area = Area.from_limits(field.top, field.center_circle_radius, 0, right_limit)
        bot_area = Area.flip_y(top_area)
        for role in self.attackers:
            player = self.assigned_roles[role]
            if player.position in top_area or player.position in bot_area:
                return True
        return False

    def their_is_no_pass_receiver(self):
        return not self.their_is_a_pass_receiver()


