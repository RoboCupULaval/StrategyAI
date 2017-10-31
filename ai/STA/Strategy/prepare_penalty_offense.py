# Under MIT license, see LICENSE.txt
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from ai.STA.Tactic.go_to_position_pathfinder import GoToPositionPathfinder
from ai.states.game_state import GameState
from ai.STA.Strategy.strategy_placehlder import Strategy
from ai.Util.role import Role


class PreparePenaltyOffense(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)
        ourgoal = Pose(Position(GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"], 0), 0)
        self.theirgoal = Pose(Position(GameState().const["FIELD_THEIR_GOAL_X_EXTERNAL"], 0), 0)

        roles_to_consider = [Role(i) for i in range(2, 6)]
        position_list = [Pose(Position(ourgoal.position.x / 8, GameState().const["FIELD_Y_TOP"] * 2 / 3)),
                         Pose(Position(ourgoal.position.x / 8, GameState().const["FIELD_Y_TOP"] / 3)),
                         Pose(Position(ourgoal.position.x / 8, GameState().const["FIELD_Y_BOTTOM"] / 3)),
                         Pose(Position(ourgoal.position.x / 8, GameState().const["FIELD_Y_BOTTOM"] * 2 / 3))]
        role_by_robots = [(i, position_list[i-2], self.game_state.get_player_by_role(i)) for i in roles_to_consider]

        goalkeeper = self.game_state.get_player_by_role(Role.GOALKEEPER)
        self.add_tactic(Role.GOALKEEPER, GoToPositionPathfinder(self.game_state, goalkeeper, ourgoal))

        kicker = self.game_state.get_player_by_role(Role(1))
        self.add_tactic(Role(1), GoToPositionPathfinder(self.game_state, kicker, self.game_state.const["FIELD_PENALTY_KICKER_POSE"]))

        for index, position, player in role_by_robots:
            if player:
                self.add_tactic(index, GoToPositionPathfinder(self.game_state, player, position))
