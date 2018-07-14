from math import copysign

from Util.geometry import wrap_to_pi
import numpy as np

from time import time
from collections import deque


class PID:
    def __init__(self, kp: float, ki: float, kd: float, *,
                 deadzone: float=0.0,
                 signed_error: bool=False,
                 anti_windup: bool=True, anti_windup_max_time: float=0.5):

        self.kp = kp
        self.ki = ki
        self.kd = kd

        self.err_sum = 0
        self.last_err = 0
        self.last_time = 0

        self.deadzone = deadzone
        self.signed_error = signed_error
        self.anti_windup = anti_windup

        self.error_deque = deque()
        self.anti_windup_time = 0
        self.anti_windup_max_time = anti_windup_max_time

    def execute(self, err: float) -> float:

        current_time = time()

        if not self.last_time:
            self.last_time = current_time
            return err * self.kp

        dt, self.last_time = current_time - self.last_time, current_time

        if self.signed_error and (abs(err) > np.pi):
            d_err = err - self.last_err
            d_err = copysign(d_err, wrap_to_pi(d_err))
        else:
            d_err = err - self.last_err

        self.last_err = err
        self.err_sum += err

        if self.anti_windup:
            self.error_deque.append((err, dt))
            self.anti_windup_time += dt
            while self.anti_windup_time > self.anti_windup_max_time:
                old_err, old_dt = self.error_deque.popleft()
                self.anti_windup_time -= old_dt
                self.err_sum -= old_err

        kd = 0 if abs(err) < self.deadzone else self.kd
        return (err * self.kp) + (self.err_sum * self.ki * dt) + (d_err * kd / dt)

    def reset(self):
        self.last_time = 0
        self.err_sum = 0
        self.last_err = 0
        self.anti_windup_time = 0
