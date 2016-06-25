# Under MIT License, see LICENSE.txt
"""
    Ce module expose un tableau blanc qui centralise l'information liée à
    l'interface de debug. Il est géré par l'infoManager.
"""

from RULEngine.Util.debug_type import Log, Point, Circle, FigureInfo, TextInfo

class DebugManager:
    """
        DebugManager représente un infoManager spécialisé dans la
        gestion des informations retournées par l'interface de
        debug.
    """

    def __init__(self):
        self.logs = []
        self.influence_map = []
        self.text = []
        self.draw = []

    def get_logs(self):
        return self.logs

    def get_influence_map(self):
        return self.influence_map

    def get_text(self):
        return self.text

    def get_draw(self):
        return self.draw

    def clear(self):

        self._clear_draw()
        self._clear_influence_map()
        self._clear_logs()
        self._clear_text()

    def _clear_logs(self):
        self.logs = []

    def _clear_influence_map(self):
        self.influence_map = []

    def _clear_text(self):
        self.text = []

    def _clear_draw(self):
        self.draw = []

    def add_log(self, level, message):
        log = Log(level, message)
        self.logs.append(log)

    def add_point(self, x, y, width):
        point = Point(x, y, width)
        self.draw.append(point)

    def add_circle(self, center, radius, width):
        circle = Circle(center, radius, width)
        self.draw.append(circle)

    def add_figure(self, figure, color):
        figure = FigureInfo(figure, color)
        self.draw.append(figure)


    def add_influence_map(self, influence_map):
        # TODO implement
        pass

    def add_text(self, position, text, color):
        text = TextInfo(position, text, color)
        self.text.append(text)

