# Under MIT license, see LICENSE.txt

from . Strategy import Strategy

class HumanControl(Strategy):
    def __init__(self, p_info_manager):
        super().__init__(p_info_manager, [])
