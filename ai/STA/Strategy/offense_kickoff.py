# Under MIT license, see LICENSE.txt

from Util.pose import Pose

from Util.position import Position
from Util.role import Role
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.stop import Stop
from ai.states.game_state import GameState


# noinspection PyUnresolvedReferences
class OffenseKickOff(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)
        self.theirgoal = Pose(Position(GameState().const["FIELD_THEIR_GOAL_X_EXTERNAL"], 0), 0)

        roles_to_consider = [Role.FIRST_ATTACK, Role.SECOND_ATTACK, Role.GOALKEEPER,
                             Role.FIRST_DEFENCE, Role.SECOND_DEFENCE]
        role_by_robots = [(i, self.game_state.get_player_by_role(i)) for i in roles_to_consider]

        middle_player = self.game_state.get_player_by_role(Role.MIDDLE)

        self.add_tactic(Role.MIDDLE, GoKick(self.game_state, middle_player, self.theirgoal))

        for index, player in role_by_robots:
            if player:
                self.add_tactic(index, Stop(self.game_state, player))
