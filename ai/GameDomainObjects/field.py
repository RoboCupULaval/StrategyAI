import copy
from enum import Enum
from typing import Dict

from Util import Position, Pose
from Util.geometry import Area
from ai.GameDomainObjects import Ball
from config.config import Config


class FieldSide(Enum):
    POSITIVE = 0
    NEGATIVE = 1


# noinspection PyPep8
class FieldCircularArc:
    def __init__(self, arc: Dict):
        self.center = Position.from_dict(arc["center"])
        self.radius      = arc["radius"]
        self.angle_start = arc["a1"]  # Counter clockwise order
        self.angle_ened  = arc["a2"]
        self.thickness   = arc["thickness"]


class FieldLineSegment:
    def __init__(self, line: Dict):
        self.p1 = Position.from_dict(line["p1"])
        self.p2 = Position.from_dict(line["p2"])
        self.length = (self.p2 - self.p1).norm
        self.thickness = line["thickness"]


class Field:
    def __init__(self, ball: Ball):

        self._ball = ball
        self._constant = constant

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

        if "RightFieldLeftPenaltyArc" not in self.field_arcs:
            # This is a new type of field for Robocup 2018, it does not have a circular goal zone
            defense_radius = self.field_lines["LeftFieldLeftPenaltyStretch"].length
        else:
            defense_radius = self.field_arcs['RightFieldLeftPenaltyArc'].radius

        self.field_length = field["field_length"]
        self.field_width = field["field_width"]

        boundary_width = field["boundary_width"]
        self.goal_width = field["goal_width"]
        center_circle_radius = self.field_arcs['CenterCircle'].radius
        defense_stretch = 100  # hard coded parce que cette valeur d'est plus valide et que plusieurs modules en ont de besoin
        # la valeur qu'on avait apres le fix a Babin était de 9295 mm, ce qui est 90 fois la grandeur d'avant.

        # TODO: All of those const should removed and replaced by mostly line and area
        self._constant["FIELD_Y_TOP"] = self.field_width / 2
        self._constant["FIELD_Y_BOTTOM"] = -self.field_width / 2
        self._constant["FIELD_X_LEFT"] = -self.field_length / 2
        self._constant["FIELD_X_RIGHT"] = self.field_length / 2

        self._constant["CENTER_CENTER_RADIUS"] = center_circle_radius

        self._constant["FIELD_Y_POSITIVE"] = self.field_width / 2
        self._constant["FIELD_Y_NEGATIVE"] = -self.field_width / 2
        self._constant["FIELD_X_NEGATIVE"] = -self.field_length / 2
        self._constant["FIELD_X_POSITIVE"] = self.field_length / 2

        self._constant["FIELD_BOUNDARY_WIDTH"] = boundary_width

        self._constant["FIELD_GOAL_RADIUS"] = defense_radius
        self._constant["FIELD_GOAL_SEGMENT"] = defense_stretch
        self._constant["FIELD_GOAL_WIDTH"] = self.goal_width

        self._constant["FIELD_GOAL_Y_TOP"] = defense_radius + (defense_stretch / 2)
        self._constant["FIELD_GOAL_Y_BOTTOM"] = -self._constant["FIELD_GOAL_Y_TOP"]

        self.constant["FIELD_THEIR_GOAL_X_EXTERNAL"] = self.constant["FIELD_X_NEGATIVE"]
        self.constant["FIELD_THEIR_GOAL_X_INTERNAL"] = self.constant["FIELD_X_NEGATIVE"] + self.constant[
            "FIELD_GOAL_RADIUS"]

        self.constant["FIELD_OUR_GOAL_X_INTERNAL"] = self.constant["FIELD_X_POSITIVE"] - self.constant[
            "FIELD_GOAL_RADIUS"]
        self.constant["FIELD_OUR_GOAL_X_EXTERNAL"] = self.constant["FIELD_X_POSITIVE"]

        self.constant["FIELD_THEIR_GOAL_TOP_CIRCLE"] = Position(self.constant["FIELD_X_NEGATIVE"],
                                                                self.constant["FIELD_GOAL_SEGMENT"] / 2)
        self.constant["FIELD_THEIR_GOAL_BOTTOM_CIRCLE"] = Position(self.constant["FIELD_X_NEGATIVE"],
                                                                   -self.constant["FIELD_GOAL_SEGMENT"] / 2)
        self.constant["FIELD_THEIR_GOAL_MID_GOAL"] = Position(self.constant["FIELD_X_NEGATIVE"], 0)

        self.constant["FIELD_OUR_GOAL_TOP_CIRCLE"] = Position(self.constant["FIELD_X_POSITIVE"],
                                                              self.constant["FIELD_GOAL_SEGMENT"] / 2)
        self.constant["FIELD_OUR_GOAL_BOTTOM_CIRCLE"] = Position(self.constant["FIELD_X_POSITIVE"],
                                                                 -self.constant["FIELD_GOAL_SEGMENT"] / 2)

        self.constant["FIELD_OUR_GOAL_MID_GOAL"] = Position(self.constant["FIELD_X_POSITIVE"], 0)

        self.our_goal = Position(self._constant["FIELD_OUR_GOAL_X_EXTERNAL"], 0)
        self.our_goal_pose = Pose(self.our_goal, 0)
        self.their_goal = Position(self._constant["FIELD_THEIR_GOAL_X_EXTERNAL"], 0)
        self.their_goal_pose = Pose(self.their_goal, 0)

        # TODO in real these constant are not provided by ssl-vision, investigate
        self.our_goal_area = Area(self.field_lines["RightPenaltyStretch"].p2,
                                  self.field_lines["RightFieldLeftPenaltyStretch"].p1)

        self.goal_line = copy.deepcopy(self.field_lines["RightGoalDepthLine"])
        self.goal_line.p1.x = self.our_goal.x # Move it to the entrance of the goal
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

    def is_ball_in_our_goal(self):
        return self.our_goal_area.point_inside(self.ball.position)
        
        
        


constant = {
    # Field Parameters
    "FIELD_Y_TOP": 3000,
    "FIELD_Y_BOTTOM": -3000,
    "FIELD_X_LEFT": -4500,
    "FIELD_X_RIGHT": 4500,

    "CENTER_CENTER_RADIUS": 1000,

    "FIELD_Y_POSITIVE": 3000,
    "FIELD_Y_NEGATIVE": -3000,
    "FIELD_X_NEGATIVE": -4500,
    "FIELD_X_POSITIVE": 4500,

    "FIELD_BOUNDARY_WIDTH": 700,

    "FIELD_GOAL_RADIUS": 1000,
    "FIELD_GOAL_SEGMENT": 500,

    # Goal Parameters
    "FIELD_GOAL_WIDTH": 1000,
    "FIELD_GOAL_Y_TOP": 1250,  # FIELD_GOAL_RADIUS + FIELD_GOAL_SEGMENT / 2
    "FIELD_GOAL_Y_BOTTOM": -1250,  # (FIELD_GOAL_RADIUS + FIELD_GOAL_SEGMENT / 2) * -1
    "FIELD_OUR_GOAL_X_EXTERNAL": 4500,  # FIELD_X_LEFT
    "FIELD_OUR_GOAL_X_INTERNAL": 3500,  # FIELD_X_LEFT + FIELD_GOAL_RADIUS
    "FIELD_THEIR_GOAL_X_INTERNAL": -3500,  # FIELD_X_RIGHT - FIELD_GOAL_RADIUS
    "FIELD_THEIR_GOAL_X_EXTERNAL": -4500,  # FIELD_X_RIGHT

    "FIELD_DEFENSE_PENALTY_MARK": Position(1, 0),
    "FIELD_OFFENSE_PENALTY_MARK": Position(1, 0),

    # Field Positions
    "FIELD_OUR_GOAL_TOP_CIRCLE": Position(4500, 250),  # FIELD_X_LEFT, FIELD_GOAL_SEGMENT / 2)
    "FIELD_OUR_GOAL_BOTTOM_CIRCLE": Position(4500, -250),  # FIELD_X_LEFT, FIELD_GOAL_SEGMENT / 2 * -1)
    "FIELD_OUR_GOAL_MID_GOAL": Position(4500, 0),
    "FIELD_THEIR_GOAL_TOP_CIRCLE": Position(-4500, 250),  # FIELD_X_RIGHT, FIELD_GOAL_SEGMENT / 2)
    "FIELD_THEIR_GOAL_BOTTOM_CIRCLE": Position(-4500, -250),  # FIELD_X_RIGHT, FIELD_GOAL_SEGMENT / 2 * -1)
    "FIELD_THEIR_GOAL_MID_GOAL": Position(-4500, 0),

    # Legal field dimensions
    "LEGAL_Y_TOP": 3000,
    # LEGAL_Y_TOP": 0
    "LEGAL_Y_BOTTOM": -3000,
    "LEGAL_X_LEFT": -4500,
    "LEGAL_X_RIGHT": 4500,
    # LEGAL_X_RIGHT": 0
}
