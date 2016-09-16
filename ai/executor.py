# Under MIT License, see LICENSE.txt
""" Module contenant les Executors """

from abc import abstractmethod, ABCMeta

from .Util.types import AICommand

from .STA.Strategy.StrategyBook import StrategyBook
from .STA.Tactic.TacticBook import TacticBook
from .STA.Tactic import tactic_constants
from .STA.Tactic.GoGetBall import GoGetBall
from .STA.Tactic.GoalKeeper import GoalKeeper
from .STA.Tactic.GoToPosition import GoToPosition
from .STA.Tactic.Stop import Stop
from .STA.Tactic.CoverZone import CoverZone

from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.constant import *


__author__ = 'RoboCupULaval'

class Executor(object, metaclass=ABCMeta):
    """ Classe abstraite des executeurs. """

    def __init__(self, info_manager):
        self.info_manager = info_manager

    @abstractmethod
    def exec(self):
        """ Méthode qui sera appelé à chaque coup de boucle. """
        pass

class StrategyExecutor(Executor):
    """
        StrategyExecutor est une classe du **Behavior Tree** qui s'occupe de
        déterminer la stratégie à choisir selon l'état de jeu calculé et
        d'assigner les tactiques aux robots pour optimiser les ressources.
    """
    def __init__(self, info_manager):
        """ Constructeur de la classe.
            :param info_manager: Référence à la facade InfoManager pour pouvoir
            accéder aux informations du GameState.
        """
        Executor.__init__(self, info_manager)
        self.strategic_state = self.info_manager.get_strategic_state() #ref au module intelligent
        self.strategy = None

    def exec(self):
        """
            #1 Détermine la stratégie en cours
            #2 Assigne les tactiques aux robots
        """
        self._set_strategy()
        self._assign_tactics()

    def _set_strategy(self):
        """
            Récupère l'état stratégique en cours, le score SWOT et choisit la
            meilleure stratégie pour le contexte.
        """
        if not self.info_manager.debug_manager.human_control:
            self.strategy_book = StrategyBook(self.info_manager)
            self.strategy = self.strategy_book.get_optimal_strategy()(self.info_manager)
        elif not self.info_manager.debug_manager.tactic_control:
            self.strategy = self.info_manager.strategy(self.info_manager)
        else:
            pass

    def _assign_tactics(self):
        """
            Détermine à quel robot assigner les tactiques de la stratégie en
            cours.
        """
        tactic_sequence = []
        try:
            tactic_sequence = self.strategy.get_next_tactics_sequence()
        except AttributeError:
            for i in range(0, 6):
                tactic_sequence.append(Stop(self.info_manager, i))

        if not self.info_manager.debug_manager.tactic_control:
            for i in range(0, 6):
                tactic = tactic_sequence[i]
                tactic.player_id = i
                self.info_manager.set_player_tactic(i, tactic_sequence[i])


class TacticExecutor(Executor):
    """ Fait avancer chaque FSM d'une itération. """
    def __init__(self, info_manager):
        """ Constructeur.
            :param info_manager: Référence à la facade InfoManager pour pouvoir
            accéder aux informations du GameState.
        """
        Executor.__init__(self, info_manager)

    def exec(self):
        """ Obtient la Tactic de chaque robot et fait progresser la FSM. """
        for player_id in range(0, 6):
            ai_command = self.info_manager.get_player_tactic(player_id).exec()
            self.info_manager.set_player_next_action(player_id, ai_command)

class ModuleExecutor(Executor):
    """ Met à jour tous les modules intelligents enregistré. """
    def __init__(self, info_manager):
        Executor.__init__(self, info_manager)

    def exec(self):
        modules = self.info_manager.modules
        for key in modules:
            try:
                modules[key].update()
            except:
                pass

class DebugExecutor(Executor):
    """ S'occupe d'interpréter les commandes de debug """
    def __init__(self, info_manager):
        Executor.__init__(self, info_manager)
        self.debug_manager = self.info_manager.debug_manager

    def exec(self):
        if self.debug_manager.human_control:
            self._exec_when_human_control()
        else:
            pass
        self._send_robot_status()

    def _exec_when_human_control(self):
        debug_commands = self.debug_manager.get_ui_commands()
        for cmd in debug_commands:
            self._parse_command(cmd)

    def _parse_command(self, cmd):
        if cmd.is_strategy_cmd():
            self._parse_strategy(cmd)
            self.info_manager.debug_manager.set_tactic_control(False)
        elif cmd.is_tactic_cmd():
            self.info_manager.debug_manager.set_tactic_control(True)
            pid = self._sanitize_pid(cmd.data['id'])
            tactic_name = cmd.data['tactic']
            tactic_ref = self._parse_tactic(tactic_name, pid, cmd.data)
            self.info_manager.set_player_tactic(pid, tactic_ref)
        else:
            pass

    def _parse_strategy(self, cmd):
        strategy_key = cmd.data['strategy']
        if strategy_key == 'pStop':
            self.info_manager.strategy = StrategyBook(self.info_manager).get_strategy('DoNothing')
        else:
            self.info_manager.strategy = StrategyBook(self.info_manager).get_strategy(strategy_key)

    def _parse_tactic(self, tactic_name, pid, data):
        # TODO: redéfinir le paquet pour set une tactique pour que les données supplémentaire
        # soit un tuple
        target = data['target']
        tactic_ref = None
        if tactic_name == "goto_position":
            tactic_ref = GoToPosition(self.info_manager, pid, Pose(Position(target[0], target[1]), self.info_manager.get_player_pose(pid).orientation))
        elif tactic_name == "goalkeeper":
            tactic_ref = GoalKeeper(self.info_manager, pid)
        elif tactic_name == "cover_zone":
            tactic_ref = CoverZone(self.info_manager, pid, FIELD_Y_TOP, FIELD_Y_TOP/2, FIELD_X_LEFT, FIELD_X_LEFT/2)
        elif tactic_name == "get_ball":
            tactic_ref = GoGetBall(self.info_manager, pid)
        elif tactic_name == "tStop":
            tactic_ref = Stop(self.info_manager, pid)
        else:
            tactic_ref = Stop(self.info_manager, pid)

        return tactic_ref

    def _sanitize_pid(self, pid):
        if pid >= 0 and pid < 6:
            return pid
        elif pid >= 6 and pid < 12:
            return pid - 6
        else:
            return 0

    def _send_robot_status(self):
        for player_id in range(6):
            robot_tactic = self.info_manager.get_player_tactic(player_id)
            robot_tactic_name = 'None'
            robot_action = 'None'
            robot_target = (0, 0)
            try:
                robot_tactic_name = robot_tactic.__class__.__name__
                robot_action = robot_tactic.current_state.__name__
                robot_target = robot_tactic.target.to_tuple()
            except AttributeError:
                robot_tactic_name = 'None'
                robot_action = 'None'

            self.info_manager.debug_manager.send_robot_status(player_id, robot_tactic_name, str(robot_action), robot_target)
