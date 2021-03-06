# Under MIT License, see LICENSE.txt

from multiprocessing import Manager
from queue import Empty

from Debug.debug_command_factory import DebugCommandFactory, DEFAULT_DEBUG_TIMEOUT

from Engine.Communication.receiver.referee_receiver import RefereeReceiver
from Engine.Communication.receiver.uidebug_command_receiver import UIDebugCommandReceiver
from Engine.Communication.receiver.vision_receiver import VisionReceiver
from Engine.Communication.sender.robot_command_sender import RobotCommandSender
from Engine.Communication.sender.uidebug_command_sender import UIDebugCommandSender

from Engine.Controller.controller import Controller
from framework_process import FrameworkProcess
from Engine.Tracker.tracker import Tracker

from Util.timing import create_fps_timer

from config.config import Config

config = Config()


class Engine(FrameworkProcess):

    def __init__(self, framework):

        super().__init__(framework)

        # Managers for shared memory between process
        manager = Manager()
        self.vision_state = manager.list([manager.dict() for _ in range(config['ENGINE']['number_of_camera'])])
        self.shared_game_state = self.framework.game_state
        self.field = self.framework.field

        # Queues for process communication
        self.ui_send_queue = self.framework.ui_send_queue
        self.ui_recv_queue = self.framework.ui_recv_queue
        self.ai_queue = self.framework.ai_queue
        self.referee_queue = self.framework.referee_queue

        # External communication
        self.vision_receiver = VisionReceiver(config['COMMUNICATION']['vision_info'], self.vision_state, self.field)
        self.ui_sender = UIDebugCommandSender(config['COMMUNICATION']['ui_sender_info'], self.ui_send_queue)
        self.ui_recver = UIDebugCommandReceiver(config['COMMUNICATION']['ui_recver_info'], self.ui_recv_queue)
        self.referee_recver = RefereeReceiver(config['COMMUNICATION']['referee_info'], self.referee_queue)
        self.robot_cmd_sender = RobotCommandSender()

        # main engine module
        self.tracker = Tracker(self.vision_state, self.ui_send_queue)
        self.controller = Controller(self.ui_send_queue)

    def start(self):
        super().start()
        self.vision_receiver.start()
        self.ui_sender.start()
        self.ui_recver.start()
        self.referee_recver.start()

    def wait_until_ready(self):
        self.logger.debug('Waiting for vision frame from the VisionReceiver...')
        sleep_vision = create_fps_timer(1)
        while not any(self.vision_state):
            sleep_vision()

    def main_loop(self):

        engine_cmds = self.get_engine_commands()

        game_state = self.tracker.update()

        self.controller.update(game_state, engine_cmds)
        robot_state = self.controller.execute(self.dt)

        self.robot_cmd_sender.send_packet(robot_state)
        self.tracker.predict(robot_state, self.dt)

        self.shared_game_state.update(game_state)
        
        self.send_debug(game_state)
        
    def get_engine_commands(self):
        try:
            engine_cmds = self.ai_queue.get_nowait()
        except Empty:
            engine_cmds = []
        return engine_cmds

    def is_alive(self):

        borked_process_not_found = all((self.vision_receiver.is_alive(),
                                        self.ui_sender.is_alive(),
                                        self.ui_recver.is_alive(),
                                        self.referee_recver.is_alive()))

        return borked_process_not_found and super().is_alive()

    def send_debug(self, game_state):
        # Send debug at the DEFAULT_DEBUG_TIMEOUT frame rate
        # ratio = int(DEFAULT_DEBUG_TIMEOUT * self.fps)
        # if ratio > 1 and self.frame_count % ratio == 0:
        if any(robot.path for robot in self.controller.robots):
            self.ui_send_queue.put_nowait(DebugCommandFactory.paths(self.controller.robots))

        self.ui_send_queue.put_nowait(DebugCommandFactory.game_state(blue=game_state['blue'],
                                                                     yellow=game_state['yellow'],
                                                                     balls=game_state['balls']))

