#Under MIT License, see LICENSE.txt
from ai.STP.Play.PlayBase import PlayBase

__author__ = 'RoboCupULaval'

SEQUENCE_DEMO_FOLLOW_BALL = ['tFollowBall', 'tFollowBall', 'tFollowBall',
                             'tFollowBall', 'tFollowBall', 'tFollowBall']

class pDemoFollowBall(PlayBase):
    """
    Demonstration mode:
     + Follow ball on the field behaviour of all bots.
    """
    def __init__(self):
        PlayBase.__init__(self, self.__class__.__name__)
        self._sequence = [SEQUENCE_DEMO_FOLLOW_BALL]

    def getTactics(self, index=None):
        if index is None:
            return self._sequence[0]
        else:
            return self._sequence[index]
