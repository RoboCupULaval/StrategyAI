# Under MIT License, see LICENSE.txt
from RULEngine.Game.Ball import Ball
from config.config_service import ConfigService
from ..Util.area import *


class Field:
    def __init__(self, ball: Ball):
        self.ball = ball

        cfg = ConfigService()
        if cfg.config_dict["GAME"]["terrain_type"] == "normal":
            self.constant = normal
        elif cfg.config_dict["GAME"]["terrain_type"] == "small":
            self.constant = small
        else:
            print("ERREUR lors de la création de l'objet field\n Mauvais terrain_type en config - normal choisi\n")
            self.constant = normal

    def move_ball(self, position, delta):
        self.ball.set_position(position, delta)

    def is_inside_goal_area(self, position, is_yellow):
        assert (isinstance(position, Position))
        assert (isinstance(is_yellow, bool))
        x_left = self.constant["FIELD_GOAL_YELLOW_X_LEFT"] if is_yellow else self.constant["FIELD_GOAL_BLUE_X_LEFT"]
        x_right = self.constant["FIELD_GOAL_YELLOW_X_RIGHT"] if is_yellow else self.constant["FIELD_GOAL_BLUE_X_RIGHT"]
        top_circle = self.constant["FIELD_GOAL_YELLOW_TOP_CIRCLE"] if is_yellow\
            else self.constant["FIELD_GOAL_BLUE_TOP_CIRCLE"]
        bot_circle = self.constant["FIELD_GOAL_YELLOW_BOTTOM_CIRCLE"] if is_yellow\
            else self.constant["FIELD_GOAL_BLUE_BOTTOM_CIRCLE"]
        if isInsideSquare(position, self.constant["FIELD_GOAL_Y_TOP"], self.constant["FIELD_GOAL_Y_BOTTOM"],
                          x_left, x_right):
            if is_inside_circle(position, top_circle, self.constant["FIELD_GOAL_RADIUS"]):
                return True
            elif is_inside_circle(position, bot_circle, self.constant["FIELD_GOAL_RADIUS"]):
                return True
            return True
        else:
            return False

    def is_outside_goal_area(self, position, is_yellow):
        return not self.is_inside_goal_area(position, is_yellow)

    def stay_inside_goal_area(self, position, is_yellow):
        # TODO Not tested: stayInsideGoalArea
        if self.is_inside_goal_area(position, is_yellow):
            return Position(position.x, position.y)
        else:
            x_left = self.constant["FIELD_GOAL_YELLOW_X_LEFT"] if is_yellow else self.constant["FIELD_GOAL_BLUE_X_LEFT"]
            x_right = self.constant["FIELD_GOAL_YELLOW_X_RIGHT"] if is_yellow\
                else self.constant["FIELD_GOAL_BLUE_X_RIGHT"]
            position = stayInsideSquare(position, self.constant["FIELD_GOAL_Y_TOP"],
                                        self.constant["FIELD_GOAL_Y_BOTTOM"], x_left, x_right)
            if isInsideSquare(position, self.constant["FIELD_GOAL_Y_TOP"], self.constant["FIELD_GOAL_Y_BOTTOM"],
                              x_left, x_right):
                return position
            else:
                circle_top = self.constant["FIELD_GOAL_YELLOW_TOP_CIRCLE"] if is_yellow\
                    else self.constant["FIELD_GOAL_BLUE_TOP_CIRCLE"]
                circle_bot = self.constant["FIELD_GOAL_YELLOW_BOTTOM_CIRCLE"] if is_yellow\
                    else self.constant["FIELD_GOAL_BLUE_BOTTOM_CIRCLE"]
                dst_top = get_distance(circle_top, position)
                dst_bot = get_distance(circle_bot, position)

                if dst_top >= dst_bot:
                    return stayInsideCircle(position, circle_top, self.constant["FIELD_GOAL_RADIUS"])
                else:
                    return stayInsideCircle(position, circle_bot, self.constant["FIELD_GOAL_RADIUS"])

    def stay_outside_goal_area(self, position, is_yellow):
        # TODO Not tested: stayOutsideGoalArea
        if self.is_outside_goal_area(position, is_yellow):
            return Position(position.x, position.y)
        else:
            x_left = self.constant["FIELD_GOAL_YELLOW_X_LEFT"] if is_yellow else self.constant["FIELD_GOAL_BLUE_X_LEFT"]
            x_right = self.constant["FIELD_GOAL_YELLOW_X_RIGHT"] if is_yellow\
                else self.constant["FIELD_GOAL_BLUE_X_RIGHT"]
            y_top = self.constant["FIELD_GOAL_SEGMENT"] / 2
            y_bottom = (self.constant["FIELD_GOAL_SEGMENT"] / 2) * -1
            circle_top = self.constant["FIELD_GOAL_YELLOW_TOP_CIRCLE"] if is_yellow\
                else self.constant["FIELD_GOAL_BLUE_TOP_CIRCLE"]
            circle_bot = self.constant["FIELD_GOAL_YELLOW_BOTTOM_CIRCLE"] if is_yellow\
                else self.constant["FIELD_GOAL_BLUE_BOTTOM_CIRCLE"]
            position = stayOutsideSquare(position, y_top, y_bottom, x_left, x_right)
            position = stayOutsideCircle(position, circle_top, self.constant["FIELD_GOAL_RADIUS"])
            position = stayOutsideCircle(position, circle_bot, self.constant["FIELD_GOAL_RADIUS"])
            return Position(position.x, position.y)


normal = {
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
    "FIELD_GOAL_RADIUS": 1000,
    "FIELD_GOAL_SEGMENT": 500,

    # Goal Parameters
    "FIELD_GOAL_Y_TOP": 1250,  # FIELD_GOAL_RADIUS + FIELD_GOAL_SEGMENT / 2
    "FIELD_GOAL_Y_BOTTOM": -1250,  # (FIELD_GOAL_RADIUS + FIELD_GOAL_SEGMENT / 2) * -1
    "FIELD_GOAL_BLUE_X_LEFT": -4500,  # FIELD_X_LEFT
    "FIELD_GOAL_BLUE_X_RIGHT": -3500,  # FIELD_X_LEFT + FIELD_GOAL_RADIUS
    "FIELD_GOAL_YELLOW_X_LEFT": 3500,  # FIELD_X_RIGHT - FIELD_GOAL_RADIUS
    "FIELD_GOAL_YELLOW_X_RIGHT": 4500,  # FIELD_X_RIGHT

    # Field Positions
    "FIELD_GOAL_BLUE_TOP_CIRCLE": Position(-4500, 250),  # FIELD_X_LEFT, FIELD_GOAL_SEGMENT / 2)
    "FIELD_GOAL_BLUE_BOTTOM_CIRCLE": Position(-4500, -250),  # FIELD_X_LEFT, FIELD_GOAL_SEGMENT / 2 * -1)
    "FIELD_GOAL_BLUE_MID_GOAL": Position(-4500, 0),
    "FIELD_GOAL_YELLOW_TOP_CIRCLE": Position(4500, 250),  # FIELD_X_RIGHT, FIELD_GOAL_SEGMENT / 2)
    "FIELD_GOAL_YELLOW_BOTTOM_CIRCLE": Position(4500, -250),  # FIELD_X_RIGHT, FIELD_GOAL_SEGMENT / 2 * -1)
    "FIELD_GOAL_YELLOW_MID_GOAL": Position(4500, 0),

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
    "POSITION_DEADZONE": 200,  # ROBOT_RADIUS*1.5

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

small = {
    "ROBOT_RADIUS": 90,
    "BALL_RADIUS": 22,
    "PLAYER_PER_TEAM": 6,
    # TODO KICKSPEED
    "KICK_MAX_SPD": 4,

    # Field Parameters
    "FIELD_Y_TOP": 1090,
    "FIELD_Y_BOTTOM": -1090,
    "FIELD_X_LEFT": -1636,
    "FIELD_X_RIGHT": 1636,
    "FIELD_GOAL_RADIUS": 363,
    "FIELD_GOAL_SEGMENT": 181,

    # Goal Parameters
    "FIELD_GOAL_Y_TOP": 536,  # FIELD_GOAL_RADIUS + FIELD_GOAL_SEGMENT / 2
    "FIELD_GOAL_Y_BOTTOM": -536,  # (FIELD_GOAL_RADIUS + FIELD_GOAL_SEGMENT / 2) * -1
    "FIELD_GOAL_BLUE_X_LEFT": -1636,  # FIELD_X_LEFT
    "FIELD_GOAL_BLUE_X_RIGHT": -1272,  # FIELD_X_LEFT + FIELD_GOAL_RADIUS
    "FIELD_GOAL_YELLOW_X_LEFT": 1272,  # FIELD_X_RIGHT - FIELD_GOAL_RADIUS
    "FIELD_GOAL_YELLOW_X_RIGHT": 1636,  # FIELD_X_RIGHT

    # Field Positions
    "FIELD_GOAL_BLUE_TOP_CIRCLE": Position(-1636, 250),  # FIELD_X_LEFT, FIELD_GOAL_SEGMENT / 2)
    "FIELD_GOAL_BLUE_BOTTOM_CIRCLE": Position(-1636, -250),  # FIELD_X_LEFT, FIELD_GOAL_SEGMENT / 2 * -1)
    "FIELD_GOAL_BLUE_MID_GOAL": Position(-1636, 0),
    "FIELD_GOAL_YELLOW_TOP_CIRCLE": Position(1636, 250),  # FIELD_X_RIGHT, FIELD_GOAL_SEGMENT / 2)
    "FIELD_GOAL_YELLOW_BOTTOM_CIRCLE": Position(1636, -250),  # FIELD_X_RIGHT, FIELD_GOAL_SEGMENT / 2 * -1)
    "FIELD_GOAL_YELLOW_MID_GOAL": Position(1636, 0),

    # Legal field dimensions
    "LEGAL_Y_TOP": 1090,
    "LEGAL_Y_BOTTOM": -1090,
    "LEGAL_X_LEFT": -1450,
    "LEGAL_X_RIGHT": 1450,

    # Simulation param
    "DELTA_T": 17,  # ms, hack, à éviter

    # Communication information
    "DEBUG_RECEIVE_BUFFER_SIZE": 100,

    # Deadzones
    "SPEED_DEAD_ZONE_DISTANCE": 150,
    "POSITION_DEADZONE": 200,  # ROBOT_RADIUS*1.5

    # Radius and angles for tactics
    "DISTANCE_BEHIND": 120,  # ROBOT_RADIUS + 30  # in millimeters
    "ANGLE_TO_GRAB_BALL": 1,  # in radians; must be large in case ball moves fast
    "RADIUS_TO_GRAB_BALL": 120,  # ROBOT_RADIUS + 30
    "ANGLE_TO_HALT": 0.09,
    "RADIUS_TO_HALT": 50,  # ROBOT_RADIUS + BALL_RADIUS

    # Orientation abs_tol
    "ORIENTATION_ABSOLUTE_TOLERANCE": 1e-4,
    "SPEED_ABSOLUTE_TOLERANCE": 1e-3,

    # Speed
    "DEFAULT_MAX_SPEED": 1,
    "DEFAULT_MIN_SPEED": 0.65,

    # Kick tactic
    "KICK_BALL_DISTANCE": 130,
    "KISS_BALL_DISTANCE": 100
}
