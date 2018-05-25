# Under MIT license, see LICENSE.txt

from Util.role import Role
from Util.position import Position
from Util.pose import Pose
from Util.role_mapping_rule import keep_prev_mapping_otherwise_random
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.align_to_defense_wall import AlignToDefenseWall
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.states.game_state import GameState


# noinspection
class DefenseWallNoKick(Strategy):
    def __init__(self, game_state: GameState, number_of_players: int = 4):
        super().__init__(game_state)

        self.robots_in_formation = [p for r, p in self.assigned_roles.items() if r != Role.GOALKEEPER]
        for role, player in self.assigned_roles.items():
            if role == Role.GOALKEEPER:
                self.create_node(Role.GOALKEEPER, GoalKeeper(self.game_state, player))
            else:
                self.create_node(role, AlignToDefenseWall(self.game_state, player,
                                                          self.robots_in_formation))

    @classmethod
    def required_roles(cls):
        return {r: keep_prev_mapping_otherwise_random for r in [Role.GOALKEEPER,
                                                                Role.FIRST_ATTACK,
                                                                Role.SECOND_ATTACK,
                                                                Role.MIDDLE,
                                                                Role.FIRST_DEFENCE,
                                                                Role.SECOND_DEFENCE]
                }
