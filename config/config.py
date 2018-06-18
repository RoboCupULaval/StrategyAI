
from configparser import ConfigParser, ParsingError
import logging
from sys import stdout

import datetime

from Util import Singleton


MANDATORY_FIELDS = {
    'COMMUNICATION': ['type', 'field_port_file', 'ui_debug_address', 'vision_port',
                      'vision_address', 'referee_port', 'referee_address'],
    'GAME': ['type'],
    'ENGINE': ['number_of_camera']
}


class Config(metaclass=Singleton):

    def __init__(self):
        self._config = Config.default_config()
        self._config_was_set = False
        self.logger = logging.getLogger(self.__class__.__name__)

    def load_file(self, filename: str):

        config = self.read_config_file(filename)
        self._config['ENGINE'].update(config['ENGINE'])
        self._config['COMMUNICATION'].update(config['COMMUNICATION'])
        self._config['GAME'].update(config['GAME'])

        field_config = self.read_config_file(self['COMMUNICATION']['field_port_file'])
        self._config['COMMUNICATION'].update(field_config['COMMUNICATION'])

        self.validate_user_input()

        self.update_content()
        self.update_ports()

        self._config_was_set = True

    def read_config_file(self, filename: str):
        config_parser = ConfigParser(allow_no_value=False)
        try:
            config_parser.read_file(open(filename))
        except FileNotFoundError:
            self.logger.critical('The .cfg file %s was not found.', filename)
            exit(1)
        except ParsingError:
            self.logger.critical('The .cfg file %s was not parse correctly.', filename)
            exit(1)

        config_dict = {section: dict(config_parser.items(section)) for section in config_parser.sections()}

        return config_dict

    def update_content(self):

        self['ENGINE']['number_of_camera'] = int(self['ENGINE']['number_of_camera'])

        if type(self['ENGINE']['disabled_camera_id']) is str:
            exec("self['ENGINE']['disabled_camera_id'] = " + self['ENGINE']['disabled_camera_id']) # SB: Sorry, it works.

    def update_ports(self):
        # DO NOT TOUCH EVER THEY ARE HARDCODED BOTH IN THE IA AND IN UI-DEBUG
        if self['GAME']['our_color'] == 'blue':
            self['COMMUNICATION']['ui_cmd_sender_port'] = 14444    # DO NOT TOUCH
            self['COMMUNICATION']['ui_cmd_receiver_port'] = 15555  # DO NOT TOUCH
        else:
            self['COMMUNICATION']['ui_cmd_sender_port'] = 16666    # DO NOT TOUCH
            self['COMMUNICATION']['ui_cmd_receiver_port'] = 17777  # DO NOT TOUCH

        if self.is_simulation():
            self['COMMUNICATION']['grsim_info'] = (self['COMMUNICATION']['grsim_address'],
                                                   int(self['COMMUNICATION']['grsim_port']))

        self['COMMUNICATION']['ui_sender_info'] = (self['COMMUNICATION']['ui_debug_address'],
                                                   int(self['COMMUNICATION']['ui_cmd_sender_port']))

        self['COMMUNICATION']['ui_recver_info'] = (self['COMMUNICATION']['ui_debug_address'],
                                                   int(self['COMMUNICATION']['ui_cmd_receiver_port']))

        self['COMMUNICATION']['vision_info'] = (self['COMMUNICATION']['vision_address'],
                                                int(self['COMMUNICATION']['vision_port']))

        self['COMMUNICATION']['referee_info'] = (self['COMMUNICATION']['referee_address'],
                                                 int(self['COMMUNICATION']['referee_port']))

    def validate_user_input(self):
        do_exit = False
        for section, fields in MANDATORY_FIELDS.items():
            for field in fields:
                if field not in self[section]:
                    self.logger.critical('Mandatory field \'%s\' is missing from section \'%s\'', field, section)
                    do_exit = True

        if self['GAME']['type'] not in ['sim', 'real']:
            self.logger.critical('Invalid type in GAME. Received: %s. Expected sim or real.', self['GAME']['type'])

        if self['COMMUNICATION']['type'] not in ['grsim', 'serial', 'disabled']:
            self.logger.critical('Invalid type in COMMUNICATION. Received: %s. Expected sim, serial or disabled.', self['COMMUNICATION']['type'])

        if type(self['ENGINE']['disabled_camera_id']) is str:
            try:
                exec(self['ENGINE']['disabled_camera_id'])
            except SyntaxError:
                self.logger.critical('disabled_camera_id argument in ENGINE is invalid: %s. Expected a list.', self['ENGINE']['disabled_camera_id'])
                do_exit = True

        if 0 > int(self['ENGINE']['number_of_camera']) > 4:
            self.logger.critical('The number of camera in ENGINE should be between 1 and 4, not %s', int(self['ENGINE']['number_of_camera']))
            do_exit = True

        if do_exit:
            exit(1)

    def is_simulation(self):
        return self['GAME']['type'] == 'sim'

    @staticmethod
    def default_config():
        return {
            'COMMUNICATION': {
                'type': 'grsim'
            },
            'GAME': {
                'type': 'sim',
                'our_color': 'yellow',
                'is_autonomous_play_at_startup': False,
                'on_negative_side': True,
                'fps': 10,
                'profiling_filename': 'profile_data_ai.prof',
                'profiling_dump_time': 10
            },
            'ENGINE': {
                'profiling_filename': 'profile_data_engine.prof',
                'profiling_dump_time': 10,
                'number_of_camera': 4,
                'max_robot_id': 12,
                'max_undetected_robot_time': 5,
                'max_undetected_ball_time': 0.25,
                'max_ball_on_field': 2,
                'max_ball_separation': 2000,
                'disabled_camera_id': []
            }
        }

    def __getitem__(self, item):
        return self._config[item]

    def __setitem__(self, key, value):
        if self._config_was_set:
            raise RuntimeError('You can\'t change the configuration after it has been loaded from a file.')
        self._config[key] = value

    def load_parameters(self, cli_args):
        self._config['ENGINE']['fps'] = cli_args.engine_fps
        self._config['ENGINE']['is_fps_locked'] = not cli_args.unlock_engine_fps
        self._config['ENGINE']['enable_profiling'] = cli_args.enable_profiling

        self._config['GAME']['our_color'] = cli_args.color
        self._config['GAME']['on_negative_side'] = cli_args.side == 'negative'
        self._config['GAME']['competition_mode'] = cli_args.competition_mode
        self._config['GAME']['is_autonomous_play_at_startup'] = cli_args.start_in_auto

        if cli_args.competition_mode:
            self._config['GAME']['is_autonomous_play_at_startup'] = True

            file_formatter = logging.Formatter('(%(asctime)s) - [%(levelname)-5.5s]  %(name)-22.22s: %(message)s')
            file_handler = logging.FileHandler('./Logs/log_' + str(datetime.date.today()) + '_at_'
                                                                  + str(datetime.datetime.now().hour) + 'h.log', 'a')
            file_handler.setFormatter(file_formatter)

            console_formatter = logging.Formatter('[%(levelname)-5.5s] - %(name)-22.22s: %(message)s')
            console_handler = logging.StreamHandler(stream=stdout)
            console_handler.setFormatter(console_formatter)

            logging.basicConfig(level=logging.NOTSET, handlers=[file_handler, console_handler])

            # NO CAMERA DISABLED IN COMPETITION MODE
            self._config['ENGINE']['disabled_camera_id'] = []

        self._config_was_set = False
        self.update_ports()
        self._config_was_set = True
