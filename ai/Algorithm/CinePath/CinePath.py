from math import pi, cos, sin
from RULEngine.Util.geometry import get_distance, get_angle
from RULEngine.Util.Position import Position


class CinePath:
    def __init__(self, world_state):
        self.game = world_state.game_state
        self.__path = [[] for _ in range(6)]
        self.__ratio = 1.0
        self.__max_t = 2.0
        self.__max_speed = 500.0
        self.__reso = 10
        self.__max_acc = 2000.0 * self.__ratio

    def create_circle_with_tzone(self, bot_player, t_zone):
        p1 = bot_player.velocity._getlength() * t_zone - 0.5 * self.__max_acc * t_zone ** 2
        p2 = bot_player.velocity._getlength() * t_zone + 0.5 * self.__max_acc * t_zone ** 2
        p2_max_speed = self.__max_speed * t_zone
        print(t_zone, p2, p2_max_speed)
        p2 = min([p2, p2_max_speed])
        rayon = (p2 - p1) / 2
        x = bot_player.pose.position.x + (p1 + rayon) * cos(bot_player.velocity.direction)
        y = bot_player.pose.position.y + (p1 + rayon) * sin(bot_player.velocity.direction)
        return Cercle(Position(x, y), rayon)

    def get_path_to(self, id_bot, final_pst):
        path = []
        for i in range(1, 25):
            circle = self.create_circle_with_tzone(self.game.get_player(id_bot, True), i * self.__max_t / self.__reso)
            path.append(circle.stay_inside(final_pst))
            if circle.is_inside(final_pst):
                break
        self.__path[id_bot] = path.copy()
        return path.copy()


class Cercle:
    def __init__(self, pt_centre=None, rayon=None):
        if pt_centre is not None and rayon is not None:
            assert type(pt_centre).__name__ == Position.__name__
            assert isinstance(rayon, (int, float))
            assert rayon >= 0
        self.centre = pt_centre
        self.rayon = rayon
        self.marque = None

    def get_mark(self, angle, pond):
        x = pond * self.rayon * cos(angle)
        y = pond * self.rayon * sin(angle)
        return Position(self.centre.x + x, self.centre.y + y)

    def mark(self, point):
        self.marque = point

    def get_score(self):
        return get_angle(self.centre, self.marque), get_distance(self.centre, self.marque) / self.rayon

    def is_inside(self, pt):
        dst = get_distance(self.centre, pt)
        return dst < self.rayon

    def is_outside(self, pt):
        return not self.is_inside(pt)

    def is_cover_by(self, circle):
        dst = get_distance(self.centre, circle.centre)
        return circle.rayon > dst + self.rayon

    def __str__(self):
        return "#> Cercle\n#> Centre:{}\n#> Rayon:{}\n---------".format(self.centre, self.rayon)

    def stay_outside(self, point):
        if self.is_inside(point):
            agl = get_angle(self.centre, point)
            x = self.centre.x + self.rayon * cos(agl)
            y = self.centre.y + self.rayon * sin(agl)
            return Position(x, y)
        else:
            return Position(point.x, point.y)

    def stay_inside(self, point):
        if self.is_outside(point):
            agl = get_angle(self.centre, point)
            x = self.centre.x + self.rayon * cos(agl)
            y = self.centre.y + self.rayon * sin(agl)
            return Position(x, y)
        else:
            return Position(point.x, point.y)