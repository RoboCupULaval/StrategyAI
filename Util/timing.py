import time

def get_fps_timer(desired_fps: float):
    ''' Returns a timing function that sleeps to allow constant time between iterations.
    The precision of the time between iterations is up to the host operating system.
    ON AVERAGE, it should be around the desired_fps value.

    '''
    if desired_fps > 0:
        timer_period = 1/desired_fps
    else:
        raise ValueError('the desired_fps must be a strictly positive value.')

    next_time = None  # None initialization so a pause causes no borking

    def fps_wait():
        current_time = time.time()
        nonlocal next_time
        if next_time is None:
            next_time = current_time + timer_period

        time_to_sleep = next_time - current_time

        if time_to_sleep > 0:
            time.sleep(time_to_sleep)

        # Bookkeeping nonlocal variable for the next sleep
        next_time += timer_period
        # The second value of the max prevents a phenomena similar to windup
        # in PID systems, for example when pausing the ai in the future.
        if next_time < current_time:
            next_time = current_time

    return fps_wait
