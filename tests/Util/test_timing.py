import time
import pytest
from Util import timing


def test_near_full_load_fps_timer():
    # example preliminary test
    START = time.time()
    TIME_TOTAL = 3
    FPS = 10
    NUM_ITERATIONS = TIME_TOTAL*FPS
    sleep = timing.get_fps_timer(10)
    sleep()  # to initialize it
    for i in range(NUM_ITERATIONS-1):  # -1 because of the first sleep
        time.sleep(1/(FPS+0.05))  # simulate load very close to full load
        sleep()
    end_time = time.time()-START
    assert end_time == pytest.approx(TIME_TOTAL, 0.1)


def test_no_load_fps_timer():
    # example preliminary test
    START = time.time()
    TIME_TOTAL = 3
    FPS = 10
    NUM_ITERATIONS = TIME_TOTAL*FPS
    sleep = timing.get_fps_timer(10)
    sleep()  # to initialize it
    for i in range(NUM_ITERATIONS-1):  # -1 because of the first sleep
        sleep()
    end_time = time.time()-START
    assert end_time == pytest.approx(TIME_TOTAL, 0.1)
