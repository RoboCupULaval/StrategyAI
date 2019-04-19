# Under MIT license, see LICENSE.txt
from functools import partial

from Util.role import Role

from ai.Algorithm.evaluation_module import closest_players_to_point_except, ball_going_toward_player, ball_not_going_toward_player
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.STA.Tactic.position_for_pass import PositionForPass
from ai.STA.Tactic.receive_pass import ReceivePass
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState


class Demo2v2(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        robots_in_formation = [p for r, p in self.assigned_roles.items() if r != Role.GOALKEEPER]

        for role, player in self.assigned_roles.items():
            if role is Role.GOALKEEPER:
                self.create_node(role, GoalKeeper(self.game_state, player))
            else:
                node_go_kick = self.create_node(role, GoKick(self.game_state,
                                                             player,
                                                             auto_update_target=True))

                node_pass = self.create_node(role, PositionForPass(self.game_state,
                                                                   player,
                                                                   auto_position=True,
                                                                   robots_in_formation=robots_in_formation))
                node_go_kick.connect_to(node_pass, when=self.is_ball_in_goal)
                node_pass.connect_to(node_go_kick, when=lambda : not self.is_ball_in_goal())

    @classmethod
    def required_roles(cls):
        return [Role.GOALKEEPER,
                Role.FIRST_ATTACK]

    @classmethod
    def optional_roles(cls):
        return []

    def is_ball_in_goal(self):
        return self.game_state.field.is_ball_in_our_goal_area() or \
               self.game_state.field.is_ball_in_their_goal_area() or \
               self.game_state.field.is_outside_wall_limit(self.game_state.ball_position, bound=0)
