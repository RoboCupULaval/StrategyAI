from UltimateStrat.Executor.Executor import Executor

__author__ = 'RoboCupULaval'


class PlayExecutor(Executor):
    """
    PlayExecutor is a sequence of request that select tactics for each players
    1 - what's current play ?
    2 - what's current play sequence ?
    3 - get specific play sequence from play book
    4 - set tactics for each players
    """
    def __init__(self, info_manager):
        Executor.__init__(self, info_manager)

    def exec(self):
        # 1 - what's current play
        current_play = self.info_manager.getCurrentPlay()

        # 2 - what's current play sequence ?
        current_seq = self.info_manager.getCurrentPlaySequence()

        # 3 - get specific play sequence from play book
        play = self.play_book[current_play]

        # 4 - set tactics (str) for each players on black board
        for i, tactic in enumerate(play.getTactics(current_seq)):
            self.info_manager.setPlayerTactic(i, tactic)

