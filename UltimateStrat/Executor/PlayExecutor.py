# Under MIT License, see LICENSE.txt
""" Executor qui se charge de mettre en place les Tactic d'un Play.
"""
from UltimateStrat.Executor.Executor import Executor

__author__ = 'RoboCupULaval'


class PlayExecutor(Executor):
    """ PlayExecutor est une série de requêtes qui sélectionnes les Tactic des
        joueurs.
    """
    def __init__(self, info_manager):
        """ Constructeur de la classe.

            :param info_manager: Référence à la facade InfoManager pour pouvoir
            accéder aux informations du GameState.
        """
        Executor.__init__(self, info_manager)

    def exec(self):
        """ Obtient le Play actuel, vérifie qu'il existe et assigne la Tactic
            appropriée à chaque robot.
        """
        # 1 - what's current play
        current_play = self.info_manager.getCurrentPlay()

        # 2 - what's current play sequence ?
        current_seq = self.info_manager.getCurrentPlaySequence()

        # 3 - get specific play sequence from play book
        play = self.play_book[current_play]

        # 4 - set tactics (str) for each players on black board
        for i, tactic in enumerate(play.getTactics(current_seq)):
            self.info_manager.setPlayerTactic(i, tactic)

