# Under MIT license, see LICENSE.txt
from RULEngine.Game.OurPlayer import OurPlayer
from ai.states.game_state import GameState
from ai.STA.Action.Action import Action
from RULEngine.Util.Pose import Pose
from ai.Util.ai_command import AICommand, AICommandType, AIControlLoopType


class AllStar(Action):
    """
    Action Stop: Arrête le robot
    Méthodes :
        exec(self): Retourne la position du joueur qui l'a appelé
    Attributs (en plus de ceux de Action):
        player_id : L'identifiant du joueur
    """
    def __init__(self, game_state: GameState, player: OurPlayer, **other_args):
        """
            :param game_state: L'état courant du jeu.
            :param player: Identifiant du joueur qui s'arrête
        """
        Action.__init__(self, game_state, player)
        self.other_args = {"dribbler_on": other_args.get("dribbler_on", False),
                           "control_loop_type": other_args.get("control_loop_type", AIControlLoopType.POSITION),
                           "pathfinder_on": other_args.get("pathfinder_on", False),
                           "kick_strength": other_args.get("kick_strength", 0),
                           "charge_kick": other_args.get("charge_kick", False),
                           "kick": other_args.get("kick", False),
                           "pose_goal": other_args.get("pose_goal", Pose())
                           }
        self.ai_command_type = other_args.get("ai_command_type", AICommandType.STOP)

        # this is for the pathfinder only no direct assignation
        # TODO put that correctly
        self.path = other_args.get("path", [])

    def exec(self):
        """
        Exécute l'arrêt
        :return: Un tuple (None, kick) où None pour activer une commande de stop et kick est nul (on ne botte pas)
        """
        # un None pour que le coachcommandsender envoi une command vide.
        self.player.ai_command = AICommand(self.player, self.ai_command_type, **self.other_args)
        return AICommand(self.player, self.ai_command_type, **self.other_args)
