from time import time, sleep
import math as m
from RULEngine.Util.Pose import Pose, Position
from RULEngine.Util.geometry import *
from Util.geometry import *



class Regulator(object):
    def __init__(self):
        self.last_dtime = None
        self.last_vector = None
        self.acceleration = 100

    def apply(self, vector, debug=False):
        if debug: print('::INFO:: REGULATOR.APPLY\nINPUT: (vector={}, debug={})'.format(vector, debug))
        assert isinstance(vector, Pose)
        pst = vector.position

        if self.last_dtime is None or self.last_vector is None:
            if debug: print('::WARN:: Regulator not initialized !')
            self.initialize(time(), pst)
            return vector
        else:
            # Usefull calculus
            dtime = time() - self.last_dtime
            dst = get_distance(self.last_vector, pst)
            angle = get_angle(self.last_vector, pst)
            dst_theorq = 0.5 * self.acceleration * dtime ** 2
            if debug: print('::INFO:: Calculates\nDTIME: {}\nDST_REEL: {}\nANGLE: {}\nDST_THEO: {}'.format(dtime, dst, angle, dst_theorq))

            # check vector
            if dst > dst_theorq:
                self.last_vector = pst
                self.last_dtime = time()
                if debug: print('::INFO:: OUTPUT: vector={}'.format(vector))
                return vector
            else:
                self.last_vector = Position(self.last_vector.x + dst_theorq * m.cos(angle),
                                            self.last_vector.y + dst_theorq * m.sin(angle))
                self.last_dtime = time()
                nvx_vector = Pose(self.last_vector, vector.orientation)
                if debug: print('::INFO:: OUTPUT: vector={}'.format(nvx_vector))
                return nvx_vector

    def initialize(self, dtime, vector):
        self.last_dtime = dtime
        self.last_vector = vector