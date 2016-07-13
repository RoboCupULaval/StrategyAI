# Under MIT License, see LICENSE.txt
""" Module contenant les Executors """

from abc import abstractmethod, ABCMeta
from .STA.Strategy.StrategyBook import StrategyBook

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
        # TODO: rendre dynamique
        self.strategy = StrategyBook().get_strategy("HumanControl")(self.info_manager)

    def _assign_tactics(self):
        """
            Détermine à quel robot assigner les tactiques de la stratégie en
            cours.
        """
        tactic_sequence = self.strategy.get_next_tactics_sequence()
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
        for i in range(0, 6):
            self.info_manager.get_player_tactic(i).exec()


class PathfinderExecutor(Executor):
    """ Récupère les paths calculés pour les robots et les assignent. """

    def __init__(self, info_manager):
        Executor.__init__(self, info_manager)
        self.pathfinder = None

    def exec(self):
        """
            Appel le module de pathfinder enregistré pour modifier le mouvement
            des joueurs de notre équipe.
        """
        self.pathfinder = self.info_manager.acquire_module('Pathfinder')
        if self.pathfinder: # on desactive l'executor si aucun module ne fournit de pathfinding
            paths = self.pathfinder.get_paths()
            for i in range(0, 6):
                self.info_manager.set_player_next_action(paths[i])


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
                print("Un module est défini à None, clef: " + str(key))


