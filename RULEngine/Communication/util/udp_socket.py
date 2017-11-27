# Under MIT License, see LICENSE.txt

from socket import socket, SOL_SOCKET, AF_INET, SOCK_DGRAM, SO_REUSEADDR


def udp_socket(host: str, port: int) -> socket:
    skt = socket(AF_INET, SOCK_DGRAM)
    skt.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    connection_info = (host, port)
    skt.connect(connection_info)
    return skt
