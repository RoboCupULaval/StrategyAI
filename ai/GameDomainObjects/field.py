
import logging
from enum import Enum
from typing import Dict, Union

from Util import Position, Pose
from Util.constant import KEEPOUT_DISTANCE_FROM_GOAL, INDIRECT_KICK_OFFSET
from Util.geometry import Area, Line
from ai.GameDomainObjects import Ball


class FieldSide(Enum):
    POSITIVE = 0
    NEGATIVE = 1


# noinspection PyPep8
class FieldCircularArc:
    def __init__(self, arc: Dict):
        self.center = Position.from_dict(arc["center"])
        self.radius = arc["radius"]
        self.angle_start = arc["a1"]  # Counter clockwise order
        self.angle_end = arc["a2"]
        self.thickness = arc["thickness"]


class FieldLineSegment(Line):
    def __init__(self, line: Dict):
        self.p1 = Position.from_dict(line["p1"])
        self.p2 = Position.from_dict(line["p2"])
        self.thickness = line["thickness"]


def convert_field_circular_arc(field_arcs: Dict):
    result = {}
    for arc in field_arcs:
        result[arc["name"]] = FieldCircularArc(arc)
    return result


def convert_field_line_segments(field_lines: Dict):
    result = {}
    for line in field_lines:
        result[line["name"]] = FieldLineSegment(line)
    return result


class Field:
    def __init__(self, ball: Ball):
        #         <-------------------------field_length------------------------>
        #
        #  ^     +------------------------------+-------------------------------+
        #  |     |        their side            |            our side           |
        #  |     |                              |                               |
        #  |     +-----------+                  |    Y+              E----------+
        # f|     |           |                  |    ^               |          |
        # i|     |           |                  |    |               |          |
        # e|  +--+           |                  |    +--> X+         |          C--+ ^
        # l|  |  |           |                  |                    |          |  | |
        # d|  |  |           |                XX|XX                  |          |  | |
        #  |  |  |           |               X  |  X                 |          |  | |
        # w|  |  B--------------------------------------------------------------A  | |  goal_width
        # i|  |  |           |               X  |  X                 |          |  | |
        # d|  |  |           |                XX|XX                  |          |  | |
        # t|  |  |           |                  |                    |          |  | |
        # h|  +--+           |                  |                    |          D--+ v
        #  |     |           |                  |                    |          |
        #  |     |           |                  |                    |          |
        #  |     +-----------+                  |                    H----------F
        #  |     |                              |                               |
        #  |     |                              |                               |
        #  v     +------------------------------+-------------------------------+
        #
        self.logger = logging.getLogger(self.__class__.__name__)
        self._ball = ball

        self.our_goal = None  # Point A
        self.our_goal_pose = None
        self.their_goal = None  # Point B
        self.their_goal_pose = None
        self.our_goal_line = None
        self.their_goal_line = None

        self.goal_line = None  # Point C to D
        self.our_goal_area = None  # Area define by Point E to F
        self.their_goal_area = None

        # Default values, used only for UT
        self.field_length = 4500
        self.field_width = 3000
        self.goal_width = 1000
        self.goal_depth = 200
        self.center_circle_radius = 1000
        self.boundary_width = 300  # Is the distance between the field and the outside wall

        self.field_lines = {
            "RightPenaltyStretch": Line(p1=Position(3495, -1000),  # H to E
                                        p2=Position(3495, +1000)),
            "RightFieldLeftPenaltyStretch": Line(p1=Position(4490, -1000),  # H to F
                                                 p2=Position(3490, -1000))
        }
        self.field_arcs = {}
        self.area = None  # Area object with same dimension as field

        self._update_field_const()

    def is_ball_in_our_goal_area(self):
        return self.ball.position in self.our_goal_area

    def is_ball_outside_our_goal_area(self):
        # Use for strategy conditions
        return self.ball.position not in self.our_goal_area

    def is_inside_wall_limit(self, pos: [Pose, Position]):
        bound = self.boundary_width
        return self.left - bound <= pos.x <= self.right + bound and \
               self.bottom - bound <= pos.y <= self.top + bound

    def is_outside_wall_limit(self, pos: [Pose, Position]):
        return not self.is_inside_wall_limit(pos)

    @property
    def ball(self):
        if not self._ball:
            raise RuntimeError('There is no ball to detect')
        return self._ball

    @property
    def constant(self):
        return self._constant

    @constant.setter
    def constant(self, field: Dict):
        field = field["field"]
        if len(field["field_lines"]) == 0:
            raise RuntimeError("Receiving legacy geometry message instead of the new geometry message. \n"
                               "Update your grsim or check your vision port.")

        self.field_lines = convert_field_line_segments(field["field_lines"])
        self.field_arcs = convert_field_circular_arc(field["field_arcs"])

        if "RightFieldLeftPenaltyStretch" not in self.field_lines:
            # In Ulaval local the line are those of the 2017 version, so we need to patch and convert them
            self.logger.warning("You are receiving geometry message from an older version of ssl-vision, \n"
                                "which has a circular penalty zone. Some positions might be incorrect.")
            self._fix_ulaval_field_line(field)

        self.field_length = field["field_length"]
        self.field_width = field["field_width"]

        self.boundary_width = field["boundary_width"]
        self.goal_width = field["goal_width"]
        self.goal_depth = field["goal_depth"]

        self.center_circle_radius = self.field_arcs['CenterCircle'].radius

        self._update_field_const()

    def _update_field_const(self):
        self.our_goal = Position(self.our_goal_x, 0)
        self.our_goal_pose = Pose(self.our_goal, 0)
        self.their_goal = Position(self.their_goal_x, 0)
        self.their_goal_pose = Pose(self.their_goal, 0)

        p1 = self.field_lines["RightPenaltyStretch"].p1
        p2 = self.field_lines["RightPenaltyStretch"].p2
        p3 = self.field_lines["RightFieldLeftPenaltyStretch"].p1
        p4 = self.field_lines["RightFieldLeftPenaltyStretch"].p2
        self.our_goal_area = Area.from_4_point(p1, p2, p3, p4)

        self.their_goal_area = Area.flip_x(self.our_goal_area)

        self.area = Area.from_limits(self.top, self.bottom, self.right, self.left)

        self.goal_line = Line(p1=Position(self.our_goal_x, +self.goal_width / 2),
                                  p2=Position(self.our_goal_x, -self.goal_width / 2))

        self.our_goal_line = Line(p1=Position(self.our_goal_x, +self.goal_width / 2),
                                  p2=Position(self.our_goal_x, -self.goal_width / 2))
        self.their_goal_line = Line(p1=Position(self.their_goal_x, +self.goal_width / 2),
                                    p2=Position(self.their_goal_x, -self.goal_width / 2))
        self.behind_our_goal_line = Area.from_limits(self.our_goal_area.top,
                                                     self.our_goal_area.bottom,
                                                     self.our_goal_area.right + 50 * self.goal_depth,
                                                     self.our_goal_area.left)
        self.behind_their_goal_line = Area.flip_x(self.behind_our_goal_line)

        self.free_kick_avoid_area = Area.pad(self.their_goal_area,
                                             INDIRECT_KICK_OFFSET + KEEPOUT_DISTANCE_FROM_GOAL)
        self.our_goal_forbidden_area = Area.pad(self.our_goal_area, KEEPOUT_DISTANCE_FROM_GOAL)
        self.their_goal_forbidden_area = Area.pad(self.their_goal_area, KEEPOUT_DISTANCE_FROM_GOAL)

        self.center = Position(0, 0)

    def _fix_ulaval_field_line(self, field):
        # The penalty x y is point E in the sketch
        penalty_x = self.field_lines["RightPenaltyStretch"].p1.x
        penalty_y = self.field_arcs["RightFieldRightPenaltyArc"].center.y + \
                    self.field_arcs["RightFieldRightPenaltyArc"].radius
        self.field_lines["RightPenaltyStretch"] \
            = Line(p1=Position(penalty_x, -penalty_y),
                   p2=Position(penalty_x, +penalty_y))
        goal_x = field["field_length"] / 2
        self.field_lines["RightFieldLeftPenaltyStretch"] \
            = Line(p1=Position(goal_x, -penalty_y),
                   p2=Position(penalty_x, -penalty_y))

    @property
    def our_goal_x(self):
        return self.right

    @property
    def their_goal_x(self):
        return self.left

    def __contains__(self, item: Union[Pose, Position]):
        return self.left <= item.x <= self.right and \
               self.bottom <= item.y <= self.top

    # FIXME MONTREAL
    @property
    def border_limits(self):

        top_area = Area.from_limits(self.top + 100 * self.boundary_width,
                                    self.top + self.boundary_width,
                                    self.right + 100 * self.boundary_width,
                                    self.left - 100 * self.boundary_width)
        bottom_area = Area.from_limits(self.bottom - self.boundary_width,
                                       self.bottom - 100 * self.boundary_width,
                                       self.right + 100 * self.boundary_width,
                                       self.left - 100 * self.boundary_width)
        right_area = Area.from_limits(self.top + 100 * self.boundary_width,
                                      self.bottom - 100 * self.boundary_width,
                                      self.right + 100 * self.boundary_width,
                                      self.right + self.boundary_width)
        left_area = Area.from_limits(self.top + 100 * self.boundary_width,
                                     self.bottom - 100 * self.boundary_width,
                                     self.left - self.boundary_width,
                                     self.left - 100 * self.boundary_width)
        return [top_area, bottom_area, right_area, left_area]

    @property
    def top(self):
        return self.field_width / 2

    @property
    def bottom(self):
        return -self.field_width / 2

    @property
    def left(self):
        return -self.field_length / 2

    @property
    def right(self):
        return self.field_length / 2
