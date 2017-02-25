# Under MIT licence, see LICENCE.txt

import math
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags, DEFAULT_TIME_TO_LIVE
from ai.STA.Action.MoveToPosition import MoveToPosition
from ai.STA.Action.Idle import Idle
from ai.states.module_state import NonExistentModule
from RULEngine.Util.geometry import get_distance, get_angle
from RULEngine.Util.Pose import Pose
from RULEngine.Util.constant import ANGLE_TO_HALT, POSITION_DEADZONE, PLAYER_PER_TEAM

from ai.states.module_state import ModuleState

__author__ = 'RoboCupULaval'


class GoToPosition(Tactic):
    # TODO : Renommer la classe pour illustrer le fait qu'elle set une Pose et non juste une Position
    """
    méthodes:
        exec(self) : Exécute une Action selon l'état courant
    attributs:
        game_state: L'état courant du jeu.
        player_id : Identifiant du joueur auquel est assigné la tactique
        current_state : L'état courant de la tactique
        next_state : L'état suivant de la tactique
        status_flag : L'indicateur de progression de la tactique
        destination_pose : La pose de destination du robot
    """

    def __init__(self, game_state, player_id, target,
                 time_to_live=DEFAULT_TIME_TO_LIVE):
        Tactic.__init__(self, game_state, player_id, target,
                        time_to_live=time_to_live)

        self.path_target = None
        self.module_state = ModuleState()
        self.path = []

        self._init_pathfinder()
        self.current_state = self.get_next_path_element
        self.next_state = self.get_next_path_element

    def _init_pathfinder(self):
        try:
            pathfinder = self.module_state.acquire_pathfinder()
            if pathfinder is not None:
                self.path = pathfinder.get_path(self.player_id, self.target)
                pathfinder.draw_path(self.path, self.player_id)
            else:
                self.path = [self.target]
        except NonExistentModule as err:
            print("Impossible de récupérer le pathfinder\n", err)
            self.path = [self.target]

    def get_next_path_element(self):
        assert(isinstance(self.path, list)), "Le chemin doit être une liste"

        if len(self.path) > 0:
            self.path_target = self.path.pop(0)  # on récupère le premier path element
            self.next_state = self.move_to_position
        else:
            self.status_flag = Flags.SUCCESS
            self.next_state = self.halt

        return Idle(self.game_state, self.player_id)

    def move_to_position(self):
        assert(isinstance(self.path_target, Pose)), "La target devrait être une Pose"
        player_position = self.game_state.get_player_pose(self.player_id).position
        player_orientation = self.game_state.get_player_pose(self.player_id).orientation

        if get_distance(player_position, self.path_target.position) <= POSITION_DEADZONE\
                and math.abs(self.path_target.orientation - player_orientation) <= ANGLE_TO_HALT:
            # TODO : remettre cette condition quand l'asservissement en orientation des robots sera fonctionnel
            self.next_state = self.get_next_path_element
        else:
            self.status_flag = Flags.WIP
            self.next_state = self.move_to_position
        return MoveToPosition(self.game_state, self.player_id, self.path_target)

    def halt(self):
        stop = Idle(self.game_state, self.player_id)

        if get_distance(self.game_state.get_player_pose(self.player_id).position, self.target.position) <= POSITION_DEADZONE:
            self.next_state = self.halt
        else:
            self._init_pathfinder()
            self.next_state = self.get_next_path_element

        return stop
