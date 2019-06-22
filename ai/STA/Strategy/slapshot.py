# Under MIT License, see LICENSE.txt

from functools import partial

from Util import Pose, Position
from Util.constant import KickForce
from Util.role import Role
from ai.Algorithm.evaluation_module import closest_players_to_point, ball_going_toward_player, \
    ball_not_going_toward_player
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.go_kick_aggressive import GoKickAggressive
from ai.STA.Tactic.go_kick_adaptative import GoKickAdaptative
from ai.STA.Tactic.go_to_position import GoToPosition
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.STA.Tactic.position_for_pass import PositionForPass
from ai.STA.Tactic.receive_pass import ReceivePass
from ai.STA.Tactic.stop import Stop
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState


# noinspection PyMethodMayBeStatic,PyMethodMayBeStatic
class SlapShot(Strategy):

    def __init__(self, p_game_state, can_kick_in_goal=True):
        super().__init__(p_game_state)
        self.player_1_pose = Pose(Position(-1000, 1000), 0)
        self.player_2_pose = Pose(Position(0, -200), 0)
        self.ball_position_start = self.player_1_pose.position + Position(500, 0)


        formation = [p for r, p in self.assigned_roles.items() if r != Role.GOALKEEPER]

        initial_position_for_pass_center = {}
        for role, player in self.assigned_roles.items():
            if role == Role.GOALKEEPER:
                self.create_node(Role.GOALKEEPER, GoalKeeper(self.game_state, player))
            elif role == Role.FIRST_ATTACK:
                node_go_to_position = self.create_node(role, GoToPosition(self.game_state, player,
                                                                          self.player_1_pose))
                node_go_kick = self.create_node(role, GoKick(self.game_state,
                                                             player,
                                                             target=Pose(Position(2000, 0), 0),
                                                             kick_force=KickForce.LOW))
                all_player_ready = partial(self.all_player_ready, player)
                has_kicked = partial(self.has_kicked, player)

                node_go_to_position.connect_to(node_go_kick, when=all_player_ready)
                node_go_kick.connect_to(node_go_to_position, when=has_kicked)

            elif role == Role.SECOND_ATTACK:
                node_go_to_position = self.create_node(role, GoToPosition(self.game_state, player,
                                                                          self.player_2_pose))
                node_go_kick = self.create_node(role, GoKickAdaptative(self.game_state, player, target=Pose(Position(4000, 0), 0)))
                node_go_kick_aggressive = self.create_node(role, GoKickAdaptative(self.game_state,
                                                                                  player,
                                                                                  target=Pose(Position(4000, 0), 0),
                                                                                  kick_force=KickForce.HIGH))
                all_player_ready = partial(self.all_player_ready, player)
                has_kicked = partial(self.has_kicked, player)
                ball_open = partial(self.is_ball_open)

                node_go_to_position.connect_to(node_go_kick_aggressive, when=has_kicked)
                node_go_to_position.connect_to(node_go_kick_aggressive, when=has_kicked)
                node_go_kick.connect_to(node_go_kick_aggressive, when=ball_open)


    @classmethod
    def required_roles(cls):
        return [Role.GOALKEEPER,
                Role.FIRST_ATTACK,
                Role.SECOND_ATTACK]

    @classmethod
    def optional_roles(cls):
        return [Role.FIRST_DEFENCE,
                Role.MIDDLE,
                Role.SECOND_DEFENCE]

    def all_player_ready(self, player):

        role = GameState().get_role_by_player_id(player.id)
        if role == Role.FIRST_ATTACK:
            player1 = GameState().get_player_by_role(Role.FIRST_ATTACK)
            player2 = GameState().get_player_by_role(Role.SECOND_ATTACK)
            if ((player1.position -self.player_1_pose.position).norm < 100) and ((player2.position -
                                                                         self.player_2_pose.position).norm < 100):
                if (GameState().ball_position - self.ball_position_start).norm < 500:

                    return True
            print("wow")
            return False

        closest_players = closest_players_to_point(GameState().ball_position, our_team=True)
        if player == closest_players[0].player:
            return True
        return closest_players[0].player == self.game_state.get_player_by_role(Role.GOALKEEPER) \
               and player == closest_players[1].player

    def has_kicked(self, player):
        return GameState().ball.is_mobile()

    def is_ball_open(self):
        if abs(self.game_state.ball_position[0])<self.game_state.field.field_length/2 and \
                abs(self.game_state.ball_position[1])<self.game_state.field.field_width/2:
            return True
        return False
