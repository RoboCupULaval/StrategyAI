from multiprocessing import Process, Event, Queue
from queue import Empty
from time import sleep

from RULEngine.Communication.util.robot_command_sender_factory import RobotCommandSenderFactory

TIME_BETWEEN_CMD_SEND = 0


class RobotCommandSenderCommunicationManager(Process):
    def __init__(self, robot_cmds_queue: Queue, stop_event: Event):
        super().__init__()
        self.robot_cmds_queue = robot_cmds_queue
        self.stop_event = stop_event
        self.server = None

    def initialize(self):
        self.server, args = RobotCommandSenderFactory.get_sender()
        self.server(*args)

    def loop(self):
        while not self.stop_event.is_set():
            sleep(TIME_BETWEEN_CMD_SEND)
            try:
                robot_cmd = self.robot_cmds_queue.get(block=False)
            except Empty:
                continue
            if robot_cmd is not None:
                self.server.send_command(robot_cmd)

    def run(self):
        self.initialize()
        self.loop()
