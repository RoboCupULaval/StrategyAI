#Under MIT License, see LICENSE.txt
# TODO: Execeptions personnalisees pour les edges cases (ex: current_skill == None)

from AI.Executor.Executor import Executor

__author__ = 'RoboCupULaval'


class SkillExecutor(Executor):
    """
    SkillExecutor est une sequence de requetes qui choisie la prochaine
    pose pour chaque joueur.

    1 - Quelle est l'action du joueur?
    2 - Quelle est la cible du joueur?
    3 - Quel est le but du joueur ?
    4 - Avoir l'objet action
    5 - Generer la pose suivante
    6 - Mettre en place la pose suivante
    """
    def __init__(self, info_manager):
        Executor.__init__(self, info_manager)

    def exec(self):
        # Execution pour chaque joueur
        for id_player in range(self.info_manager.get_count_player()):
            # 1 - Quelle est l'action du joueur ?
            current_skill = self.info_manager.get_player_skill(id_player)

            # 2 - Quelle est la cible du joueur ?
            current_target = self.info_manager.get_player_target(id_player)

            # 3 - Quel est le but du joueur ?
            current_goal = self.info_manager.get_player_goal(id_player)

            # 4 - Avoir l'objet action
            skill = self.skill_book[current_skill]

            current_pose = self.info_manager.get_player_pose(id_player)
            # 5 - Generer la pose suivante
            next_pose = skill().act(current_pose, current_target, current_goal)

            # 6 - Mettre en place la pose suivante
            if next_pose is not None:
                self.info_manager.set_player_next_action(id_player, next_pose)
