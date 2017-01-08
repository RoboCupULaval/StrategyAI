# Under MIT License, see LICENSE.txt
""" Point d'entrée de l'intelligence artificielle. """

import argparse

from RULEngine.Framework import Framework
from RULEngine.Util.constant import TeamColor
from coach import Coach

__author__ = 'RoboCupULaval'


def set_arg_parser():
    prog_desc = "Module de l'intelligence artificielle. Les options " \
                "permettent de manipuler la configuration de l'IA concernant " \
                "la communication et les equipes."
    arg_parser = argparse.ArgumentParser(description=prog_desc)
    serial_choices = ['disabled', 'rf', 'bluetooth']
    serial_help = 'type de communitation série, incompatible avec --simulation'
    ai_type_option = arg_parser.add_mutually_exclusive_group()
    ai_type_option.add_argument("--serial", type=str, default='disabled',
                                dest='serial', choices=serial_choices,
                                nargs='?', help=serial_help)
    simulation_help = "active la simulation"
    ai_type_option.add_argument("--simulation", default='True',
                                dest='simulation', action='store_const',
                                const='True', help=simulation_help)
    color_choices = ['blue', 'yellow']
    color_help = "choix de la couleur (default=blue)"
    arg_parser.add_argument("--color", type=str, default='blue',
                            dest='color', choices=color_choices, nargs='?',
                            help=color_help)
    async_help = 'active le mode async pour le framework'
    arg_parser.add_argument("--async", type=bool, default='False',
                            dest='async', help=async_help)
    return arg_parser


def get_color(color_arg):
    if color_arg == "blue":
        return TeamColor.BLUE_TEAM
    else:
        return TeamColor.YELLOW_TEAM


if __name__ == '__main__':
    parser = set_arg_parser()
    args = parser.parse_args()
    color = get_color(args.color)

    ai_coach = Coach()
    framework = Framework(serial=args.serial)
    framework.start_game(ai_coach.main_loop, ai_coach.set_reference,
                         team_color=color, async=args.async)
