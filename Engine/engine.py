# Under MIT License, see LICENSE.txt

import logging
import os
import sys
from multiprocessing import Process, Queue, Manager
from multiprocessing.managers import DictProxy
from queue import Empty
from time import time, sleep

from Debug.debug_command_factory import DebugCommandFactory
from Engine.Communication.receiver.referee_receiver import RefereeReceiver
from Engine.Communication.receiver.uidebug_command_receiver import UIDebugCommandReceiver
from Engine.Communication.receiver.vision_receiver import VisionReceiver
from Engine.Communication.sender.robot_command_sender import RobotCommandSender
from Engine.Communication.sender.uidebug_command_sender import UIDebugCommandSender
from Engine.controller import Controller
from Engine.tracker import Tracker

try:
    from Util.csv_plotter import CsvPlotter
except ImportError:
    print('Fail to import csv_plotter. It will be disable.')
    from Util.csv_plotter import Observer as CsvPlotter

from config.config_service import ConfigService

__author__ = 'Maxime Gagnon-Legault and Simon Bouchard'


class Engine(Process):

    DEFAULT_CAMERA_NUMBER = 4
    DEFAULT_FPS_LOCK_STATE = True
    DEFAULT_FPS = 30

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
        self.team_color = self.cfg['GAME']['our_color']

        # Managers for shared memory between process
        manager = Manager()
        self._camera_number = self.cfg['IMAGE'].get('number_of_camera', Engine.DEFAULT_CAMERA_NUMBER)
        self.vision_state = manager.list([manager.dict() for _ in range(self._camera_number)])
        self.game_state = game_state
        self.field = field

        # Queues for inter process communication with the AI
        self.ui_send_queue = ui_send_queue
        self.ui_recv_queue = ui_recv_queue
        self.ai_queue = ai_queue
        self.referee_queue = referee_queue

        # vision subprocess
        vision_connection_info = (self.cfg['COMMUNICATION']['vision_udp_address'],
                                  int(self.cfg['COMMUNICATION']['vision_port']))

        self.vision_receiver = VisionReceiver(vision_connection_info, self.vision_state, self.field)

        # UIDebug communication sub processes
        ui_debug_host = self.cfg['COMMUNICATION']['ui_debug_address']
        ui_sender_connection_info = (ui_debug_host, int(self.cfg['COMMUNICATION']['ui_cmd_sender_port']))
        ui_recver_connection_info = (ui_debug_host, int(self.cfg['COMMUNICATION']['ui_cmd_receiver_port']))

        self.ui_sender = UIDebugCommandSender(ui_sender_connection_info, self.ui_send_queue)
        self.ui_recver = UIDebugCommandReceiver(ui_recver_connection_info, self.ui_recv_queue)

        # Referee communication
        referee_recver_connection_info = (self.cfg['COMMUNICATION']['referee_udp_address'],
                                          int(self.cfg['COMMUNICATION']['referee_port']))
        self.referee_recver = RefereeReceiver(referee_recver_connection_info, self.referee_queue)

        # Subprocess to send robot commands
        robot_connection_info = (self.cfg['COMMUNICATION']['vision_udp_address'], 20011)

        self.robot_cmd_sender = RobotCommandSender(robot_connection_info)

        self.tracker = Tracker(self.vision_state)
        self.controller = Controller(observer=CsvPlotter)

        self._fps = Engine.DEFAULT_FPS
        self._is_fps_locked = Engine.DEFAULT_FPS_LOCK_STATE

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
        self.wait_for_vision()

        logged_string = 'Running with process ID {}'.format(os.getpid())
        if self.is_fps_locked:
            logged_string += ' at {} fps'.format(self.fps)
        else:
            logged_string += ' without fps limitation'
        logged_string += ' with {} cameras.'.format(self.camera_number)

        self.logger.debug(logged_string)
        self.time_bank = time()
        try:
            while True:
                self.time_bank += 1.0 / self.fps

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
        self.tracker.predict(robot_state)

        if any(robot.path for robot in self.controller.robots):
            self.ui_send_queue.put_nowait(DebugCommandFactory.paths(self.controller.robots))

        self.ui_send_queue.put_nowait(DebugCommandFactory.game_state(blue=self.game_state['blue'],
                                                                     yellow=self.game_state['yellow'],
                                                                     balls=self.game_state['balls']))

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
        if not self.is_fps_locked:
            return
        if time_ahead > 0:
            sleep(time_ahead)
        if time_ahead < -2:
            raise RuntimeError(
                'The required frame rate is too fast for the engine.\n'
                'To find out what is the best frame rate for your computer,\n'
                'launch the engine with FIX_FRAME_RATE at false and use the minimum FPS that you get.')

    def print_frame_rate(self):
        self.frame_count += 1
        dt = time() - self.time_last_print
        if dt > 10:
            self.logger.info('Updating at {:.2f} fps'.format(self.frame_count / dt))
            self.time_last_print = time()
            self.frame_count = 0

    def unlock_fps(self):
        self.is_fps_locked = False

    @property
    def fps(self):
        return self._fps

    @fps.setter
    def fps(self, engine_fps):
        self._fps = engine_fps

    @property
    def is_fps_locked(self):
        if not self.fps:
            return False
        else:
            return self._is_fps_locked

    @is_fps_locked.setter
    def is_fps_locked(self, is_lock):
        self._is_fps_locked = is_lock

    @property
    def camera_number(self):
        return self._camera_number

    @camera_number.setter
    def camera_number(self, num):
        if 0 > num > 4:
            raise ValueError('Invalid number of camera.')
        self._camera_number = num
        self.vision_state = Manager().list([Manager().dict() for _ in range(self._camera_number)])
