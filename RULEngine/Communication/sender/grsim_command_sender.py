# Under MIT License, see LICENSE.txt
import logging
from typing import Dict
from multiprocessing import Process, Event, Queue
from queue import Empty

from RULEngine.Communication.protobuf import grSim_Packet_pb2 as grSim_Packet
from RULEngine.Communication.util.udp_socket import udp_socket


class GrSimCommandSender(Process):
    def __init__(self, host, port, stop_event: Event, robot_cmd_queue: Queue):
        super(GrSimCommandSender, self).__init__(name=__name__)
        self.logger = logging.getLogger("GrSimCommandSender")

        self.host = host
        self.port = port

        self.stop_event = stop_event
        self.robot_cmd_queue = robot_cmd_queue

        self.server = None

    def _initialize(self) -> None:
        self.server = udp_socket(self.host, self.port)

    def run(self):
        self._initialize()

        try:
            self._serve()
        except KeyboardInterrupt:
            pass

        self._stop()

    def _serve(self):
        while not self.stop_event.is_set():
            try:
                self._send_command(self.robot_cmd_queue.get(block=False))
            except Empty:
                pass

    def _send_command(self, command: Dict):
        try:
            self._send_packet(self._create_protobuf_packet(command))
        except KeyError as e:
            self.logger.error("Dictionnary supplied is missing a key when creating the protobuf for GrSim")
            raise e

    def _send_packet(self, packet):
        self.server.send(packet.SerializeToString())

    def _stop(self):
        self.logger.debug("has exited.")
        exit(0)

    @staticmethod
    def _create_protobuf_packet(command: Dict) -> grSim_Packet.grSim_Packet:
        packet = grSim_Packet.grSim_Packet()
        packet.commands.isteamyellow = command["is_team_yellow"]
        packet.commands.timestamp = 0
        grsim_command = packet.commands.robot_commands.add()
        grsim_command.id = command["id"]
        grsim_command.wheelsspeed = False
        grsim_command.veltangent = command["x"]
        grsim_command.velnormal = command["y"]
        grsim_command.velangular = command["orientation"]
        grsim_command.spinner = True
        grsim_command.kickspeedx = command["kick"]
        grsim_command.kickspeedz = 0

        return packet
