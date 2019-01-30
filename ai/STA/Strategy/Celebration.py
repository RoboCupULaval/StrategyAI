from functools import partial
from typing import Dict, Callable

from Util.constant import ROBOT_DIAMETER
from Util.pose import Position, Pose
from Util.role import Role

from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.go_to_position import GoToPosition
from ai.STA.Tactic.tactic_constants import Flags


class Celebration(Strategy):

    def __init__(self, game_state):
        super().__init__(game_state)

        topGuy = self.assigned_roles[Role.FIRST_DEFENCE]
        topGuy_role = Role.FIRST_DEFENCE

        bottomGuy = self.assigned_roles[Role.SECOND_DEFENCE]
        bottomGuy_role = Role.SECOND_DEFENCE

        losange1 = self.assigned_roles[Role.FIRST_ATTACK]
        losange1_role = Role.FIRST_ATTACK

        losange2 = self.assigned_roles[Role.MIDDLE]
        losange2_role = Role.MIDDLE

        losange3 = self.assigned_roles[Role.SECOND_ATTACK]
        losange3_role = Role.SECOND_ATTACK

        position1_x = self.game_state.field.right - 200
        position1_y = self.game_state.field.top - 200

        top1 = Pose(Position(position1_x, position1_y), topGuy.pose.orientation)

        position2_x = 200
        position2_y = self.game_state.field.top - 200

        top2 = Pose(Position(position2_x, position2_y), topGuy.pose.orientation)

        position3_x = self.game_state.field.right - 200
        position3_y = self.game_state.field.bottom + 200

        bottom1 = Pose(Position(position3_x, position3_y), bottomGuy.pose.orientation)

        position4_x = 200
        position4_y = self.game_state.field.bottom + 200

        bottom2 = Pose(Position(position4_x, position4_y), bottomGuy.pose.orientation)

        position5_x = self.game_state.field.right - 800
        position5_y = 0

        position6_x = self.game_state.field.right - self.game_state.field.right / 2
        position6_y = self.game_state.field.bottom + 600

        position7_x = 200
        position7_y = 0

        position8_x = self.game_state.field.right - self.game_state.field.right / 2
        position8_y = self.game_state.field.top - 600

        position9_x = self.game_state.field.right - 200
        position9_y = 0

        position10_x = self.game_state.field.right - self.game_state.field.right / 2
        position10_y = self.game_state.field.top - self.game_state.field.top / 2

        topBottom_success = partial(self.top_bottom_tactic_succeed, topGuy_role, bottomGuy_role)

        node_top_1 = self.create_node(topGuy_role, GoToPosition(self.game_state, topGuy, top1))
        node_top_2 = self.create_node(topGuy_role, GoToPosition(self.game_state, topGuy, top2))
        node_bottom_1 = self.create_node(bottomGuy_role, GoToPosition(self.game_state, bottomGuy, bottom1))
        node_bottom_2 = self.create_node(bottomGuy_role, GoToPosition(self.game_state, bottomGuy, bottom2))

        node_top_1.connect_to(node_top_2, when=topBottom_success)
        node_top_2.connect_to(node_top_1, when=topBottom_success)

        node_bottom_1.connect_to(node_bottom_2, when=topBottom_success)
        node_bottom_2.connect_to(node_bottom_1, when=topBottom_success)

    def top_bottom_tactic_succeed(self, i, j):
        return self.roles_graph[i].current_tactic.status_flag == Flags.SUCCESS\
               and self.roles_graph[j].current_tactic.status_flag == Flags.SUCCESS

    @classmethod
    def required_roles(cls):
        return [Role.MIDDLE, Role.FIRST_ATTACK, Role.FIRST_DEFENCE, Role.SECOND_ATTACK, Role.SECOND_DEFENCE]
