# Under MIT License, see LICENSE.txt

from functools import partial

from RULEngine.Util.Pose import Position, Pose
from ai.STA.Strategy.Strategy import Strategy
from RULEngine.Util.constant import PLAYER_PER_TEAM
from ai.STA.Tactic.GoToPositionNoPathfinder import GoToPositionNoPathfinder
from ai.STA.Tactic.goToPositionPathfinder import GoToPositionPathfinder
from ai.STA.Tactic.Stop import Stop
from ai.STA.Tactic.tactic_constants import Flags


class PrepareKickOffOffense(Strategy):

    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        attack_left = self.game_state.my_team.available_players[3]
        attack_right = self.game_state.my_team.available_players[0]
        middle = self.game_state.my_team.available_players[1]
        defense_right = self.game_state.my_team.available_players[2]
        defense_left = self.game_state.my_team.available_players[4]
        goalkeeper = self.game_state.my_team.available_players[5]


        # Positions objectifs des joueurs
        attack_left_position = Pose(Position(self.game_state.const["FIELD_X_LEFT"] / 15,
                                                    self.game_state.const["FIELD_Y_BOTTOM"] * 3 / 5))
        attack_right_position = Pose(Position(self.game_state.const["FIELD_X_LEFT"] / 15,
                                                    self.game_state.const["FIELD_Y_TOP"] * 3 / 5))
        middle_position = Pose(Position(self.game_state.const["FIELD_X_LEFT"] / 30, 0))
        defense_right_position = Pose(Position(self.game_state.const["FIELD_X_LEFT"] / 2,
                                                    self.game_state.const["FIELD_Y_BOTTOM"] / 3))
        defense_left_position = Pose(Position(self.game_state.const["FIELD_X_LEFT"] / 2,
                                                    self.game_state.const["FIELD_Y_TOP"] / 3))
        goalkeeper_position = Pose(Position(self.game_state.const["FIELD_X_LEFT"] * 9/10, 0))


        # Tactiques
        self.add_tactic(attack_right.id, GoToPositionPathfinder(self.game_state, attack_right, attack_right_position))
        self.add_tactic(attack_right.id, Stop(self.game_state, attack_right))
        self.add_condition(attack_right.id, 0, 1, partial(self.arrived_to_position, attack_right))

        self.add_tactic(attack_left.id, GoToPositionPathfinder(self.game_state, attack_left, attack_left_position))
        self.add_tactic(attack_left.id, Stop(self.game_state, attack_left))
        self.add_condition(attack_left.id, 0, 1, partial(self.arrived_to_position, attack_left))

        self.add_tactic(middle.id, GoToPositionPathfinder(self.game_state, middle, middle_position))
        self.add_tactic(middle.id, Stop(self.game_state, middle))
        self.add_condition(middle.id, 0, 1, partial(self.arrived_to_position, middle))

        self.add_tactic(defense_right.id, GoToPositionPathfinder(self.game_state, defense_right, defense_right_position))
        self.add_tactic(defense_right.id, Stop(self.game_state, defense_right))
        self.add_condition(defense_right.id, 0, 1, partial(self.arrived_to_position, defense_right))

        self.add_tactic(defense_left.id, GoToPositionPathfinder(self.game_state, defense_left, defense_left_position))
        self.add_tactic(defense_left.id, Stop(self.game_state, defense_left))
        self.add_condition(defense_left.id, 0, 1, partial(self.arrived_to_position, defense_left))

        self.add_tactic(goalkeeper.id, GoToPositionPathfinder(self.game_state, goalkeeper, goalkeeper_position))
        self.add_tactic(goalkeeper.id, Stop(self.game_state, goalkeeper))
        self.add_condition(goalkeeper.id, 0, 1, partial(self.arrived_to_position, goalkeeper))


        # print("{} -- {} \n {} -- {}".format(y_down, y_top, x_right, x_left))

    def arrived_to_position(self, i):
        # print(i, self.graphs[i].get_current_tactic().status_flag == Flags.SUCCESS)
        return self.graphs[i.id].get_current_tactic().status_flag == Flags.SUCCESS

