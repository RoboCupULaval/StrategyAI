# Under MIT license, see LICENSE.txt
from functools import partial

from Util.constant import KickForce

from Util.role import Role

from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.STA.Tactic.stop import Stop
from ai.STA.Tactic.tactic_constants import Flags


# noinspection PyMethodMayBeStatic,PyMethodMayBeStatic
class TestGoalKeeper(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)
        our_goal = self.game_state.field.our_goal_pose

        self.create_node(Role.GOALKEEPER,
                         GoalKeeper(self.game_state, self.assigned_roles[Role.GOALKEEPER]))

        attacker = self.assigned_roles[Role.FIRST_ATTACK]
        node_idle = self.create_node(Role.FIRST_ATTACK, Stop(self.game_state, attacker))
        node_go_kick = self.create_node(Role.FIRST_ATTACK, GoKick(self.game_state,
                                                                  attacker,
                                                                  target=our_goal,
                                                                  kick_force=KickForce.HIGH))

        player_has_kicked = partial(self.has_kicked, Role.FIRST_ATTACK)

        node_idle.connect_to(node_go_kick, when=self.ball_is_outside_goal)
        node_go_kick.connect_to(node_idle, when=self.ball_is_inside_goal)
        node_go_kick.connect_to(node_go_kick, when=player_has_kicked)

    @classmethod
    def required_roles(cls):
        return [Role.GOALKEEPER,
                Role.FIRST_ATTACK]

    def has_kicked(self, role):
        return self.roles_graph[role].current_tactic.status_flag == Flags.SUCCESS

    def ball_is_outside_goal(self):
        return not self.ball_is_inside_goal()

    def ball_is_inside_goal(self):
        return self.game_state.field.our_goal_area.point_inside(self.game_state.ball_position) \
            or self.game_state.field.field_length / 2 < self.game_state.ball_position.x

