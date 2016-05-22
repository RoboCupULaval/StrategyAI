#Under MIT License, see LICENSE.txt
from UltimateStrat.Executor.Executor import Executor


__author__ = 'RoboCupULaval'


class CoachExecutor(Executor):
    """
    CoachExecutor is a sequence of requests that select Play for game :
    1 - what's new state ?
    2 - what's current play
    3 - what's play with new state ?
    4 - compare current play ans generate play
    5 - set play and init sequence if play is not same
    """
    def __init__(self, info_manager):
        Executor.__init__(self, info_manager)

    def exec(self):
        # 1 - what's current state ?
        state = self.info_manager.getNextState()

        # 2 - what's current play
        current_play = self.info_manager.getCurrentPlay()

        # 3 - what's play with state ?
        play = self.info_manager.getNextPlay(state)

        # 4 - compare current play and generate play
        if not current_play == play:
            # 5 - set play and init sequence if play is not same
            self.info_manager.setPlay(play)
            self.info_manager.initPlaySequence()

