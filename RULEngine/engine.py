
import logging
import sys
from multiprocessing import Process, Queue, Event
from time import sleep

from RULEngine.Communication.receiver.uidebug_command_receiver import UIDebugCommandReceiver
from RULEngine.Communication.receiver.vision_receiver import VisionReceiver
from RULEngine.Communication.sender.robot_command_sender import RobotCommandSender
from RULEngine.Communication.sender.uidebug_command_sender import UIDebugCommandSender
from RULEngine.controller import Controller
from RULEngine.tracker import Tracker
from config.config_service import ConfigService


class Engine(Process):
    VISION_QUEUE_MAXSIZE = 20
    ROBOT_COMMAND_SENDER_QUEUE_MAXSIZE = 24
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

        self.tracker = None
        self.controller = None

        self.vision_receiver = None
        self.robot_cmd_sender = None
        self.ui_sender = None
        self.ui_recver = None

    def _initialize_subprocess(self):

        vision_connection_info = (self.cfg.config_dict['COMMUNICATION']['vision_udp_address'],
                                  int(self.cfg.config_dict['COMMUNICATION']['vision_port']))
        self.vision_receiver = VisionReceiver(vision_connection_info, self.vision_queue, self.stop_event)

        ui_sender_connection_info = ('127.0.0.1', int(self.cfg.config_dict['COMMUNICATION']['ui_cmd_sender_port']))
        self.ui_sender = UIDebugCommandSender(ui_sender_connection_info, self.ui_send_queue, self.stop_event)

        ui_recver_connection_info = ('127.0.0.1', 12345)  # TODO set the port in the config file
        self.ui_recver = UIDebugCommandReceiver(ui_recver_connection_info, self.ui_recv_queue, self.stop_event)

        robot_connection_info = ('127.0.0.1', 12346)  # TODO set the port in the config file
        self.robot_cmd_sender = RobotCommandSender(robot_connection_info, self.robot_cmd_queue, self.stop_event)

        self.tracker = Tracker(self.vision_queue)
        self.controller = Controller(self.ai_queue)

        self.vision_receiver.start()
        self.ui_sender.start()
        self.ui_recver.start()

        self.logger.debug('has initialized.')

    def loop(self):
        while not self.stop_event.is_set():

            track_frame = self.tracker.execute()
            self.game_state_queue.put(track_frame)

            self.controller.update(track_frame[self.team_color])
            commands = self.controller.execute()
            
            self.robot_cmd_queue.put(commands)

            sleep(0)

    def run(self):
        self._initialize_subprocess()
        try:
            self.loop()
        except KeyboardInterrupt:
            pass
        sys.stdout.flush()
        self.stop()
        exit(0)

    def stop(self):
        self.vision_receiver.join(0.3)  # timeout needed for some reason even though the process exit gracefully
        self.logger.debug('VisionReceiver joined now is -> {0}'.
                          format('alive' if self.vision_receiver.is_alive() else 'dead'))
        self.ui_sender.join(0.3)
        logging.debug('UIDebugSender joined now is -> {0}'.
                      format('alive' if self.ui_sender.is_alive() else 'dead'))
        self.ui_recver.join(0.3)
        logging.debug('UIDebugReceiver joined now is -> {0}'.
                      format('alive' if self.ui_recver.is_alive() else 'dead'))
