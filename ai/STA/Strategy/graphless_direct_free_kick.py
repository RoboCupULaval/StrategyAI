# Under MIT License, see LICENSE.txt

from ai.STA.Strategy.graphless_freekick import GraphlessFreeKick


class GraphlessDirectFreeKick(GraphlessFreeKick):
    def __init__(self, p_game_state):
        super().__init__(p_game_state, can_kick_in_goal=True)

