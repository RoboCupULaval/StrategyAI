# Under MIT License, see LICENSE.txt
""" Module supérieur de l'IA """
import math

from RULEngine.Command import command
from RULEngine.Util.Position import Position
from RULEngine.Util.Pose import Pose

import ai.executor as executor
from ai.InfoManager import InfoManager
import ai.Debug.debug_manager as ui_debug
from ai.STA.Strategy.StrategyBook import StrategyBook
from ai.STA.Tactic.TacticBook import TacticBook
from ai.Algorithm.PathfinderRRT import PathfinderRRT
from ai.Algorithm.InfluenceMap import InfluenceMap
from ai.Debug.debug_manager import DebugManager, DebugCommand

__author__ = 'RoboCupULaval'

TIMESTAMP_MINIMAL_DELTA = 0.015 # 15 ms de mise à jour pour la boucle de l'ia


class Coach(object):
    """
        Niveau supérieur de l'IA, est appelé et créé par Framework.

        La classe créée une partie du GameState et exécute la boucle principale
        de la logique de l'IA.

        À chaque itération, les Executors sont déclenchés et InfoManager est
        mit à jour.

        À la fin d'une itération, les commandes des robots sont récupérées de
        l'InfoManager et finalement envoyée au serveur de communication.
    """

    def __init__(self):
        """
            Constructeur, réplique une grande partie du GameState pour
            construire l'InfoManager.
        """
        self.info_manager = InfoManager()
        self._init_intelligent_modules()
        self.debug_manager = self.info_manager.debug_manager
        self.debug_executor = executor.DebugExecutor(self.info_manager)
        self.module_executor = executor.ModuleExecutor(self.info_manager)
        self.strategy_executor = executor.StrategyExecutor(self.info_manager)
        self.coach_command_sender = CoachCommandSender(self.info_manager)
        self._init_ui_debug()

        self.last_update_timestamp = 0

    def main_loop(self, p_game_state):
        """ Interface RULEngine/StrategyIA, boucle principale de l'IA"""
        delta_timestamp = p_game_state.timestamp - self.last_update_timestamp
        tick_log = "Tick: " + str(p_game_state.timestamp) + " (delta=" + str(delta_timestamp) + ")"
        self.info_manager.debug_manager.add_log(1, tick_log)

        if delta_timestamp > TIMESTAMP_MINIMAL_DELTA or math.isclose(delta_timestamp, TIMESTAMP_MINIMAL_DELTA, abs_tol=1e-4):
            self.last_update_timestamp = p_game_state.timestamp
            self._update_ai(p_game_state)
            self.coach_command_sender.generate_and_send_commands(p_game_state)
        else:
            pass

    def halt(self):
        """ Hack pour sync les frames de vision et les itérations de l'IA """
        pass

    def stop(self, game_state):
        """ *Devrait* déinit pour permettre un arrêt propre. """
        pass

    @property
    def robot_commands(self):
        return self.coach_command_sender.robot_commands

    def get_debug_commands_and_clear(self):
        """ Élément de l'interface entre RULEngine/StrategyIA """
        if self.debug_manager:
            debug_commands = self.debug_manager.get_commands()
            return debug_commands
        else:
            return []

    def _init_intelligent_modules(self):
        self.info_manager.register_module('InfluenceMap', InfluenceMap)
        self.info_manager.register_module('Pathfinder', PathfinderRRT)

    def _init_ui_debug(self):
        # FIXME: exécuter uniquement sur handshake plutôt qu'à l'init du coach
        cmd_tactics = {'strategy': StrategyBook(self.info_manager).get_strategies_name_list(),
                       'tactic': TacticBook().get_tactics_name_list(),
                       'action': ['None']}
        cmd = DebugCommand(1001, cmd_tactics)
        self.debug_manager.add_odd_command(cmd)

    def _update_ai(self, p_game_state):
        """ Effectue une itération de mise à jour de l'ia. """
        self.info_manager.update(p_game_state)
        self.debug_executor.exec()
        self.module_executor.exec()
        self.strategy_executor.exec()


class CoachCommandSender(object):
    """
        Construit les commandes et les places dans un champ pour que Framework
        puissent les envoyer aux robots.
    """

    def __init__(self, p_info_manager):
        self.game_state = None
        self.info_manager = p_info_manager
        self.current_player_id = None
        self.robot_commands = []

    def generate_and_send_commands(self, p_game_state):
        self.game_state = p_game_state
        self._clear_commands()
        for i in range(len(self.game_state.friends.players)):
            self.current_player_id = i
            next_action = self.info_manager.get_player_next_action(i)
            command = self._generate_command(next_action)
            self.robot_commands.append(command)

    def _clear_commands(self):
        self.robot_commands = []

    def _generate_command(self, p_next_action):
        if p_next_action is not None:
            if p_next_action.kick_strength > 0:
                return self._generate_kick_command(p_next_action.kick_strength)
            elif p_next_action.move_destination:
                assert(isinstance(p_next_action.move_destination, Pose))
                return self._generate_move_command(p_next_action.move_destination)
            else:
                return self._generate_empty_command()
        else:
            return self._generate_empty_command()

    def _generate_kick_command(self, p_kick_strength):
        kick_strength = self._sanitize_kick_strength(p_kick_strength)

        return command.Kick(self._get_player(), kick_strength)

    def _generate_move_command(self, p_move_destination):
        return command.MoveToAndRotate(self._get_player(), p_move_destination)

    def _generate_empty_command(self):
        # Envoi d'une command vide qui fait l'arrêt du robot
        return command.Stop(self._get_player())

    def _get_player(self):
        return self.game_state.friends.players[self.current_player_id]

    def _sanitize_kick_strength(self, p_kick_strength):
        if p_kick_strength > 1:
            return 1
        else:
            return p_kick_strength
