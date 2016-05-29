# Under MIT License, see LICENSE.txt
""" Cet Executor détermine selon les informations du GameState le prochain Play. """
from UltimateStrat.Executor.Executor import Executor


__author__ = 'RoboCupULaval'


class CoachExecutor(Executor):
    """ CoachExecutor est une série de requêtes pour choisir un Play.

    1 - Quel est le nouvel état?
    2 - Quel est le Play actuel?
    3 - Quel devrait être le nouveau Play?
    4 - Générer le Play selon le Play choisie et le GameState actuel.
    5 - Assigner le Play s'il est différent que l'actuel.
    """
    def __init__(self, info_manager):
        Executor.__init__(self, info_manager)

    def exec(self):
        # 1 - what's current state ?
        state = self.info_manager.get_next_state()

        # 2 - what's current play
        current_play = self.info_manager.get_current_play()

        # 3 - what's play with state ?
        play = self.info_manager.get_next_play(state)

        # 4 - compare current play and generate play
        if not current_play == play:
            # 5 - set play and init sequence if play is not same
            self.info_manager.set_play(play)
            self.info_manager.init_play_sequence()

