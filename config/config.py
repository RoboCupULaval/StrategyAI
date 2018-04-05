
from configparser import ConfigParser, ParsingError
import logging
from Util import Singleton

mandatory_fields = {
    'COMMUNICATION': ['type', 'field_port_file', 'vision_port', 'ui_debug_address'],
    'GAME': ['our_color', 'type', 'is_autonomous_play_at_startup'],
    'IMAGE': ['number_of_camera']
}


class Config(metaclass=Singleton):

    def __init__(self):
        self._config = Config.default_config()
        self._config_was_set = False
        self.logger = logging.getLogger('Config')

    def load_file(self, filename: str):

        self._config = self.read_config_file(filename)

        field_config_filename = self['COMMUNICATION']['field_port_file']
        if 'field_port_file' in self['COMMUNICATION']:
            field_config = self.read_config_file(field_config_filename)
            self._config['COMMUNICATION'].update(field_config['COMMUNICATION'])
        else:
            self.logger.critical('Cannot find the field_port_file field in {}.'.format(field_config_filename))
            exit(1)

        self.validate_user_input()
        self.update_content()

        self._config_was_set = True

    def read_config_file(self, filename: str):

        config_parser = ConfigParser(allow_no_value=False)
        try:
            config_parser.read_file(open(filename))
        except FileNotFoundError:
            self.logger.critical('The .cfg file {} was not found.'.format(filename))
            exit(1)
        except ParsingError:
            self.logger.critical('The .cfg file {} was not parse correctly.'.format(filename))
            exit(1)

        config_dict = {section: dict(config_parser.items(section)) for section in config_parser.sections()}

        return config_dict

    def update_content(self):
        self['ENGINE'] = dict()
        self['IMAGE']['number_of_camera'] = int(self['IMAGE']['number_of_camera'])
        self['GAME']['coach_fps'] = int(self['GAME']['coach_fps'])
        self['GAME']['is_autonomous_play_at_startup'] = self['GAME']['is_autonomous_play_at_startup'] == 'true'

        # DO NOT TOUCH EVER THEY ARE HARDCODED BOTH IN THE IA AND IN UI-DEBUG
        if self['GAME']['our_color'] == 'blue':
            self['COMMUNICATION']['ui_cmd_sender_port'] = 14444    # DO NOT TOUCH
            self['COMMUNICATION']['ui_cmd_receiver_port'] = 15555  # DO NOT TOUCH
        else:
            self['COMMUNICATION']['ui_cmd_sender_port'] = 16666    # DO NOT TOUCH
            self['COMMUNICATION']['ui_cmd_receiver_port'] = 17777  # DO NOT TOUCH

        self['COMMUNICATION']['ui_sender_info'] = (self['COMMUNICATION']['ui_debug_address'],
                                                   int(self['COMMUNICATION']['ui_cmd_sender_port']))

        self['COMMUNICATION']['ui_recver_info'] = (self['COMMUNICATION']['ui_debug_address'],
                                                   int(self['COMMUNICATION']['ui_cmd_receiver_port']))

        self['COMMUNICATION']['vision_info'] = (self['COMMUNICATION']['vision_udp_address'],
                                                int(self['COMMUNICATION']['vision_port']))

        self['COMMUNICATION']['referee_info'] = (self['COMMUNICATION']['referee_udp_address'],
                                                 int(self['COMMUNICATION']['referee_port']))

        if self['COMMUNICATION']['type'] == 'sim':
            self['COMMUNICATION']['grsim_info'] = (self['COMMUNICATION']['grsim_udp_address'],
                                                   int(self['COMMUNICATION']['grsim_port']))

    def validate_user_input(self):
        do_exit = False
        for section, fields in mandatory_fields.items():
            for field in fields:
                if field not in self[section]:
                    self.logger.critical('Mandatory field \'{}\' is missing from section \'{}\''.format(field, section))
                    do_exit = True

        if 'play_zone' in self['GAME']:
            if self['GAME']['play_zone'] not in ['full', 'positive', 'negative']:
                self.logger.critical('play_zone is either full, positive or negative.')
                do_exit = True

        if self['GAME']['our_color'] not in ['yellow', 'blue']:
            self.logger.critical('our_color should be either blue or yellow, not {}.'.format(self['GAME']['our_color']))
            do_exit = True

        if do_exit:
            exit(1)

    @staticmethod
    def default_config():
        return {
            'GAME': {
                'our_color': 'yellow',
                'their_color': 'blue',
                'is_autonomous_play_at_startup': False
            }
        }

    def __getitem__(self, item):
        return self._config[item]

    def __setitem__(self, key, value):
        if self._config_was_set:
            raise RuntimeError('You can\'t change the configuration after it has been loaded from a file.')
        self._config[key] = value

    def load_parameters(self, cli_args):
        self._config['ENGINE']['engine_fps'] = cli_args.engine_fps
        self._config['ENGINE']['unlock_engine_fps'] = cli_args.unlock_engine_fps
        self._config['GAME']['on_negative_side'] = cli_args.on_negative_side
        self._config['ENGINE']['enable_profiling'] = cli_args.enable_profiling
        self._config['GAME']['competition_mode'] = cli_args.competition_mode
