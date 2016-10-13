# Under MIT licence, see LICENCE.txt

from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic import tactic_constants
from ai.STA.Action.MoveTo import MoveTo
from ai.STA.Action.Idle import Idle
from ai.states.ModuleState import NonExistentModule
from RULEngine.Util.geometry import get_distance, get_angle
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

    def __init__(self, info_manager, player_id, target, time_to_live=tactic_constants.DEFAULT_TIME_TO_LIVE):
        Tactic.__init__(self, info_manager, target, time_to_live=time_to_live)
        assert isinstance(player_id, int)
        assert PLAYER_PER_TEAM >= player_id >= 0
        assert isinstance(target, Pose), "La target devrait être une Pose"

        self.player_id = player_id
        self.target = target
        self.path_target = target
        self.paths = {}
        self.module_state = ModuleState()

        self._init_pathfinder()
        self.current_state = self.move_to_position
        self.next_state = self.move_to_position

    def _init_pathfinder(self):
        try:
            # FIXME
            print(self.module_state)
            pathfinder = self.module_state.acquire_pathfinder()
            print(pathfinder)
            self.paths[self.player_id] = pathfinder.get_path(self.player_id, self.target)
            pathfinder.draw_path(self.paths[self.player_id], self.player_id)
        except NonExistentModule as err:
            print(err)
            self.game_state.paths[self.player_id] = [self.target]

    def get_next_path_element(self):
        path = self.paths[self.player_id]
        assert(isinstance(path, list)), "Le chemin doit être une liste"

        if len(path) > 0:
            self.path_target = path.pop(0) # on récupère le premier path element
            self.next_state = self.move_to_position
        else:
            self.status_flag = tactic_constants.SUCCESS
            self.next_state = self.halt

        return Idle(self.game_state, self.player_id)

    def move_to_position(self):
        assert(isinstance(self.target, Pose)), "La target devrait être une Pose"
        player_position = self.game_state.get_player_pose(self.player_id).position
        player_orientation = self.game_state.get_player_pose(self.player_id).orientation

        if get_distance(player_position, self.target.position) <= POSITION_DEADZONE or \
                get_angle(player_position, self.target.position) <= ANGLE_TO_HALT:
                self.next_state = self.halt
                self.status_flag = tactic_constants.SUCCESS
        else:
            self.status_flag = tactic_constants.WIP
            self.next_state = self.move_to_position
        return MoveTo(self.game_state, self.player_id, self.path_target)
        # return MoveTo(self.game_state, self.player_id, Pose()) # pathfinder desactivé

    def halt(self, reset=False):
        stop = Idle(self.game_state, self.player_id)

        if get_distance(self.game_state.get_player_pose(self.player_id).position, self.target.position) <= POSITION_DEADZONE:
            self.next_state = self.halt
        else:
            self._init_pathfinder()
            self.next_state = self.get_next_path_element

        return stop
