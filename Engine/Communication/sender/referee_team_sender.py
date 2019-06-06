import logging
import threading
from threading import Thread
from time import sleep

from google.protobuf.internal.encoder import _VarintBytes
from google.protobuf.internal.decoder import _DecodeVarint32
from protobuf_to_dict import protobuf_to_dict

from Engine.Communication.protobuf.ssl_game_controller_common_pb2 import ControllerReply
from Engine.Communication.protobuf.ssl_game_controller_team_pb2 import TeamRegistration, ControllerToTeam, \
    TeamToController
from Engine.Communication.sender.udp_socket import tcp_socket


class RefereeTeamSender:
    """
    The new referee (ssl-game-controller) supports a bidirectional connection for team registration.
    Teams can send their robot goalkeeper id and their team's name to the referee.
    It can also be used to resolve faults.
    """

    def __init__(self, team_name: str, goalkeeper_id: int, port: int = 10008):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.team_name = team_name
        self.goalkeeper_id = goalkeeper_id
        self.port = port

        self.started = False
        self.connection = None
        self.connection_info = None


    def start(self, ip):
        if not self.started and ip is not None:
            self.started = True
            self.connect((ip, self.port))

            self.thread = Thread(target=self.run, daemon=True)
            self.thread.start()

    def connect(self, connection_info):
        self.logger.info(f"Connecting to ip {connection_info[0]}")
        self.connection = tcp_socket(connection_info)
        self.connection_info = connection_info

    def run(self):
        # Establish connection
        res = self.receive()

        if not self._is_ok(res):
            self.logger.error(f"Not able to establish connection, reason: {self._get_reason(res)}")
            return

        if not self._register_team():
            return

        while True:
            self._send_desired_keeper()
            sleep(5)

            # except BrokenPipeError:
            #     self.logger.error("Can not register team")

    def _register_team(self):
        team_reg = TeamRegistration()
        team_reg.team_name = self.team_name

        self.logger.info(f"Registrating our team '{self.team_name}' to the referee")
        self.send(team_reg)
        res = self.receive()
        if not self._is_ok(res):
            self.logger.error(f"Not able to register the team, reason: {self._get_reason(res)}")
            return False
        self.logger.info("Successfully register team!")
        return True
    def _is_ok(self, res):
        return "controller_reply" in res and res["controller_reply"]['status_code'] == ControllerReply.OK

    def _send_desired_keeper(self):
        request = TeamToController()
        request.desired_keeper = self.goalkeeper_id
        self.send(request)
        res = self.receive()

        if not self._is_ok(res):
            self.logger.error(f"Not able set the desired goalkeeper, reason: {self._get_reason(res)}")

    def _get_reason(self, res):
        if "controller_reply" in res and "reason" in res["controller_reply"]:
            return res['controller_reply']['reason']
        else:
            return str(res)

    def send(self, packet):
        self.connection.send(_VarintBytes(packet.ByteSize()) + packet.SerializeToString())

    def receive(self):
        data = self.connection.recv(1024)

        msg_len, new_pos = _DecodeVarint32(data, 0)
        msg_buf = data[new_pos:new_pos + msg_len]

        response = ControllerToTeam()
        response.ParseFromString(msg_buf)
        return protobuf_to_dict(response)



