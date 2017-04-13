from configparser import ConfigParser, ParsingError
from RULEngine.Util.singleton import Singleton


class ConfigService(metaclass=Singleton):

    def __init__(self):
        self.config_dict = {}

    def load_file(self, input_config_file):
        config_parser = ConfigParser(allow_no_value=False)
        try:
            config_parser.read_file(open(input_config_file))
        except FileNotFoundError:
            print("Impossible de lire le fichier de configuration.\nExiting!")
            exit(1)
        except ParsingError:
            print("Le fichier de configuration est mal configuré.\nExiting!")
            exit(1)

        self.config_dict = {s: dict(config_parser.items(s)) for s in config_parser.sections()}
