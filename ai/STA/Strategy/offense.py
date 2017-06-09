# Under MIT license, see LICENSE.txt
from functools import partial

from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from ai.Algorithm.evaluation_module import closest_player_to_point
from ai.STA.Tactic.GoalKeeper import GoalKeeper
from ai.STA.Tactic.goToPositionPathfinder import GoToPositionPathfinder
from ai.STA.Tactic.go_kick import GoKick
from ai.states.game_state import GameState
from . Strategy import Strategy


# stratégie: tout le monde fonce vers la balle car c'est tout ce qu'on sait faire


class offense(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)
        goal1 = Pose(Position(-1636, 0))
        goal2 = Pose(Position(1636, 0))
        goalkeeper = closest_player_to_point(goal1.position, True)[0][0]

        self.add_tactic(goalkeeper.id, GoalKeeper(self.game_state, goalkeeper))

        for i in GameState().my_team.available_players.values():
            if not i.id == goalkeeper.id:
                self.add_tactic(i.id, GoToPositionPathfinder(self.game_state, i, goal2))
                self.add_tactic(i.id, GoKick(self.game_state, i, goal1))
                self.add_condition(i.id, 0, 1, partial(self.is_closest, i))
                self.add_condition(i.id, 1, 0, partial(self.is_not_closest, i))


    def is_closest(self, player):
        return player == closest_player_to_point(GameState().get_ball_position(), True)[0][0]

    def is_not_closest(self, player):
        return not (player == closest_player_to_point(GameState().get_ball_position(), True)[0][0])