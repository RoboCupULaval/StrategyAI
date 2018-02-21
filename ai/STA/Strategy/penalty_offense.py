# Under MIT license, see LICENSE.txt

from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from ai.STA.Tactic.go_to_position_pathfinder import GoToPositionPathfinder
from ai.STA.Tactic.go_kick import GoKick
from ai.states.game_state import GameState
from ai.STA.Strategy.strategy import Strategy
from ai.Util.role import Role


class PenaltyOffense(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)
        ourgoal = Pose(Position(GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"], 0), 0)
        self.theirgoal = Pose(Position(GameState().const["FIELD_THEIR_GOAL_X_EXTERNAL"], 0), 0)

        roles_in_waiting_line = [Role.SECOND_ATTACK, Role.MIDDLE,
                             Role.FIRST_DEFENCE, Role.SECOND_DEFENCE]
        position_list = [Pose(Position(ourgoal.position.x / 8, GameState().const["FIELD_Y_TOP"] * 2 / 3)),
                         Pose(Position(ourgoal.position.x / 8, GameState().const["FIELD_Y_TOP"] / 3)),
                         Pose(Position(ourgoal.position.x / 8, GameState().const["FIELD_Y_BOTTOM"] / 3)),
                         Pose(Position(ourgoal.position.x / 8, GameState().const["FIELD_Y_BOTTOM"] * 2 / 3))]
        postions_for_roles = dict(zip(roles_in_waiting_line, position_list))

        goalkeeper = self.game_state.get_player_by_role(Role.GOALKEEPER)
        self.add_tactic(Role.GOALKEEPER, GoToPositionPathfinder(self.game_state, goalkeeper, ourgoal))

        kicker = self.game_state.get_player_by_role(Role.FIRST_ATTACK)
        self.add_tactic(Role.FIRST_ATTACK, GoKick(self.game_state, kicker, self.theirgoal))

        for role in roles_in_waiting_line:
            position = postions_for_roles[role]
            player = self.game_state.get_player_by_role(role)
            if player:
                self.add_tactic(role, GoToPositionPathfinder(self.game_state, player, position))
