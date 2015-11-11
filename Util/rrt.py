__author__ = 'agingrasc'

from types import isinstance

class Tree:
    """
    Implemente un arbre a branche multiple pour supporter le pathfinder RRT
    """
    def __init__(self, data):
        self.root = None
        if isinstance(data, tuple):
            self.data = data
        else
            raise TypeError
        self.childs = [] #sub RRT

    def find_nearest(self, path):
        return None

    def __eq__(self, obj):
        x1, y1 = self.data
        x2, y2 = obj.data
        ret = False
        if x1 == x2 and y1 == y2:
            ret = True

        return ret

    def __lt__(self, obj):
        x1, y1 = self.data
        x2, y2 = self.data
        ret = False
        if x1 >= x2:
            if y1 >= y2:
                ret = False
            else:
                ret = True
        else:
            ret = True

        return ret

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
        for i in len(self.childs):
            ret += str(self.childs[i])
