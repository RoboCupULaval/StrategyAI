# Under MIT license, see LICENSE.txt

import numpy as np

from Util.geometry import wrap_to_pi
from Util.role import Role
from ai.Algorithm.evaluation_module import closest_players_to_point_except, ball_going_toward_player
from ai.GameDomainObjects import Player
from ai.STA.Strategy.graphless_strategy import GraphlessStrategy
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.STA.Tactic.position_for_pass import PositionForPass
from ai.STA.Tactic.receive_pass import ReceivePass
from ai.STA.Tactic.stay_away_from_ball import StayAwayFromBall
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState

MAX_DISTANCE_TO_SWITCH_TO_RECEIVE_PASS = 1500


class GraphlessOffense(GraphlessStrategy):

    MOVING_BALL_VELOCITY = 50  # mm/s
    DANGER_BALL_VELOCITY = 600  # mm/s

    def __init__(self, p_game_state: GameState):
        super().__init__(p_game_state)

        self.robots_in_formation = [p for r, p in self.assigned_roles.items() if r != Role.GOALKEEPER]

        for role, player in self.assigned_roles.items():
            if role is Role.GOALKEEPER:
                self.roles_to_tactics[role] = GoalKeeper(self.game_state, player)
            else:
                self.roles_to_tactics[role] = PositionForPass(self.game_state,
                                                              player,
                                                              auto_position=True,
                                                              robots_in_formation=self.robots_in_formation)
        self.next_state = self.go_get_ball

        self.current_pass_receiver = None

    def go_get_ball(self):
        for role, player in self.assigned_roles.items():
            if role == Role.GOALKEEPER:
                continue
            tactic = self.roles_to_tactics[role]
            if isinstance(tactic, GoKick):
                if not self.is_closest_not_goalkeeper(player):
                    self.logger.info(f"Robot {player.id} was not closest. Returning to PositionForPass")
                    self.roles_to_tactics[role] = PositionForPass(self.game_state,
                                                                  player,
                                                                  auto_position=True,
                                                                  robots_in_formation=self.robots_in_formation)
                elif tactic.status_flag == Flags.PASS_TO_PLAYER and self._will_probably_kick_soon(player):
                    self.logger.info(f"Robot {player.id} is passing to Robot {tactic.current_player_target.id}")
                    self._assign_target_to_receive_pass(tactic.current_player_target, passing_robot=player)

                    self.logger.info("Switching to receive_pass")
                    self.next_state = self.receive_pass
                    return  # We dont want to override self.current_pass_receiver

            elif self.is_closest_not_goalkeeper(player):
                self.logger.info(f"Robot {player.id} is closest! Switching to GoKick")
                self.roles_to_tactics[role] = GoKick(self.game_state,
                                                     player,
                                                     auto_update_target=True,
                                                     can_kick_in_goal=True)

            # Robots must not stay in receive pass if they are not receiving a pass
            elif isinstance(tactic, ReceivePass):
                self.roles_to_tactics[role] = PositionForPass(self.game_state,
                                                              player,
                                                              auto_position=True,
                                                              robots_in_formation=self.robots_in_formation)

            elif ball_going_toward_player(self.game_state, player):
                self.logger.info(f"Ball is going toward Robot {player.id}!")
                if self._ball_going_toward_goal():
                    self.logger.info(f"Robot {player.id} is blocking the ball from entering goal. Switching its tactic to stay away.")
                    self.roles_to_tactics[role] = StayAwayFromBall(self.game_state, player)
                else:
                    self._assign_target_to_receive_pass(player, passing_robot=None)
                    self.logger.info("Switching to receive_pass")
                    self.next_state = self.receive_pass

    def receive_pass(self):
        for role, player in self.assigned_roles.items():
            if role == Role.GOALKEEPER:
                continue
            tactic = self.roles_to_tactics[role]
            if isinstance(tactic, GoKick):
                gokick_target = tactic.current_player_target
                if gokick_target is not None:
                    if gokick_target != self.current_pass_receiver:
                        self.logger.info(
                            f"Robot {player.id} changed its target! Last target: Robot {self.current_pass_receiver.id}  -- New target : {gokick_target.id}")

                        self.logger.info(f"Switching Robot {self.current_pass_receiver.id} tactic to PositionForPass")
                        last_receiver_role = self.game_state.get_role_by_player_id(self.current_pass_receiver.id)

                        self.roles_to_tactics[last_receiver_role] = PositionForPass(self.game_state,
                                                                                    self.current_pass_receiver,
                                                                                    auto_position=True,
                                                                                    robots_in_formation=self.robots_in_formation)

                        self._assign_target_to_receive_pass(gokick_target, player)

                    if tactic.status_flag == Flags.SUCCESS:
                        self.logger.info(f"Robot {player.id} has kicked!")
                        receiver_role = self.game_state.get_role_by_player_id(self.current_pass_receiver.id)
                        receiver_tactic = self.roles_to_tactics[receiver_role]
                        assert isinstance(receiver_tactic, ReceivePass)
                        receiver_tactic.passing_robot_has_kicked = True

            elif isinstance(tactic, ReceivePass) and tactic.status_flag == Flags.SUCCESS:
                self.logger.info(f"Robot {player.id} has received ball!")
                self.logger.info("Switching to go_get_ball")
                self.next_state = self.go_get_ball

        if all(not isinstance(self.roles_to_tactics[role], GoKick) for role, _ in self.assigned_roles.items()):
            self.next_state = self.go_get_ball

    def _assign_target_to_receive_pass(self, target: Player, passing_robot):
        self.logger.info(f"Switching Robot {target.id} tactic to ReceivePass")
        role = self.game_state.get_role_by_player_id(target.id)
        self.roles_to_tactics[role] = ReceivePass(self.game_state, target, passing_robot=passing_robot)
        self.current_pass_receiver = target

    @classmethod
    def required_roles(cls):
        return [Role.GOALKEEPER,
                Role.FIRST_ATTACK,
                Role.MIDDLE]

    @classmethod
    def optional_roles(cls):
        return [Role.FIRST_DEFENCE,
                Role.SECOND_ATTACK,
                Role.SECOND_DEFENCE]

    def is_closest_not_goalkeeper(self, player: Player):
        ban_players = self.game_state.ban_players
        if player in ban_players:
            return False

        closests = closest_players_to_point_except(self.game_state.ball.position,
                                                   except_roles=[Role.GOALKEEPER],
                                                   except_players=ban_players)

        return len(closests) > 0 and closests[0].player == player

    def _will_probably_kick_soon(self, player: Player):
        tactic = self.roles_to_tactics[self.game_state.get_role_by_player_id(player.id)]
        assert isinstance(tactic, GoKick)

        player_to_ball_distance = (self.game_state.ball_position - player.position).norm
        is_close_to_ball = player_to_ball_distance < MAX_DISTANCE_TO_SWITCH_TO_RECEIVE_PASS
        if is_close_to_ball:
            self.logger.info("Go Kick is close to ball")

        ball_to_receiver_unit = (tactic.current_player_target.position - self.game_state.ball_position).unit
        is_approaching_ball = player.velocity.position.unit.dot(ball_to_receiver_unit) > 0.5
        if is_approaching_ball:
            self.logger.info("Go Kick is approaching the ball")

        return is_close_to_ball or is_approaching_ball

    def _ball_going_toward_goal(self):
        angle_p1 = wrap_to_pi((self.game_state.field.their_goal_line.p1 - self.game_state.ball.position).angle + np.pi)
        angle_p2 = wrap_to_pi((self.game_state.field.their_goal_line.p2 - self.game_state.ball.position).angle + np.pi)
        lower_angle = angle_p1 - 5 * np.pi / 180.0
        upper_angle = angle_p2 + 5 * np.pi / 180.0
        ball_velocity_angle = wrap_to_pi(self.game_state.ball.velocity.angle + np.pi)
        ball_speed = self.game_state.ball.velocity.norm
        return (ball_speed > self.DANGER_BALL_VELOCITY and self.game_state.ball.velocity.x < 0) or \
               (ball_speed > self.MOVING_BALL_VELOCITY and lower_angle <= ball_velocity_angle <= upper_angle)
