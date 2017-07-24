# Under MIT License, see LICENSE.txt
from config.config_service import ConfigService
from RULEngine.Util.area import *


class FieldSide(Enum):
    POSITIVE = 0
    NEGATIVE = 1


class Field:
    def __init__(self, ball):
        self.ball = ball
        cfg = ConfigService()            
        if cfg.config_dict["GAME"]["our_side"] == "positive":
            self.our_side = FieldSide.POSITIVE
            self.constant = positive_side_constant
        else:
            self.our_side = FieldSide.NEGATIVE
            self.constant = negative_side_constant

    def move_ball(self, position, delta):
        self.ball.set_position(position, delta)

    def is_inside_goal_area(self, position, dist_from_goal_area=0, our_goal=True):
        assert (isinstance(position, Position))
        assert (isinstance(our_goal, bool))
        x1 = self.constant["FIELD_OUR_GOAL_X_EXTERNAL"] if our_goal else self.constant["FIELD_THEIR_GOAL_X_EXTERNAL"]
        x2 = self.constant["FIELD_OUR_GOAL_X_INTERNAL"] if our_goal else self.constant["FIELD_THEIR_GOAL_X_INTERNAL"]

        x_right = max(x1, x2) + dist_from_goal_area
        x_left = min(x1, x2) - dist_from_goal_area

        top_circle = self.constant["FIELD_OUR_GOAL_TOP_CIRCLE"] if our_goal\
            else self.constant["FIELD_THEIR_GOAL_TOP_CIRCLE"]
        bot_circle = self.constant["FIELD_OUR_GOAL_BOTTOM_CIRCLE"] if our_goal\
            else self.constant["FIELD_THEIR_GOAL_BOTTOM_CIRCLE"]

        if isInsideSquare(position, self.constant["FIELD_GOAL_Y_TOP"], self.constant["FIELD_GOAL_Y_BOTTOM"],
                          x_left, x_right):
            if is_inside_circle(position, top_circle, self.constant["FIELD_GOAL_RADIUS"] + dist_from_goal_area):
                return True
            elif is_inside_circle(position, bot_circle, self.constant["FIELD_GOAL_RADIUS"] + dist_from_goal_area):
                return True
            return True
        else:
            return False

    def is_outside_goal_area(self, position, dist_from_goal_area=0, our_goal=True):
        return not self.is_inside_goal_area(position, dist_from_goal_area, our_goal)

    def stay_inside_goal_area(self, position, our_goal=True):
        # TODO Not tested: stayInsideGoalArea
        if self.is_inside_goal_area(position, our_goal):
            return Position(position.x, position.y)
        else:
            x1 = self.constant["FIELD_OUR_GOAL_X_EXTERNAL"] if our_goal else self.constant["FIELD_THEIR_GOAL_X_EXTERNAL"]
            x2 = self.constant["FIELD_OUR_GOAL_X_INTERNAL"] if our_goal else self.constant["FIELD_THEIR_GOAL_X_INTERNAL"]

            x_right = max(x1, x2)
            x_left = min(x1, x2)

            position = stayInsideSquare(position, self.constant["FIELD_GOAL_Y_TOP"],
                                        self.constant["FIELD_GOAL_Y_BOTTOM"], x_left, x_right)
            if isInsideSquare(position, self.constant["FIELD_GOAL_Y_TOP"], self.constant["FIELD_GOAL_Y_BOTTOM"],
                              x_left, x_right):
                return position
            else:
                circle_top = self.constant["FIELD_OUR_GOAL_TOP_CIRCLE"] if our_goal\
                    else self.constant["FIELD_THEIR_GOAL_TOP_CIRCLE"]
                circle_bot = self.constant["FIELD_OUR_GOAL_BOTTOM_CIRCLE"] if our_goal\
                    else self.constant["FIELD_THEIR_GOAL_BOTTOM_CIRCLE"]
                dst_top = get_distance(circle_top, position)
                dst_bot = get_distance(circle_bot, position)

                if dst_top >= dst_bot:
                    return stayInsideCircle(position, circle_top, self.constant["FIELD_GOAL_RADIUS"])
                else:
                    return stayInsideCircle(position, circle_bot, self.constant["FIELD_GOAL_RADIUS"])

    def stay_outside_goal_area(self, position, dist_from_goal_area=200, our_goal=True):
        # TODO Not tested: stayOutsideGoalArea
        if self.is_outside_goal_area(position, dist_from_goal_area, our_goal):
            return Position(position.x, position.y)
        else:
            x1 = self.constant["FIELD_OUR_GOAL_X_EXTERNAL"] if our_goal else self.constant["FIELD_THEIR_GOAL_X_EXTERNAL"]
            x2 = self.constant["FIELD_OUR_GOAL_X_INTERNAL"] if our_goal else self.constant["FIELD_THEIR_GOAL_X_INTERNAL"]
            x1 = 2*x1-x2

            x_right = max(x1, x2) + dist_from_goal_area
            x_left = min(x1, x2) - dist_from_goal_area

            y_top = self.constant["FIELD_GOAL_SEGMENT"] / 2
            y_bottom = (self.constant["FIELD_GOAL_SEGMENT"] / 2) * -1

            circle_top = self.constant["FIELD_OUR_GOAL_TOP_CIRCLE"] if our_goal\
                else self.constant["FIELD_THEIR_GOAL_TOP_CIRCLE"]
            circle_bot = self.constant["FIELD_OUR_GOAL_BOTTOM_CIRCLE"] if our_goal\
                else self.constant["FIELD_THEIR_GOAL_BOTTOM_CIRCLE"]

            position = stayOutsideSquare(position, y_top, y_bottom, x_left, x_right)
            position = stayOutsideCircle(position, circle_top, self.constant["FIELD_GOAL_RADIUS"] + dist_from_goal_area)
            position = stayOutsideCircle(position, circle_bot, self.constant["FIELD_GOAL_RADIUS"] + dist_from_goal_area)
            return Position(position.x, position.y)

    def stay_inside_play_field(self, position):
        return stayInsideSquare(position, Y_TOP=self.constant["FIELD_Y_TOP"],
                                          Y_BOTTOM=self.constant["FIELD_Y_BOTTOM"],
                                          X_LEFT=self.constant["FIELD_X_LEFT"],
                                          X_RIGHT=self.constant["FIELD_X_RIGHT"])

    def stay_inside_full_field(self, position):
        return stayInsideSquare(position, Y_TOP=self.constant["FIELD_Y_TOP"] + self.constant["FIELD_BOUNDARY_WIDTH"],
                                Y_BOTTOM=self.constant["FIELD_Y_BOTTOM"] - self.constant["FIELD_BOUNDARY_WIDTH"],
                                X_LEFT=self.constant["FIELD_X_LEFT"] - self.constant["FIELD_BOUNDARY_WIDTH"],
                                X_RIGHT=self.constant["FIELD_X_RIGHT"] + self.constant["FIELD_BOUNDARY_WIDTH"])

    def respect_field_rules(self, position):
        new_position = self.stay_outside_goal_area(position, our_goal=False)
        return self.stay_inside_play_field(new_position)

    def update_field_dimensions(self, packets):
        if not packets:
            return False

        for packet in packets:
            if packet.HasField("geometry"):
                field = packet.geometry.field
                self._line_width = field.line_width
                self._field_length = field.field_length
                self._field_width = field.field_width
                self._boundary_width = field.boundary_width
                self._referee_width = field.referee_width
                self._goal_width = field.goal_width
                self._goal_depth = field.goal_depth
                self._goal_wall_width = field.goal_wall_width
                self._center_circle_radius = field.center_circle_radius
                self._defense_radius = field.defense_radius
                self._defense_stretch = field.defense_stretch
                self._free_kick_from_defense_dist = field.free_kick_from_defense_dist
                self._penalty_spot_from_field_line_dist = field.penalty_spot_from_field_line_dist
                self._penalty_line_from_spot_dist = field.penalty_line_from_spot_dist

                self.constant["FIELD_Y_TOP"] = self._field_width / 2
                self.constant["FIELD_Y_BOTTOM"] = -self._field_width / 2
                self.constant["FIELD_X_LEFT"] = -self._field_length / 2
                self.constant["FIELD_X_RIGHT"] = self._field_length / 2

                self.constant["CENTER_CENTER_RADIUS"] = self._center_circle_radius

                self.constant["FIELD_Y_POSITIVE"] = self._field_width / 2
                self.constant["FIELD_Y_NEGATIVE"] = -self._field_width / 2
                self.constant["FIELD_X_NEGATIVE"] = -self._field_length / 2
                self.constant["FIELD_X_POSITIVE"] = self._field_length / 2

                self.constant["FIELD_BOUNDARY_WIDTH"] = self._boundary_width

                self.constant["FIELD_GOAL_RADIUS"] = self._defense_radius
                self.constant["FIELD_GOAL_SEGMENT"] = self._defense_stretch
                self.constant["FIELD_GOAL_WIDTH"] = self._goal_width

                self.constant["FIELD_GOAL_Y_TOP"] = self._defense_radius + (self._defense_stretch / 2)
                self.constant["FIELD_GOAL_Y_BOTTOM"] = -self.constant["FIELD_GOAL_Y_TOP"]

                if self.our_side == FieldSide.POSITIVE:
                    self.constant["FIELD_THEIR_GOAL_X_EXTERNAL"] = self.constant["FIELD_X_NEGATIVE"]
                    self.constant["FIELD_THEIR_GOAL_X_INTERNAL"] = self.constant["FIELD_X_NEGATIVE"] + self.constant["FIELD_GOAL_RADIUS"]

                    self.constant["FIELD_OUR_GOAL_X_INTERNAL"] = self.constant["FIELD_X_POSITIVE"] - self.constant["FIELD_GOAL_RADIUS"]
                    self.constant["FIELD_OUR_GOAL_X_EXTERNAL"] = self.constant["FIELD_X_POSITIVE"]

                    self.constant["FIELD_THEIR_GOAL_TOP_CIRCLE"] = Position(self.constant["FIELD_X_NEGATIVE"], self.constant["FIELD_GOAL_SEGMENT"] / 2)
                    self.constant["FIELD_THEIR_GOAL_BOTTOM_CIRCLE"] = Position(self.constant["FIELD_X_NEGATIVE"], -self.constant["FIELD_GOAL_SEGMENT"] / 2)
                    self.constant["FIELD_THEIR_GOAL_MID_GOAL"] = Position(self.constant["FIELD_X_NEGATIVE"], 0)

                    self.constant["FIELD_OUR_GOAL_TOP_CIRCLE"] = Position(self.constant["FIELD_X_POSITIVE"], self.constant["FIELD_GOAL_SEGMENT"] / 2)
                    self.constant["FIELD_OUR_GOAL_BOTTOM_CIRCLE"] = Position(self.constant["FIELD_X_POSITIVE"], -self.constant["FIELD_GOAL_SEGMENT"] / 2)
                    self.constant["FIELD_OUR_GOAL_MID_GOAL"] = Position(self.constant["FIELD_X_POSITIVE"], 0)
                else:
                    self.constant["FIELD_OUR_GOAL_X_EXTERNAL"] = self.constant["FIELD_X_NEGATIVE"]
                    self.constant["FIELD_OUR_GOAL_X_INTERNAL"] = self.constant["FIELD_X_NEGATIVE"] + self.constant["FIELD_GOAL_RADIUS"]
                    
                    self.constant["FIELD_THEIR_GOAL_X_INTERNAL"] = self.constant["FIELD_X_POSITIVE"] - self.constant["FIELD_GOAL_RADIUS"]
                    self.constant["FIELD_THEIR_GOAL_X_EXTERNAL"] = self.constant["FIELD_X_POSITIVE"]

                    self.constant["FIELD_OUR_GOAL_TOP_CIRCLE"] = Position(self.constant["FIELD_X_NEGATIVE"], self.constant["FIELD_GOAL_SEGMENT"] / 2)
                    self.constant["FIELD_OUR_GOAL_BOTTOM_CIRCLE"] = Position(self.constant["FIELD_X_NEGATIVE"], -self.constant["FIELD_GOAL_SEGMENT"] / 2)
                    self.constant["FIELD_OUR_GOAL_MID_GOAL"] = Position(self.constant["FIELD_X_NEGATIVE"], 0)
                    
                    self.constant["FIELD_THEIR_GOAL_TOP_CIRCLE"] = Position(self.constant["FIELD_X_POSITIVE"], self.constant["FIELD_GOAL_SEGMENT"] / 2)
                    self.constant["FIELD_THEIR_GOAL_BOTTOM_CIRCLE"] = Position(self.constant["FIELD_X_POSITIVE"], -self.constant["FIELD_GOAL_SEGMENT"] / 2)
                    self.constant["FIELD_THEIR_GOAL_MID_GOAL"] = Position(self.constant["FIELD_X_POSITIVE"], 0)
                return True
            else:
                return False



positive_side_constant = {
    "ROBOT_RADIUS": 90,
    "BALL_RADIUS": 22,
    "PLAYER_PER_TEAM": 6,
    # TODO KICKSPEED
    "KICK_MAX_SPD": 4,
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

    # Simulation param
    "DELTA_T": 17,  # ms, hack, à éviter

    # Communication information
    "DEBUG_RECEIVE_BUFFER_SIZE": 100,

    # Deadzones
    "SPEED_DEAD_ZONE_DISTANCE": 150,
    "POSITION_DEADZONE": 20,  # ROBOT_RADIUS*1.5

    # Radius and angles for tactics
    "DISTANCE_BEHIND": 120,  # ROBOT_RADIUS + 30  # in millimeters
    "ANGLE_TO_GRAB_BALL": 1,  # in radians; must be large in case ball moves fast
    "RADIUS_TO_GRAB_BALL": 120,  # ROBOT_RADIUS + 30
    "ANGLE_TO_HALT": 0.09,
    "RADIUS_TO_HALT": 102,  # ROBOT_RADIUS + BALL_RADIUS

    # Orientation abs_tol
    "ORIENTATION_ABSOLUTE_TOLERANCE": 1e-4,
    "SPEED_ABSOLUTE_TOLERANCE": 1e-3,

    # Speed
    "DEFAULT_MAX_SPEED": 1,
    "DEFAULT_MIN_SPEED": 0.65,

    # Kick tactic
    "KICK_BALL_DISTANCE": 80,
    "KISS_BALL_DISTANCE": 80
}

negative_side_constant = {
    "ROBOT_RADIUS": 90,
    "BALL_RADIUS": 22,
    "PLAYER_PER_TEAM": 6,
    # TODO KICKSPEED
    "KICK_MAX_SPD": 4,

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
    
    "FIELD_GOAL_RADIUS": 1000,
    "FIELD_GOAL_SEGMENT": 500,


    # Goal Parameters
    "FIELD_GOAL_WIDTH": 1000,
    "FIELD_GOAL_Y_TOP": 1250,  # FIELD_GOAL_RADIUS + FIELD_GOAL_SEGMENT / 2
    "FIELD_GOAL_Y_BOTTOM": -1250,  # (FIELD_GOAL_RADIUS + FIELD_GOAL_SEGMENT / 2) * -1
    "FIELD_OUR_GOAL_X_EXTERNAL": -4500,  # FIELD_X_LEFT
    "FIELD_OUR_GOAL_X_INTERNAL": -3500,  # FIELD_X_LEFT + FIELD_GOAL_RADIUS
    "FIELD_THEIR_GOAL_X_INTERNAL": 3500,  # FIELD_X_RIGHT - FIELD_GOAL_RADIUS
    "FIELD_THEIR_GOAL_X_EXTERNAL": 4500,  # FIELD_X_RIGHT

    # Field Positions
    "FIELD_OUR_GOAL_TOP_CIRCLE": Position(-4500, 250),  # FIELD_X_LEFT, FIELD_GOAL_SEGMENT / 2)
    "FIELD_OUR_GOAL_BOTTOM_CIRCLE": Position(-4500, -250),  # FIELD_X_LEFT, FIELD_GOAL_SEGMENT / 2 * -1)
    "FIELD_OUR_GOAL_MID_GOAL": Position(-4500, 0),
    "FIELD_THEIR_GOAL_TOP_CIRCLE": Position(4500, 250),  # FIELD_X_RIGHT, FIELD_GOAL_SEGMENT / 2)
    "FIELD_THEIR_GOAL_BOTTOM_CIRCLE": Position(4500, -250),  # FIELD_X_RIGHT, FIELD_GOAL_SEGMENT / 2 * -1)
    "FIELD_THEIR_GOAL_MID_GOAL": Position(4500, 0),


    # Legal field dimensions
    "LEGAL_Y_TOP": 3000,
    # LEGAL_Y_TOP": 0
    "LEGAL_Y_BOTTOM": -3000,
    "LEGAL_X_LEFT": -4500,
    "LEGAL_X_RIGHT": 4500,
    # LEGAL_X_RIGHT": 0

    # Simulation param
    "DELTA_T": 17,  # ms, hack, à éviter

    # Communication information
    "DEBUG_RECEIVE_BUFFER_SIZE": 100,

    # Deadzones
    "SPEED_DEAD_ZONE_DISTANCE": 150,
    "POSITION_DEADZONE": 20,  # ROBOT_RADIUS*1.5

    # Radius and angles for tactics
    "DISTANCE_BEHIND": 120,  # ROBOT_RADIUS + 30  # in millimeters
    "ANGLE_TO_GRAB_BALL": 1,  # in radians; must be large in case ball moves fast
    "RADIUS_TO_GRAB_BALL": 120,  # ROBOT_RADIUS + 30
    "ANGLE_TO_HALT": 0.09,
    "RADIUS_TO_HALT": 102,  # ROBOT_RADIUS + BALL_RADIUS

    # Orientation abs_tol
    "ORIENTATION_ABSOLUTE_TOLERANCE": 1e-4,
    "SPEED_ABSOLUTE_TOLERANCE": 1e-3,

    # Speed
    "DEFAULT_MAX_SPEED": 1,
    "DEFAULT_MIN_SPEED": 0.65,

    # Kick tactic
    "KICK_BALL_DISTANCE": 80,
    "KISS_BALL_DISTANCE": 80
}
