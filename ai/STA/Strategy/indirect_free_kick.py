# Under MIT License, see LICENSE.txt

from functools import partial
from RULEngine.Util.Pose import Position, Pose
from ai.Algorithm.evaluation_module import closest_player_to_point
from ai.STA.Strategy.Strategy import Strategy
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.STA.Tactic.go_to_position_pathfinder import GoToPositionPathfinder
from ai.STA.Tactic.stop import Stop
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.position_for_pass import PositionForPass
from ai.STA.Tactic.tactic_constants import Flags
from ai.Util.role import Role
from ai.states.game_state import GameState


class IndirectFreeKick(Strategy):

    def __init__(self, p_game_state):
        super().__init__(p_game_state)
        ourgoal = Pose(Position(GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"], 0), 0)
        self.theirgoal = Pose(Position(GameState().const["FIELD_THEIR_GOAL_X_EXTERNAL"], 0), 0)

        roles_to_consider = [Role.FIRST_ATTACK, Role.SECOND_ATTACK, Role.MIDDLE,
                             Role.FIRST_DEFENCE, Role.SECOND_DEFENCE]
        role_by_robots = [(i, self.game_state.get_player_by_role(i)) for i in roles_to_consider]

        goalkeeper = self.game_state.get_player_by_role(Role.GOALKEEPER)

        self.add_tactic(Role.GOALKEEPER, GoalKeeper(self.game_state, goalkeeper, ourgoal))

        for index, player in role_by_robots:
            if player:
                self.add_tactic(index, PositionForPass(self.game_state, player, auto_position=True))
                self.add_tactic(index, GoKick(self.game_state, player, auto_update_target=True))

                self.add_condition(index, 0, 1, partial(self.is_closest, player))
                self.add_condition(index, 1, 0, partial(self.is_not_closest, player))
                self.add_condition(index, 1, 1, partial(self.has_kicked, player))

    def is_closest(self, player):
        return player == closest_player_to_point(GameState().get_ball_position(), True).player

    def is_not_closest(self, player):
        return player != closest_player_to_point(GameState().get_ball_position(), True).player

    def has_kicked(self, player):
        role = GameState().get_role_by_player_id(player.id)
        if self.roles_graph[role].get_current_tactic_name() == 'GoKick':
            return self.roles_graph[role].get_current_tactic().status_flag == Flags.SUCCESS
        else:
            return False
