# Under MIT License, see LICENSE.txt

from functools import partial

from Util.constant import ROBOT_DIAMETER
from Util.pose import Position, Pose
from Util.role import Role

from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.go_to_position import GoToPosition
from ai.STA.Tactic.tactic_constants import Flags


class BeFree2(Strategy):

    DISTANCE_LIMIT = 300

    def __init__(self, game_state):
        super().__init__(game_state)

        goalie = self.assigned_roles[Role.GOALKEEPER]
        goalie_role = Role.GOALKEEPER

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

        mouvement_losange = {losange1: losange1_role, losange2: losange2_role, losange3: losange3_role}

        for player, role in mouvement_losange.items():

            losange_right = Pose(Position(self.game_state.field.right - 2000, self.game_state.field.bottom + 1500),
                         player.pose.orientation)
            losange_left = Pose(Position(self.game_state.field.right - 2000, self.game_state.field.top - 1500),
                               player.pose.orientation)
            losange_top = Pose(Position(self.game_state.field.right - 2750, 0), player.pose.orientation)
            losange_bottom = Pose(Position(self.game_state.field.right - 1250, 0), player.pose.orientation)

            node_go_to_lr = self.create_node(role, GoToPosition(self.game_state, player, losange_right, live_zone=self.DISTANCE_LIMIT))
            node_go_to_ll = self.create_node(role, GoToPosition(self.game_state, player, losange_left, live_zone=self.DISTANCE_LIMIT))
            node_go_to_lt = self.create_node(role, GoToPosition(self.game_state, player, losange_top, live_zone=self.DISTANCE_LIMIT))
            node_go_to_lb = self.create_node(role, GoToPosition(self.game_state, player, losange_bottom, live_zone=self.DISTANCE_LIMIT))

            BeFree2_succeeded = partial(self.current_tactic_succeed, role)

            node_go_to_lr.connect_to(node_go_to_lb, when=BeFree2_succeeded)
            node_go_to_ll.connect_to(node_go_to_lt, when=BeFree2_succeeded)
            node_go_to_lt.connect_to(node_go_to_lr, when=BeFree2_succeeded)
            node_go_to_lb.connect_to(node_go_to_ll, when=BeFree2_succeeded)

        corner_rightnext = Pose(Position(100, self.game_state.field.top - 500),
                            topGuy.pose.orientation)
        corner_leftnext = Pose(Position(100, self.game_state.field.bottom + 500),
                           bottomGuy.pose.orientation)
        corner_right = Pose(Position(self.game_state.field.right - 500, self.game_state.field.top - 500),
                            topGuy.pose.orientation)
        corner_left = Pose(Position(self.game_state.field.right - 500, self.game_state.field.bottom + 500),
                           bottomGuy.pose.orientation)

        node_go_to_cornerR = self.create_node(topGuy_role, GoToPosition(self.game_state, topGuy, corner_rightnext))
        node_go_to_cornerL = self.create_node(bottomGuy_role, GoToPosition(self.game_state, bottomGuy, corner_leftnext))
        node_go_to_cornerRN = self.create_node(topGuy_role, GoToPosition(self.game_state, topGuy, corner_right))
        node_go_to_cornerLN = self.create_node(bottomGuy_role, GoToPosition(self.game_state, bottomGuy, corner_left))

        cornertop_succeeded = partial(self.current_tactic_succeed, topGuy_role)
        cornerbottom_succeeded = partial(self.current_tactic_succeed, bottomGuy_role)

        node_go_to_cornerR.connect_to(node_go_to_cornerRN, when=cornertop_succeeded)
        node_go_to_cornerRN.connect_to(node_go_to_cornerR, when=cornertop_succeeded)
        node_go_to_cornerL.connect_to(node_go_to_cornerLN, when=cornerbottom_succeeded)
        node_go_to_cornerLN.connect_to(node_go_to_cornerL, when=cornerbottom_succeeded)

        top_line = Pose(Position(0, 500), goalie.pose.orientation)
        bottom_line = Pose(Position(0, -500), goalie.pose.orientation)

        node_go_top_line = self.create_node(goalie_role, GoToPosition(self.game_state, goalie, top_line, live_zone=self.DISTANCE_LIMIT))
        node_go_bottom_line = self.create_node(goalie_role, GoToPosition(self.game_state, goalie, bottom_line, live_zone=self.DISTANCE_LIMIT))

        goalie_succeeded = partial(self.current_tactic_succeed, goalie_role)

        node_go_top_line.connect_to(node_go_bottom_line, when=goalie_succeeded)
        node_go_bottom_line.connect_to(node_go_top_line, when=goalie_succeeded)

    def current_tactic_succeed(self, i):
        return self.roles_graph[i].current_tactic.status_flag == Flags.SUCCESS

    @classmethod
    def required_roles(cls):
        return [Role.GOALKEEPER, Role.MIDDLE, Role.FIRST_DEFENCE,
                Role.FIRST_ATTACK, Role.SECOND_DEFENCE, Role.SECOND_ATTACK]