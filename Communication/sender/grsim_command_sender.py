# Under MIT License, see LICENSE.txt

from RULEngine.Communication.protobuf import grSim_Packet_pb2 as grSim_Packet
from RULEngine.Communication.util.udp_socket import udp_socket


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
        packet.commands.isteamyellow = command.player.team.is_team_yellow()
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

        print("Command (x, y, t): {} -- {} -- {}".format(command.pose.position.x, command.pose.position.y,
                                                                 command.pose.orientation))
        self._send_packet(packet)