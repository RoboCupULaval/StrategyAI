# Under MIT License, see LICENSE.txt

from functools import partial
from RULEngine.Util.Pose import Position, Pose
from ai.STA.Strategy.Strategy import Strategy
from ai.STA.Tactic.GoalKeeper import GoalKeeper
from ai.STA.Tactic.goToPositionPathfinder import GoToPositionPathfinder
from ai.STA.Tactic.Stop import Stop
from ai.STA.Tactic.tactic_constants import Flags
from ai.Util.role import Role
from ai.states.game_state import GameState


class PrepareKickOffOffense(Strategy):

    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        # Attribution des joueurs
        attack_top = self.game_state.get_player_by_role(Role.FIRST_ATTACK)
        attack_bottom = self.game_state.get_player_by_role(Role.SECOND_ATTACK)
        middle = self.game_state.get_player_by_role(Role.MIDDLE)
        defense_top = self.game_state.get_player_by_role(Role.FIRST_DEFENCE)
        defense_bottom = self.game_state.get_player_by_role(Role.SECOND_DEFENCE)

        goalkeeper = self.game_state.get_player_by_role(Role.GOALKEEPER)

        # Positions objectifs des joueurs
        attack_top_position = Pose(Position(GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"] / 15,
                                            GameState().const["FIELD_Y_BOTTOM"] * 3 / 5))
        attack_bottom_position = Pose(Position(GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"] / 15,
                                               GameState().const["FIELD_Y_TOP"] * 3 / 5))
        middle_position = Pose(Position(GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"] / 30, 0))
        defense_bottom_position = Pose(Position(GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"] / 2,
                                                GameState().const["FIELD_Y_BOTTOM"] / 3))
        defense_top_position = Pose(Position(GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"] / 2,
                                             GameState().const["FIELD_Y_TOP"] / 3))
        ourgoal = Pose(Position(GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"], 0), 0)

        # Tactiques
        self.add_tactic(Role.SECOND_ATTACK, GoToPositionPathfinder(self.game_state, attack_bottom,
                                                                   attack_bottom_position))
        self.add_tactic(Role.SECOND_ATTACK, Stop(self.game_state, attack_bottom))
        self.add_condition(Role.SECOND_ATTACK, 0, 1, partial(self.arrived_to_position, attack_bottom))

        self.add_tactic(Role.FIRST_ATTACK, GoToPositionPathfinder(self.game_state, attack_top, attack_top_position))
        self.add_tactic(Role.FIRST_ATTACK, Stop(self.game_state, attack_top))
        self.add_condition(Role.FIRST_ATTACK, 0, 1, partial(self.arrived_to_position, attack_top))

        self.add_tactic(Role.MIDDLE, GoToPositionPathfinder(self.game_state, middle, middle_position))
        self.add_tactic(Role.MIDDLE, Stop(self.game_state, middle))
        self.add_condition(Role.MIDDLE, 0, 1, partial(self.arrived_to_position, middle))

        self.add_tactic(Role.SECOND_DEFENCE, GoToPositionPathfinder(self.game_state, defense_bottom,
                                                                    defense_bottom_position))
        self.add_tactic(Role.SECOND_DEFENCE, Stop(self.game_state, defense_bottom))
        self.add_condition(Role.SECOND_DEFENCE, 0, 1, partial(self.arrived_to_position, defense_bottom))

        self.add_tactic(Role.FIRST_DEFENCE, GoToPositionPathfinder(self.game_state, defense_top, defense_top_position))
        self.add_tactic(Role.FIRST_DEFENCE, Stop(self.game_state, defense_top))
        self.add_condition(Role.FIRST_DEFENCE, 0, 1, partial(self.arrived_to_position, defense_top))

        self.add_tactic(Role.GOALKEEPER, GoalKeeper(self.game_state, goalkeeper, ourgoal))

    def arrived_to_position(self, player):
        role = GameState().get_role_by_player_id(player.id)
        return self.roles_graph[role].get_current_tactic().status_flag == Flags.SUCCESS
