# Under MIT License, see LICENSE.txt
""" Point d'entrée de l'intelligence artificielle. """

import argparse

from RULEngine.Communication.sender.serial_command_sender import SerialType, SERIAL_DISABLED
from RULEngine.Communication.util.serial_protocol import MCUVersion
from RULEngine.Framework import Framework
from RULEngine.Util.constant import TeamColor
from coach import Coach

__author__ = 'RoboCupULaval'

DEFAULT_MCU_VERSION = "stm32f407"


def set_arg_parser():
    # TODO add mode debug, redirect, pathfinder!
    prog_desc = "Module de l'intelligence artificielle. Les options " \
                "permettent de manipuler la configuration de l'IA concernant " \
                "la communication et les equipes."
    arg_parser = argparse.ArgumentParser(description=prog_desc)
    serial_choices = ['disabled', 'nrf', 'bluetooth']
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
    mcu_choices = ['c2000', 'stm32f407']
    mcu_help = "Choix du microcontroleur a utiliser."
    arg_parser.add_argument("--mcu", type=str, default=DEFAULT_MCU_VERSION, dest='mcu',
                            choices=mcu_choices, help=mcu_help)
    return arg_parser


def get_color(color_arg):
    if color_arg == "blue":
        return TeamColor.BLUE_TEAM
    else:
        return TeamColor.YELLOW_TEAM

def get_mcu(mcu):
    if mcu == "c2000":
        return MCUVersion.C2000
    elif mcu == "stm32f407":
        return MCUVersion.STM32F407
    else:
        raise Exception("Le choix de MCU est invalide")


def get_serial(serial):
    if serial == "disabled":
        return SERIAL_DISABLED
    elif serial == "nrf":
        return SerialType.NRF
    elif serial == "bluetooth":
        return SerialType.BLUETOOTH
    else:
        raise Exception("Le choix du type de port serie est invalide")

if __name__ == '__main__':
    # parser for command line arguments
    parser = set_arg_parser()
    args = parser.parse_args()
    color = get_color(args.color)
    mcu = get_mcu(args.mcu)
    serial = get_serial(args.serial)

    simulation = serial == SERIAL_DISABLED
    # ai init
    ai_coach = Coach(is_simulation=simulation)
    # RULEngine init
    framework = Framework(serial=serial, redirect=True, mcu_version=mcu)
    # Starting point
    framework.start_game(ai_coach.main_loop, ai_coach.set_reference,
                         team_color=color, async=args.async)
