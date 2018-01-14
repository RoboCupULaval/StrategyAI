
from .geometry import wrap_to_pi


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

        # pre-multiply ki with desired dt and divided kd

        self.kp = kp
        self.ki = ki
        self.kd = kd

        self.err_sum = 0
        self.last_err = 0

        self.wrap_error = wrap_error

    def execute(self, err) -> float:

        if self.wrap_error:
            err = wrap_to_pi(err)
            d_err = wrap_to_pi(err - self.last_err)
            self.last_err = wrap_to_pi(self.last_err)
        else:
            d_err = err - self.last_err
            self.last_err = err

        self.err_sum += err

        return (err * self.kp) + (self.err_sum * self.ki) + (d_err * self.kd)

    def reset(self):
        self.err_sum = 0
        self.last_err = 0
