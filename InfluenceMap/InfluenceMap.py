#Under MIT License, see LICENSE.txt

from math import ceil, sqrt
from RULEngine.Util.constant import *
from os import remove
import numpy

__author__ = 'RoboCupULaval'


class InfluenceMap(object):
    """
    Class InfluenceMap
    A class to represent a influence map for a Robocup SSL field.

    Parameter:
        TODO implement them

    decay algorithm = strengthpeak * (strengthdecay**distance)

    """
    def __init__(self, resolution=100.0, strengthdecay = 0.8, strengthpeak=100, effectradius=8):
        assert(isinstance(resolution, float))
        assert(isinstance(strengthdecay, float))
        assert(0 < strengthdecay < 1)
        assert(isinstance(strengthpeak, int))
        assert(isinstance(effectradius, int))
        assert(0 < effectradius)

        #todo see how to better implement a graphic representation!
        #this option is not useful anymore
        #numpy.set_printoptions(threshold=10000)
        #GOD NO!
        try:
            remove("IMBoard")
            remove("StaticBoard")
        except:
            print("Nothing to remove!")

        self._resolution = resolution
        self._strengthdecay = strengthdecay
        self._strengthpeak = strengthpeak
        self._effectradius = effectradius
        self._borderstrength = -strengthpeak * 0.02
        self._addedpoint = []

        #set the number of Horizontal/Vertical case for the field given the resolution chosen
        numberOfColumn = (abs(FIELD_X_LEFT) + FIELD_X_RIGHT) / self._resolution
        numberOfRow = (abs(FIELD_Y_BOTTOM) + FIELD_Y_TOP) / self._resolution

        self._numberOfRow = int(ceil(numberOfRow)) + 2
        self._numberOfColumn = int(ceil(numberOfColumn)) + 2

        self._IMBoard = numpy.zeros( (self._numberOfRow, self._numberOfColumn), numpy.int16)
        self._StarterIMBoard = numpy.zeros( (self._numberOfRow, self._numberOfColumn), numpy.int16)

        self._StaticBoard = numpy.zeros((self._numberOfRow, self._numberOfColumn), numpy.bool)
        self._StarterStaticBoard = numpy.zeros((self._numberOfRow, self._numberOfColumn), numpy.bool)

    def printNumberOfCases(self):
        numpy.savetxt("IMBoard", self._IMBoard, fmt='%4i')
        numpy.savetxt("StaticBoard", self._StaticBoard, fmt='%4i')
        print(self._numberOfRow, "  ", self._numberOfColumn, "  -  ", self._addedpoint)

    def setStarterBoard(self):
        self.setBorders()
        self.distributeStartingStrength()

    def setBorders(self):
        self._StarterIMBoard[0] = self._borderstrength
        self._StarterStaticBoard[0] = True
        self._StarterIMBoard[:, 0] = self._borderstrength
        self._StarterStaticBoard[:, 0] = True
        self._StarterIMBoard[:, -1] = self._borderstrength
        self._StarterStaticBoard[:, -1] = True
        self._StarterIMBoard[-1] = self._borderstrength
        self._StarterStaticBoard[-1] = True

    def distributeStartingStrength(self):

        for border in range(self._numberOfColumn):

            for x in range(1, self._effectradius):

                if border - self._effectradius - 1 < 1:
                    columnmin = 1
                else:
                    columnmin = border - self._effectradius - 1

                if border + self._effectradius + 1 > self._numberOfColumn:
                    columnmax = self._numberOfColumn
                else:
                    columnmax = border + self._effectradius + 1

                for y in range(columnmin, columnmax):
                    if not self._StarterStaticBoard[x, y] and ((x - 0)**2 + (y - border)**2) <= self._effectradius**2:
                        decay = int((self._borderstrength * (self._strengthdecay ** \
                                                                        self.distance(0, border, x, y))))
                        self._StarterIMBoard[x, y] += decay

        for border in range(self._numberOfColumn):

            for x in range(self._numberOfRow - 2, self._numberOfRow - self._effectradius, -1):

                if border - self._effectradius - 1 < 1:
                    columnmin = 1
                else:
                    columnmin = border - self._effectradius - 1

                if border + self._effectradius + 1 > self._numberOfColumn:
                    columnmax = self._numberOfColumn
                else:
                    columnmax = border + self._effectradius + 1

                for y in range(columnmin, columnmax):
                    if not self._StarterStaticBoard[x, y] and \
                       ((x - self._numberOfRow-1)**2 + (y - border)**2) <= self._effectradius**2:

                        decay = int((self._borderstrength * (self._strengthdecay ** \
                                                        self.distance(self._numberOfRow - 1, border, x, y))))
                        self._StarterIMBoard[x, y] += decay

        for border in range(self._numberOfRow):

            for y in range(1, self._effectradius):

                if border - self._effectradius - 1 < 1:
                    rowmin = 1
                else:
                    rowmin = border - self._effectradius - 1

                if border + self._effectradius + 1 > self._numberOfRow:
                    rowmax = self._numberOfRow
                else:
                    rowmax = border + self._effectradius + 1

                for x in range(rowmin, rowmax):
                    if not self._StarterStaticBoard[x, y] and ((x - border)**2 + (y - 0)**2) <= self._effectradius**2:
                        decay = int((self._borderstrength * (self._strengthdecay ** \
                                                                        self.distance(border, 0, x, y))))
                        self._StarterIMBoard[x, y] += decay

        for border in range(self._numberOfRow):

            for y in range(self._numberOfColumn - 2, self._numberOfColumn - self._effectradius, -1):

                if border - self._effectradius - 1 < 1:
                    rowmin = 1
                else:
                    rowmin = border - self._effectradius - 1

                if border + self._effectradius + 1 > self._numberOfRow:
                    rowmax = self._numberOfRow
                else:
                    rowmax = border + self._effectradius + 1

                for x in range(rowmin, rowmax):
                    if not self._StarterStaticBoard[x, y] and \
                                    ((x - border)**2 + (y - self._numberOfColumn - 1)**2) <= self._effectradius**2:
                        decay = int((self._borderstrength * (self._strengthdecay ** \
                                    self.distance(border, self._numberOfColumn - 1, x, y))))
                        self._StarterIMBoard[x, y] += decay

        self._IMBoard = numpy.copy(self._StarterIMBoard)
        self._StaticBoard = numpy.copy(self._StarterStaticBoard)

    def addPoint(self, row, column, strength=0):
        assert(isinstance(row, int))
        assert(isinstance(column, int))
        assert(isinstance(strength, int))
        assert(0 <= row <= self._numberOfRow)
        assert(0 <= column <= self._numberOfColumn)
        assert(-self._strengthpeak <= strength <= self._strengthpeak)

        self._IMBoard[row, column] = strength
        self._StaticBoard[row, column] = True
        self._addedpoint.append((row, column, strength))


    def addPointAndInfluence(self, row, column, strength=0):
        assert(isinstance(row, int))
        assert(isinstance(column, int))
        assert(isinstance(strength, int))
        assert(0 <= row <= self._numberOfRow)
        assert(0 <= column <= self._numberOfColumn)
        assert(-self._strengthpeak <= strength <= self._strengthpeak)

        self._IMBoard[row, column] = strength
        self._StaticBoard[row, column] = True
        self._addedpoint.append((row, column, strength))

        if row - self._effectradius - 1 < 1:
            rowmin = 1
        else:
            rowmin = row - self._effectradius - 1

        if row + self._effectradius + 1> self._numberOfRow:
            rowmax = self._numberOfRow
        else:
            rowmax = row + self._effectradius + 1

        if column - self._effectradius - 1 < 1:
            columnmin = 1
        else:
            columnmin = column - self._effectradius - 1

        if column + self._effectradius + 1 > self._numberOfColumn:
            columnmax = self._numberOfColumn
        else:
            columnmax = column + self._effectradius + 1

        for x in range(rowmin, rowmax):
            for y in range(columnmin, columnmax):
                if not self._StaticBoard[x,y] and ((x - row)**2 + (y - column)**2) <= self._effectradius**2:
                    decay = int((strength * (self._strengthdecay ** self.distance(x, y, row, column))))
                    self._IMBoard[x, y] += decay

    def addSquareAndInfluence(self, top, bottom, left, right, strength):
        assert(isinstance(top, int))
        assert(isinstance(bottom, int))
        assert(isinstance(left, int))
        assert(isinstance(right, int))
        assert(0 < top < self._numberOfRow - 1)
        assert(0 < bottom < self._numberOfRow - 1)
        assert(0 < left < self._numberOfColumn - 1)
        assert(0 < right < self._numberOfColumn - 1)
        assert(top <= bottom)
        assert(left <= right)
        assert(isinstance(strength, int))
        assert(-self._strengthpeak <= strength <= self._strengthpeak)

        for x in range(top, bottom):
            for y in range(left, right):
                self.addPointOfInfluence(x, y, strength)

    def addSimplisticRobotOnBoard(self, row, column):
        #TODO THIS FUNCTION IS NOT DONE!
        #TODO see what we do with this function, is it the one used?
        assert(isinstance(row, int))
        assert(isinstance(column, int))
        assert(0 <= row <= self._numberOfRow - 2)
        assert(0 <= column <= self._numberOfColumn - 2)

        robotRadius = int(ROBOT_RADIUS / self._resolution) - 1

        if robotRadius < 1:
            self._StaticBoard[row, column] = True
        else:
            for x in range(-robotRadius, robotRadius+1):
                self._StaticBoard[row+x, column] = True
                self._StaticBoard[row, column+x] = True
                #TODO please change that for the love of god
                self._StaticBoard[row-1, column-1] = True
                self._StaticBoard[row+1, column+1] = True
                self._StaticBoard[row-1, column+1] = True
                self._StaticBoard[row+1, column-1] = True

    def addRobotOnBoard(self, row, column, strength):
        assert(isinstance(row, int))
        assert(isinstance(column, int))
        assert(isinstance(strength, int))
        assert(0 <= row <= self._numberOfRow - 2)
        assert(0 <= column <= self._numberOfColumn - 2)
        assert(-self._strengthpeak <= strength <= self._strengthpeak)
        #todo see if this useful.
        pass



    def findClosestPoint(self, row, column, strengthrequired):
        assert(isinstance(row, int))
        assert(isinstance(column, int))
        assert(isinstance(strengthrequired, int))
        assert(0 <= row <= self._numberOfRow)
        assert(0 <= column <= self._numberOfColumn)
        assert(-4*self._strengthpeak <= strengthrequired <= 4*self._strengthpeak)


        result = []
        counter = 1
        rtop = False
        rbottom = False
        cleft = False
        cright = False
        rowinsidesquare = [row]
        columninsidesquare = [column]

        while not result:

            for x in range(row-counter,row+counter+1):

                if rtop and rbottom and cleft and cright:
                    result.append(0)
                    break

                if x < 1:
                    rtop = True
                    continue

                if x > self._numberOfRow - 1:
                    rbottom = True
                    break

                for y in range(column-counter,column+counter+1):

                    if y < 1:
                        cleft = True
                        continue

                    if y > self._numberOfColumn - 1:
                        cright = True
                        break

                    if x in rowinsidesquare and y in columninsidesquare:
                        continue

                    if self._IMBoard[x,y] >= strengthrequired:
                        result.append((x,y))

            counter += 1
            rowinsidesquare = range(row-counter+1, row+counter)
            columninsidesquare = range(column-counter+1, column+counter)

        if not result[0]:
            result.clear()

        return result

    def clearBoard(self):
        self._IMBoard = numpy.copy(self._StarterIMBoard)
        self._StaticBoard = numpy.copy(self._StarterStaticBoard)
        self._addedpoint.clear()

    def transformFieldPositionToGridPosition(self, position):
        assert(isinstance(position, Position))
        assert(position.x <= FIELD_X_RIGHT + 100)
        assert(position.x >= FIELD_X_LEFT - 100)
        assert(position.y <= FIELD_Y_TOP + 100)
        assert(position.y >= FIELD_Y_BOTTOM - 100)

        Xpos = position.x + ((abs(FIELD_X_LEFT) + FIELD_X_RIGHT) / 2)
        Ypos = position.y + ((abs(FIELD_Y_BOTTOM) + FIELD_Y_TOP) / 2)

        Xpos = int(round(Xpos / self._resolution, 0))
        Ypos = int(round(Ypos / self._resolution, 0))

        return (Xpos, Ypos)

    def transformGridPositionToFieldPosition(self, row, column):
        assert(isinstance(row, int))
        assert(isinstance(column, int))
        assert(0 <= row <= self._numberOfRow - 2)
        assert(0 <= column <= self._numberOfColumn - 2)

        Xpos = FIELD_X_LEFT + (column * self._resolution)
        Ypos = FIELD_Y_TOP - (row * self._resolution)

        tempPosition = Position(Xpos, Ypos)
        return tempPosition

    def distance(self, x1, y1, x2, y2):
        assert(isinstance(x1, int) or isinstance(x1, float))
        assert(isinstance(x2, int) or isinstance(x2, float))
        assert(isinstance(y1, int) or isinstance(y1, float))
        assert(isinstance(y2, int) or isinstance(y2, float))
        return sqrt((x2 - x1)**2 + (y2 - y1)**2)

