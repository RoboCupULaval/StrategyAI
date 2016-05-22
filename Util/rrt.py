Under MIT License, see LICENSE.txt
__author__ = 'agingrasc'

from types import *
import math

class Tree:
    """
    Implemente un arbre a branche multiple pour supporter le pathfinder RRT
    """
    def __init__(self, data):
        self.root = None
        if isinstance(data, tuple):
            self.data = data
        else:
            raise TypeError
        self.childs = [] #sub RRT

    def add(self, data):
        t = Tree(data)
        t.root = self

        nbr_childs = len(self.childs)
        for i in range(nbr_childs):
            if t < self.childs[i]:
                self.childs.insert(i, t)

        if nbr_childs == len(self.childs):
            self.childs.append(t)


    def get_childs(self):
        return self.childs

    def find_nearest(self, path):
        norm = self.norm(path, self.data)
        candidate = self.data
        for i in self.childs:
            t_candidate = i.find_nearest(path)
            t_norm = self.norm(path, t_candidate)
            if norm > t_norm:
                norm = t_norm
                candidate = t_candidate
        return candidate

    def find(self, data):
        all_nodes = self.get_all_nodes()
        all_data = map(lambda t: t.data, all_nodes)
        if data in all_data:
            for i in all_nodes:
                if i.data == data:
                    return i
        else:
            return None

    def get_all_nodes(self):
        ret = [self]
        for i in self.childs:
            ret += i.get_all_nodes()

        return ret

    def norm(self, p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        x = x1 - x2
        y = y1 - y2
        return math.sqrt(x*x + y*y)

    def __eq__(self, obj):
        x1, y1 = self.data
        x2, y2 = obj.data
        ret = False
        if x1 == x2 and y1 == y2:
            ret = True

        return ret

    def __lt__(self, obj):
        x1, y1 = self.data
        x2, y2 = obj.data
        return x1 < x2 or (x1 == x2 and y1 < y2)

    def __le__(self, obj):
        return self < obj or self == obj

    def __gt__(self, obj):
        return not self < obj and not self == obj

    def __ge__(self, obj):
        return self > obj or self == obj

    def __ne__(self, obj):
        return not self == obj

    def __str__(self):
        ret = str(self.data) + "\n"
        if len(self.childs) > 0 :
            for i in len(self.childs):
                ret += str(self.childs[i])
        return ret
