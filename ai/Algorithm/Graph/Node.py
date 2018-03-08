# Under MIT license, see LICENSE.txt

from ai.Algorithm.Graph.Vertex import Vertex
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from typing import Callable


class Node:
    """
    Node: Noeud d'un graphe simple orienté représentant la tactique en cours. Il ne peut y avoir qu'un seul vertex entre
          deux noeuds donnés dans un certain sens (ex: un seul vertex du noeud 1 au noeud 2, mais il peut y en avoir un
          du noeud 2 au noeud 1 aussi.
    Méthodes:
        add_vertex: Ajoute un vertex au noeud.
        remove_vertex: Retire un vertex du noeud.
        exec: Évalue si on peut passer à un noeud suivant et exécute la tactique.
        __str__: Retourne une représentation du noeud sous forme d'une chaîne de caractères.
    Attributs:
        tactic: La tactique du noeud.
        vertices: Une liste de vertex reliant le noeud courant aux noeuds adjacents.
    """
    def __init__(self, p_tactic):
        """
        :param p_tactic: La tactique du noeud.
        """
        # print(p_tactic)
        assert isinstance(p_tactic, Tactic)
        self.tactic = p_tactic
        self.vertices = []

    def add_vertex(self, p_vertex):
        """
        Ajoute un vertex au noeud. Comme il ne peut y avoir qu'un seul vertex entre deux noeuds donnés dans un certain
        sens, si on ajoute un autre vertex, il remplacera l'ancien.
        :param p_vertex: Le vertex à ajouter.
        """
        assert isinstance(p_vertex, Vertex)
        for i in range(len(self.vertices)):
            if self.vertices[i].next_node == p_vertex.next_node:
                self.vertices[i] = p_vertex
                return
        self.vertices.append(p_vertex)

    def connect_to(self, dst_node, when: Callable[..., bool]):
        self.add_vertex(Vertex(dst_node, when))

    def remove_vertex(self, p_ending):
        """
        Retire un vertex du noeud, spécifié par le numéro de son noeud d'arrivé. Si le noeud courant ne possède pas de
        vertex vers le noeud spécifé, rien ne se passe.
        :param p_ending: Un entier positif représentant le numéro du noeud d'arrivé du vertex à retirer.
        """
        assert isinstance(p_ending, int)
        assert 0 <= p_ending
        for i in range(len(self.vertices)):
            if self.vertices[i].next_node == p_ending:
                self.vertices.pop(i)

    def exec(self):
        """
        Fait avancer la machine d'état de la tactique d'une itération et évalue la condition de chacun des vertices du
        noeud afin de déterminer si on peut passer à un noeud suivant.
        :return: Un tuple contenant la prochaine commande à envoyer au robot et le numéro du noeud pointé par le vertex
        dont la condition est remplie, sous forme de int. Ce numéro vaut -1 si aucune condition n'est remplie.
        """
        next_ai_command = self.tactic.exec()
        for vertex in self.vertices:
            if vertex.evaluate_condition():
                return next_ai_command, vertex.next_node
        return next_ai_command, self

    def set_flag(self, status_flag):
        """
        Modifie l'attribut status flag de la tactique du noeud.
        :param status_flag: Une valeur de l'enum Flags de tactic_constant
        """
        assert isinstance(status_flag, Flags)
        self.tactic.status_flag = status_flag

    def __str__(self):
        """
        :return: Une représentation du noeud sous forme d'une chaîne de caractères.
        """
        output_string = "Tactic: " + str(self.tactic) + "/ Vertices: "
        for vertex in self.vertices:
            output_string += "\n    " + str(vertex)
        return output_string
