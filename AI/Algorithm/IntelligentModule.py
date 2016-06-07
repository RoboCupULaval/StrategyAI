# Under MIT license, see LICENSE.txt
"""
    Contient la classe mère pour les modules intelligents.
"""
from abc import abstractmethod

__author__ = 'RoboCupULaval'

class IntelligentModule(object):
    """
        Cette classe mère des modules intelligents.
        Actuellement ne défini que l'attribut *state*
    """

    def __init__(self, pInfoManager):
        """
            Reçoit une référence vers InfoManager. Cette référence est rennomée
            comme étant *state*.

            :param pInfoManager: Référence vers l'InfoManager
        """

        self.state = pInfoManager

    def get_info_manager(self):
        """ Retourne la référence de l'InfoManager """
        return self.state

    @abstractmethod
    def str(self):
        """ Ne pas utiliser """
