# Under MIT license, see LICENSE.txt

from Util.role import Role
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.STA.Tactic.penalty_goalkeeper import PenaltyGoalKeeper


class ShootoutDefense(Strategy):
    def __init__(self, game_state):
        super().__init__(game_state)

        self.ball_start_position = self.game_state.ball_position
        goalkeeper = self.assigned_roles[Role.GOALKEEPER]

        node_penalty_goalkeeper = self.create_node(Role.GOALKEEPER, PenaltyGoalKeeper(game_state, goalkeeper))
        node_goalkeeper = self.create_node(Role.GOALKEEPER, GoalKeeper(game_state, goalkeeper))

        node_penalty_goalkeeper.connect_to(node_goalkeeper, when=self._ball_is_in_play)

    def _ball_is_in_play(self):
        return (self.game_state.ball_position - self.ball_start_position).norm > 50

    @classmethod
    def required_roles(cls):
        return [Role.GOALKEEPER]
