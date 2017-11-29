# Under MIT license, see LICENSE.txt
from functools import partial

import numpy as np

from RULEngine.GameDomainObjects.Player import Player
from ai.Algorithm.evaluation_module import closest_players_to_point, Pose, Position
from ai.STA.Tactic.AlignToDefenseWall import AlignToDefenseWall
from ai.STA.Tactic.GoalKeeper import GoalKeeper
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.position_for_pass import PositionForPass
from ai.STA.Tactic.tactic_constants import Flags
from ai.Util.role import Role
from ai.states.game_state import GameState
from . Strategy import Strategy

class DefenseWallNoKick(Strategy):
    def __init__(self, game_state: GameState, number_of_players: int = 4):
        super().__init__(game_state)
        self.number_of_players = number_of_players
        self.robots = []
        ourgoal = Pose(Position(GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"], 0), 0)
        self.theirgoal = Pose(Position(GameState().const["FIELD_THEIR_GOAL_X_EXTERNAL"], 0), 0)

        roles_to_consider = [Role.FIRST_ATTACK, Role.SECOND_ATTACK, Role.MIDDLE,
                             Role.FIRST_DEFENCE, Role.SECOND_DEFENCE]

        goalkeeper = self.game_state.get_player_by_role(Role.GOALKEEPER)

        self.add_tactic(Role.GOALKEEPER, GoalKeeper(self.game_state, goalkeeper, ourgoal))

        role_by_robots = [(i, self.game_state.get_player_by_role(i)) for i in roles_to_consider]
        self.robots = [player for _, player in role_by_robots if player is not None]
        for role, player in role_by_robots:
            if player:
                self.add_tactic(role, AlignToDefenseWall(self.game_state, player, self.robots))


