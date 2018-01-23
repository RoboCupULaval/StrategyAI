# # Under MIT license, see LICENSE.txt
# from typing import List
#
# import pygame
# from Util.Pose import Pose
#
# from RULEngine.GameDomainObjects.player import Player
# # from Util import AICommandType, AIControlLoopType
# from Util import Position
# # from Util import RobotJoystick
# from ai.STA.Action.AllStar import AllStar
# from ai.STA.Action.Idle import Idle
# from ai.STA.Tactic.tactic import Tactic
# from ai.STA.Tactic.tactic_constants import Flags
# from ai.states.game_state import GameState
#
#
# class Joystick(Tactic):
#     def __init__(self, game_state: GameState, player: Player, target: Pose=Pose(), args: List[str]=None):
#         super().__init__(game_state, player, target, args)
#         self.status_flag = Flags.INIT
#
#         self.inv_x = int(args[0])
#         self.inv_y = int(args[1])
#         self.joy_id = int(args[2])
#
#         self.current_state = self.handle_joystick
#         self.next_state = self.handle_joystick
#
#         pygame.init()
#         pygame.joystick.init()
#         joystick_count = pygame.joystick.get_count()
#         if int(self.joy_id) < joystick_count:
#             pygame.display.set_mode([1, 1])
#             joystick = pygame.joystick.Joystick(self.joy_id)
#             joystick.init()
#             self.joy = RobotJoystick(joystick)
#         else:
#             self.status_flag = Flags.FAILURE
#
#     def handle_joystick(self):
#         if self.status_flag is not Flags.FAILURE:
#             self.status_flag = Flags.WIP
#             pygame.event.pump()
#
#             x, y = self.joy.get_left_axis_vector()
#             _, t = self.joy.get_right_axis_vector()
#
#             if self.joy.get_btn_value("X"):
#                 charge_kick = True
#             else:
#                 charge_kick = False
#
#             if self.joy.get_btn_value("A"):
#                 kick = 4
#             else:
#                 kick = 0
#
#             if self.joy.get_btn_value("B"):
#                 dribbler = 2
#             else:
#                 dribbler = 0
#
#             if self.joy.get_btn_value("Y"):
#                 self.next_state = self.halt
#
#             x_speed = -y * self.inv_y
#             y_speed = x * self.inv_x
#
#             speed_pose = Pose(Position(x_speed, y_speed), t * 5)
#
#             if kick == 0:
#                 next_action = AllStar(self.game_state, self.player,
#                                       **{"ai_command_type": AICommandType.MOVE,
#                                          "pose_goal": speed_pose,
#                                          "control_loop_type": AIControlLoopType.SPEED,
#                                          "charge_kick": charge_kick,
#                                          "kick_strength": kick,
#                                          "dribbler_on": dribbler})
#             else:
#                 next_action = AllStar(self.game_state, self.player, **{"ai_command_type": AICommandType.KICK,
#                                                                        "kick_strength": kick})
#         else:
#             next_action = Idle(self.game_state, self.player)
#
#         return next_action
#
#     def halt(self):
#         self.status_flag = Flags.SUCCESS
#         pygame.quit()
#         return super(Joystick, self).halt()
