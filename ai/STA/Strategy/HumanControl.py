# Under MIT license, see LICENSE.txt

from . Strategy import Strategy


class HumanControl(Strategy):
    def __init__(self, p_gamestatemanager, p_playmanager):
        super().__init__(p_gamestatemanager, p_playmanager, [])
