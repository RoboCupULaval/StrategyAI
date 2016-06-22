# Under MIT License, see LICENSE.txt
"""
    Implémente la logique et les services nécessaires pour communiquer avec le
    serveur de vision.
"""

from .udp_service import PBPacketReceiver
from .protobuf import messages_robocup_ssl_wrapper_pb2 as ssl_wrapper

class Vision(PBPacketReceiver):
    """ Initie le serveur de vision, semble superflue. """
    # FIXME: est-ce réellement utile? la classe ne semble aucunement générique

    def __init__(self, host="224.5.23.2", port=10020):
        super(Vision, self).__init__(host, port, ssl_wrapper.SSL_WrapperPacket)
