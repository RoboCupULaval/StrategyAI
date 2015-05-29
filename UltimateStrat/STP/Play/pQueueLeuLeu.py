from UltimateStrat.STP.Play.PlayBase import PlayBase

__author__ = 'jbecirovski'


class pQueueLeuLeu(PlayBase):
    """
    pQueueLeuLeu is a simple play where first follow ball and others follow previous friend id
    """
    def __init__(self):
        PlayBase.__init__(self, self.__class__.__name__)
        self.sequence = [['tFollowBall', 'tFollowPrevFriend', 'tFollowPrevFriend',
                          'tFollowPrevFriend', 'tFollowPrevFriend', 'tFollowPrevFriend']]

    def getTactics(self, index=None):
        if index is None:
            return self.sequence
        else:
            return self.sequence[index]
