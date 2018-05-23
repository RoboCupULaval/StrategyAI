import copy
import logging
from enum import Enum
from typing import Dict

from Util import Position, Pose
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
        self.length = (self.p2 - self.p1).norm
        self.thickness = line["thickness"]


class Field:
    def __init__(self, ball: Ball):
        #         <-------------------------field_length------------------------>
        #
        #  ^     +------------------------------+-------------------------------+
        #  |     |                              |                               |
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
        #  |     +-----------+                  |                    +----------F
        #  |     |                              |                               |
        #  |     |                              |                               |
        #  v     +------------------------------+-------------------------------+
        #
        self.logger = logging.getLogger(self.__class__.__name__)

        self.our_goal = None  # Point A
        self.our_goal_pose = None
        self.their_goal = None  # Point B
        self.their_goal_pose = None

        self.goal_line = None  # Point C to D
        self.our_goal_area = None # Area define by Point E to F

        self.field_length = None
        self.field_width = None
        self.goal_width = None

        self._ball = ball
        self._constant = constant

        self.field_lines = field_lines
        self.field_arcs = {}

        self._update_field_const()

    def is_ball_in_our_goal(self):
        return self.our_goal_area.point_inside(self.ball.position)

    def is_ball_outside_our_goal(self):
        # Use for strategy conditions
        return not self.is_ball_in_our_goal()

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
            raise RuntimeError(
                "Receiving legacy geometry message instead of the new geometry message. Update your grsim or check your vision port.")

        self.field_lines = self._convert_field_line_segments(field["field_lines"])
        self.field_arcs = self._convert_field_circular_arc(field["field_arcs"])

        if "RightFieldLeftPenaltyStretch" not in self.field_lines:
            # In Ulaval local the line are those of the 2017 version, so we need to patch and convert them
            self.logger.warning("You are receiving geometry message from an older version of ssl-vision, \n"
                                "which has a circular penality zone. Some positions might be incorrect.")
            self._fix_ulaval_field_line(field)

        self.field_length = field["field_length"]
        self.field_width = field["field_width"]

        boundary_width = field["boundary_width"]
        self.goal_width = field["goal_width"]
        center_circle_radius = self.field_arcs['CenterCircle'].radius

        self._constant["CENTER_CENTER_RADIUS"] = center_circle_radius

        self._constant["FIELD_BOUNDARY_WIDTH"] = boundary_width

        self._constant["FIELD_GOAL_WIDTH"] = self.goal_width

        self._constant["FIELD_THEIR_GOAL_X_EXTERNAL"] = self.left
        self._constant["FIELD_OUR_GOAL_X_EXTERNAL"] = self.right

        self._update_field_const()

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

    def _update_field_const(self):
        self.field_length = self._constant["FIELD_X_RIGHT"] * 2
        self.field_width = self._constant["FIELD_Y_TOP"] * 2
        self.goal_width = self._constant["FIELD_GOAL_WIDTH"]

        self.our_goal = Position(self._constant["FIELD_OUR_GOAL_X_EXTERNAL"], 0)
        self.our_goal_pose = Pose(self.our_goal, 0)
        self.their_goal = Position(self._constant["FIELD_THEIR_GOAL_X_EXTERNAL"], 0)
        self.their_goal_pose = Pose(self.their_goal, 0)

        self.our_goal_area = Area(self.field_lines["RightPenaltyStretch"].p2,
                                  self.field_lines["RightFieldLeftPenaltyStretch"].p1)

        self.goal_line = copy.deepcopy(self.field_lines["RightGoalDepthLine"])
        self.goal_line.p1.x = self.our_goal.x  # Move it to the entrance of the goal
        self.goal_line.p2.x = self.our_goal.x

    def _convert_field_circular_arc(self, field_arcs: Dict):
        result = {}
        for arc in field_arcs:
            result[arc["name"]] = FieldCircularArc(arc)
        return result

    def _convert_field_line_segments(self, field_lines: Dict):
        result = {}
        for line in field_lines:
            result[line["name"]] = FieldLineSegment(line)
        return result

    def _fix_ulaval_field_line(self, field):
        # The penalty x y is point E in the sketch
        penalty_x = self.field_lines["RightPenaltyStretch"].p1.x
        penalty_y = self.field_arcs["RightFieldRightPenaltyArc"].center.y \
                    + self.field_arcs["RightFieldRightPenaltyArc"].radius
        self.field_lines["RightPenaltyStretch"] \
            = Line(p1=Position(penalty_x, -penalty_y),
                   p2=Position(penalty_x, +penalty_y))
        goal_x = field["field_length"] / 2
        self.field_lines["RightFieldLeftPenaltyStretch"] \
            = Line(p1=Position(goal_x, -penalty_y),
                   p2=Position(penalty_x, -penalty_y))
        self.field_lines["RightGoalDepthLine"] \
            = Line(p1=Position(goal_x + field["goal_depth"], -field["goal_width"] / 2),
                   p2=Position(goal_x + field["goal_depth"], +field["goal_width"]/2))


field_lines = {
    "RightPenaltyStretch": Line(p1=Position(3495, -1000),
                                p2=Position(3495, +1000)),
    "RightFieldLeftPenaltyStretch": Line(p1=Position(4490, -1000),
                                         p2=Position(3490, -1000)),
    "RightGoalDepthLine": Line(p1=Position(4685, -500),
                               p2=Position(4685, +500))
}

constant = {
    # Field Parameters
    "FIELD_Y_TOP": 3000,
    "FIELD_X_RIGHT": 4500,

    "CENTER_CENTER_RADIUS": 1000,

    "FIELD_BOUNDARY_WIDTH": 700,

    # Goal Parameters
    "FIELD_GOAL_WIDTH": 100,
    "FIELD_OUR_GOAL_X_EXTERNAL": 4500,  # FIELD_X_LEFT
    "FIELD_THEIR_GOAL_X_EXTERNAL": -4500,  # FIELD_X_RIGHT

}
