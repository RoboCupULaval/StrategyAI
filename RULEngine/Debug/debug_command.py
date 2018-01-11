# Under MIT License, see LICENSE.txt
__author__ = "Maxime Gagnon-Legault, and others"

SENDER_NAME = "AI"


class DebugCommand(dict):

    def __new__(cls, p_type, p_data, p_link=None, p_version="1.0"):
        command = dict()
        command['name'] = 'Engine'
        command['version'] = p_version
        command['type'] = p_type
        command['link'] = p_link
        command['data'] = p_data

        return command

