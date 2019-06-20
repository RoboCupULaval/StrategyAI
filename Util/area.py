from typing import Union

from Util.geometry import Position, Pose, Line, intersection_between_segments, intersection_between_line_and_segment, \
    closest_point_on_segment


class Area:
    def __init__(self, a, b):
        neg_x, pos_x = min(a.x, b.x), max(a.x, b.x)
        neg_y, pos_y = min(a.y, b.y), max(a.y, b.y)
        self.upper_left = Position(neg_x, pos_y)
        self.upper_right = Position(pos_x, pos_y)
        self.lower_right = Position(pos_x, neg_y)
        self.lower_left = Position(neg_x, neg_y)

    def point_inside(self, p: Position) -> bool:
        return self.left <= p.x <= self.right and \
               self.bottom <= p.y <= self.top

    def __str__(self):
        return f'Area(top={self.top}, bottom={self.bottom}, right={self.right}, left={self.left})'

    def __contains__(self, item: Union[Pose, Position]):
        if type(item) is Pose:
            return self.point_inside(item.position)
        elif type(item) is Position:
            return self.point_inside(item)
        else:
            raise ValueError('You can only test if a position or a pose is contained inside the area.')

    def intersect(self, seg: Line):
        assert isinstance(seg, Line)
        if self.point_inside(seg.p1) and self.point_inside(seg.p2):
            return []

        inters = []
        for segment in self.segments:
            inter = intersection_between_segments(segment.p1, segment.p2, seg.p1, seg.p2)
            if inter is not None:
                inters.append(inter)
        return inters

    def intersect_with_line(self, line: Line):
        assert isinstance(line, Line)

        inters = []
        for segment in self.segments:
            inter = intersection_between_line_and_segment(segment.p1, segment.p2, line.p1, line.p2)
            if inter is not None:
                inters.append(inter)
        return inters

    def closest_border_point(self, p: Position):
        closest_on_borders = None
        for segment in self.segments:
            closest_on_segment = closest_point_on_segment(p, segment.p1, segment.p2)
            if closest_on_borders is None or (closest_on_segment - p).norm < (closest_on_borders - p).norm:
                closest_on_borders = closest_on_segment
        return closest_on_borders

    @property
    def segments(self):
        return [Line(self.upper_left,  self.upper_right),
                Line(self.upper_right, self.lower_right),
                Line(self.lower_right, self.lower_left),
                Line(self.lower_left,  self.upper_left)]

    @property
    def center(self):
        return self.lower_left + Position(self.width / 2, self.height / 2)

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.top - self.bottom

    @property
    def top(self):
        return self.upper_left.y

    @property
    def bottom(self):
        return self.lower_right.y

    @property
    def left(self):
        return self.upper_left.x

    @property
    def right(self):
        return self.lower_right.x

    @classmethod
    def pad(cls, area, padding=0):
        return cls.from_limits(area.top + padding, area.bottom - padding,
                               area.right + padding, area.left - padding)

    @classmethod
    def from_limits(cls, top, bottom, right, left):
        return cls(Position(left, top), Position(right, bottom))

    @classmethod
    def flip_x(cls, area):
        return cls.from_limits(area.top, area.bottom, -area.left, -area.right)

    @classmethod
    def from_4_point(cls, p1, p2, p3, p4):
        top = max(p1.y, p2.y, p3.y, p4.y)
        bot = min(p1.y, p2.y, p3.y, p4.y)
        right = max(p1.x, p2.x, p3.x, p4.x)
        left = min(p1.x, p2.x, p3.x, p4.x)
        return cls.from_limits(top, bot, right, left)


class ForbiddenZone(Area):
    def __init__(self, a, b, inside_forbidden=True):
        super(ForbiddenZone, self).__init__(a, b)
        self.inside_forbidden = inside_forbidden

    def __contains__(self, item: Union[Pose, Position]):
        if type(item) is Pose:
            return self.point_inside(item.position)
        elif type(item) is Position:
            return self.point_inside(item)
        else:
            raise ValueError('You can only test if a position or a pose is contained inside the area.')

    def point_inside(self, p: Position) -> bool:
        is_inside = self.left <= p.x <= self.right and \
                   self.bottom <= p.y <= self.top
        # If inside_forbidden is false, the outside is the forbidden zone
        return self.inside_forbidden == is_inside
