from configparser import ConfigParser, ParsingError
from RULEngine.Util.singleton import Singleton


class ConfigService(metaclass=Singleton):

    def __init__(self):
        self.config_dict = {}

    def load_file(self, input_config_file) -> None:
        config_parser = ConfigParser(allow_no_value=False)
        try:
            config_parser.read_file(open(input_config_file))
        except FileNotFoundError:
            print("Impossible de lire le fichier de configuration.\nLoading default simulation with kalman settings")
            config_parser.read_dict(default_dict)
        except ParsingError:
            print("Le fichier de configuration est mal configuré.\nExiting!")
            exit(1)

        self.config_dict = {s: dict(config_parser.items(s)) for s in config_parser.sections()}


default_dict = {"GAME": {"type": "sim",
                         "terrain_type": "normal",
                         "our_color": "blue",
                         "their_color": "yellow",
                         "autonomous_play": "false",
                         "ai_timestamp": "0.05"},
                "COMMUNICATION": {"type": "sim",
                                  "redirect": "true",
                                  "udp_address": "224.5.23.2",
                                  "referee_port": "10003",
                                  "vision_port": "10020",
                                  "ui_debug_address": "127.0.0.1",
                                  "ui_cmd_sender_port": "20021",
                                  "ui_cmd_receiver_port": "10021",
                                  "ui_vision_sender_port": "10022"},
                "IMAGE": {"kalman": "true",
                          "number_of_camera": "1"},
                "STRATEGY": {"pathfinder": "path_part"},
                "DEBUG": {"using_debug": "true",
                          "allow_debug": "true"}
                }
