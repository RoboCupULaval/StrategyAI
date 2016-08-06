# Under MIT license, see LICENSE.txt
""" Livre des stratégies. """

from . strategy_conditionals import *

# import strategies
from . HumanControl import HumanControl

class StrategyBook(object):
    """
        Cette classe est capable de récupérer les stratégies enregistrés dans la
        configuration des stratégies et de les exposer au Behavior Tree en
        charge de sélectionner la stratégie courante.
    """

    def __init__(self, p_info_manager):
        self.info_manager = p_info_manager

    def ball_in_offense_zone(self):
        self.team_zone_side = "left"  # constante bidon TODO: trouver une facon de demander au InfoManager notre zone initiale
        self.ball_x_position = self.info_manager.get_ball_position().x

        if self.team_zone_side == "left":
            return self.ball_x_position > 0
        return self.ball_x_position < 0

    def most_opponents_in_our_zone(self):
        pass

    def get_optimal_strategy(self):

        # simple choice
        if self.ball_in_offense_zone():
            self.chosen_strategy = HumanControl # offensive strat
        else:
            self.chosen_strategy = HumanControl # defensive strat

        return self.chosen_strategy