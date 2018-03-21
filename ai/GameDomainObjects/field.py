from typing import Dict

from Util import Position
from ai.GameDomainObjects import Ball
from config.config import Config


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
        print(field)
        if len(field.field_lines) == 0:
            raise RuntimeError(
                "Receiving legacy geometry message instead of the new geometry message. Update your grsim or check your vision port.")

        field_lines = self._convert_field_line_segments(field.field_lines)
        field_arcs = self._convert_field_circular_arc(field.field_arcs)

        if "RightFieldLeftPenaltyArc" not in self.field_arcs:
            # This is a new type of field for Robocup 2018, it does not have a circular goal zone
            defense_radius = self.field_lines["LeftFieldLeftPenaltyStretch"].length
        else:
            defense_radius = self.field_arcs['RightFieldLeftPenaltyArc'].radius

        field_length = field.field_length
        field_width = field.field_width
        boundary_width = field.boundary_width
        goal_width = field.goal_width
        center_circle_radius = self.field_arcs['CenterCircle'].radius
        defense_stretch = 100  # hard coded parce que cette valeur d'est plus valide et que plusieurs modules en ont de besoin
        # la valeur qu'on avait apres le fix a Babin était de 9295 mm, ce qui est 90 fois la grandeur d'avant.
        self._constant["FIELD_Y_TOP"] = field_width / 2
        self._constant["FIELD_Y_BOTTOM"] = -field_width / 2
        self._constant["FIELD_X_LEFT"] = -field_length / 2
        self._constant["FIELD_X_RIGHT"] = field_length / 2

        self._constant["CENTER_CENTER_RADIUS"] = center_circle_radius

        self._constant["FIELD_Y_POSITIVE"] = field_width / 2
        self._constant["FIELD_Y_NEGATIVE"] = -field_width / 2
        self._constant["FIELD_X_NEGATIVE"] = -field_length / 2
        self._constant["FIELD_X_POSITIVE"] = field_length / 2

        self._constant["FIELD_BOUNDARY_WIDTH"] = boundary_width

        self._constant["FIELD_GOAL_RADIUS"] = defense_radius
        self._constant["FIELD_GOAL_SEGMENT"] = defense_stretch
        self._constant["FIELD_GOAL_WIDTH"] = goal_width

        self._constant["FIELD_GOAL_Y_TOP"] = defense_radius + (defense_stretch / 2)
        self._constant["FIELD_GOAL_Y_BOTTOM"] = -self._constant["FIELD_GOAL_Y_TOP"]

        if not Config()['ENGINE']['on_negative_side']:
            self._constant["FIELD_THEIR_GOAL_X_EXTERNAL"] = self._constant["FIELD_X_NEGATIVE"]
            self._constant["FIELD_THEIR_GOAL_X_INTERNAL"] = self._constant["FIELD_X_NEGATIVE"] + self._constant[
                "FIELD_GOAL_RADIUS"]

            self._constant["FIELD_OUR_GOAL_X_INTERNAL"] = self._constant["FIELD_X_POSITIVE"] - self._constant[
                "FIELD_GOAL_RADIUS"]
            self._constant["FIELD_OUR_GOAL_X_EXTERNAL"] = self._constant["FIELD_X_POSITIVE"]

            self._constant["FIELD_THEIR_GOAL_TOP_CIRCLE"] = Position(self._constant["FIELD_X_NEGATIVE"],
                                                                    self._constant["FIELD_GOAL_SEGMENT"] / 2)
            self._constant["FIELD_THEIR_GOAL_BOTTOM_CIRCLE"] = Position(self._constant["FIELD_X_NEGATIVE"],
                                                                       -self._constant["FIELD_GOAL_SEGMENT"] / 2)
            self._constant["FIELD_THEIR_GOAL_MID_GOAL"] = Position(self._constant["FIELD_X_NEGATIVE"], 0)

            self._constant["FIELD_OUR_GOAL_TOP_CIRCLE"] = Position(self._constant["FIELD_X_POSITIVE"],
                                                                  self._constant["FIELD_GOAL_SEGMENT"] / 2)
            self._constant["FIELD_OUR_GOAL_BOTTOM_CIRCLE"] = Position(self._constant["FIELD_X_POSITIVE"],
                                                                     -self._constant["FIELD_GOAL_SEGMENT"] / 2)
            self._constant["FIELD_OUR_GOAL_MID_GOAL"] = Position(self._constant["FIELD_X_POSITIVE"], 0)

        else:
            self._constant["FIELD_OUR_GOAL_X_EXTERNAL"] = self._constant["FIELD_X_NEGATIVE"]
            self._constant["FIELD_OUR_GOAL_X_INTERNAL"] = self._constant["FIELD_X_NEGATIVE"] + self._constant[
                "FIELD_GOAL_RADIUS"]

            self._constant["FIELD_THEIR_GOAL_X_INTERNAL"] = self._constant["FIELD_X_POSITIVE"] - self._constant[
                "FIELD_GOAL_RADIUS"]
            self._constant["FIELD_THEIR_GOAL_X_EXTERNAL"] = self._constant["FIELD_X_POSITIVE"]

            self._constant["FIELD_OUR_GOAL_TOP_CIRCLE"] = Position(self._constant["FIELD_X_NEGATIVE"],
                                                                  self._constant["FIELD_GOAL_SEGMENT"] / 2)
            self._constant["FIELD_OUR_GOAL_BOTTOM_CIRCLE"] = Position(self._constant["FIELD_X_NEGATIVE"],
                                                                     -self._constant["FIELD_GOAL_SEGMENT"] / 2)
            self._constant["FIELD_OUR_GOAL_MID_GOAL"] = Position(self._constant["FIELD_X_NEGATIVE"], 0)

            self._constant["FIELD_THEIR_GOAL_TOP_CIRCLE"] = Position(self._constant["FIELD_X_POSITIVE"],
                                                                    self._constant["FIELD_GOAL_SEGMENT"] / 2)
            self._constant["FIELD_THEIR_GOAL_BOTTOM_CIRCLE"] = Position(self._constant["FIELD_X_POSITIVE"],
                                                                       -self._constant["FIELD_GOAL_SEGMENT"] / 2)
            self._constant["FIELD_THEIR_GOAL_MID_GOAL"] = Position(self._constant["FIELD_X_POSITIVE"], 0)
        
        
        
        
        


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
