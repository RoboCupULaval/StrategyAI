# Under MIT License, see LICENSE.txt

from functools import partial

from Util.pose import Position, Pose
from Util.role import Role
from ai.Algorithm.evaluation_module import closest_player_to_point
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.STA.Tactic.position_for_pass import PositionForPass
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState


# noinspection PyMethodMayBeStatic,PyMethodMayBeStatic,PyUnresolvedReferences,PyUnresolvedReferences
class IndirectFreeKick(Strategy):

    def __init__(self, p_game_state):
        super().__init__(p_game_state)
        ourgoal = Pose(Position(GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"], 0), 0)
        self.theirgoal = Pose(Position(GameState().const["FIELD_THEIR_GOAL_X_EXTERNAL"], 0), 0)

        roles_to_consider = [Role.FIRST_ATTACK, Role.SECOND_ATTACK, Role.MIDDLE,
                             Role.FIRST_DEFENCE, Role.SECOND_DEFENCE]
        role_by_robots = [(i, self.game_state.get_player_by_role(i)) for i in roles_to_consider]

        goalkeeper = self.game_state.get_player_by_role(Role.GOALKEEPER)

        self.create_node(Role.GOALKEEPER, GoalKeeper(self.game_state, goalkeeper, ourgoal))

        for index, player in role_by_robots:
            if player:
                node_pass = self.create_node(index, PositionForPass(self.game_state, player, auto_position=True))
                node_go_kick = self.create_node(index, GoKick(self.game_state, player, auto_update_target=True))

                player_is_closest = partial(self.is_closest, player)
                player_is_not_closest = partial(self.is_not_closest, player)
                player_has_kicked = partial(self.has_kicked, player)

                node_pass.connect_to(node_go_kick, when=player_is_closest)
                node_go_kick.connect_to(node_pass, when=player_is_not_closest)
                node_go_kick.connect_to(node_go_kick, when=player_has_kicked)

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
