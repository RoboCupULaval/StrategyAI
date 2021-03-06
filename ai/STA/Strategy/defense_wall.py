# Under MIT license, see LICENSE.txt
from functools import partial
from itertools import cycle

import numpy as np

from Util.geometry import normalize
from Util.role import Role

from ai.Algorithm.evaluation_module import closest_players_to_point, ball_not_going_toward_player, \
    ball_going_toward_player
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.align_to_defense_wall import AlignToDefenseWall, FETCH_BALL_ZONE_RADIUS
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.go_kick_3way import GoKick3Way
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.STA.Tactic.position_for_pass import PositionForPass
from ai.STA.Tactic.receive_pass import ReceivePass
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState

DEFENSIVE_ROLE = [Role.FIRST_DEFENCE, Role.SECOND_DEFENCE]
COVER_ROLE = [Role.MIDDLE]


# noinspection PyMethodMayBeStatic,
class DefenseWall(Strategy):

    def __init__(self, game_state: GameState, can_kick=True, multiple_cover=True, stay_away_from_ball=False):
        super().__init__(game_state)

        their_goal = self.game_state.field.their_goal_pose

        # If we can not kick, the attackers are part of the defense wall
        # TODO find a more useful thing to do for the attackers when we are in a no kick state
        self.can_kick = can_kick
        self.multiple_cover = multiple_cover
        self.defensive_role = DEFENSIVE_ROLE.copy()
        self.cover_role = COVER_ROLE.copy()

        self.robots_in_wall_formation = []
        self.robots_in_cover_formation = []
        self.attackers = []
        self.cover_to_coveree = {}
        self.cover_to_formation = {}

        self._dispatch_player()

        for role, player in self.assigned_roles.items():
            if role == Role.GOALKEEPER:
                self.create_node(Role.GOALKEEPER, GoalKeeper(self.game_state, player))
            elif player in self.attackers:
                node_position_pass = self.create_node(role, PositionForPass(self.game_state,
                                                                            player,
                                                                            robots_in_formation=self.attackers,
                                                                            auto_position=True))
                node_go_kick = self.create_node(role, GoKick3Way(self.game_state, player, auto_update_target=True)) # target=their_goal
                node_wait_for_pass = self.create_node(role, ReceivePass(self.game_state, player))

                attacker_should_go_kick = partial(self.should_go_kick, player)
                attacker_should_not_go_kick = partial(self.should_not_go_kick, player)
                attacker_has_kicked = partial(self.has_kicked, role)
                player_is_receiving_pass = partial(ball_going_toward_player, game_state, player)
                player_is_not_receiving_pass = partial(ball_not_going_toward_player, game_state, player)
                player_has_received_ball = partial(self.has_received, player)

                node_position_pass.connect_to(node_wait_for_pass, when=player_is_receiving_pass)
                node_position_pass.connect_to(node_go_kick, when=attacker_should_go_kick)
                node_wait_for_pass.connect_to(node_go_kick, when=player_has_received_ball)
                node_wait_for_pass.connect_to(node_position_pass, when=player_is_not_receiving_pass)
                # node_go_kick.connect_to(node_wait_for_pass, when=player_is_receiving_pass)
                node_go_kick.connect_to(node_position_pass, when=attacker_should_not_go_kick)
                node_go_kick.connect_to(node_go_kick, when=attacker_has_kicked)
            elif role in self.cover_role:
                enemy_to_block = self.cover_to_coveree[player]
                formation = self.cover_to_formation[player]
                node_align_to_covered_object = self.create_node(role,
                                                                AlignToDefenseWall(self.game_state,
                                                                                   player,
                                                                                   robots_in_formation=formation,
                                                                                   object_to_block=enemy_to_block,
                                                                                   stay_away_from_ball=stay_away_from_ball))
                node_position_pass = self.create_node(role, PositionForPass(self.game_state,
                                                                            player,
                                                                            robots_in_formation=self.robots_in_cover_formation,
                                                                            auto_position=True))

                node_go_kick = self.create_node(role, GoKick3Way(self.game_state, player, target=their_goal, auto_update_target=True))
                node_wait_for_pass = self.create_node(role, ReceivePass(self.game_state, player))

                player_is_receiving_pass = partial(ball_going_toward_player, game_state, player)
                player_is_not_receiving_pass = partial(ball_not_going_toward_player, game_state, player)
                player_has_received_ball = partial(self.has_received, player)
                player_has_kicked = partial(self.has_kicked, role)

                node_align_to_covered_object.connect_to(node_position_pass,
                                                        when=self.game_state.field.is_ball_in_our_goal_area)
                node_position_pass.connect_to(node_align_to_covered_object,
                                              when=self.game_state.field.is_ball_outside_our_goal_area)
                node_wait_for_pass.connect_to(node_go_kick, when=player_has_received_ball)
                node_wait_for_pass.connect_to(node_align_to_covered_object, when=player_is_not_receiving_pass)
                node_position_pass.connect_to(node_wait_for_pass, when=player_is_receiving_pass)
                node_go_kick.connect_to(node_align_to_covered_object, when=player_has_kicked)
            else:
                node_align_to_defense_wall = \
                    self.create_node(role, AlignToDefenseWall(self.game_state,
                                                              player,
                                                              robots_in_formation=self.robots_in_wall_formation,
                                                              object_to_block=GameState().ball,
                                                              stay_away_from_ball=stay_away_from_ball))
                node_position_pass = self.create_node(role, PositionForPass(self.game_state,
                                                                            player,
                                                                            robots_in_formation=self.robots_in_wall_formation,
                                                                            auto_position=True))

                node_go_kick = self.create_node(role, GoKick(self.game_state, player, target=their_goal))
                node_wait_for_pass = self.create_node(role, ReceivePass(self.game_state, player))

                player_is_receiving_pass = partial(ball_going_toward_player, game_state, player)
                player_is_not_receiving_pass = partial(ball_not_going_toward_player, game_state, player)
                player_has_received_ball = partial(self.has_received, player)
                player_has_kicked = partial(self.has_kicked, role)

                node_align_to_defense_wall.connect_to(node_position_pass, when=self.game_state.field.is_ball_in_our_goal_area)
                node_position_pass.connect_to(node_align_to_defense_wall, when=self.game_state.field.is_ball_outside_our_goal_area)

                node_wait_for_pass.connect_to(node_go_kick, when=player_has_received_ball)
                node_wait_for_pass.connect_to(node_position_pass, when=self.game_state.field.is_ball_in_our_goal_area)
                node_go_kick.connect_to(node_position_pass, when=self.game_state.field.is_ball_in_our_goal_area)
                node_go_kick.connect_to(node_align_to_defense_wall, when=player_has_kicked)
                node_position_pass.connect_to(node_wait_for_pass, when=player_is_receiving_pass)
                # node_position_pass.connect_to(node_align_to_defense_wall, when=player_is_not_receiving_pass)


    @classmethod
    def required_roles(cls):
        return [Role.GOALKEEPER,
                Role.FIRST_ATTACK,
                Role.FIRST_DEFENCE]

    @classmethod
    def optional_roles(cls):
        return [Role.SECOND_ATTACK,
                Role.MIDDLE,
                Role.SECOND_DEFENCE]

    def should_go_kick(self, player):
        if self.game_state.field.is_ball_in_our_goal_area():
            return False
        # Player can go kick
        ban_players = self.game_state.double_touch_checker.ban_players
        if player in ban_players:
            return False
        # If no defenser can exit wall to kick
        for p in self.robots_in_wall_formation:
            if (p.position - self.game_state.ball.position).norm < FETCH_BALL_ZONE_RADIUS:
                return False
        # And no attacker is closer
        dist_to_ball = (player.position - self.game_state.ball.position).norm
        for p in self.attackers:
            if p not in ban_players and p != player and (p.position - self.game_state.ball.position).norm < dist_to_ball:
                return False
        return True

    def should_not_go_kick(self, player):
        return not self.should_go_kick(player)

    def has_kicked(self, role):
        if self.roles_graph[role].current_tactic_name == 'GoKick':
            return self.roles_graph[role].current_tactic.status_flag == Flags.SUCCESS
        else:
            return False

    def _remove_not_available_roles(self, unfiltered_roles):
        return [r for r in unfiltered_roles if r in self.assigned_roles.keys()]

    def _dispatch_player(self):

        if not self.can_kick and self.multiple_cover:
            self.defensive_role += [Role.FIRST_ATTACK]
            self.cover_role += [Role.SECOND_ATTACK]
        if not self.can_kick and not self.multiple_cover:
            self.defensive_role += [Role.FIRST_ATTACK, Role.SECOND_ATTACK]
        self.defensive_role = self._remove_not_available_roles(self.defensive_role)
        self.cover_role = self._remove_not_available_roles(self.cover_role)

        self.robots_in_wall_formation = [p for r, p in self.assigned_roles.items() if r in self.defensive_role]
        self.robots_in_cover_formation = [p for r, p in self.assigned_roles.items() if r in self.cover_role]
        self.attackers = [p for r, p in self.assigned_roles.items() if r not in self.defensive_role and
                          r not in self.cover_role and
                          r != Role.GOALKEEPER]
        if len(self.game_state.enemy_team.players.values()) < len(self.robots_in_cover_formation):
            self.robots_in_wall_formation += self.robots_in_cover_formation
            self.defensive_role += self.cover_role
            self.cover_role = []
            self.robots_in_cover_formation = []
        else:
            self.cover_to_coveree, self.cover_to_formation = self._generate_cover_to_coveree_mapping()

    def _generate_cover_to_coveree_mapping(self):
        # We want to assign a coveree(enemy) to every cover(ally)
        # We also want to know for each cover(ally), the other covers that share the same target(enemy)
        closest_enemies_to_ball = closest_players_to_point(self.game_state.ball_position, our_team=False)
        if len(closest_enemies_to_ball) > 0:
            closest_enemy_to_ball = closest_enemies_to_ball[0].player
            closest_enemies_to_our_goal = closest_players_to_point(self.game_state.field.our_goal, our_team=False)
            enemy_not_with_ball = [enemy.player for enemy in closest_enemies_to_our_goal if enemy.player is not closest_enemy_to_ball]
        else:
            enemy_not_with_ball = []

        # If we don't have enough player we cover the ball
        if len(enemy_not_with_ball) == 0:
            cover_to_coveree = dict(zip(self.robots_in_cover_formation, cycle([self.game_state.ball])))
            cover_to_formation = {cover: self.robots_in_cover_formation for cover in self.robots_in_cover_formation}
            # If we don't have enough enemy to cover, we group the player in formation
        elif len(self.robots_in_cover_formation) > len(enemy_not_with_ball):
            cover_to_coveree = dict(zip(self.robots_in_cover_formation, cycle(enemy_not_with_ball)))
            cover_to_formation = {}
            for cover, coveree in cover_to_coveree.items():
                formation = [teamate for teamate, teamate_coveree in cover_to_coveree.items() if teamate_coveree == coveree]
                cover_to_formation[cover] = formation
        else:
            cover_to_coveree = dict(zip(self.robots_in_cover_formation, enemy_not_with_ball))
            cover_to_formation = {cover: [cover] for cover in self.robots_in_cover_formation}

        return cover_to_coveree, cover_to_formation

    def has_received(self, player):
        role = GameState().get_role_by_player_id(player.id)
        if self.roles_graph[role].current_tactic_name == 'ReceivePass':
            return self.roles_graph[role].current_tactic.status_flag == Flags.SUCCESS
        else:
            return False