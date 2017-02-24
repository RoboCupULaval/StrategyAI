# Under MIT license, see LICENSE.txt
from .Action import Action
# from ...Util.types import AICommand
from RULEngine.Util.Position import Position
from RULEngine.Util.constant import PLAYER_PER_TEAM
from ai.Util.ai_command import AICommand, AICommandType, RotateAroundCommand


class RotateAround(Action):
    """

    """
    def __init__(self, p_game_state, p_player_id, p_rotate_around_cmd):
        """
            :param p_game_state: L'état courant du jeu.
            :param p_player_id: Identifiant du joueur qui se déplace
            :param p_rotate_around_cmd: RotateAroundCommand
        """
        Action.__init__(self, p_game_state)
        assert(isinstance(p_player_id, int))
        assert PLAYER_PER_TEAM >= p_player_id >= 0
        assert(isinstance(p_rotate_around_cmd, RotateAroundCommand))
        self.player_id = p_player_id
        self.rotate_around_cmd = p_rotate_around_cmd

    def exec(self):
        """
        Exécute le déplacement
        """
        rotate_around_goal = self.rotate_around_cmd
        return AICommand(self.player_id, AICommandType.MOVE,
                         **{"rotate_around_flag": True,
                            "rotate_around_goal": rotate_around_goal})
