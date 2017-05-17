# Under MIT License, see LICENSE.txt
""" Point d'entrée de l'intelligence artificielle. """

import argparse

from RULEngine.Framework import Framework
from coach import Coach
from config.config_service import ConfigService

__author__ = 'RoboCupULaval'


def set_arg_parser():
    # TODO add mode debug, redirect, pathfinder!
    prog_desc = "Module de l'intelligence artificielle. L'option est de charger un fichier de configuration."
    arg_parser = argparse.ArgumentParser(prog="RobocupULaval's Team ULtron AI", description=prog_desc)

    arg_parser.add_argument('config_file', nargs='?', help="load a configuration file(.ini/cfg style)",
                            default="config/sim_kalman_redirect.cfg")

    return arg_parser

if __name__ == '__main__':
    # parser for command line arguments
    parser = set_arg_parser()
    args = parser.parse_args()

    config_service = ConfigService().load_file(args.config_file)
    # ai init
    ai_coach = Coach()
    # RULEngine init
    framework = Framework()
    # Starting point
    framework.start_game(ai_coach.main_loop, ai_coach.set_reference)
