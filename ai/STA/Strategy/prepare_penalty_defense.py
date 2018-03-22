# Under MIT license, see LICENSE.txt

from Util.pose import Pose, Position
from Util.role import Role

from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.go_to_position_pathfinder import GoToPositionPathfinder
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.states.game_state import GameState


# noinspection PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences
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
        postions_for_roles = dict(zip(roles_to_consider, position_list))

        goalkeeper = self.game_state.get_player_by_role(Role.GOALKEEPER)

        self.create_node(Role.GOALKEEPER, GoalKeeper(self.game_state, goalkeeper, ourgoal, penalty_kick=True))

        for role in roles_to_consider:
            position = postions_for_roles[role]
            player = self.game_state.get_player_by_role(role)
            if player:
                self.create_node(role, GoToPositionPathfinder(self.game_state, player, position))
