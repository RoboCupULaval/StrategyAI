# Under MIT license, see LICENSE.txt
from functools import partial

from Util import Position, Pose
from Util.constant import ROBOT_RADIUS
from Util.role import Role
from Util.role_mapping_rule import keep_prev_mapping_otherwise_random
from ai.states.game_state import GameState
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.go_to_position_pathfinder import GoToPositionPathfinder


class LineUp(Strategy):
    def __init__(self, game_state: GameState):
        super().__init__(game_state)
        self.robots = []
        self.robots_in_lineup = []
        self.position_offset = Position(0, 0)
        self.positions_in_formations = 0
        self.target_position = Position(0, 0)
        roles_to_consider = [Role.FIRST_ATTACK, Role.SECOND_ATTACK, Role.MIDDLE,
                             Role.FIRST_DEFENCE, Role.SECOND_DEFENCE, Role.GOALKEEPER]

        # self.robots_in_lineup = closest_players_to_point(self.target_position, True)

        role_by_robots = [(i, self.game_state.get_player_by_role(i)) for i in roles_to_consider]

        self.robots = [player for player in role_by_robots if player is not None]
        i = 0
        for role, player in role_by_robots:

            destination_orientation = 0
            self.position_offset = Position(i * ROBOT_RADIUS * 3, 0)
            self.positions_in_formations = self.target_position + self.position_offset
            i += 1
            always = partial(self.always)
            node_move_to = self.create_node(role, GoToPositionPathfinder(self.game_state, player,
                                                                         Pose(self.positions_in_formations,
                                                                              destination_orientation)))
            node_move_to.connect_to(node_move_to, when=always)

            # self.add_condition(idx, 0, 0, partial(self.is_closest, player))
    @staticmethod
    def always():

        return True

    @classmethod
    def required_roles(cls):
        return {r: keep_prev_mapping_otherwise_random for r in [Role.GOALKEEPER]
                }

    @classmethod
    def optional_roles(cls):
        return {r: keep_prev_mapping_otherwise_random for r in [Role.FIRST_DEFENCE,
                                                                Role.SECOND_DEFENCE,
                                                                Role.FIRST_ATTACK,
                                                                Role.MIDDLE,
                                                                Role.SECOND_ATTACK]
                }
