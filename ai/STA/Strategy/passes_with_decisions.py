# Under MIT License, see LICENSE.txt

from functools import partial

from Util.pose import Position, Pose
from ai.Algorithm.evaluation_module import best_passing_option
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.pass_to_player import PassToPlayer
from ai.STA.Tactic.stop import Stop
from ai.STA.Tactic.tactic_constants import Flags
from Util.role import Role


class PassesWithDecisions(Strategy):

    def __init__(self, p_game_state):
        super().__init__(p_game_state)




        #  goalkeeper = self.game_state.get_player_by_role(Role.GOALKEEPER)
        roles_to_consider = [Role.FIRST_ATTACK, Role.SECOND_ATTACK, Role.MIDDLE]
        #  role_by_robots = [(i, self.game_state.get_player_by_role(i)) for i in roles_to_consider]
        self.goal_ID = None
        self.goal = (Pose(Position(self.game_state.const["FIELD_THEIR_GOAL_X_EXTERNAL"], 0), 0))

        self.create_node(Role.FIRST_ATTACK, PassToPlayer(self.game_state, self.game_state.get_player_by_role(Role.FIRST_ATTACK), target_id=self.game_state.get_player_by_role(Role.SECOND_ATTACK).id))
        self.create_node(Role.FIRST_ATTACK, PassToPlayer(self.game_state, self.game_state.get_player_by_role(Role.FIRST_ATTACK), target_id=self.game_state.get_player_by_role(Role.MIDDLE).id))
        self.create_node(Role.FIRST_ATTACK, GoKick(self.game_state, self.game_state.get_player_by_role(Role.FIRST_ATTACK), self.goal))

        self.add_condition(Role.FIRST_ATTACK, 0, 1, partial(self.is_best_receiver, Role.SECOND_ATTACK))
        self.add_condition(Role.FIRST_ATTACK, 0, 2, partial(self.is_best_receiver, Role.MIDDLE))

        self.add_condition(Role.FIRST_ATTACK, 0, 0, partial(self.condition, Role.FIRST_ATTACK))
        self.add_condition(Role.FIRST_ATTACK, 1, 0, partial(self.condition, Role.FIRST_ATTACK))
        self.add_condition(Role.FIRST_ATTACK, 2, 0, partial(self.condition, Role.FIRST_ATTACK))

        for i in roles_to_consider:
            if not (i == Role.FIRST_ATTACK):
                self.create_node(i, Stop(self.game_state, self.game_state.get_player_by_role(i)))

    def condition(self, role):

        if self.roles_graph[role].get_current_tactic_name() == 'PassToPlayer':
            return self.roles_graph[role].get_current_tactic().status_flag == Flags.SUCCESS
        else:
            return False

    def is_best_receiver(self, role):
        if self.condition(role):
            if best_passing_option(self.game_state.get_player_by_role(Role.FIRST_ATTACK).id) == self.game_state.get_player_by_role(role).id:
                return True
        return False
