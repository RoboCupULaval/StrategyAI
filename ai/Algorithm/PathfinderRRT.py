# Under MIT License, see LICENSE.txt
"""
    Module intelligent contenant l'implementation d'un Rapidly exploring Random
    Tree. Le module contient une classe qui peut être instanciée et qui calcule
    les trajectoires des robots de l'équipe. Les détails de l'algorithme sont
    disponibles sur la page wikipedia.
"""
from .IntelligentModule import IntelligentModule
from ....Util import geometry

class PathfinderRRT(IntelligentModule):
    """
        La classe hérite de IntelligentModule pour définir sa propriété state.
        L'interface expose une méthode qui force le calcul de toutes les
        trajectoires. Celles-ci sont enregistrés par effet de bords dans le
        GameState.

        Une méthode permet de récupérer la trajectoire d'un robot spécifique.
    """

    def __init__(self, pInfoManager):
        """
            Constructeur, appel le constructeur de la classe mère pour assigner
            la référence sur l'InfoManager.

            :param pInfoManager: référence sur l'InfoManager
        """
        super().__init__(pInfoManager)
        self.paths = {}
        for i in range(6):
            self.paths[i] = []


    def _compute_path(self, pid):
        """
            Cette méthode calcul la trajectoire pour un robot.

            :param pid: L'identifiant du robot, 0 à 5.
            :return: None
        """
        pass

    def compute_paths(self):
        """
            Méthode qui lance le calcul de la trajectoire pour chaque robot de
            l'équipe.

            :return: None
        """
        pass

    def get_path(self, pid):
        """
            Retourne la trajectoire du robot.

            :param pid: Identifiant du robot, 0 à 5.
            :return: Une liste de Pose, [Pose]
        """
        pass

    def str(self):
        """ Affichage en String directe """
        return str(self.paths)
