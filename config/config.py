
from configparser import ConfigParser, ParsingError
import logging
from Util import Singleton

mandatory_fields = {
    'COMMUNICATION': ['type', 'field_port_file', 'vision_port', 'ui_debug_address'],
    'GAME': ['our_color', 'type', 'our_side', 'autonomous_play', 'ai_timestamp'],
    'IMAGE': ['number_of_camera'],
    'DEBUG': ['using_debug'],
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

        if 'play_zone' not in self['GAME']:
            self['GAME']['play_zone'] = 'full'

        self['IMAGE']['number_of_camera'] = int(self['IMAGE']['number_of_camera'])
        self['GAME']['ai_timestamp'] = float(self['GAME']['ai_timestamp'])

        # DO NOT TOUCH EVER THEY ARE HARDCODED BOTH IN THE IA AND IN UI-DEBUG
        if self['GAME']['our_color'] == 'blue':
            self['COMMUNICATION']['ui_cmd_sender_port'] = 14444    # DO NOT TOUCH
            self['COMMUNICATION']['ui_cmd_receiver_port'] = 15555  # DO NOT TOUCH
        else:
            self['COMMUNICATION']['ui_cmd_sender_port'] = 16666    # DO NOT TOUCH
            self['COMMUNICATION']['ui_cmd_receiver_port'] = 17777  # DO NOT TOUCH

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
                'their_color': 'blue'
            }
        }

    def __getitem__(self, item):
        return self._config[item]

    def __setitem__(self, key, value):
        if self._config_was_set:
            raise RuntimeError('You can\'t change the configuration after it has been loaded from a file.')
        self._config[key] = value