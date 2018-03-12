# Under MIT License, see LICENSE.txt
""" Point d'entrée de l'intelligence artificielle. """

import argparse

from Engine.Framework import Framework
from config.config_service import ConfigService


def set_arg_parser():
    prog_desc = "Artificial intelligent and Engine software for the ULtron team in the Robocup SSL."
    arg_parser = argparse.ArgumentParser(prog="ULtron's AI of the Robocup ULaval group.", description=prog_desc)

    arg_parser.add_argument('config_file',
                            nargs='?',
                            action='store',
                            help="Load a configuration file(.ini/cfg style).",
                            default="config/sim.cfg")

    arg_parser.add_argument('--engine_fps',
                            action='store',
                            type=int,
                            help="Set the engine FPS if engine fps is locked.",
                            default=30)

    arg_parser.add_argument('--unlock_engine_fps',
                            action='store_true',
                            help="Flag to unlock the engine FPS.",
                            default=False)

    arg_parser.add_argument('--on_negative_side',
                            action='store_true',
                            help="Flag when we are on the negative x side of the field",
                            default=False)

    return arg_parser


if __name__ == '__main__':
    # parser for command line arguments
    PARSER = set_arg_parser()
    ARGS = PARSER.parse_args()
    ConfigService().load_file(ARGS.config_file)

    # Engine init
    FRAMEWORK = Framework(ARGS)
