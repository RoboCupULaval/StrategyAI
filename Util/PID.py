
from Util.geometry import wrap_to_pi

from time import time
from collections import deque


class PID(object):
    def __init__(self, kp: float, ki: float, kd: float, *, wrap_error=False):
        """
        Simple PID parallel implementation
        Args:
            kp: proportional gain
            ki: integral gain
            kd: derivative gain
            antiwindup_size: max error accumulation of the error integration
            wrap_err: wrap the error. Use with angle control
        """

        self.kp = kp
        self.ki = ki
        self.kd = kd

        self.err_sum = 0
        self.last_err = 0
        self.last_time = 0

        self.wrap_error = wrap_error

        self.anti_windup = True
        self.error_deque = deque()
        self.anti_windup_time = 0.0
        self.anti_windup_max_time = 0.50
        self.dt = 0

    def execute(self, err) -> float:
        self.dt, self.last_time = time() - self.last_time, time()

        if self.wrap_error:
            err = wrap_to_pi(err)
            d_err = wrap_to_pi(err - self.last_err)
            self.last_err = wrap_to_pi(self.last_err)
        else:
            d_err = err - self.last_err
            self.last_err = err

        self.err_sum += err

        if self.anti_windup:
            self.error_deque.append((err, self.dt))
            self.anti_windup_time += self.dt
            while self.anti_windup_time > self.anti_windup_max_time:
                old_err, old_dt = self.error_deque.popleft()
                self.anti_windup_time -= old_dt
                self.err_sum -= old_err

        return (err * self.kp) + (self.err_sum * self.ki * self.dt) + (d_err * self.kd / self.dt)

    def reset(self):
        self.err_sum = 0.0
        self.last_err = 0.0
        self.anti_windup_time = 0.0
