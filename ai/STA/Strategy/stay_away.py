# Under MIT license, see LICENSE.txt

from ai.STA.Tactic.stay_away_from_ball import StayAwayFromBall
from ai.STA.Strategy.Strategy import Strategy
from ai.Util.role import Role

class StayAway(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        roles_to_consider = [Role.FIRST_ATTACK, Role.SECOND_ATTACK, Role.MIDDLE,
                             Role.FIRST_DEFENCE, Role.SECOND_DEFENCE, Role.GOALKEEPER]
        role_by_robots = [(i, self.game_state.get_player_by_role(i)) for i in roles_to_consider]

        for index, player in role_by_robots:
            if player:
                self.add_tactic(index, StayAwayFromBall(self.game_state, player))
