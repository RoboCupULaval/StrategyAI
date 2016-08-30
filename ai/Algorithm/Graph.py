# Under MIT license, see LICENSE.txt

from ai.STA.Tactic.Tactic import Tactic

__author__ = 'RoboCupULaval'


class Vertex:
    """
    Vertex: Arête orientée et unidirectionnelle reliant deux noeuds du graphe. Le vertex possède une condition qui doit
            être respectée pour passée au noeud suivant. Cette condition prend la forme d'une fonction retournant un
            booléen.
    Méthodes:
        evaluate_condition(self): Évalue si la condition pour passer au noeud suivant est respectée. Cette méthode
                                  appelle la fonction de condition et retourne son résultat.
        __str__(self): Retourne une représentation du vertex sous forme de chaîne de caractères.
    Attributs:
        next_node: Le numéro du noeud suivant, pointé par l'extrémité du vertex.
        condition: Une fonction retournant un booléen indiquant si on peut passer au noeud suivant.
    """
    def __init__(self, p_next_node, p_condition):
        assert isinstance(p_next_node, int)
        assert p_next_node >= 0
        assert callable(p_condition)

        self.next_node = p_next_node
        self.condition = p_condition

    def evaluate_condition(self):
        return self.condition()

    def __str__(self):
        return "Next node: " + str(self.next_node) + " Condition: " + self.condition.__name__


class Node:
    def __init__(self, p_tactic):
        assert isinstance(p_tactic, Tactic)
        self.tactic = p_tactic
        self.vertices = []

    def add_vertex(self, p_vertex):
        assert isinstance(p_vertex, Vertex)
        for i in range(len(self.vertices)):
            if self.vertices[i].next_node == p_vertex.next_node:
                self.vertices[i] = p_vertex
                return
        self.vertices.append(p_vertex)

    def remove_vertex(self, p_ending):
        assert isinstance(p_ending, int)
        pass

    def evaluate(self):
        for vertex in self.vertices:
            if vertex.evaluate_condition():
                return vertex.next
        return -1

    def __str__(self):
        return_string = "Tactic: " + str(self.tactic) + " Vertices: "
        for vertex in self.vertices:
            return_string += "\n" + str(vertex)
        return return_string


class Graph:
    def __init__(self):
        self.nodes = []
        self.current_node = 0

    def add_node(self, p_node):
        assert isinstance(p_node, Node)
        self.nodes.append(p_node)

    def remove_node(self):
        pass

    def add_vertex(self, p_starting_node, p_ending_node, p_condition):
        assert isinstance(p_starting_node, int)
        assert 0 <= p_starting_node < len(self.nodes)
        assert isinstance(p_ending_node, int)
        assert 0 <= p_ending_node < len(self.nodes)
        assert callable(p_condition)
        self.nodes[p_starting_node].add_vertex(Vertex(p_ending_node, p_condition))

    def remove_vertex(self, p_starting_node, p_ending_node):
        assert isinstance(p_starting_node, int)
        assert 0 <= p_starting_node < len(self.nodes)
        assert isinstance(p_ending_node, int)
        assert 0 <= p_ending_node < len(self.nodes)
        self.nodes[p_starting_node]

    def evaluate(self):
        next_node = self.nodes[self.current_node].evaluate()
        if next_node == -1:
            return
        else:
            self.switch_node(next_node)

    def switch_node(self, node):
        assert isinstance(node, int)
        assert 0 <= node < len(self.nodes)
        self.current_node = node
