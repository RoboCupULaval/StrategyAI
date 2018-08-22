import time
from typing import Optional, Callable


def create_fps_timer(desired_fps: float, on_miss_callback: Optional[Callable] = None):
    """ Returns a timing function that sleeps to allow constant time between iterations.
    The precision of the time between iterations is up to the host operating system.
    ON AVERAGE, it should be around the desired_fps value.

    The callback is a function reference that accepts one parameter, which is the time
    that lateness delay in seconds. This function is only called when the desired_fps
    cannot be respected (in other words, the function would need to go back in time).
    """
    assert desired_fps > 0, 'the desired_fps must be a strictly positive value.'
    timer_period = 1/desired_fps

    next_time = None  # None initialization so a pause causes no borking

    def fps_wait():
        current_time = time.time()
        nonlocal next_time
        if next_time is None:
            next_time = current_time + timer_period

        time_to_sleep = next_time - current_time

        if time_to_sleep > 0:
            time.sleep(time_to_sleep)
        elif on_miss_callback is not None:
            on_miss_callback(-time_to_sleep)

        # Bookkeeping nonlocal variable for the next sleep
        next_time += timer_period
        # The second value of the max prevents a phenomena similar to windup
        # in PID systems, for example when pausing the ai in the future.
        if next_time < current_time:
            next_time = current_time

    return fps_wait
