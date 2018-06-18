# Under MIT License, see LICENSE.txt

import argparse
import logging
from time import sleep
from sys import stdout

from Engine.Framework import Framework
from config.config import Config
from Util.sysinfo import git_version


def set_arg_parser():
    prog_desc = 'Artificial intelligent and Engine software for the ULtron team in the RoboCup SSL.'
    arg_parser = argparse.ArgumentParser(prog='ULtron\'s AI of the RoboCup ULaval group.', description=prog_desc)

    arg_parser.add_argument('config_file',
                            action='store',
                            help='Load a configuration file(.ini/cfg style).',
                            default='config/sim.cfg')

    arg_parser.add_argument('color',
                            help='Select team color',
                            choices=['blue', 'yellow'])

    arg_parser.add_argument('side',
                            help='Select if the team is playing on the positive of negative side',
                            choices=['positive', 'negative'])

    arg_parser.add_argument('--engine_fps',
                            action='store',
                            type=int,
                            help='Set the engine FPS if engine fps is locked.',
                            default=30)

    arg_parser.add_argument('--unlock_engine_fps',
                            action='store_true',
                            help='Flag to unlock the engine FPS.',
                            default=False)

    arg_parser.add_argument('--enable_profiling',
                            action='store_true',
                            help='Enables profiling options through the project.',
                            default=False)

    arg_parser.add_argument('--start_in_auto',
                            action='store_true',
                            help='Start the AI directly in autonomous mode.',
                            default=False)

    arg_parser.add_argument('--competition_mode',
                            action='store_true',
                            help='Enables watchdog which reset the Framework if it stop.',
                            default=False)
    return arg_parser


if __name__ == '__main__':

    consoleFormatter = logging.Formatter('[%(levelname)-5.5s] - %(name)-22.22s: %(message)s')
    consoleHandler = logging.StreamHandler(stream=stdout)
    consoleHandler.setFormatter(consoleFormatter)

    logging.basicConfig(level=logging.NOTSET, handlers=[consoleHandler])

    cli_args = set_arg_parser().parse_args()
    Config().load_file(cli_args.config_file)
    Config().load_parameters(cli_args)

    logger = logging.getLogger('Main')

    logger.info('Color: {}, Field side: {}, Mode: {}'.format(Config()['GAME']['our_color'].upper(),
                                                    'NEGATIVE' if Config()['GAME']['on_negative_side'] else 'POSITIVE',
                                                    'COMPETITION' if cli_args.competition_mode else 'NORMAL'))

    logger.info('Current git commit hash: ' + git_version())

    stop_framework = False
    while not stop_framework:
        try:
            Framework(profiling=cli_args.enable_profiling).start()
        except SystemExit:
            logger.debug('Framework stopped.')
        except:
            logger.exception('An error occurred.')
        finally:
            if not cli_args.competition_mode:
                stop_framework = True
            else:
                logger.debug('Restarting Framework.')
                sleep(0.5)
