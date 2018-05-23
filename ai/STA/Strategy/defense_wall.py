# Under MIT license, see LICENSE.txt
from functools import partial

from Util.role import Role
from Util.position import Position
from Util.pose import Pose
from Util.role_mapping_rule import keep_prev_mapping_otherwise_random

from ai.Algorithm.evaluation_module import closest_players_to_point
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.align_to_defense_wall import AlignToDefenseWall, FETCH_BALL_ZONE_RADIUS
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.go_to_position_pathfinder import GoToPositionPathfinder
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.STA.Tactic.position_for_pass import PositionForPass
from ai.STA.Tactic.stop import Stop
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState


# noinspection PyMethodMayBeStatic,
class DefenseWall(Strategy):
    DEFENSIVE_ROLE = [Role.MIDDLE, Role.FIRST_DEFENCE, Role.SECOND_DEFENCE]

    def __init__(self, game_state: GameState, can_kick=True):
        super().__init__(game_state)

        their_goal = self.game_state.field.their_goal_pose

        # If we can not kick, the attackers are part of the defense wall
        # TODO find a more useful thing to do for the attackers
        if not can_kick:
            self.DEFENSIVE_ROLE += [Role.FIRST_ATTACK, Role.SECOND_ATTACK]
        self.robots_in_formation = [p for r, p in self.assigned_roles.items() if r in self.DEFENSIVE_ROLE]
        self.attackers = [p for r, p in self.assigned_roles.items() if r not in self.DEFENSIVE_ROLE and r != Role.GOALKEEPER]
        for role, player in self.assigned_roles.items():
            if role == Role.GOALKEEPER:
                self.create_node(Role.GOALKEEPER, GoalKeeper(self.game_state, player))
            elif can_kick and player in self.attackers:
                node_position_pass = self.create_node(role, PositionForPass(self.game_state, player, auto_position=True))
                node_go_kick = self.create_node(role, GoKick(self.game_state, player, target=their_goal))

                attacker_should_go_kick = partial(self.should_go_kick, player)
                attacker_should_not_go_kick = partial(self.should_not_go_kick, player)
                attacker_has_kicked = partial(self.has_kicked, role)

                node_position_pass.connect_to(node_go_kick, when=attacker_should_go_kick)
                node_go_kick.connect_to(node_position_pass, when=attacker_should_not_go_kick)
                node_go_kick.connect_to(node_go_kick, when=attacker_has_kicked)
            else:
                node_align_to_defense_wall = \
                    self.create_node(role, AlignToDefenseWall(self.game_state,
                                                              player,
                                                              robots_in_formation=self.robots_in_formation))
                node_position_pass = self.create_node(role, PositionForPass(self.game_state,
                                                                            player,
                                                                            auto_position=True))

                node_align_to_defense_wall.connect_to(node_position_pass, when=self.game_state.field.is_ball_in_our_goal)
                node_position_pass.connect_to(node_align_to_defense_wall, when=self.game_state.field.is_ball_outside_our_goal)

    @classmethod
    def required_roles(cls):
        return {r: keep_prev_mapping_otherwise_random for r in [Role.GOALKEEPER,
                                                                Role.FIRST_ATTACK,
                                                                Role.FIRST_DEFENCE]
                }

    @classmethod
    def optional_roles(cls):
        return {r: keep_prev_mapping_otherwise_random for r in [Role.SECOND_ATTACK,
                                                                Role.MIDDLE,
                                                                Role.SECOND_DEFENCE]
                }

    def should_go_kick(self, player):
        if self.game_state.field.is_ball_in_our_goal():
            return False
        # If no defenser can exit wall to kick
        for r in self.DEFENSIVE_ROLE:
            p = self.assigned_roles[r]
            if (p.position - self.game_state.ball.position).norm < FETCH_BALL_ZONE_RADIUS:
                return False
        # And no attacker is closer
        dist_to_ball = (player.position - self.game_state.ball.position).norm
        for p in self.attackers:
            if p != player and (p.position - self.game_state.ball.position).norm < dist_to_ball:
                return False
        return True

    def should_not_go_kick(self, player):
        return not self.should_go_kick(player)

    def has_kicked(self, role):
        if self.roles_graph[role].current_tactic_name == 'GoKick':
            return self.roles_graph[role].current_tactic.status_flag == Flags.SUCCESS
        else:
            return False
