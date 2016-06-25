# Under MIT License, see LICENSE.txt
""" Module supérieur de l'IA """

from RULEngine.Command import Command

import ai.executor as executor
from ai.InfoManager import InfoManager

__author__ = 'RoboCupULaval'

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
        self.info_manager = InfoManager(is_debug=True)
        self.module_executor = executor.ModuleExecutor(self.info_manager)
        self.strategy_executor = executor.StrategyExecutor(self.info_manager)
        self.tatic_executor = executor.TacticExecutor(self.info_manager)
        self.pathfinder_executor = executor.PathfinderExecutor(self.info_manager)
        self.coach_command_sender = CoachCommandSender(self.info_manager)
        self._init_intelligent_modules()

    def on_start(self, p_game_state):
        """ *État* actif du **Coach**. """
        self._update_ai(p_game_state)
        self.coach_command_sender.generate_and_send_commands(p_game_state)


    def on_halt(self, game_state):
        self.on_start(game_state)

    def on_stop(self, game_state):
        self.on_start(game_state)

    @property
    def commands(self):
        return self.coach_command_sender.commands

    def _init_intelligent_modules(self):
        self.info_manager.register_module('Pathfinder', None)

    def _update_ai(self, p_game_state):
        """ Effectue une itération de mise à jour de l'ia. """
        self.info_manager.update(p_game_state)
        self.strategy_executor.exec()
        self.tatic_executor.exec()
        # TODO: Optimiser les moments de mises à jours des modules intelligents
        self.module_executor.exec()
        self.pathfinder_executor.exec()

class CoachCommandSender(object):
    
    def __init__(self, p_info_manager):
        self.game_state = None
        self.info_manager = p_info_manager
        self.current_player_id = None
        self.commands = []

    def generate_and_send_commands(self, p_game_state):
        self.game_state = p_game_state
        self._clear_commands()
        for i in range(6):
            self.current_player_id = i
            next_action = self.info_manager.get_player_next_action(i)
            command = self._generate_command(next_action)
            self.commands.append(command)

    def _clear_commands(self):
        self.commands = []

    def _generate_command(self, p_next_action):
        if p_next_action.kick_strength > 0:
            return self._generate_kick_command(p_next_action.kick_strength)
        else:
            return self._generate_move_command(p_next_action.move_destination)

    def _generate_kick_command(self, p_kick_strength):
        kick_strength = self._sanitize_kick_strength(p_kick_strength)

        return Command.Kick(self._get_player(), kick_strength)

    def _generate_move_command(self, p_move_destination):
        return Command.MoveToAndRotate(self._get_player(), p_move_destination)

    def _get_player(self):
        # FIXME: On ne parle qu'à ses amis
        return self.game_state.friends.players[self.current_player_id]


    def _sanitize_kick_strength(self, p_kick_strength):
        if p_kick_strength > 1:
            return 1
        else:
            return p_kick_strength
