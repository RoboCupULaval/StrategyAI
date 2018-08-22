# Under MIT License, see LICENSE.txt

from functools import partial

from Util.pose import Position, Pose

from ai.Algorithm.evaluation_module import best_passing_option
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.STA.Tactic.pass_to_player import PassToPlayer
from ai.STA.Tactic.stop import Stop
from ai.STA.Tactic.tactic_constants import Flags
from Util.role import Role


# TODO: This strategy is quite limited, only a two player move (FIRST_ATTACK and GOALER)
class PassesWithDecisions(Strategy):

    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        their_goal = self.game_state.field.their_goal_pose

        node_pass_to_second_attack = self.create_node(Role.FIRST_ATTACK,
                                                      PassToPlayer(self.game_state,
                                                                   self.assigned_roles[Role.FIRST_ATTACK],
                                                                   args=[self.assigned_roles[Role.SECOND_ATTACK].id]))

        node_pass_to_middle = self.create_node(Role.FIRST_ATTACK,
                                               PassToPlayer(self.game_state,
                                                            self.assigned_roles[Role.FIRST_ATTACK],
                                                            args=[self.assigned_roles[Role.MIDDLE].id]))

        node_go_kick = self.create_node(Role.FIRST_ATTACK, GoKick(self.game_state,
                                                                  self.assigned_roles[Role.FIRST_ATTACK],
                                                                  their_goal))

        second_attack_is_best_receiver = partial(self.is_best_receiver, Role.SECOND_ATTACK)
        middle_is_best_receiver = partial(self.is_best_receiver, Role.MIDDLE)
        current_tactic_succeeded = partial(self.current_tactic_succeed, Role.FIRST_ATTACK)

        node_pass_to_second_attack.connect_to(node_pass_to_middle, when=second_attack_is_best_receiver)
        node_pass_to_second_attack.connect_to(node_go_kick, when=middle_is_best_receiver)
        node_pass_to_second_attack.connect_to(node_pass_to_second_attack, when=current_tactic_succeeded)
        node_pass_to_middle.connect_to(node_pass_to_second_attack, when=current_tactic_succeeded)
        node_go_kick.connect_to(node_pass_to_second_attack, when=current_tactic_succeeded)

        self.create_node(Role.GOALKEEPER, GoalKeeper(self.game_state, self.assigned_roles[Role.GOALKEEPER]))


    @classmethod
    def required_roles(cls):
        return [Role.GOALKEEPER,
                Role.FIRST_ATTACK,
                Role.SECOND_ATTACK,
                Role.MIDDLE]

    def current_tactic_succeed(self, role):
        if self.roles_graph[role].current_tactic_name == 'PassToPlayer':
            return self.roles_graph[role].current_tactic.status_flag == Flags.SUCCESS
        else:
            return False

    def is_best_receiver(self, role):
        if self.current_tactic_succeed(role):
            if best_passing_option(self.assigned_roles[Role.FIRST_ATTACK].id) == self.assigned_roles[role].id:
                return True
        return False
