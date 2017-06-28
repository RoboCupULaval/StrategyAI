
from .geometry import wrap_to_pi


class PID(object):
    def __init__(self, kp: float, ki: float, kd: float, antiwindup_size=0, wrap_err=False):
        """
        Simple PID parallel implementation
        Args:
            kp: proportional gain
            ki: integral gain
            kd: derivative gain
            antiwindup_size: max error accumulation of the error integration
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd

        self.err_sum = 0
        self.last_err = 0

        self.antiwindup_size = antiwindup_size
        if self.antiwindup_size > 0:
            self.antiwindup_active = True
            self.old_err = [0 for _ in range(self.antiwindup_size)]
            self.antiwindup_idx = 0
        else:
            self.antiwindup_active = False

        self.wrap_err = wrap_err

    def update(self, err: float) -> float:
        d_err = err - self.last_err
        self.last_err = err
        self.err_sum += err

        if self.wrap_err:
            d_err = wrap_to_pi(d_err)
            self.last_err = wrap_to_pi(self.last_err)
            self.err_sum = wrap_to_pi(err)

        if self.antiwindup_active:
            self.err_sum -= self.old_err[self.antiwindup_idx]
            self.old_err[self.antiwindup_idx] = err
            self.antiwindup_idx = (self.antiwindup_idx + 1) % self.antiwindup_size

        return (err * self.kp) + (self.err_sum * self.ki) + (d_err * self.kd)

    def reset(self):
        if self.antiwindup_active:
            self.old_err = [0 for _ in range(self.antiwindup_size)]
        self.err_sum = 0
