"""
    Module définissant les **Exception** du moteur de l'intelligence
    artificielle et des stratégies.
"""

class InvalidDebugType(Exception):
    """ Est levée si un paquet de débogage n'a pas le bon type. """
    pass

class StopPlayerError(Exception):
    """
        Est levée si le moteur est incapable d'envoyer la commande pour arrêter
        les joueurs.
    """
    pass

class NonExistentModule(Exception):
    """ Est levé par l'InfoManager quand un module intelligent n'existe pas. """
    pass
