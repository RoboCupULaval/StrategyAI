# Under MIT License, see LICENSE.txt

from math import ceil, sqrt
from RULEngine.Util.constant import *
from os import remove
import numpy

__author__ = 'RoboCupULaval'


class InfluenceMap(object):
    """
    Class InfluenceMap
    A class to amke an influence map

    Parameter:
        TODO implement them

    by convention in this class the row are x and the column is y.
    decay algorithm = strengthpeak * (strengthdecay**distance)

    """
    def __init__(self, resolution=100.0, strengthdecay=0.8, strengthpeak=100, effectradius=8):
        assert(isinstance(resolution, float))
        assert(isinstance(strengthdecay, float))
        assert(0 < strengthdecay < 1)
        assert(isinstance(strengthpeak, int))
        assert(isinstance(effectradius, int))
        assert(0 < effectradius)

        # todo see how to better implement a graphic representation!
        # this option is not useful anymore
        # numpy.set_printoptions(threshold=10000)
        # GOD NO!
        try:
            remove("IMBoard")
        except OSError:
            print("Nothing to remove!")

        self._resolution = resolution
        self._strengthdecay = strengthdecay
        self._strengthpeak = strengthpeak
        self._effectradius = effectradius
        self._borderstrength = -strengthpeak * 0.03 # TODO change this variable for something not magic!
        self._addedpoint = [] # TODO find a better name for this variable please.
        self._board = [] # this is the board that change
        self._starterboard = [] # this is the board that stay the same after the border are applied.

        number_of_rows_and_columns = self.calculate_rows_and_columns()

        self._numberofrows = number_of_rows_and_columns[0]
        self._numberofcolumns = number_of_rows_and_columns[1]

        self._starterboard = self.create_influence_board()

    def calculate_rows_and_columns(self):
        """
        Determine the best number of rows and columns for the set resolution with the field constants.

        Returns: tuple (int * int), the number of rows and the number of columns

        """

        # set the number of Horizontal/Vertical case for the field given the resolution chosen
        numberofrow = (abs(FIELD_Y_BOTTOM) + FIELD_Y_TOP) / self._resolution
        numberofcolumn = (abs(FIELD_X_LEFT) + FIELD_X_RIGHT) / self._resolution

        # make sure we have int and more than the resolution needs
        numberofrow = int(ceil(numberofrow)) + 2
        numberofcolumn = int(ceil(numberofcolumn)) + 2

        return numberofrow, numberofcolumn

    def create_influence_board(self):
        """
        Create the list of zeros that represent the influence board with numpy

        Returns: List, a numpy matrix self._numberofrows x self._numberofcolumns of int16 initiated at 0.

        """

        return numpy.zeros((self._numberofrows, self._numberofcolumns), numpy.int16)

    def print_board_to_file(self):
        """
        Create a file in the same running directory with a representation of the current board.
        """

        numpy.savetxt("IMBoard", self._board, fmt='%4i')
        # todo remove this line while not in debug mode
        print(self._numberofrows, "  ", self._numberofcolumns, "  -  ", self._addedpoint)

    def determine_influence_radius(self):
        pass

    def initialize_borders(self):
        """
        Initialize the borders of the starterboard and make a copy for the board.
        """
        self.put_boarders()
        self.propagate_borders()
        self._board = numpy.copy(self._starterboard)

    def put_boarders(self):
        """
        Set the border to the borderstrength on all the border cases.
        """
        self._starterboard[0] = self._borderstrength
        self._starterboard[:, 0] = self._borderstrength
        self._starterboard[:, -1] = self._borderstrength
        self._starterboard[-1] = self._borderstrength

    def propagate_borders(self):
        """
        Propagate the borders on the starterboard.
        """

        # Top border
        for border in range(self._numberofcolumns):
            # only for the rows affected by the change.
            for x in range(1, self._effectradius):

                if border - self._effectradius - 1 < 1:
                    columnmin = 1
                else:
                    columnmin = border - self._effectradius - 1

                if border + self._effectradius + 1 > self._numberofcolumns:
                    columnmax = self._numberofcolumns
                else:
                    columnmax = border + self._effectradius + 1
                # for every columns affected
                for y in range(columnmin, columnmax):
                    if not (y == 0 or y == self._numberofcolumns) and\
                           ((x - 0)**2 + (y - border)**2) <= self._effectradius**2:

                        decay = int((self._borderstrength * (self._strengthdecay **
                                     self.distance(0, border, x, y))))
                        self._starterboard[x, y] += decay

        # bottom border
        for border in range(self._numberofcolumns):

            for x in range(self._numberofrows - 2, self._numberofrows - self._effectradius, -1):

                if border - self._effectradius - 1 < 1:
                    columnmin = 1
                else:
                    columnmin = border - self._effectradius - 1

                if border + self._effectradius + 1 > self._numberofcolumns:
                    columnmax = self._numberofcolumns
                else:
                    columnmax = border + self._effectradius + 1

                for y in range(columnmin, columnmax):
                    if not (y == 0 or y == self._numberofcolumns) and \
                           ((x - self._numberofrows-1)**2 + (y - border)**2) <= self._effectradius**2:

                        decay = int((self._borderstrength * (self._strengthdecay **
                                                        self.distance(self._numberofrows - 1, border, x, y))))
                        self._starterboard[x, y] += decay

        # left border
        for border in range(self._numberofrows):

            for y in range(1, self._effectradius):

                if border - self._effectradius - 1 < 1:
                    rowmin = 1
                else:
                    rowmin = border - self._effectradius - 1

                if border + self._effectradius + 1 > self._numberofrows:
                    rowmax = self._numberofrows
                else:
                    rowmax = border + self._effectradius + 1

                for x in range(rowmin, rowmax):
                    if not (x == 0 or x == self._numberofrows) and\
                           ((x - border)**2 + (y - 0)**2) <= self._effectradius**2:

                        decay = int((self._borderstrength * (self._strengthdecay ** \
                                                                        self.distance(border, 0, x, y))))
                        self._starterboard[x, y] += decay

        # right border
        for border in range(self._numberofrows):

            for y in range(self._numberofcolumns - 2, self._numberofcolumns - self._effectradius, -1):

                if border - self._effectradius - 1 < 1:
                    rowmin = 1
                else:
                    rowmin = border - self._effectradius - 1

                if border + self._effectradius + 1 > self._numberofrows:
                    rowmax = self._numberofrows
                else:
                    rowmax = border + self._effectradius + 1

                for x in range(rowmin, rowmax):
                    if not (x == 0 or x == self._numberofrows) and \
                           ((x - border)**2 + (y - self._numberofcolumns - 1)**2) <= self._effectradius**2:

                        decay = int((self._borderstrength * (self._strengthdecay ** \
                                    self.distance(border, self._numberofcolumns - 1, x, y))))
                        self._starterboard[x, y] += decay

    def add_point(self, row, column, strength=0):
        """
        Do not use, depreciated.
        Args:
            row: The row of the point
            column: The column of the point
            strength: The strength of the point

        """
        # TODO see to remove it maybe? Useless
        assert(isinstance(row, int))
        assert(isinstance(column, int))
        assert(isinstance(strength, int))
        assert(0 <= row <= self._numberofrows)
        assert(0 <= column <= self._numberofcolumns)
        assert(-self._strengthpeak <= strength <= self._strengthpeak)

        self._board[row, column] = strength
        self._addedpoint.append((row, column, strength))

    def add_point_and_propagate_influence(self, row, column, strength=0):
        """
        Add a point to the board and apply its influence on it.
        Args:
            row: The row of the point
            column: The column of the point
            strength: The strength of the point
        """
        assert(isinstance(row, int))
        assert(isinstance(column, int))
        assert(isinstance(strength, int))
        assert(0 <= row <= self._numberofrows)
        assert(0 <= column <= self._numberofcolumns)
        assert(-self._strengthpeak <= strength <= self._strengthpeak)

        self._board[row, column] = strength
        self._addedpoint.append((row, column, strength))

        if row - self._effectradius - 1 < 1:
            rowmin = 1
        else:
            rowmin = row - self._effectradius - 1

        if row + self._effectradius + 1 > self._numberofrows:
            rowmax = self._numberofrows
        else:
            rowmax = row + self._effectradius + 1

        if column - self._effectradius - 1 < 1:
            columnmin = 1
        else:
            columnmin = column - self._effectradius - 1

        if column + self._effectradius + 1 > self._numberofcolumns:
            columnmax = self._numberofcolumns
        else:
            columnmax = column + self._effectradius + 1

        for x in range(rowmin, rowmax):
            for y in range(columnmin, columnmax):
                if not (x == row and y == column) and ((x - row)**2 + (y - column)**2) <= self._effectradius**2:
                    decay = int((strength * (self._strengthdecay ** self.distance(x, y, row, column))))
                    self._board[x, y] += decay

    def add_square_and_propagate(self, top, bottom, left, right, strength):
        assert(isinstance(top, int))
        assert(isinstance(bottom, int))
        assert(isinstance(left, int))
        assert(isinstance(right, int))
        assert(0 < top < self._numberofrows - 1)
        assert(0 < bottom < self._numberofrows - 1)
        assert(0 < left < self._numberofcolumns - 1)
        assert(0 < right < self._numberofcolumns - 1)
        assert(top <= bottom)
        assert(left <= right)
        assert(isinstance(strength, int))
        assert(-self._strengthpeak <= strength <= self._strengthpeak)

        for x in range(top, bottom):
            for y in range(left, right):
                self.add_point_and_propagate_influence(x, y, strength)

    def find_closest_point_of_strength_around(self, row, column, strengthrequired):
        assert(isinstance(row, int))
        assert(isinstance(column, int))
        assert(isinstance(strengthrequired, int))
        assert(0 <= row <= self._numberofrows)
        assert(0 <= column <= self._numberofcolumns)
        assert(-(self._strengthpeak**2) <= strengthrequired <= self._strengthpeak**2)

        result = []
        counter = 1
        rtop = False
        rbottom = False
        cleft = False
        cright = False
        rowinsidesquare = [row]
        columninsidesquare = [column]

        while not result:

            for x in range(row-counter, row+counter+1):

                if rtop and rbottom and cleft and cright:
                    result.append(0)
                    break

                if x < 1:
                    rtop = True
                    continue

                if x > self._numberofrows - 1:
                    rbottom = True
                    break

                for y in range(column-counter, column+counter+1):

                    if y < 1:
                        cleft = True
                        continue

                    if y > self._numberofcolumns - 1:
                        cright = True
                        break

                    if x in rowinsidesquare and y in columninsidesquare:
                        continue

                    if self._board[x, y] >= strengthrequired:
                        result.append((x, y))

            counter += 1
            rowinsidesquare = range(row-counter+1, row+counter)
            columninsidesquare = range(column-counter+1, column+counter)

        if not result[0]:
            result.clear()

        return result

    def find_points_of_strength_in_square(self, centerx, centery, radius, strength, over=True):
        assert(isinstance(centerx, int))
        assert(isinstance(centery, int))
        assert(isinstance(radius, int))
        assert(isinstance(strength, int))
        assert(isinstance(over, bool))
        assert(0 <= centerx <= self._numberofrows)
        assert(0 <= centery <= self._numberofcolumns)
        assert(radius < self._numberofcolumns)
        assert(-(self._strengthpeak**2) <= strength <= self._strengthpeak**2)

        result = []

        if centerx - radius - 1 < 1:
            rowmin = 1
        else:
            rowmin = centerx - radius - 1

        if centerx + radius + 1 > self._numberofrows:
            rowmax = self._numberofrows
        else:
            rowmax = centerx + radius + 1

        if centery - radius - 1 < 1:
            columnmin = 1
        else:
            columnmin = centery - radius - 1

        if centery + radius + 1 > self._numberofcolumns:
            columnmax = self._numberofcolumns
        else:
            columnmax = centery + radius + 1

        if over:
            for x in range(rowmin, rowmax + 1):
                for y in range(columnmin, columnmax + 1):
                    if self._board[x, y] >= strength:
                        result.append((x, y))
        else:
            for x in range(rowmin, rowmax + 1):
                for y in range(columnmin, columnmax + 1):
                    if self._board[x, y] <= strength:
                        result.append((x, y))

        return result

    def clear_point_on_board(self):
        self._board = numpy.copy(self._starterboard)
        self._addedpoint.clear()

    def transform_field_to_board_position(self, position):
        assert(isinstance(position, Position))
        assert(position.x <= FIELD_X_RIGHT + 100)
        assert(position.x >= FIELD_X_LEFT - 100)
        assert(position.y <= FIELD_Y_TOP + 100)
        assert(position.y >= FIELD_Y_BOTTOM - 100)

        xpos = position.x + ((abs(FIELD_X_LEFT) + FIELD_X_RIGHT) / 2)
        ypos = position.y + ((abs(FIELD_Y_BOTTOM) + FIELD_Y_TOP) / 2)

        xpos = int(round(xpos / self._resolution, 0))
        ypos = int(round(ypos / self._resolution, 0))

        return (xpos, ypos)

    def transform_board_to_field_position(self, row, column):
        assert(isinstance(row, int))
        assert(isinstance(column, int))
        assert(0 <= row <= self._numberofrows - 2)
        assert(0 <= column <= self._numberofcolumns - 2)

        xpos = FIELD_X_LEFT + (column * self._resolution)
        ypos = FIELD_Y_TOP - (row * self._resolution)

        tempposition = Position(xpos, ypos)
        return tempposition

    def distance(self, x1, y1, x2, y2):
        # TODO possibly move this function somewhere else
        assert(isinstance(x1, int) or isinstance(x1, float))
        assert(isinstance(x2, int) or isinstance(x2, float))
        assert(isinstance(y1, int) or isinstance(y1, float))
        assert(isinstance(y2, int) or isinstance(y2, float))
        return sqrt((x2 - x1)**2 + (y2 - y1)**2)
