# Under MIT license, see LICENSE.txt

from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from ai.STA.Tactic.placeholder_goalkeeper import GoalKeeper
from ai.STA.Tactic.go_to_position_pathfinder import GoToPositionPathfinder
from ai.states.game_state import GameState
from ai.STA.Strategy.Strategy import Strategy
from ai.Util.role import Role


class PreparePenaltyDefense(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)
        ourgoal = Pose(Position(GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"], 0), 0)
        self.theirgoal = Pose(Position(GameState().const["FIELD_THEIR_GOAL_X_EXTERNAL"], 0), 0)

        roles_to_consider = [Role.FIRST_ATTACK, Role.SECOND_ATTACK, Role.MIDDLE,
                             Role.FIRST_DEFENCE, Role.SECOND_DEFENCE]
        position_list = [Pose(Position(self.theirgoal.position.x / 8, GameState().const["FIELD_Y_TOP"] * 2 / 3)),
                         Pose(Position(self.theirgoal.position.x / 8, GameState().const["FIELD_Y_TOP"] / 3)),
                         Pose(Position(self.theirgoal.position.x / 8, 0)),
                         Pose(Position(self.theirgoal.position.x / 8, GameState().const["FIELD_Y_BOTTOM"] / 3)),
                         Pose(Position(self.theirgoal.position.x / 8, GameState().const["FIELD_Y_BOTTOM"] * 2 / 3))]
        role_by_robots = [(i, position_list[i-1], self.game_state.get_player_by_role(i)) for i in roles_to_consider]

        goalkeeper = self.game_state.get_player_by_role(Role.GOALKEEPER)

        self.add_tactic(Role.GOALKEEPER, GoToPositionPathfinder(self.game_state, goalkeeper, ourgoal))

        for index, position, player in role_by_robots:
            if player:
                self.add_tactic(index, GoToPositionPathfinder(self.game_state, player, position))
