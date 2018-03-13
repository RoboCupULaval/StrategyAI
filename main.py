# Under MIT License, see LICENSE.txt
""" Point d'entrée de l'intelligence artificielle. """

import argparse

from Engine.Framework import Framework
from config.config import Config


def set_arg_parser():
    prog_desc = 'Artificial intelligent and Engine software for the ULtron team in the RoboCup SSL.'
    arg_parser = argparse.ArgumentParser(prog='ULtron\'s AI of the RoboCup ULaval group.', description=prog_desc)

    arg_parser.add_argument('config_file',
                            nargs='?',
                            action='store',
                            help='Load a configuration file(.ini/cfg style).',
                            default='config/sim.cfg')

    arg_parser.add_argument('--engine_fps',
                            action='store',
                            type=int,
                            help='Set the engine FPS if engine fps is locked.',
                            default=30)

    arg_parser.add_argument('--unlock_engine_fps',
                            action='store_true',
                            help='Flag to unlock the engine FPS.',
                            default=False)

    arg_parser.add_argument('--on_negative_side',
                            action='store_true',
                            help='Flag when we are on the negative x side of the field.',
                            default=False)

    return arg_parser


if __name__ == '__main__':
    cli_args = set_arg_parser().parse_args()
    Config().load_file(cli_args.config_file)
    FRAMEWORK = Framework(cli_args)
