from UltimateStrat.STP.Play.PlayBase import PlayBase

__author__ = 'RoboCupULaval'


class pQueueLeuLeu(PlayBase):
    """
    pQueueLeuLeu is a simple play where first follow ball and others follow previous friend id
    """
    def __init__(self):
        PlayBase.__init__(self, self.__class__.__name__)

    def getTactics(self, index=None):
        sequence = [['tFollowBall', 'tFollowPrevFriend', 'tFollowPrevFriend',
                          'tFollowPrevFriend', 'tFollowPrevFriend', 'tFollowPrevFriend']]
        if index is None:
            return sequence[0]
        else:
            return sequence[index]
