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

A_LIST_OF_CLOSE_POSITION = [Position(1, 1), Position(1, -1), Position(1, -2),
                            Position(10, 1), Position(10, 1), Position(10, 2),
                            Position(10, 21), Position(10, 20), Position(10, 22),
                            Position(30, 21), Position(30, 20), Position(30, 22)]

A_PATH_WITH_CLOSE_POINTS = Path.from_points(A_LIST_OF_CLOSE_POSITION)
A_PATH_WITH_CLOSE_POINTS_FILTERED = Path.from_points([Position(1, 1),
                                                      Position(10, 1),
                                                      Position(10, 21),
                                                      Position(30, 22)])

def test_create_path_start_end():
    path = Path(start=A_START, target=A_TARGET)
    assert path.start == A_START
    assert path.target == A_TARGET

def test_create_path_from_array():
    path = Path.from_array(A_START_ARRAY, A_TARGET_ARRAY)
    assert path.start == A_START
    assert path.target == A_TARGET

def test_create_path_point_list():
    path = Path.from_points(A_LIST_OF_POSITION)
    assert path.points == A_LIST_OF_POSITION

def test_path_filtering_keep_ends():
    path = A_PATH_WITH_CLOSE_POINTS.copy()
    path.filter(threshold=5)
    assert path.points == A_PATH_WITH_CLOSE_POINTS_FILTERED.points
    assert path.start == A_PATH_WITH_CLOSE_POINTS_FILTERED.start
    assert path.target == A_PATH_WITH_CLOSE_POINTS_FILTERED.target

def test_path_copy():
    path = A_PATH.copy()
    assert path is not A_PATH

def test_path_length():
    length = A_LONG_PATH.length
    assert length == PATH_LENGTH
