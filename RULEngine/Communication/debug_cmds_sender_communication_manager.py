import pickle
from multiprocessing import Process, Event, Queue

from RULEngine.Communication.util.udp_socket import udp_socket
from config.config_service import ConfigService


class DebugCommandSenderCommunicationManager(Process):
    def __init__(self, debug_cmds_queue: Queue, stop_event: Event):
        super().__init__()
        cfg = ConfigService()
        self.host = cfg.config_dict["COMMUNICATION"]["ui_debug_address"]
        self.port = int(cfg.config_dict["COMMUNICATION"]["ui_cmd_sender_port"])
        self.debug_cmds_queue = debug_cmds_queue
        self.stop_event = stop_event
        self.client = None

    def initialize(self):
        self.client = udp_socket(self.host, self.port)

    def loop(self):
        while not self.stop_event.is_set():
            self.client._send_packet(self.debug_cmds_queue.get())

    def run(self):
        self.initialize()
        self.loop()

    def _send_packet(self, p_packet):
        """ Envoi un seul paquet. """
        try:
            self.client.send(pickle.dumps(p_packet))
        except ConnectionRefusedError:
            # FIXME: hack
            pass

    def send_packets(self, p_packets):
        """ Reçoit une liste de paquets et les envoies. """
        for packet in p_packets:
            self._send_packet(packet)
