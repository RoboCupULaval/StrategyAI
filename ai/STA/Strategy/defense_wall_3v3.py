# Under MIT license, see LICENSE.txt
from functools import partial

from Util import Pose
from Util.role import Role
from ai.Algorithm.evaluation_module import closest_players_to_point, Position
from ai.STA.Tactic.align_to_defense_wall import AlignToDefenseWall
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState
from ai.STA.Strategy.strategy import Strategy


# noinspection PyMethodMayBeStatic,PyMethodMayBeStatic,PyPep8Naming,PyUnresolvedReferences,PyUnresolvedReferences
class DefenseWall_3v3(Strategy):
    def __init__(self, game_state: GameState, number_of_players: int = 3):
        super().__init__(game_state)

        role_mapping = {Role.GOALKEEPER: 4, Role.FIRST_ATTACK: 3, Role.SECOND_ATTACK: 2}
        self.game_state.map_players_to_roles_by_player_id(role_mapping)

        self.number_of_players = number_of_players
        self.robots = []
        their_goal = self.game_state.field.their_goal

        roles_to_consider = [Role.FIRST_ATTACK, Role.SECOND_ATTACK]

        goalkeeper = self.game_state.get_player_by_role(Role.GOALKEEPER)
        self.create_node(Role.GOALKEEPER, GoalKeeper(self.game_state, goalkeeper))

        role_by_robots = [(i, self.game_state.get_player_by_role(i)) for i in roles_to_consider]
        self.robots = [player for _, player in role_by_robots if player is not None]
        for role, player in role_by_robots:
            if player:
                node_align_to_defense_wall = self.create_node(role, AlignToDefenseWall(self.game_state, player, robots_in_formation=self.robots))
                node_go_kick = self.create_node(role, GoKick(self.game_state, player, target=self.their_goal))

                player_is_closest = partial(self.is_closest, player)
                player_is_not_closest = partial(self.is_not_closest, player)

                node_align_to_defense_wall.connect_to(node_go_kick, when=player_is_closest)
                node_go_kick.connect_to(node_go_kick, when=player_is_closest)
                node_go_kick.connect_to(node_align_to_defense_wall, when=player_is_not_closest)

    def is_closest(self, player):
        if player == closest_players_to_point(GameState().ball_position, True)[0].player:
            return True
        return False

    def is_second_closest(self, player):
        if player == closest_players_to_point(GameState().ball_position, True)[1].player:
            return True
        return False

    def is_not_closest(self, player):
        return not(self.is_closest(player))

    def is_not_one_of_the_closests(self, player):
        # print(player.id)
        # print(not(self.is_closest(player) or self.is_second_closest(player)))
        return not(self.is_closest(player) or self.is_second_closest(player))

    def has_kicked(self, player):
        role = GameState().get_role_by_player_id(player.id)
        if self.roles_graph[role].current_tactic_name == 'GoKick':
            return self.roles_graph[role].current_tactic.status_flag == Flags.SUCCESS
        else:
            return False
