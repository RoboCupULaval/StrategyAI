from multiprocessing import Queue
from queue import Full


class Controller:
    def __init__(self, robot_cmds_queue: Queue):
        self.robot_cmds_queue = robot_cmds_queue

    def send_commands(self):
        pass

