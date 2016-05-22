#Under MIT License, see LICENSE.txt
class Field():
    def __init__(self, ball):
        self.ball = ball

    def move_ball(self, position, delta):
        self.ball.set_position(position, delta)
