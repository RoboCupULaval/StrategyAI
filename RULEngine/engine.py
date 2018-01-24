
import logging
import sys
from collections import namedtuple
from multiprocessing import Process, Queue, Event
from queue import Full

from RULEngine.Communication.receiver.uidebug_command_receiver import UIDebugCommandReceiver
from RULEngine.Communication.receiver.vision_receiver import VisionReceiver
from RULEngine.Communication.sender.robot_command_sender import RobotCommandSender
from RULEngine.Communication.sender.uidebug_command_sender import UIDebugCommandSender
from RULEngine.Debug.uidebug_command_factory import UIDebugCommandFactory

from RULEngine.controller import Controller
from RULEngine.tracker import Tracker

from config.config_service import ConfigService


class AICommand(namedtuple('AICommand', 'robot_id target kick_type kick_force dribbler_active')):

    __slots__ = ()

    def __new__(cls, robot_id, target=None, kick_type=None, kick_force=0, dribbler_active=False, command=None):
        return super().__new__(cls, robot_id, target, kick_type, kick_force, dribbler_active)


class Engine(Process):
    VISION_QUEUE_MAXSIZE = 4
    ROBOT_COMMAND_SENDER_QUEUE_MAXSIZE = 100
    UI_DEBUG_COMMAND_SENDER_QUEUE_MAXSIZE = 100
    UI_DEBUG_COMMAND_RECEIVER_QUEUE_MAXSIZE = 100
    REFEREE_QUEUE_MAXSIZE = 100

    def __init__(self, game_state_queue: Queue, ai_queue: Queue, ui_send_queue: Queue, ui_recv_queue: Queue, stop_event: Event):
        super(Engine, self).__init__(name=__name__)

        self.logger = logging.getLogger('Engine')
        self.cfg = ConfigService()
        self.team_color = self.cfg.config_dict['GAME']['our_color']
        self.stop_event = stop_event

        self.vision_queue = Queue(self.VISION_QUEUE_MAXSIZE)
        self.ui_send_queue = ui_send_queue
        self.ui_recv_queue = ui_recv_queue
        self.ai_queue = ai_queue
        self.game_state_queue = game_state_queue
        self.robot_cmd_queue = Queue()

        vision_connection_info = (self.cfg.config_dict['COMMUNICATION']['vision_udp_address'],
                                  int(self.cfg.config_dict['COMMUNICATION']['vision_port']))

        self.vision_receiver = VisionReceiver(vision_connection_info, self.vision_queue, self.stop_event)

        ui_debug_host = self.cfg.config_dict['COMMUNICATION']['ui_debug_address']
        ui_sender_connection_info = (ui_debug_host, int(self.cfg.config_dict['COMMUNICATION']['ui_cmd_sender_port']))
        ui_recver_connection_info = (ui_debug_host, int(self.cfg.config_dict['COMMUNICATION']['ui_cmd_receiver_port']))

        self.ui_sender = UIDebugCommandSender(ui_sender_connection_info, self.ui_send_queue, self.stop_event)
        self.ui_recver = UIDebugCommandReceiver(ui_recver_connection_info, self.ui_recv_queue, self.stop_event)

        robot_connection_info = (self.cfg.config_dict['COMMUNICATION']['vision_udp_address'], 20011)

        self.robot_cmd_sender = RobotCommandSender(robot_connection_info, self.robot_cmd_queue, self.stop_event)

        self.tracker = Tracker(self.vision_queue)
        self.controller = Controller(self.ai_queue)

        self.vision_receiver.start()
        self.ui_sender.start()
        self.ui_recver.start()
        self.robot_cmd_sender.start()

    def run(self):

        self.logger.debug('Running')

        self.ai_queue.put([AICommand(robot_id=0, target={'x': -4200, 'y': 0, 'orientation': 0}),
                           AICommand(robot_id=1, target={'x': -90, 'y': -2000, 'orientation': 0}),
                           AICommand(robot_id=2, target={'x': -90, 'y': -1000, 'orientation': 0}),
                           AICommand(robot_id=3, target={'x': -590, 'y': 0, 'orientation': 0}),
                           AICommand(robot_id=4, target={'x': -90, 'y': 1000, 'orientation': 0}),
                           AICommand(robot_id=5, target={'x': -90, 'y': 2000, 'orientation': 0})])

        try:
            while not self.stop_event.is_set():

                track_frame = self.tracker.update()
                robot_packets_frame = self.controller.execute(track_frame)
                self.robot_cmd_queue.put(robot_packets_frame)
                self.tracker.predict(robot_packets_frame.packet)

                self.follow_ball(track_frame, robot_id=0)
                self.ui_send_queue.put(UIDebugCommandFactory().track_frame(track_frame))

        except KeyboardInterrupt:
            pass
        finally:
            self.logger.info('Killed')

        sys.stdout.flush()
        exit(0)

    def follow_ball(self, track_frame, robot_id):
        if track_frame['balls']:
            ball_pose = track_frame['balls'][0]['pose']
            ball_pose['orientation'] = 0
            self.ai_queue.put([AICommand(robot_id=robot_id, target=ball_pose)])
        try:
            self.game_state_queue.put(track_frame, block=False)
        except Full:
            pass


