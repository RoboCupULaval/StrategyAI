# Under MIT License, see LICENSE.txt

import logging
import os
import sys
from multiprocessing import Process, Queue, Manager
from multiprocessing.managers import DictProxy

from queue import Empty
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
except ImportError:
    print('Fail to import csv_plotter. It will be disable.')
    from Util.csv_plotter import Observer as CsvPlotter

from config.config_service import ConfigService

__author__ = 'Maxime Gagnon-Legault and Simon Bouchard'


class Engine(Process):

    FPS = 70  # same as camera's fps! (or Frame Rate in GrSim)
    NUM_CAMERA = 4
    FIX_FRAME_RATE = True

    def __init__(self,
                 game_state: DictProxy,
                 field: DictProxy,
                 ai_queue: Queue,
                 referee_queue: Queue,
                 ui_send_queue: Queue,
                 ui_recv_queue: Queue):
        super().__init__(name=__name__)

        self.logger = logging.getLogger('Engine')
        self.cfg = ConfigService()
        self.team_color = self.cfg.config_dict['GAME']['our_color']

        # Managers for shared memory between process
        manager = Manager()
        self.vision_state = manager.list([manager.dict() for _ in range(Engine.NUM_CAMERA)])
        self.game_state = game_state
        self.field = field

        # Queues for inter process communication with the AI
        self.ui_send_queue = ui_send_queue
        self.ui_recv_queue = ui_recv_queue
        self.ai_queue = ai_queue
        self.referee_queue = referee_queue

        # vision subprocess
        vision_connection_info = (self.cfg.config_dict['COMMUNICATION']['vision_udp_address'],
                                  int(self.cfg.config_dict['COMMUNICATION']['vision_port']))

        self.vision_receiver = VisionReceiver(vision_connection_info, self.vision_state, self.field)

        # UIDebug communication sub processes
        ui_debug_host = self.cfg.config_dict['COMMUNICATION']['ui_debug_address']
        ui_sender_connection_info = (ui_debug_host, int(self.cfg.config_dict['COMMUNICATION']['ui_cmd_sender_port']))
        ui_recver_connection_info = (ui_debug_host, int(self.cfg.config_dict['COMMUNICATION']['ui_cmd_receiver_port']))

        self.ui_sender = UIDebugCommandSender(ui_sender_connection_info, self.ui_send_queue)
        self.ui_recver = UIDebugCommandReceiver(ui_recver_connection_info, self.ui_recv_queue)

        # Referee communication
        referee_recver_connection_info = (self.cfg.config_dict['COMMUNICATION']['referee_udp_address'],
                                          int(self.cfg.config_dict['COMMUNICATION']['referee_port']))
        self.referee_recver = RefereeReceiver(referee_recver_connection_info, self.referee_queue)

        # Subprocess to send robot commands
        robot_connection_info = (self.cfg.config_dict['COMMUNICATION']['vision_udp_address'], 20011)

        self.robot_cmd_sender = RobotCommandSender(robot_connection_info)

        self.tracker = Tracker(self.vision_state)
        self.controller = Controller(observer=CsvPlotter)

        # print frame rate
        self.frame_count = 0
        self.time_last_print = time()

        self.time_bank = 0

    def start(self):
        super().start()
        self.vision_receiver.start()
        self.ui_sender.start()
        self.ui_recver.start()
        self.referee_recver.start()

    def run(self):
        own_pid = os.getpid()
        self.wait_for_vision()
        self.logger.debug('Running with process ID {}'.format(own_pid))

        self.time_bank = time()
        try:
            while True:
                self.time_bank += 1.0/Engine.FPS

                self.main_loop()
                
                self.print_frame_rate()
                self.limit_frame_rate()
        except KeyboardInterrupt:
            pass
        finally:
            self.logger.info('Killed')

        sys.stdout.flush()
        exit(0)

    def wait_for_vision(self):
        self.logger.debug('Waiting for vision frame from the VisionReceiver...')
        while not any(self.vision_state):
            sleep(0.1)

    def main_loop(self):

        engine_cmds = self.get_engine_commands()

        game_state = self.tracker.update()
        self.game_state.update(game_state)

        self.controller.update(self.game_state, engine_cmds)
        robot_state = self.controller.execute()

        self.robot_cmd_sender.send_packet(robot_state)
        self.tracker.predict(robot_state.packet)

        # self.ui_send_queue.put_nowait(UIDebugCommandFactory.robot_state(robot_state)) TODO send robot speed command
        self.ui_send_queue.put_nowait(UIDebugCommandFactory.game_state(self.game_state))
        self.ui_send_queue.put_nowait(UIDebugCommandFactory.robots_path(self.controller))

    def get_engine_commands(self):
        try:
            engine_cmds = self.ai_queue.get(block=False)
        except Empty:
            engine_cmds = []
        return engine_cmds

    def is_any_subprocess_borked(self):
        borked_process_found = not all((self.vision_receiver.is_alive(),
                                        self.ui_sender.is_alive(),
                                        self.ui_recver.is_alive()))
        return borked_process_found

    def terminate_subprocesses(self):
        self.vision_receiver.terminate()
        self.ui_sender.terminate()
        self.ui_recver.terminate()

    def limit_frame_rate(self):
        time_ahead = self.time_bank - time()
        if not Engine.FIX_FRAME_RATE:
            return
        if time_ahead > 0:
            sleep(time_ahead)
        if time_ahead < -2:
           raise RuntimeError(
                'The required frame rate is too fast for the engine. '
                'To find out what is the best frame rate for your computer,'
                'launch the engine with FIX_FRAME_RATE at false and use the minimum FPS that you get.')

    def print_frame_rate(self):
        self.frame_count += 1
        dt = time() - self.time_last_print
        if dt > 10:
            self.logger.info('Updating at {:.2f} fps'.format(self.frame_count / dt))
            self.time_last_print = time()
            self.frame_count = 0
