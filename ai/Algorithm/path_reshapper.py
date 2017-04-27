from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.geometry import get_distance, conv_position_2_list
from ai.Algorithm.IntelligentModule import Pathfinder
from ai.Algorithm.path_partitionner import Path
from ai.states.world_state import WorldState
import numpy as np


class Path_reshaper:
    def __init__(self, p_world_state: WorldState, path: Path,  vel_cruise, player_id):

        self.p_world_state = p_world_state
        self.path = path
        self.vel_max = vel_cruise
        self.player_id = player_id
        self.player = self.p_world_state.game_state.get_player(player_id)

    def reshape_path(self):


        P1 = self.path.points[0].conv_2_np()
        P2 = self.path.points[1].conv_2_np()
        P3 = self.path.points[2].conv_2_np()
