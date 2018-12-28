# Under MIT license, see LICENSE.txt
from functools import partial

from Util import Position, Pose
from Util.constant import KickForce, ROBOT_RADIUS

from Util.role import Role

from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.go_to_position import GoToPosition
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.STA.Tactic.stop import Stop
from ai.STA.Tactic.tactic_constants import Flags


class TestHighSpeed(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        SPEED = 4

        field = self.game_state.field
        point_a = Position(self.game_state.field.left + 2 * ROBOT_RADIUS,
                           self.game_state.field.top - 2 * ROBOT_RADIUS)
        point_b = point_a.flip_y().flip_x()

        attacker = self.assigned_roles[Role.FIRST_ATTACK]

        node_go_a = self.create_node(Role.FIRST_ATTACK, GoToPosition(self.game_state,
                                                                     attacker,
                                                                     Pose(point_a),
                                                                     cruise_speed=SPEED))
        node_go_b = self.create_node(Role.FIRST_ATTACK, GoToPosition(self.game_state,
                                                                     attacker,
                                                                     Pose(point_b),
                                                                     cruise_speed=SPEED))
        node_go_kick = self.create_node(Role.FIRST_ATTACK, GoKick(self.game_state,
                                                                  attacker,
                                                                  auto_update_target=True,
                                                                  kick_force=KickForce.HIGH,
                                                                  forbidden_areas=field.border_limits))

        node_idle = self.create_node(Role.FIRST_ATTACK, Stop(self.game_state, attacker))

        node_idle.connect_to(node_go_a, when=self.current_tactic_succeed)
        node_go_a.connect_to(node_go_b, when=self.current_tactic_succeed)
        node_go_b.connect_to(node_go_kick, when=self.current_tactic_succeed)
        node_go_kick.connect_to(node_idle, when=self.current_tactic_succeed)

    @classmethod
    def required_roles(cls):
        return [Role.FIRST_ATTACK]

    def current_tactic_succeed(self):
        return self.roles_graph[Role.FIRST_ATTACK].current_tactic.status_flag == Flags.SUCCESS

