import time
import pytest
from Util import timing


def test_near_full_load_fps_timer():
    # example preliminary test
    start = time.time()
    time_total = 2
    fps = 10
    num_iterations = time_total*fps
    sleep = timing.create_fps_timer(fps)
    sleep()  # to initialize it
    for _ in range(num_iterations-1):  # -1 because of the first sleep
        time.sleep(1/(fps+0.05))  # simulate load very close to full load
        sleep()
    end_time = time.time()-start
    assert end_time == pytest.approx(time_total, 0.1)


def test_no_load_fps_timer():
    # example preliminary test
    start = time.time()
    time_total = 2
    fps = 10
    num_iterations = time_total*fps
    sleep = timing.create_fps_timer(fps)
    sleep()  # to initialize it
    for _ in range(num_iterations-1):  # -1 because of the first sleep
        sleep()
    end_time = time.time()-start
    assert end_time == pytest.approx(time_total, 0.1)

def test_callback_called_fps_timer():
    fps = 10
    callback_called = False

    def mock_callback(time_var):  # pylint: disable=unused-argument
        nonlocal callback_called
        callback_called = True
    sleep = timing.create_fps_timer(fps, on_miss_callback=mock_callback)
    sleep()
    time.sleep(0.2)
    sleep()
    assert callback_called is True

def test_callback_delay_fps_timer():
    fps = 10
    callback_time = None

    def mock_callback(time_var):
        nonlocal callback_time
        callback_time = time_var
    sleep = timing.create_fps_timer(fps, on_miss_callback=mock_callback)
    sleep()
    time.sleep(0.2)
    sleep()
    assert callback_time >= 0
