# Under MIT licence, see LICENCE.txt

from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags, DEFAULT_TIME_TO_LIVE
from ai.STA.Action.MoveTo import MoveTo
from ai.STA.Action.Idle import Idle
from ai.states.ModuleState import NonExistentModule
from ai.Util.geometry import get_distance, get_angle
from RULEngine.Util.Pose import Pose
from RULEngine.Util.constant import ANGLE_TO_HALT, POSITION_DEADZONE, PLAYER_PER_TEAM

from ai.states.ModuleState import ModuleState

__author__ = 'RoboCupULaval'


class GoToPosition(Tactic):
    # TODO : Renommer la classe pour illustrer le fait qu'elle set une Pose et non juste une Position
    """
    méthodes:
        exec(self) : Exécute une Action selon l'état courant
    attributs:
        info_manager: référence à la façade InfoManager
        player_id : Identifiant du joueur auquel est assigné la tactique
        current_state : L'état courant de la tactique
        next_state : L'état suivant de la tactique
        status_flag : L'indicateur de progression de la tactique
        destination_pose : La pose de destination du robot
    """

    def __init__(self, info_manager, player_id, target, time_to_live=DEFAULT_TIME_TO_LIVE):
        Tactic.__init__(self, info_manager, target, time_to_live=time_to_live)
        assert isinstance(player_id, int)
        assert PLAYER_PER_TEAM >= player_id >= 0
        assert isinstance(target, Pose), "La target devrait être une Pose"

        self.player_id = player_id
        self.target = target
        self.path_target = None
        self.module_state = ModuleState()
        self.path = []

        self._init_pathfinder()
        self.current_state = self.get_next_path_element
        self.next_state = self.get_next_path_element

    def _init_pathfinder(self):
        try:
            pathfinder = self.module_state.acquire_pathfinder()
            self.path = pathfinder.get_path(self.player_id, self.target)
            pathfinder.draw_path(self.path, self.player_id)
        except NonExistentModule as err:
            print(err)
            self.game_state.paths[self.player_id] = [self.target]

    def get_next_path_element(self):
        assert(isinstance(self.path, list)), "Le chemin doit être une liste"

        if len(self.path) > 0:
            self.path_target = self.path.pop(0) # on récupère le premier path element
            self.next_state = self.move_to_position
        else:
            self.status_flag = Flags.SUCCESS
            self.next_state = self.halt

        return Idle(self.game_state, self.player_id)

    def move_to_position(self):
        assert(isinstance(self.target, Pose)), "La target devrait être une Pose"
        player_position = self.game_state.get_player_pose(self.player_id).position
        player_orientation = self.game_state.get_player_pose(self.player_id).orientation

        if get_distance(player_position, self.path_target.position) <= POSITION_DEADZONE:
                self.next_state = self.get_next_path_element
        else:
            self.status_flag = Flags.WIP
            self.next_state = self.move_to_position
        return MoveTo(self.game_state, self.player_id, self.path_target)

    def halt(self):
        stop = Idle(self.game_state, self.player_id)
        return stop
