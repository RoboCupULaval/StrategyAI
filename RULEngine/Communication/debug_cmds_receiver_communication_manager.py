from multiprocessing import Process, Event, Queue

from RULEngine.Communication.receiver.debug_command_receiver import DebugCommandReceiver


class DebugCommandReceiverCommunicationManager(Process):
    def __init__(self, robot_cmds_queue: Queue, stop_event: Event):
        super().__init__()
        self.robot_cmds_queue = robot_cmds_queue
        self.stop_event = stop_event
        self.server = None

    def initialize(self):
        self.server = DebugCommandReceiver()

    def loop(self):
        while not self.stop_event.is_set():
            self.server.send_command(self.robot_cmds_queue.get())

    def run(self):
        self.initialize()
        self.loop()
