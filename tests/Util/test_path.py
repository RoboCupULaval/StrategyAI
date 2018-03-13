
import unittest
from Util import Path, Position

__author__ = 'Simon Bouchard'


A_START = Position(100, 200)
A_TARGET = Position(123, -456)
A_PATH = Path(start=A_START, target=A_TARGET)

A_START_ARRAY = A_START.array
A_TARGET_ARRAY = A_TARGET.array

A_LIST_OF_POSITION = [Position(0, 0),
                      Position(0, 10),
                      Position(10, 10),
                      Position(10, 20),
                      Position(20, 20),
                      Position(20, 30)]

A_LONG_PATH = Path.from_points(A_LIST_OF_POSITION)
PATH_LENGTH = 50

A_LIST_OF_CLOSE_POSITION =  [Position(1,1), Position(1,-1), Position(1, -2),
                             Position(10,1), Position(10,1), Position(10,2),
                             Position(10, 21), Position(10, 20), Position(10, 22),
                             Position(30, 21), Position(30, 20), Position(30, 22)]

A_PATH_WITH_CLOSE_POINTS = Path.from_points(A_LIST_OF_CLOSE_POSITION)


class TestPosition(unittest.TestCase):

    def test_givenStartTarget_whenNew_thenReturnPath(self):
        path = Path(start=A_START, target=A_TARGET)
        self.assertEqual(path.start, A_START)
        assert path.target == A_TARGET

    def test_givenStartTargetArray_whenFromArray_thenReturnPath(self):
        path = Path.from_array(A_START_ARRAY, A_TARGET_ARRAY)
        self.assertEqual(path.start, A_START)
        assert path.target == A_TARGET

    def test_whenInitializingFromAListOfPoints_thenAListOfPointsIsAssigned(self):
        path = Path.from_points(A_LIST_OF_POSITION)
        assert path.points == A_LIST_OF_POSITION

    def test_givenPath_whenFilter_thenRemoveClosePointsAndKeepTarget(self):
        path = A_PATH_WITH_CLOSE_POINTS.copy()
        path.filter(threshold=5)
        assert path.points == [Position(1, 1), Position(10, 1), Position(10, 21), Position(30, 22)]
        assert path.start == A_PATH_WITH_CLOSE_POINTS.start
        assert path.target == A_PATH_WITH_CLOSE_POINTS.target

    def test_givenPath_whenCopy_thenReturnPathCopy(self):
        path = A_PATH.copy()
        assert path is not A_PATH

    def test_givenPath_whenGettingLength_thenReturnLength(self):
        length = A_LONG_PATH.length
        assert length == PATH_LENGTH
