# Under MIT license, see LICENSE.txt

# TODO: Create a new UT for the new IA command
#
# import unittest
# from unittest.mock import Mock
#
# from RULEngine.Game.Player import Player
#
# from Util import AICommand, AICommandType, AIControlLoopType, _default_keys, _keys_type
# from Util import pose
# from Util import velocity
# from Util.pose import Pose
# from Util.velocity import Velocity
#
#
# class AICommandTestCase(unittest.TestCase):
#
#     def setUp(self):
#         self.robot_id = 1
#         self.player = Mock(return_value=None, id=self.robot_id, spec=Player)
#
#         self.STOP = AICommandType.STOP
#         self.MOVE = AICommandType.MOVE
#
#         self.OPEN = AIControlLoopType.OPEN
#         self.SPEED = AIControlLoopType.SPEED
#         self.POSITION = AIControlLoopType.POSITION
#
#         pose = Mock(return_value=None, spec=Pose)
#         speed_pose = Mock(return_value=None, spec=Velocity)
#         self.new_keys = {
#             'dribbler_on': True,
#             'pathfinder_on': True,
#             'kick_strength': 10,
#             'charge_kick': True,
#             'kick': True,
#             'pose_goal': pose,
#             'speed': speed_pose,
#             'cruise_speed': 1,
#             'end_speed': 0,
#             'collision_ball': False,
#             'control_loop_type': self.OPEN,
#             'path': [1, 2, 3],
#             'path_speeds': [1, 1, 0],
#         }
#
#
# class AICommandDefaultKeysTest(unittest.TestCase):
#
#     def test_default_keys_type(self):
#         for key, val in _default_keys.items():
#             if val is not None:
#                 self.assertIsInstance(val, _keys_type[key])
#
#
# class AICommandInitTest(AICommandTestCase):
#
#     def test_no_arg(self):
#         with self.assertRaises(TypeError):
#             AICommand()
#
#     def test_bad_player(self):
#         with self.assertRaises(TypeError):
#             bad_player = Mock(return_value=None)
#             AICommand(bad_player)
#
#     def test_bad_command_type(self):
#         with self.assertRaises(TypeError):
#             AICommand(self.player, self.SPEED)
#
#     def test_default(self):
#         ai_cmd = AICommand(self.player)
#         self.assertEqual(self.player, ai_cmd.player)
#         self.assertEqual(self.robot_id, ai_cmd.robot_id)
#         self.assertEqual(self.STOP, ai_cmd.command)
#
#     def test_2_args(self):
#         ai_cmd = AICommand(self.player, self.MOVE)
#         self.assertEqual(self.robot_id, ai_cmd.robot_id)
#         self.assertEqual(self.MOVE, ai_cmd.command)
#
#     def test_3_args(self):
#         with self.assertRaises(TypeError):
#             AICommand(self.player, self.MOVE, 1)
#
#     def test_good_kwargs(self):
#         ai_cmd = AICommand(self.player, **self.new_keys)
#         self.assertEqual(self.player, ai_cmd.player)
#         self.assertEqual(self.robot_id, ai_cmd.robot_id)
#         self.assertEqual(self.STOP, ai_cmd.command)
#
#         for key, val in self.new_keys.items():
#             self.assertEqual(ai_cmd[key], val)
#
#     def test_bad_kwargs_value(self):
#         self.new_keys['kick_strength'] = '1'
#         with self.assertRaises(TypeError):
#             AICommand(self.player, **self.new_keys)
#
#     def test_bad_kwargs_key(self):
#         self.new_keys['kick_strenght'] = 5
#         with self.assertRaises(KeyError):
#             AICommand(self.player, **self.new_keys)
#
#
# class AICommandGetSetTest(AICommandTestCase):
#
#     def test_set_attr(self):
#         ai_cmd = AICommand(self.player, self.MOVE)
#         ai_cmd.command_type = self.STOP
#         self.assertEqual(ai_cmd.command_type, self.STOP)
#         ai_cmd.command_type = self.MOVE
#         self.assertEqual(ai_cmd.command_type, self.MOVE)
#
#     def test_locked_keys(self):
#         ai_cmd = AICommand(self.player)
#         with self.assertRaises(KeyError):
#             ai_cmd.player = ()
#
# if __name__ == '__main__':
#     unittest.main()
