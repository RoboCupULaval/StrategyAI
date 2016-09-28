# Under MIT license, see LICENSE.txt

from ai.Algorithm.Node import Node
from ai.Algorithm.Vertex import Vertex

__author__ = 'RoboCupULaval'


class Graph:
    """
    Graph:
    Méthodes:
        add_node: Ajoute un noeud au graphe.
        remove_node: Retire un noeud du graphe.
        add_vertex: Ajoute un vertex entre deux noeuds du graphe.
        remove_vertex: Retire un vertex entre deux noeuds du graphe.
        exec: Appelle la méthode exec du noeud courant et effectue la transition vers un noued suivant si nécessaire.
        set_current_node: Change le noeud courant du graphe.
        __str__: Retourne une représentation du graphe sous forme d'une chaîne de caractères.
    Attributs:
        nodes: Une liste des noeuds du graphe.
        current_node: L'index du noeud courant dans la liste des noeuds.
    """
    def __init__(self):
        self.nodes = []
        self.current_node = 0

    def add_node(self, p_node):
        """
        Ajoute un noeud à la liste de noeud du graphe.
        :param p_node: Le noeud à ajouter.
        """
        assert isinstance(p_node, Node)
        self.nodes.append(p_node)

    def remove_node(self, p_node_index):
        """
        Retire un noeud de la liste de noeuds, puis détruit tous les vertices pointant vers ce noeud.
        :param p_node_index: L'index du noeud à retirer dans la liste de noeuds.
        """
        assert isinstance(p_node_index, int)
        assert 0 <= p_node_index < len(self.nodes)
        for i in range(len(self.nodes)):
            self.remove_vertex(i, p_node_index)
        self.nodes.pop(p_node_index)

    def add_vertex(self, p_starting_node, p_ending_node, p_condition):
        """
        Ajoute un vertex entre deux noeuds du graphe. Il ne peut y avoir qu'un seul vertex entre deux noeuds donnés dans
        un certain sens. Si on en ajoute un autre, celui-ci remplacera l'ancien.
        :param p_starting_node: L'index du noeud de départ dans la liste de noeuds.
        :param p_ending_node: L'index du noeud d'arrivée dans la liste de noeuds.
        :param p_condition: Une fonction retournant un booléen indiquant si on peut passer au noeud suivant.
        """
        assert isinstance(p_starting_node, int)
        assert 0 <= p_starting_node < len(self.nodes)
        assert isinstance(p_ending_node, int)
        assert 0 <= p_ending_node < len(self.nodes)
        assert callable(p_condition)
        self.nodes[p_starting_node].add_vertex(Vertex(p_ending_node, p_condition))

    def remove_vertex(self, p_starting_node, p_ending_node):
        """
        Retire un vertex entre deux noeuds du graphe.
        :param p_starting_node: L'index du noeud de départ dans la liste de noeuds.
        :param p_ending_node: L'index du noeud d'arrivée dans la liste de noeuds.
        """
        assert isinstance(p_starting_node, int)
        assert 0 <= p_starting_node < len(self.nodes)
        assert isinstance(p_ending_node, int)
        assert 0 <= p_ending_node < len(self.nodes)
        self.nodes[p_starting_node].remove_vertex(p_ending_node)

    def exec(self):
        """
        Appelle la méthode exec du noeud courant et effectue la transition vers un noued suivant si une des conditions
        est remplie, ce qui a pour effet de changer la tactique en cours.
        """
        next_ai_command, next_node = self.nodes[self.current_node].exec()
        if next_node != -1:
            self.set_current_node(next_node)

        return next_ai_command

    def set_current_node(self, node_index):
        """
        Change le noeud courant du graphe, ce qui a pour effet de changer la tactique en cours.
        :param node_index: L'index du prochain noeud courant dans la liste de noeuds.
        """
        assert isinstance(node_index, int)
        assert 0 <= node_index < len(self.nodes)
        self.current_node = node_index

    def __str__(self):
        """
        :return: Une représentation du graphe sous forme d'une chaîne de caractères.
        """
        output_string = ""
        for i in range(len(self.nodes)):
            output_string += "Node " + str(i) + ": " + str(self.nodes[i]) + "\n"
        return output_string
