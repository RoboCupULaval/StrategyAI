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

# stratégie: attaque


class Offense(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)
        ourgoal = Pose(Position(GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"], 0), 0)
        self.theirgoal = Pose(Position(GameState().const["FIELD_THEIR_GOAL_X_EXTERNAL"], 0), 0)

        self.robots_position = self.generate_robot_positions()

        # Goal Keeper fixé en début de stratégie
        goalkeeper = closest_player_to_point(ourgoal.position, True)
        self.add_tactic(goalkeeper.id, GoalKeeper(self.game_state, goalkeeper, ourgoal))

        count = 0
        for i in GameState().my_team.available_players.values():
            if not i.id == goalkeeper.id:
                self.add_tactic(i.id, GoToPositionPathfinder(self.game_state, i, self.robots_position[count]))
                self.add_tactic(i.id, GoKick(self.game_state, i, auto_update_target=True))

                self.add_condition(i.id, 0, 1, partial(self.is_closest, i))
                self.add_condition(i.id, 1, 0, partial(self.is_not_closest, i))
                count += 1

    def is_closest(self, player):
        return player == closest_player_to_point(GameState().get_ball_position(), True)

    def is_not_closest(self, player):
        return player != closest_player_to_point(GameState().get_ball_position(), True)

    def generate_robot_positions(self):
        return [Pose(Position(2000, 1000), 0),
                Pose(Position(2000, -1000), 0),
                Pose(Position(-1000, 1000), 0),
                Pose(Position(-1000, -1000), 0),
                Pose(Position(-1000, 0), 0),
                Pose(Position(0, 0), 0)]