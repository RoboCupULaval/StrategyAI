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

DEFENSIVE_ROLE = [Role.FIRST_DEFENCE, Role.SECOND_DEFENCE]
COVER_ROLE = [Role.MIDDLE]

# noinspection PyMethodMayBeStatic,
class DefenseWall(Strategy):

    def __init__(self, game_state: GameState, can_kick=True):
        super().__init__(game_state)

        their_goal = self.game_state.field.their_goal_pose

        # If we can not kick, the attackers are part of the defense wall
        # TODO find a more useful thing to do for the attackers when we are in a no kick state
        self.defensive_role = DEFENSIVE_ROLE.copy()
        self.cover_role = COVER_ROLE.copy()
        if not can_kick:
            self.defensive_role += [Role.FIRST_ATTACK]
            self.cover_role += [Role.SECOND_ATTACK]

        self.robots_in_wall_formation = [p for r, p in self.assigned_roles.items() if r in self.defensive_role]
        self.robots_in_cover_formation = [p for r, p in self.assigned_roles.items() if r in self.cover_role]
        self.attackers = [p for r, p in self.assigned_roles.items() if r not in self.defensive_role and
                          r not in self.cover_role and
                          r != Role.GOALKEEPER]
        self.player_to_cover = self.get_player_to_cover()
        for role, player in self.assigned_roles.items():
            if role == Role.GOALKEEPER:
                self.create_node(Role.GOALKEEPER, GoalKeeper(self.game_state, player))
            elif can_kick and player in self.attackers:
                node_position_pass = self.create_node(role, PositionForPass(self.game_state,
                                                                            player,
                                                                            robots_in_formation=self.attackers,
                                                                            auto_position=True))
                node_go_kick = self.create_node(role, GoKick(self.game_state, player, target=their_goal))

                attacker_should_go_kick = partial(self.should_go_kick, player)
                attacker_should_not_go_kick = partial(self.should_not_go_kick, player)
                attacker_has_kicked = partial(self.has_kicked, role)

                node_position_pass.connect_to(node_go_kick, when=attacker_should_go_kick)
                node_go_kick.connect_to(node_position_pass, when=attacker_should_not_go_kick)
                node_go_kick.connect_to(node_go_kick, when=attacker_has_kicked)
            elif role in self.cover_role:
                for coverer, enemy_to_block in self.player_to_cover:
                    if coverer is player:
                        node_align_to_covered_object = self.create_node(role,
                                                                        AlignToDefenseWall(self.game_state,
                                                                                           coverer,
                                                                                           robots_in_formation=[coverer],
                                                                                           object_to_block=enemy_to_block))
                        node_position_pass = self.create_node(role, PositionForPass(self.game_state,
                                                                                    coverer,
                                                                                    auto_position=True))
                        node_align_to_covered_object.connect_to(node_position_pass,
                                                                when=self.game_state.field.is_ball_in_our_goal_area)
                        node_position_pass.connect_to(node_align_to_covered_object,
                                                      when=self.game_state.field.is_ball_outside_our_goal_area)
            else:
                node_align_to_defense_wall = \
                    self.create_node(role, AlignToDefenseWall(self.game_state,
                                                              player,
                                                              robots_in_formation=self.robots_in_wall_formation,
                                                              object_to_block=GameState().ball))
                node_position_pass = self.create_node(role, PositionForPass(self.game_state,
                                                                            player,
                                                                            robots_in_formation=self.robots_in_formation,
                                                                            auto_position=True))

                node_align_to_defense_wall.connect_to(node_position_pass, when=self.game_state.field.is_ball_in_our_goal_area)
                node_position_pass.connect_to(node_align_to_defense_wall, when=self.game_state.field.is_ball_outside_our_goal_area)


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
        if self.game_state.field.is_ball_in_our_goal_area():
            return False
        # If no defenser can exit wall to kick
        for p in self.robots_in_wall_formation:
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

    def get_player_to_cover(self):
        closest_enemy_to_ball = closest_players_to_point(GameState().ball_position, our_team=False)

        closest_enemies_to_our_goal = closest_players_to_point(self.game_state.field.our_goal, our_team=False)

        number_of_covering_players = len(self.robots_in_cover_formation)

        result = []
        i = 0
        for enemy in closest_enemies_to_our_goal:
            if enemy is not closest_enemy_to_ball:
                result += [(self.robots_in_cover_formation[i], enemy.player)]
                i += 1
            if len(result) == number_of_covering_players:
                break

        return result
