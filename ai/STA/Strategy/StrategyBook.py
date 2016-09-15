# Under MIT license, see LICENSE.txt
""" Livre des stratégies. """

from . HumanControl import HumanControl
from . SimpleDefense import SimpleDefense
from . SimpleOffense import SimpleOffense
from .DoNothing import DoNothing

class StrategyBook(object):
    """
        Cette classe est capable de récupérer les stratégies enregistrés dans la
        configuration des stratégies et de les exposer au Behavior Tree en
        charge de sélectionner la stratégie courante.
    """

    def __init__(self, p_info_manager):
        self.strategy_book = {'SimpleDefense' : SimpleDefense,
                              'SimpleOffense' : SimpleOffense,
                              'HumanControl' : HumanControl,
                              'DoNothing' : DoNothing}
        self.info_manager = p_info_manager

    def get_strategies_name_list(self):
        return list(self.strategy_book.keys())

    def ball_in_offense_zone(self):
        self.team_zone_side = "left"  # constante bidon TODO: trouver une facon de demander au InfoManager notre zone initiale
        self.ball_x_position = self.info_manager.get_ball_position().x

        if self.team_zone_side == "left":
            return self.ball_x_position >= -50
        return self.ball_x_position < -50

    def most_opponents_in_our_zone(self):
        pass

    def get_optimal_strategy(self):

        # simple choice
        if self.ball_in_offense_zone():
            self.chosen_strategy = SimpleOffense
        else:
            self.chosen_strategy = SimpleDefense

        self.chosen_strategy = DoNothing

        return self.chosen_strategy

    def get_strategy(self, strategy_name):
        self.strategy_book[strategy_name]

    def debug_show_all_players_tactics(self):
        for i in range(0,6):
            debug_string = ""
            debug_string += "Robot:" + str(i) + str(self.info_manager.get_player_tactic(i))
        print(debug_string)
