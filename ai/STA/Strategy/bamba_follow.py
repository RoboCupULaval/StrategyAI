# Under MIT License, see LICENSE.txt

from Util.role import Role

from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.demo_follow_ball import DemoFollowBall
from ai.STA.Tactic.demo_follow_robot import DemoFollowRobot


class BambaFollow(Strategy):

    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        p1 = self.game_state.get_player_by_role(Role.FIRST_ATTACK)
        p2 = self.game_state.get_player_by_role(Role.SECOND_ATTACK)
        p3 = self.game_state.get_player_by_role(Role.MIDDLE)

        self.add_tactic(Role.FIRST_ATTACK, DemoFollowBall(self.game_state, p1))
        self.add_tactic(Role.SECOND_ATTACK, DemoFollowRobot(self.game_state, p2, args=[p1.id]))
        self.add_tactic(Role.MIDDLE, DemoFollowRobot(self.game_state, p3, args=[p2.id]))
