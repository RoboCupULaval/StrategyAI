# Under MIT License, see LICENSE.txt

from socket import socket, SOL_SOCKET, AF_INET, SOCK_DGRAM, SO_REUSEADDR, SOCK_STREAM
from typing import Tuple

__author__ = "Maxime Gagnon-Legault"


def udp_socket(connection_info: Tuple) -> socket:
    skt = socket(AF_INET, SOCK_DGRAM)
    skt.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    skt.connect(connection_info)
    return skt


def tcp_socket(connection_info: Tuple) -> socket:
    skt = socket(AF_INET, SOCK_STREAM)
    skt.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    skt.connect(connection_info)
    return skt