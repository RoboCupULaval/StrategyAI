# Under MIT license, see LICENSE.txt
from functools import partial

from Util.pose import Pose

from Util.position import Position
from Util.role import Role
from Util.role_mapping_rule import keep_prev_mapping_otherwise_random
from ai.Algorithm.evaluation_module import closest_player_to_point
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.STA.Tactic.position_for_pass import PositionForPass
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState


# noinspection PyMethodMayBeStatic,PyMethodMayBeStatic
class Offense(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)
        our_goal = Pose(Position(GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"], 0), 0)

        for role, player in self.assigned_roles.items():
            if role is Role.GOALKEEPER:
                self.create_node(Role.GOALKEEPER, GoalKeeper(self.game_state, player, our_goal))
            else:
                node_pass = self.create_node(role, PositionForPass(self.game_state, player, auto_position=True))
                node_go_kick = self.create_node(role, GoKick(self.game_state, player, auto_update_target=True))

                player_is_closest = partial(self.is_closest, player)
                player_is_not_closest = partial(self.is_not_closest, player)
                player_has_kicked = partial(self.has_kicked, player)

                node_pass.connect_to(node_go_kick, when=player_is_closest)
                node_go_kick.connect_to(node_pass, when=player_is_not_closest)
                node_go_kick.connect_to(node_go_kick, when=player_has_kicked)

    @classmethod
    def required_roles(cls):
        return {r: keep_prev_mapping_otherwise_random for r in [Role.GOALKEEPER,
                                                                Role.FIRST_ATTACK,
                                                                Role.SECOND_ATTACK,
                                                                Role.MIDDLE,
                                                                Role.FIRST_DEFENCE,
                                                                Role.SECOND_DEFENCE]
                }

    def is_closest(self, player):
        return player == closest_player_to_point(GameState().ball_position, True).player

    def is_not_closest(self, player):
        return player != closest_player_to_point(GameState().ball_position, True).player

    def has_kicked(self, player):
        role = GameState().get_role_by_player_id(player.id)
        if self.roles_graph[role].current_tactic_name == 'GoKick':
            return self.roles_graph[role].current_tactic.status_flag == Flags.SUCCESS
        else:
            return False

