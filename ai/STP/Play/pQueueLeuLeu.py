#Under MIT License, see LICENSE.txt
from ai.STP.Play.PlayBase import PlayBase

__author__ = 'RoboCupULaval'

SEQUENCE_QUEUELEULEU = ['tFollowBall', 'tFollowPrevFriend', 'tFollowPrevFriend',
                        'tFollowPrevFriend', 'tFollowPrevFriend', 'tFollowPrevFriend']

class pQueueLeuLeu(PlayBase):
    """
    pQueueLeuLeu is a simple play where first follow ball and others follow previous friend id
    """
    def __init__(self):
        PlayBase.__init__(self, self.__class__.__name__)
        self._sequence = [SEQUENCE_QUEUELEULEU]

    def getTactics(self, index=None):
        if index is None:
            return self._sequence[0]
        else:
            return self._sequence[index]
