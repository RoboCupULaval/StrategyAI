# Under MIT License, see LICENSE.txt
"""
    Regroupe les services utilisant l'UDP pour la communication. Ceux-ci
    permettent l'envoie et la réceptions de paquets pour le débogage, ainsi que
    l'envoie des commandes aux robots au niveau des systèmes embarqués.
"""

from collections import deque
import pickle
from socketserver import BaseRequestHandler

from .protobuf import grSim_Packet_pb2 as grSim_Packet
from .udp_utils import udp_socket, MulticastThreadedUDPServer, ThreadedUDPServer

from ..Util.constant import DEBUG_RECEIVE_BUFFER_SIZE

class PBPacketReceiver(object):
    """
        Service qui implémente un serveur multicast UDP avec comme type de
        paquets ceux défini par la SSL en utilisant protobuf. Le serveur est
        async.
    """

    def __init__(self, host, port, packet_type):
        self.packet_list = deque(maxlen=100)
        handler = self.get_udp_handler(self.packet_list, packet_type)
        self.server = MulticastThreadedUDPServer(host, port, handler)

    def get_udp_handler(self, packet_list, packet_type):
        class ThreadedUDPRequestHandler(BaseRequestHandler):

            def handle(self):
                data = self.request[0]
                packet = packet_type()
                packet.ParseFromString(data)
                packet_list.append(packet)

        return ThreadedUDPRequestHandler

    def pop_frames(self):
        """ Retourne une frame de la deque. """
        new_list = list(self.packet_list)
        self.packet_list.clear()
        return new_list

    def get_latest_frame(self):
        """ Retourne sans erreur la dernière frame reçu. """
        try:
            return self.packet_list[-1]
        except IndexError:
            return None


class GrSimCommandSender(object):
    """ Service qui envoie les commandes de mouvements aux robots. """

    def __init__(self, host, port):
        """ Constructeur """
        self.server = udp_socket(host, port)

    def _send_packet(self, packet):
        """
            Envoie un paquet en sérialisant au préalable.

            :param packet: Un paquet prêt à l'envoie
        """
        self.server.send(packet.SerializeToString())

    def send_command(self, command):
        """
            Construit le paquet à envoyer à partir de la commande reçut.

            :param command: Command pour un robot
        """
        packet = grSim_Packet.grSim_Packet()
        packet.commands.isteamyellow = command.team.is_team_yellow
        packet.commands.timestamp = 0
        grsim_command = packet.commands.robot_commands.add()
        grsim_command.id = command.player.id
        grsim_command.wheelsspeed = False
        grsim_command.veltangent = command.pose.position.x
        grsim_command.velnormal = command.pose.position.y
        grsim_command.velangular = command.pose.orientation
        grsim_command.spinner = True
        grsim_command.kickspeedx = command.kick_speed
        grsim_command.kickspeedz = 0

        self._send_packet(packet)

class DebugCommandSender(object):
    """
        Définition du service capable d'envoyer des paquets de débogages au
        serveur et à l'interface de débogage. S'occupe de la sérialisation.
    """
    def __init__(self, host, port):
        """ Constructeur """
        self.server = udp_socket(host, port)

    def _send_packet(self, p_packet):
        """ Envoi un seul paquet. """
        self.server.send(pickle.dumps(p_packet))

    def send_command(self, p_packets):
        """ Reçoit une liste de paquets et les envoies. """
        for packet in p_packets:
            self._send_packet(packet)

class DebugCommandReceiver(object):
    """
        Service capable d'écouter un port multicast UDP, de reçevoir et de
        traiter les paquets brutes envoyer par le serveur de débogage.
    """
    def __init__(self, host, port):
        self.packet_list = deque(maxlen=DEBUG_RECEIVE_BUFFER_SIZE)
        handler = self.get_udp_handler(self.packet_list)
        self.server = ThreadedUDPServer(host, port, handler)

    def get_udp_handler(self, p_packet_list):
        """ Retourne la classe pour reçevoir async les paquets """

        class ThreadedUDPRequestHandler(BaseRequestHandler):
            """ Contient la logique pour traiter en callback une request. """
            def handle(self):
                """
                    Récupère la request et unpickle le paquet brute dans la
                    deque.
                """
                data = self.request[0]
                p_packet_list.append(pickle.loads(data))
        return ThreadedUDPRequestHandler

    def receive_command(self):
        """ Vide la file et retourne une liste des paquets brutes. """
        for _ in range(len(self.packet_list)):
            yield self.packet_list.pop()
