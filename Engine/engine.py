# Under MIT License, see LICENSE.txt
import cProfile
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

from config.config import Config


class Engine(Process):

    DEFAULT_CAMERA_NUMBER = 4
    DEFAULT_FPS_LOCK_STATE = True
    DEFAULT_FPS = 30  # Please don't change this constant, instead run 'python main.py --engine_fps desired_fps'
    MAX_TIME_BEHIND = 2
    STATUS_LOG_TIME = 10
    PROFILE_DUMP_TIME = 10
    PROFILE_DATA_FILENAME = 'profile_data_engine.prof'

    def __init__(self,
                 game_state: DictProxy,
                 field: DictProxy,
                 ai_queue: Queue,
                 referee_queue: Queue,
                 ui_send_queue: Queue,
                 ui_recv_queue: Queue):

        super().__init__(name=__name__)

        self.logger = logging.getLogger(self.__class__.__name__)

        # Managers for shared memory between process
        manager = Manager()
        self.vision_state = manager.list([manager.dict() for _ in range(Config()['IMAGE']['number_of_camera'])])
        self.game_state = game_state
        self.field = field

        # Queues for process communication
        self.ui_send_queue = ui_send_queue
        self.ui_recv_queue = ui_recv_queue
        self.ai_queue = ai_queue
        self.referee_queue = referee_queue

        # External communication
        self.vision_receiver = VisionReceiver(Config()['COMMUNICATION']['vision_info'], self.vision_state, self.field)
        self.ui_sender = UIDebugCommandSender(Config()['COMMUNICATION']['ui_sender_info'], self.ui_send_queue)
        self.ui_recver = UIDebugCommandReceiver(Config()['COMMUNICATION']['ui_recver_info'], self.ui_recv_queue)
        self.referee_recver = RefereeReceiver(Config()['COMMUNICATION']['referee_info'], self.referee_queue)
        self.robot_cmd_sender = RobotCommandSender()

        # main engine module
        self.tracker = Tracker(self.vision_state)
        self.controller = Controller(observer=CsvPlotter)

        # fps and limitation
        self._fps = Engine.DEFAULT_FPS
        self._is_fps_locked = Engine.DEFAULT_FPS_LOCK_STATE
        self.frame_count = 0
        self.last_frame_count = 0
        self.last_log_time = time()
        self.time_bank = 0

        # profiling
        self.profiling_enabled = False
        self.profiler = None

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
            logged_string += ' at {} fps.'.format(self.fps)
        else:
            logged_string += ' without fps limitation.'

        self.logger.debug(logged_string)

        self.time_bank = time()
        try:
            while True:
                self.time_bank += 1.0 / self.fps
                self.frame_count += 1
                self.main_loop()
                self.dump_profiling_stats()
                self.log_status()
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
            sleep(1/self.fps)

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

    def limit_frame_rate(self):
        time_ahead = self.time_bank - time()
        if not self.is_fps_locked:
            return
        if time_ahead > 0:
            sleep(time_ahead)
        if time_ahead < -Engine.MAX_TIME_BEHIND:
            raise RuntimeError(
                'The required frame rate is too high for the engine.\n'
                'Launch the engine with the flag --unlock_fps and use the minimum FPS that you get.')

    def log_status(self):
        if self.frame_count % (self.fps * Engine.STATUS_LOG_TIME) == 0:
            df, self.last_frame_count = self.frame_count - self.last_frame_count, self.frame_count
            dt, self.last_log_time = time() - self.last_log_time, time()
            self.logger.info('Updating at {:.2f} fps'.format(df / dt))

    def dump_profiling_stats(self):
        if self.profiling_enabled:
            if self.frame_count % (self.fps * Engine.PROFILE_DUMP_TIME) == 0:
                self.profiler.dump_stats(Engine.PROFILE_DATA_FILENAME)
                self.logger.debug('Profile data written to {}.'.format(Engine.PROFILE_DATA_FILENAME))

    def is_any_subprocess_borked(self):
        borked_process_found = not all((self.vision_receiver.is_alive(),
                                        self.ui_sender.is_alive(),
                                        self.ui_recver.is_alive(),
                                        self.referee_recver.is_alive()))
        return borked_process_found

    def terminate_subprocesses(self):
        self.vision_receiver.terminate()
        self.ui_sender.terminate()
        self.ui_recver.terminate()
        self.referee_recver.terminate()

    def enable_profiling(self):
        self.profiling_enabled = True
        self.profiler = cProfile.Profile()
        self.profiler.enable()
        self.logger.debug('Profiling mode activate.')

    def unlock_fps(self):
        self.is_fps_locked = False

    @property
    def fps(self):
        return self._fps

    @fps.setter
    def fps(self, engine_fps):
        if not engine_fps > 0:
            raise ValueError('FPS must be greater than zero.')
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
