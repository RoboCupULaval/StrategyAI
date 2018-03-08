# Under MIT license, see LICENSE.txt

from ai.Algorithm.Graph.Node import Node
from ai.Algorithm.Graph.Vertex import Vertex
from ai.STA.Tactic.tactic_constants import Flags


class Graph:
    """
    Graph: Graphe simple orienté regroupant une série de noeuds contenant des tactiques. Les transitions entre les
           tactiques sont déterminées par des conditions associées aux vertices reliant les noeuds.
    Méthodes:
        get_current_tactic_name: Retourne le nom de la tactique en cours, sous forme d'une chaîne de caractères.
        get_current_tactic: Retourne la tactique en cours.
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
        self.current_node = None

    def get_current_tactic_name(self):
        """
        :return: Le nom de la tactique en cours, sous forme d'une chaîne de caractères.
        """
        if len(self.nodes) > 0:
            return str(self.current_node.tactic)
        else:
            return None

    def get_current_tactic(self):
        """
        :return: La tactique en cours.
        """
        if len(self.nodes) > 0:
            return self.current_node.tactic
        else:
            return None

    def add_node(self, p_node):
        """
        Ajoute un noeud à la liste de noeud du graphe.
        :param p_node: Le noeud à ajouter.
        """
        assert isinstance(p_node, Node)
        self.nodes.append(p_node)

        if len(self.nodes) > 0:
            self.set_current_node(p_node)

    def remove_node(self, dst_node):
        """
        Retire un noeud de la liste de noeuds, puis détruit tous les vertices pointant vers ce noeud.
        :param p_node_index: L'index du noeud à retirer dans la liste de noeuds.
        """
        assert isinstance(dst_node, Node)
        assert dst_node in self.nodes
        for src_node in self.nodes:
            self.remove_vertex(src_node, dst_node)
        self.nodes.pop(dst_node)

    def add_vertex(self, starting_node, ending_node, condition):
        """
        Ajoute un vertex entre deux noeuds du graphe. Il ne peut y avoir qu'un seul vertex entre deux noeuds donnés dans
        un certain sens. Si on en ajoute un autre, celui-ci remplacera l'ancien.
        :param p_starting_node: L'index du noeud de départ dans la liste de noeuds.
        :param p_ending_node: L'index du noeud d'arrivée dans la liste de noeuds.
        :param p_condition: Une fonction retournant un booléen indiquant si on peut passer au noeud suivant.
        """
        assert isinstance(starting_node, Node)
        assert starting_node in self.nodes
        assert isinstance(ending_node, Node)
        assert ending_node in self.nodes
        assert callable(condition)
        starting_node.add_vertex(Vertex(ending_node, condition))

    def remove_vertex(self, starting_node, ending_node):
        """
        Retire un vertex entre deux noeuds du graphe.
        :param p_starting_node: L'index du noeud de départ dans la liste de noeuds.
        :param p_ending_node: L'index du noeud d'arrivée dans la liste de noeuds.
        """
        assert isinstance(starting_node, Node)
        assert starting_node in self.nodes
        assert isinstance(ending_node, Node)
        assert ending_node in self.nodes
        starting_node.remove_vertex(ending_node)

    def exec(self):
        """
        Appelle la méthode exec du noeud courant et effectue la transition vers un noued suivant si une des conditions
        est remplie, ce qui a pour effet de changer la tactique en cours.
        """
        if len(self.nodes) > 0:
            next_ai_command, next_node = self.current_node.exec()
            if next_node != self.current_node:
                self.set_current_node(next_node)
            return next_ai_command
        else:
            raise EmptyGraphException("Le graph ne contient aucun noeud. "
                                      "(avez vous appliqué une tactique sur chacun des joueurs)")

    def set_current_node(self, node):
        """
        Change le noeud courant du graphe, ce qui a pour effet de changer la tactique en cours.
        :param node_index: L'index du prochain noeud courant dans la liste de noeuds.
        """
        assert isinstance(node, Node)
        assert node in self.nodes
        node.set_flag(Flags.INIT)
        self.current_node = node

    def __str__(self):
        """
        :return: Une représentation du graphe sous forme d'une chaîne de caractères.
        """
        output_string = ""
        for i in range(len(self.nodes)):
            output_string += "Node " + str(i) + ": " + str(self.nodes[i])
        return output_string


class EmptyGraphException(Exception):
    """ Est levée si la méthode exec d'un graph vide est appelée"""
    pass
