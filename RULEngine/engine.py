# Under MIT License, see LICENSE.txt

import logging
import os
import sys
from multiprocessing import Process, Queue, Manager
from multiprocessing.managers import DictProxy

from queue import Full
from time import time, sleep


from RULEngine.Communication.receiver.uidebug_command_receiver import UIDebugCommandReceiver
from RULEngine.Communication.receiver.vision_receiver import VisionReceiver
from RULEngine.Communication.receiver.referee_receiver import RefereeReceiver

from RULEngine.Communication.sender.robot_command_sender import RobotCommandSender
from RULEngine.Communication.sender.uidebug_command_sender import UIDebugCommandSender

from RULEngine.Debug.uidebug_command_factory import UIDebugCommandFactory

from RULEngine.controller import Controller
from RULEngine.tracker import Tracker

try:
    from Util.csv_plotter import CsvPlotter
except:
    print("Fail to import csv_plotter. It will be disable.")
    from RULEngine.controller import Observer as CsvPlotter

from config.config_service import ConfigService

__author__ = "Maxime Gagnon-Legault and Simon Bouchard"


class Engine(Process):

    ROBOT_COMMAND_SENDER_QUEUE_MAXSIZE = 1
    UI_DEBUG_COMMAND_SENDER_QUEUE_MAXSIZE = 100
    UI_DEBUG_COMMAND_RECEIVER_QUEUE_MAXSIZE = 100
    REFEREE_QUEUE_MAXSIZE = 100
    FPS = 60
    NUM_CAMERA = 4

    def __init__(self,
                 game_state: DictProxy,
                 ai_queue: Queue,
                 referee_queue: Queue,
                 ui_send_queue: Queue,
                 ui_recv_queue: Queue):
        super(Engine, self).__init__(name=__name__)

        self.logger = logging.getLogger('Engine')
        self.cfg = ConfigService()
        self.team_color = self.cfg.config_dict['GAME']['our_color']

        manager = Manager()
        self.vision_state = manager.list([manager.dict() for _ in range(Engine.NUM_CAMERA)])

        self.ui_send_queue = ui_send_queue
        self.ui_recv_queue = ui_recv_queue
        self.ai_queue = ai_queue
        self.referee_queue = referee_queue
        self.game_state = game_state
        self.robot_cmd_queue = Queue()

        # vision subprocess
        vision_connection_info = (self.cfg.config_dict['COMMUNICATION']['vision_udp_address'],
                                  int(self.cfg.config_dict['COMMUNICATION']['vision_port']))

        self.vision_receiver = VisionReceiver(vision_connection_info, self.vision_state)

        # UIDebug communication subprocesses
        ui_debug_host = self.cfg.config_dict['COMMUNICATION']['ui_debug_address']
        ui_sender_connection_info = (ui_debug_host, int(self.cfg.config_dict['COMMUNICATION']['ui_cmd_sender_port']))
        ui_recver_connection_info = (ui_debug_host, int(self.cfg.config_dict['COMMUNICATION']['ui_cmd_receiver_port']))

        self.ui_sender = UIDebugCommandSender(ui_sender_connection_info, self.ui_send_queue)
        self.ui_recver = UIDebugCommandReceiver(ui_recver_connection_info, self.ui_recv_queue)

        # Referee communication
        referee_recver_connection_info = ( self.cfg.config_dict['COMMUNICATION']['referee_udp_address'],
                                           int(self.cfg.config_dict['COMMUNICATION']['referee_port']))
        self.referee_recver = RefereeReceiver(referee_recver_connection_info, self.referee_queue)

        # Subprocess to send robot commands
        robot_connection_info = (self.cfg.config_dict['COMMUNICATION']['vision_udp_address'], 20011)

        self.robot_cmd_sender = RobotCommandSender(robot_connection_info, self.robot_cmd_queue)

        self.tracker = Tracker(self.vision_state)
        self.controller = Controller(self.ai_queue, CsvPlotter)

        # print framerate
        self.framecount = 0
        self.time_last_print = time()

        self.vision_receiver.start()
        self.ui_sender.start()
        self.ui_recver.start()
        self.referee_recver.start()
        self.robot_cmd_sender.start()

    def run(self):
        own_pid = os.getpid()
        self.logger.debug('Running with process ID {}'.format(own_pid))

        try:
            while True:

                start = time()

                game_state = self.tracker.update()
                self.game_state.update(game_state)
                robot_packets_frame = self.controller.execute(self.game_state)

                try:
                    self.robot_cmd_queue.put_nowait(robot_packets_frame)
                except Full:
                    pass

                self.tracker.predict(robot_packets_frame.packet)

                self.ui_send_queue.put_nowait(UIDebugCommandFactory.game_state(self.game_state))
                self.ui_send_queue.put_nowait(UIDebugCommandFactory.robots_path(self.controller))

                self.print_framerate()

                sleep_time = max(1/Engine.FPS - (time() - start), 0)
                if sleep_time > 0:
                    sleep(sleep_time)

        except KeyboardInterrupt:
            pass
        finally:
            self.logger.info('Killed')

        sys.stdout.flush()
        exit(0)

    def is_any_subprocess_borked(self):
        borked_process_found = not self.vision_receiver.is_alive() or \
                               not self.ui_sender.is_alive() or \
                               not self.ui_recver.is_alive() or \
                               not self.robot_cmd_sender.is_alive()
        return borked_process_found

    def terminate_subprocesses(self):
        self.vision_receiver.terminate()
        self.ui_sender.terminate()
        self.ui_recver.terminate()
        self.robot_cmd_sender.terminate()

    def print_framerate(self):
        self.framecount += 1
        dt = time() - self.time_last_print
        if dt > 2:
            self.logger.info('Updating at {:.2f} fps'.format(self.framecount / dt))
            self.time_last_print = time()
            self.framecount = 0
