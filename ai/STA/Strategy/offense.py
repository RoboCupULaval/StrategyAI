# Under MIT license, see LICENSE.txt
from functools import partial

from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from ai.Algorithm.evaluation_module import closest_player_to_point
from ai.STA.Tactic.GoalKeeper import GoalKeeper
from ai.STA.Tactic.tactic_constants import Flags
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.position_for_pass import PositionForPass
from ai.states.game_state import GameState
from . Strategy import Strategy

# stratégie: attaque


class Offense(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)
        ourgoal = Pose(Position(GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"], 0), 0)
        self.theirgoal = Pose(Position(GameState().const["FIELD_THEIR_GOAL_X_EXTERNAL"], 0), 0)

        # Goal Keeper fixé en début de stratégie
        goalkeeper = closest_player_to_point(ourgoal.position, True)
        self.add_tactic(goalkeeper.id, GoalKeeper(self.game_state, goalkeeper, ourgoal))

        for i in GameState().my_team.available_players.values():
            if not i.id == goalkeeper.id:
                self.add_tactic(i.id, PositionForPass(self.game_state, i, auto_position=True))
                self.add_tactic(i.id, GoKick(self.game_state, i, auto_update_target=True))

                self.add_condition(i.id, 0, 1, partial(self.is_closest, i))
                self.add_condition(i.id, 1, 0, partial(self.is_not_closest, i))
                self.add_condition(i.id, 1, 1, partial(self.has_kicked, i))

    def is_closest(self, player):
        return player == closest_player_to_point(GameState().get_ball_position(), True)

    def is_not_closest(self, player):
        return player != closest_player_to_point(GameState().get_ball_position(), True)

    def has_kicked(self, player):
        if self.graphs[player.id].get_current_tactic_name() == 'GoKick':
            return self.graphs[player.id].get_current_tactic().status_flag == Flags.SUCCESS
        else:
            return False
