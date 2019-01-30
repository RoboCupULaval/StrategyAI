from functools import partial

from Util.constant import ROBOT_DIAMETER
from Util.pose import Position, Pose
from Util.role import Role

from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.go_to_position import GoToPosition
from ai.STA.Tactic.tactic_constants import Flags


class Triangle(Strategy):

    def __init__(self, game_state):
        super().__init__(game_state)

        for robot in self.assigned_roles:
            celeb = self.assigned_roles[robot]
            celeb_role = robot

            start_x = self.game_state.field.right - self.game_state.field.right / 2
            start_y = 0

            start = (Pose(Position(start_x, start_y), celeb.pose.orientation))

            middle_x = self.game_state.field.left + self.game_state.field.right / 2
            middle_y = 0

            middle = (Pose(Position(middle_x, middle_y), celeb.pose.orientation))

            last_x = 0
            last_y = self.game_state.field.top - 500

            last = (Pose(Position(last_x, last_y), celeb.pose.orientation))

            node_go_to_start = self.create_node(celeb_role, GoToPosition(self.game_state, celeb, start))
            node_go_to_middle = self.create_node(celeb_role, GoToPosition(self.game_state, celeb, middle))
            node_go_to_last = self.create_node(celeb_role, GoToPosition(self.game_state, celeb, last))

            celeb_succeeded = partial(self.current_tactic_succeed, celeb_role)

            node_go_to_start.connect_to(node_go_to_middle, when=celeb_succeeded)
            node_go_to_middle.connect_to(node_go_to_last, when=celeb_succeeded)
            node_go_to_last.connect_to(node_go_to_start, when=celeb_succeeded)

    def current_tactic_succeed(self, i):
            return self.roles_graph[i].current_tactic.status_flag == Flags.SUCCESS

    @classmethod
    def required_roles(cls):
        return [Role.MIDDLE, Role.FIRST_ATTACK, Role.FIRST_DEFENCE, Role.SECOND_ATTACK, Role.SECOND_DEFENCE,
                Role.GOALKEEPER]
