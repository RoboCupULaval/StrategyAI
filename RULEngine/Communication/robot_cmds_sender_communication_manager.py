from multiprocessing import Process, Event, Queue

from RULEngine.Communication.util.robot_command_sender_factory import RobotCommandSenderFactory
from config.config_service import ConfigService
from RULEngine.Communication.protobuf import referee_pb2 as ssl_referee
from RULEngine.Communication.util.protobuf_packet_receiver import ProtobufPacketReceiver


class RobotCommandSenderCommunicationManager(Process):
    def __init__(self, robot_cmds_queue: Queue, stop_event: Event):
        super().__init__()
        self.robot_cmds_queue = robot_cmds_queue
        self.stop_event = stop_event
        self.server = None

    def initialize(self):
        self.server, args = RobotCommandSenderFactory.get_sender()
        self.server(args)

    def loop(self):
        while not self.stop_event.is_set():
            self.server.send_command(self.robot_cmds_queue.get())

    def run(self):
        self.initialize()
        self.loop()
