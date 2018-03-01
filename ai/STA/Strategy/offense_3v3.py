# Under MIT license, see LICENSE.txt
from functools import partial

from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from ai.Algorithm.Graph.Graph import Graph
from ai.Algorithm.evaluation_module import closest_player_to_point
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.STA.Tactic.tactic_constants import Flags
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.position_for_pass import PositionForPass
from ai.states.game_state import GameState
from ai.STA.Strategy.strategy import Strategy
from ai.Util.role import Role

class Offense_3v3(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state, keep_roles=False)

        # TODO: HARDCODED ID FOR QUALIFICATION, REMOVE LATER
        self.roles_graph = {r: Graph() for r in Role}
        role_mapping = {Role.GOALKEEPER: 2, Role.MIDDLE: 4, Role.FIRST_ATTACK: 6}
        self.game_state.map_players_to_roles_by_player_id(role_mapping)

        ourgoal = Pose(Position(GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"], 0), 0)
        self.theirgoal = Pose(Position(GameState().const["FIELD_THEIR_GOAL_X_EXTERNAL"], 0), 0)

        roles_to_consider = [Role.MIDDLE, Role.FIRST_ATTACK, Role.GOALKEEPER]
        role_by_robots = [(i, self.game_state.get_player_by_role(i)) for i in roles_to_consider]
        self.robots = [player for _, player in role_by_robots if player is not None]

        goalkeeper = self.game_state.get_player_by_role(Role.GOALKEEPER)

        self.add_tactic(Role.GOALKEEPER, GoalKeeper(self.game_state, goalkeeper, ourgoal, penalty_kick=True))

        for index, player in role_by_robots:
            if player:
                self.add_tactic(index, PositionForPass(self.game_state, player, auto_position=True,
                                                       robots_in_formation=self.robots))
                self.add_tactic(index, GoKick(self.game_state, player, target=self.theirgoal))

                self.add_condition(index, 0, 1, partial(self.is_closest, player))
                self.add_condition(index, 1, 0, partial(self.is_not_closest, player))
                self.add_condition(index, 1, 1, partial(self.has_kicked, player))

    def is_closest(self, player):
        return player == closest_player_to_point(GameState().get_ball_position(), True, robots=self.robots).player

    def is_not_closest(self, player):
        return player != closest_player_to_point(GameState().get_ball_position(), True, robots=self.robots).player

    def has_kicked(self, player):
        role = GameState().get_role_by_player_id(player.id)
        if self.roles_graph[role].get_current_tactic_name() == 'GoKick':
            return self.roles_graph[role].get_current_tactic().status_flag == Flags.SUCCESS
        else:
            return False
