# Under MIT license, see LICENSE.txt


class Vertex:
    """
    Vertex: Arête orientée et unidirectionnelle reliant deux noeuds du graphe. Le vertex possède une condition qui doit
            être respectée pour passer au noeud suivant. Cette condition prend la forme d'une fonction retournant un
            booléen.
    Méthodes:
        evaluate_condition: Évalue si la condition pour passer au noeud suivant est respectée. Cette méthode
                                  appelle la fonction de condition et retourne son résultat.
        __str__: Retourne une représentation du vertex sous forme d'une chaîne de caractères.
    Attributs:
        next_node: Le numéro du noeud suivant, pointé par l'extrémité du vertex.
        condition: Une fonction retournant un booléen indiquant si on peut passer au noeud suivant.
    """
    def __init__(self, next_node, p_condition):
        """
        :param next_node: Un entier positif représentant le numéro du noeud suivant, pointé par l'extrémité du vertex.
        :param p_condition: Une fonction retournant un booléen indiquant si on peut passer au noeud suivant.
        """
        assert callable(p_condition)

        self.next_node = next_node
        self.condition = p_condition

    def evaluate_condition(self):
        """
        Évalue si la condition pour passer au noeud suivant est respectée. Cette méthode appelle la fonction de
        condition et retourne son résultat.
        :return: Un booléen indiquant si la condition pour passer au noeud suivant est remplie.
        """
        return self.condition()

    def __str__(self):
        """
        :return: Une représentation du vertex sous forme d'une chaîne de caractères.
        """
        return "Next node: " + str(self.next_node) + " Condition: " + self.condition.__name__
