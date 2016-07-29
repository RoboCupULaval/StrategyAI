# Under MIT license, see LICENSE.txt

from .Tactic import Tactic
from . import tactic_constants


class Stop(Tactic):
    def __init__(self, p_info_manager):
        super().__init__(p_info_manager)
        self.status_flag = tactic_constants.SUCCESS
