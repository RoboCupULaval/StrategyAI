from configparser import ConfigParser, ParsingError

from Util import Singleton


class ConfigService(metaclass=Singleton):

    def __init__(self):
        self.config_dict = self._load_defaults()

    def load_file(self, input_config_file) -> None:
        config_parser = ConfigParser(allow_no_value=False)
        try:
            config_parser.read_file(open(input_config_file))
        except FileNotFoundError:
            print('Impossible de lire le fichier de configuration.\nLoading default simulation with kalman settings')
            config_parser.read_dict(default_dict)
        except ParsingError:
            print('Le fichier de configuration est mal configuré.\nExiting!')
            exit(1)

        self.config_dict = {s: dict(config_parser.items(s)) for s in config_parser.sections()}

        if 'field_port_file' not in self.config_dict['COMMUNICATION']:
            raise RuntimeError('field_port_file must now be specify and point to the port of vision and ref')
        if 'vision_port' in self.config_dict['COMMUNICATION']:
            raise RuntimeError('The vision_port must be specify in the \'field_port_file\' file')

        if 'ui_cmd_sender_port' in self.config_dict['COMMUNICATION'] or \
           'ui_cmd_receiver_port' in self.config_dict['COMMUNICATION']:
            raise RuntimeError('The ui_cmd_sender_port and ui_cmd_receiver_port are hardcoded base'
                               ' on the our team color, removed them from config file')
        field_port_file = self.config_dict['COMMUNICATION']['field_port_file']
        try:
            config_parser.read_file(open(field_port_file))
        except FileNotFoundError:
            print('Impossible de lire le fichier de configuration.\nLoading default simulation with kalman settings')
            config_parser.read_dict(default_dict)
        except ParsingError:
            print('Le fichier de configuration est mal configuré.\nExiting!')
            exit(1)
        field_port = {s: dict(config_parser.items(s)) for s in config_parser.sections()}
        self.config_dict['COMMUNICATION'] = field_port['COMMUNICATION']

        if 'play_zone' not in self.config_dict['GAME']:
            self.config_dict['GAME']['play_zone'] = 'full'
        if self.config_dict['GAME']['play_zone'] not in ['full', 'positive', 'negative']:
            raise RuntimeError('play_zone is either full, positive or negative')

        # DO NOT TOUCH EVER THEY ARE HARDCODED BOTH IN THE IA AND IN UI-DEBUG
        our_color = self.config_dict['GAME']['our_color']
        if our_color == 'blue':
            self.config_dict['COMMUNICATION']['ui_cmd_sender_port'] = 14444    # DO NOT TOUCH
            self.config_dict['COMMUNICATION']['ui_cmd_receiver_port'] = 15555  # DO NOT TOUCH
        elif our_color == "yellow":
            self.config_dict['COMMUNICATION']['ui_cmd_sender_port'] = 16666    # DO NOT TOUCH
            self.config_dict['COMMUNICATION']['ui_cmd_receiver_port'] = 17777  # DO NOT TOUCH
        else:
            ValueError("Config file contains wrong colors! Should be either blue or yellow, not {}".format(our_color))

        # [print(key,':' ,value) for key, value in self.config_dict['COMMUNICATION'].items()]

        self.config_dict['GAME']['ai_timestamp'] = float(self.config_dict['GAME']['ai_timestamp'])

    @staticmethod
    def _load_defaults():
        config_parser = ConfigParser(allow_no_value=False)
        config_parser.read_dict(default_dict)
        return {s: dict(config_parser.items(s)) for s in config_parser.sections()}


default_dict = {'GAME': {'type': 'sim',
                         'our_color': 'blue',
                         'their_color': 'yellow',
                         'our_side': 'positive',
                         'autonomous_play': 'false',
                         'ai_timestamp': '0.05',
                         'play_zone': 'full',
                         'kalman_matrix_flag': 'false'},
                'COMMUNICATION': {'type': 'sim',
                                  'redirect': 'true',
                                  'referee_udp_address': '224.5.23.2',
                                  'referee_port': '10003',
                                  'vision_referee_udp_address': '224.5.23.2',
                                  'vision_port': '10020',
                                  'ui_debug_address': '127.0.0.1',
                                  'ui_cmd_sender_port': '14444',
                                  'ui_cmd_receiver_port': '15555',
                                  'ui_vision_sender_port': '10022'},
                'IMAGE': {'kalman': 'true',
                          'number_of_camera': '1',
                          'frames_to_extrapolate': '20'},
                'STRATEGY': {'pathfinder': 'path_part'},
                'DEBUG': {'using_debug': 'true',
                          'allow_debug': 'true'}
                }
