# Under MIT license, see LICENSE.txt
from functools import partial

from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from ai.Algorithm.evaluation_module import closest_player_to_point, best_passing_option
from ai.STA.Tactic.GoGetBall import GoGetBall
from ai.STA.Tactic.GoalKeeper import GoalKeeper
from ai.STA.Tactic.goToPositionPathfinder import GoToPositionPathfinder
from ai.STA.Tactic.go_kick import GoKick
from ai.states.game_state import GameState
from . Strategy import Strategy
from ai.STA.Tactic.tactic_constants import Flags


# stratégie: attaque


class Offense(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)
        ourgoal = Pose(Position(GameState().const["FIELD_GOAL_BLUE_X_LEFT"], 0), 0)
        self.theirgoal = Pose(Position(GameState().const["FIELD_GOAL_YELLOW_X_LEFT"], 0), 0)

        self.robots_position = self.generate_robot_positions()

        # Goal Keeper fixé en début de stratégie
        goalkeeper = closest_player_to_point(ourgoal.position, True)
        self.add_tactic(goalkeeper.id, GoalKeeper(self.game_state, goalkeeper, ourgoal))

        count = 0
        for i in GameState().my_team.available_players.values():
            if not i.id == goalkeeper.id:
                self.add_tactic(i.id, GoToPositionPathfinder(self.game_state, i, self.robots_position[count]))
                self.add_tactic(i.id, GoGetBall(self.game_state, i, Pose(GameState().get_ball_position())))
                self.add_tactic(i.id, GoKick(self.game_state, i, auto_update_target=True))

                self.add_condition(i.id, 0, 1, partial(self.is_closest, i))
                self.add_condition(i.id, 1, 0, partial(self.is_not_closest, i))
                self.add_condition(i.id, 1, 2, partial(self.is_behind_ball, i))
                self.add_condition(i.id, 2, 0, partial(self.is_not_closest, i))
                count += 1

    def is_closest(self, player):
        return player == closest_player_to_point(GameState().get_ball_position(), True)

    def is_not_closest(self, player):
        return player != closest_player_to_point(GameState().get_ball_position(), True)

    def is_behind_ball(self, i):
        if self.graphs[i.id].get_current_tactic_name() == 'GoGetBall':
            return self.graphs[i.id].get_current_tactic().status_flag == Flags.SUCCESS and \
                   best_passing_option(GameState().my_team.available_players[i.id]) is not None
        else:
            return False

    def generate_robot_positions(self):
        return [Pose(Position(2000, 1000), 0),
                Pose(Position(2000, -1000), 0),
                Pose(Position(-1000, 1000), 0),
                Pose(Position(-1000, -1000), 0),
                Pose(Position(-1000, 0), 0),
                Pose(Position(0, 0), 0)]
