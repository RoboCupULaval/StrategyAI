# Under MIT license, see LICENSE.txt

from ai.Algorithm.evaluation_module import closest_players_to_point, Pose, Position
from ai.states.game_state import GameState
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.go_to_position_pathfinder import GoToPositionPathfinder
from RULEngine.Util.constant import ROBOT_RADIUS
from ai.Util.role import Role


class LineUp(Strategy):
    def __init__(self, game_state: GameState):
        super().__init__(game_state)
        self.robots = []
        self.robots_in_lineup = []
        self.position_offset = 0
        self.positions_in_formations = 0
        self.target_position = Position(self.game_state.const["FIELD_Y_NEGATIVE"],
                                        self.game_state.const["FIELD_X_NEGATIVE"])
        roles_to_consider = [Role.FIRST_ATTACK, Role.SECOND_ATTACK, Role.MIDDLE,
                             Role.FIRST_DEFENCE, Role.SECOND_DEFENCE, Role.GOALKEEPER]

        # self.robots_in_lineup = closest_players_to_point(self.target_position, True)

        role_by_robots = [(i, self.game_state.get_player_by_role(i)) for i in roles_to_consider]

        self.robots = [player for player in role_by_robots if player is not None]
        for role, player in role_by_robots:

            destination_orientation = 0
            self.position_offset = (role * ROBOT_RADIUS * 3, 0)
            self.positions_in_formations = self.target_position + self.position_offset

            self.add_tactic(role, GoToPositionPathfinder(self.game_state, player,
                                                         Pose(self.positions_in_formations, destination_orientation)))

            # self.add_condition(idx, 0, 0, partial(self.is_closest, player))

