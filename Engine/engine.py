# Under MIT License, see LICENSE.txt
import cProfile
import logging
import os
import sys

from multiprocessing import Process, Queue, Manager
from multiprocessing.managers import DictProxy
from queue import Empty

import time

from Debug.debug_command_factory import DebugCommandFactory

from Engine.Communication.receiver.referee_receiver import RefereeReceiver
from Engine.Communication.receiver.uidebug_command_receiver import UIDebugCommandReceiver
from Engine.Communication.receiver.vision_receiver import VisionReceiver
from Engine.Communication.sender.robot_command_sender import RobotCommandSender
from Engine.Communication.sender.uidebug_command_sender import UIDebugCommandSender

from Engine.controller import Controller
from Engine.tracker import Tracker

from Util.timing import create_fps_timer

from config.config import Config

config = Config()


class Engine(Process):

    MAX_EXCESS_TIME = 0.050

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
        self.vision_state = manager.list([manager.dict() for _ in range(config['ENGINE']['number_of_camera'])])
        self.game_state = game_state
        self.field = field

        # Queues for process communication
        self.ui_send_queue = ui_send_queue
        self.ui_recv_queue = ui_recv_queue
        self.ai_queue = ai_queue
        self.referee_queue = referee_queue

        # External communication
        self.vision_receiver = VisionReceiver(config['COMMUNICATION']['vision_info'], self.vision_state, self.field)
        self.ui_sender = UIDebugCommandSender(config['COMMUNICATION']['ui_sender_info'], self.ui_send_queue)
        self.ui_recver = UIDebugCommandReceiver(config['COMMUNICATION']['ui_recver_info'], self.ui_recv_queue)
        self.referee_recver = RefereeReceiver(config['COMMUNICATION']['referee_info'], self.referee_queue)
        self.robot_cmd_sender = RobotCommandSender()

        # main engine module
        self.tracker = Tracker(self.vision_state, self.ui_send_queue)
        self.controller = Controller(self.ui_send_queue)

        # fps and limitation
        self.fps = config['ENGINE']['fps']
        self.is_fps_locked = config['ENGINE']['is_fps_locked']
        self.frame_count = 0
        self.last_frame_count = 0
        self.dt = 0
        self.last_time = 0

        def callback(excess_time):
            if excess_time > self.dt:
                self.logger.debug('Overloaded (%d cycles behind schedule)', excess_time//self.dt)

        self.fps_sleep = create_fps_timer(self.fps, on_miss_callback=callback)

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

        logged_string = 'Running with process ID {}'.format(os.getpid())
        if self.is_fps_locked:
            logged_string += ' at {} fps.'.format(self.fps)
        else:
            logged_string += ' without fps limitation.'

        self.logger.debug(logged_string)

        try:
            self.wait_for_vision()
            self.last_time = time.time()
            while True:
                self.update_dt()
                self.frame_count += 1
                self.main_loop()
                if self.is_fps_locked: self.fps_sleep()
        except KeyboardInterrupt:
            self.logger.info('A keyboard interrupt was raise.')
        except:
            self.logger.exception('message')
            raise

    def wait_for_vision(self):
        self.logger.debug('Waiting for vision frame from the VisionReceiver...')
        sleep_vision = create_fps_timer(1)
        while not any(self.vision_state):
            sleep_vision()

    def update_dt(self):
        current_time = time.time()
        self.dt = current_time - self.last_time
        self.last_time = current_time

    def main_loop(self):
        engine_cmds = self.get_engine_commands()

        game_state = self.tracker.update()
        self.game_state.update(game_state)

        self.controller.update(self.game_state, engine_cmds, self.dt)
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
            engine_cmds = self.ai_queue.get_nowait()
        except Empty:
            engine_cmds = []
        return engine_cmds

    def dump_profiling_stats(self):
        if self.profiling_enabled:
            if self.frame_count % (self.fps * config['ENGINE']['profiling_dump_time']) == 0:
                self.profiler.dump_stats(config['ENGINE']['profiling_filename'])
                self.logger.debug('Profiling data written to {}.'.format(config['ENGINE']['profiling_filename']))

    def is_alive(self):
        borked_process_not_found = all((self.vision_receiver.is_alive(),
                                        self.ui_sender.is_alive(),
                                        self.ui_recver.is_alive(),
                                        self.referee_recver.is_alive()))
        return borked_process_not_found and super().is_alive()

    def terminate(self):
        self.dump_profiling_stats()
        self.vision_receiver.terminate()
        self.ui_sender.terminate()
        self.ui_recver.terminate()
        self.referee_recver.terminate()
        self.logger.debug('Terminated')
        super().terminate()

    def enable_profiling(self):
        self.profiling_enabled = True
        self.profiler = cProfile.Profile()
        self.profiler.enable()
        self.logger.debug('Profiling mode activate.')

