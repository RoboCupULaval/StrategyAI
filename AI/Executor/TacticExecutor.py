# Under MIT License, see LICENSE.txt
""" Cet Executor se charge d'assigner les Skill aux robots en fonction de leur
    Tactic.
"""
from AI.Executor.Executor import Executor

__author__ = 'RoboCupULaval'


class TacticExecutor(Executor):
    """ TacticExecutor est une séquence de requêtes qui assigne un Skill à
        chaque robot.
    """
    def __init__(self, info_manager):
        """ Constructeur.

            :param info_manager: Référence à la facade InfoManager pour pouvoir
            accéder aux informations du GameState.
        """
        Executor.__init__(self, info_manager)

    def exec(self):
        """ Obtient la Tactic de chaque robot et calcul la Skill à assigner."""
        # Execution for each players
        for id_player in range(self.info_manager.get_count_player()):

            # 1 - what's player tactic ?
            current_tactic = self.info_manager.get_player_tactic(id_player)

            # 2 - get specific tactic from tactic book
            tactic = self.tactic_book[current_tactic]

            # 3 - select skill, target, goal from tactic object
            action = tactic().apply(self.info_manager, id_player)

            # 4 - set skill, target, goal
            self.info_manager.set_player_skill_target_goal(id_player, action)
