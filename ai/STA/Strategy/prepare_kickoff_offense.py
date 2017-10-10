# Under MIT License, see LICENSE.txt

from functools import partial
from RULEngine.Util.Pose import Position, Pose
from ai.STA.Strategy.Strategy import Strategy
from ai.STA.Tactic.placeholder_goalkeeper import GoalKeeper
from ai.STA.Tactic.go_to_position_pathfinder import GoToPositionPathfinder
from ai.STA.Tactic.placehlder_stop import Stop
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
        # TODO: Why are those constant different in kickoff_offense and kickoff_defense
        attack_top_position = Pose(GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"] / 15,
                                   GameState().const["FIELD_Y_BOTTOM"] * 3 / 5)
        attack_bottom_position = Pose(GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"] / 15,
                                      GameState().const["FIELD_Y_TOP"] * 3 / 5)
        middle_position = Pose((GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"] / 15, 0))
        defense_top_position = Pose(GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"] / 2,
                                    GameState().const["FIELD_Y_TOP"] / 3)
        defense_bottom_position = Pose(GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"] / 2,
                                       GameState().const["FIELD_Y_BOTTOM"] / 3)

        our_goal = Pose((GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"], 0), 0)

        self.add_tactic(Role.GOALKEEPER, GoalKeeper(self.game_state, goalkeeper, our_goal))

        robots_and_positions = [(attack_top, attack_top_position),
                                (attack_bottom, attack_bottom_position),
                                (middle, middle_position),
                                (defense_top, defense_top_position),
                                (defense_bottom, defense_bottom_position)]

        for player, position in robots_and_positions:
            if player:
                role = GameState().get_role_by_player_id(player.id)
                self.add_tactic(role, GoToPositionPathfinder(self.game_state, player, position))
                self.add_tactic(role, Stop(self.game_state, player))
                self.add_condition(role, 0, 1, partial(self.arrived_to_position, player))

    def arrived_to_position(self, player):
        role = GameState().get_role_by_player_id(player.id)
        return self.roles_graph[role].get_current_tactic().status_flag == Flags.SUCCESS
