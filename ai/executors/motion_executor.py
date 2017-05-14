# Under MIT License, see LICENSE.txt


from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from ai.Util.ai_command import AICommandType, AIControlLoopType, AICommand
from ai.executors.executor import Executor
from ai.states.world_state import WorldState

from enum import IntEnum
import numpy as np

from config.config_service import ConfigService


class Pos(IntEnum):
    X = 0
    Y = 1
    THETA = 2


class DotDict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class MotionExecutor(Executor):
    def __init__(self, p_world_state: WorldState):
        super().__init__(p_world_state)
        self.is_simulation = ConfigService().config_dict["GAME"]["type"] == "sim"
        self.robot_motion = [RobotMotion(p_world_state, player_id, is_sim=self.is_simulation) for player_id in range(12)]

    def exec(self):
        commands = self.ws.play_state.current_ai_commands
        delta_t = self.ws.game_state.game.delta_t

        for cmd in commands.values():
            robot_idx = cmd.robot_id
            active_player = self.ws.game_state.game.friends.players[robot_idx]
            if cmd.command is AICommandType.MOVE:
                if cmd.control_loop_type is AIControlLoopType.POSITION:
                    cmd.speed = self.robot_motion[robot_idx].update(cmd)
                elif cmd.control_loop_type is AIControlLoopType.SPEED:
                    speed = robot2fixed(cmd.pose_goal.conv_2_np(), active_player.pose.orientation)
                    cmd.speed = Pose(Position(speed[0], speed[1]), speed[2])
                elif cmd.control_loop_type is AIControlLoopType.OPEN:
                    cmd.speed = cmd.pose_goal
            elif cmd.command is AICommandType.STOP:
                cmd.speed = Pose(Position(0,0),0)
                self.robot_motion[robot_idx].stop()


class RobotMotion(object):
    def __init__(self,  p_world_state: WorldState, player_id, is_sim=True):

        self.ws = p_world_state

        self.setting = get_control_setting(is_sim)
        self.id = player_id
        self.player = None
        self.setting.translation.max_acc =None

        self.current_position = np.zeros(3)
        self.current_velocity = np.zeros(3)

        self.target_position = np.zeros(3)
        self.target_velocity = np.zeros(3)

        self.x_controller = PID(self.setting.translation.kp,
                                self.setting.translation.ki,
                                self.setting.translation.kd,
                                self.setting.translation.antiwindup)

        self.y_controller = PID(self.setting.translation.kp,
                                self.setting.translation.ki,
                                self.setting.translation.kd,
                                self.setting.translation.antiwindup)

        self.angle_controller = PID(self.setting.rotation.kp,
                                    self.setting.rotation.ki,
                                    self.setting.rotation.kd,
                                    self.setting.rotation.antiwindup)

        self.last_translation_cmd = np.zeros(2)
        self.commanded_speed = 0

    def update(self, cmd : AICommand) -> Pose():
        self.player = self.ws.game_state.get_player(self.id)
        self.setting.translation.max_acc = self.player.max_acc
        self.update_state(cmd)
        self.commanded_speed = cmd.robot_speed

        pos_error = self.target_position - self.current_position   # TODO: limit the pos_error to the next position (actual_pos+speed*dt)

        # Rotation control

        rotation_cmd = self.angle_controller.update(pos_error[2])

        # Limit the angular speed
        if np.abs(rotation_cmd) > self.setting.rotation.max_speed:
            if rotation_cmd > 0:
                rotation_cmd = self.setting.rotation.max_speed
            else:
                rotation_cmd = -self.setting.rotation.max_speed

        # Translation control

        translation_cmd = self.get_next_speed()
        #print(translation_cmd)
        #print(np.array([self.x_controller.update(pos_error[0]), self.y_controller.update(pos_error[1])]))
        translation_cmd += np.array([self.x_controller.update(pos_error[0]), self.y_controller.update(pos_error[1])])

        translation_cmd = self.limit_acceleration(translation_cmd)

        translation_cmd = robot2fixed(translation_cmd, self.current_position[2])

        return Pose(Position(translation_cmd[0]/1000, translation_cmd[1]/1000), rotation_cmd)

    def get_next_speed(self):

        next_speed = np.array([0.0, 0.0])

        delta_pos_tot = robot2fixed(self.target_position - self.current_position, -self.current_position[2])
        delta_pos_tot = abs(delta_pos_tot[0: 2])
        accel = self.setting.translation.max_acc * 1000 * delta_pos_tot / np.linalg.norm(delta_pos_tot)
        commanded_speed = self.commanded_speed * delta_pos_tot / np.linalg.norm(delta_pos_tot)
        target_velocity = self.target_velocity[0:2] * 1000
        current_velocity = self.current_velocity[0:2] * np.array([1000])
        if np.linalg.norm(commanded_speed) < 0.0001:
            return next_speed
        # explications dans le block comment juste en dessous

        '''                                                                     
        Plusieurs ca sont possibles:                                            
        v(t) |                                                                  
             |<----------------------->     Distance totale de parcours         
        v_cmd|     _______________                                              
             |    /               \ 
             |   /                 \ 
             |  /                   \ 
         ____|_/_____________________\____________
             |
               <-->               <-->
                 ⇑                  ⇑
                  \_________         \______________
                           \                        \ 
                            \                        \ 
        distance acceleration    distance deceleration


        En gros, on verifie si on a assez de place pour etre capable d'accelerer et de décélérer en essayant d'arriver
        a la vitesse demandée. Si on est pas capable, on est en présence d'un profil triangulaire.

        v(t) |
             | <------>     Distance totale de parcours
        v_cmd|
             |     
             |    /\ 
             |   /  \ 
             |  /    \ 
         ____|_/______\__________
             |
               <--><-->
                 ⇑    |____________________________
                  \________                        \ 
                           \                        \ 
                            \                        \ 
        distance acceleration    distance deceleration

        on prend la formule v_f² = vi² + 2a*delta_pos
        on calcul le delta_pos pour accelerer a vf = v_cmd (proveneant du path finder) à partir de vi = current_vel
        on calcul la meme chose pour la decelaration avec vf = v_terminale (provenant du pathfinder) et vi = c_cmd
        On verifie que l'addition de ces deux delta_pos sont plus petits que la distance entre les points de départ et 
        le point d'arrivée.
        Si ce n'est pas le cas, on est dans un profil triangulaire.
        On calcul la vitesse maximale atteinte:
        v_pointe = sqrt(acc*delta_pos_total - current_vel²/2 + v_terminale²/2)

        '''

        # delta_position_phase_acceleration
        delta_pos_decel = (current_velocity ** 2 - target_velocity ** 2) / (2 * abs(accel))
        comparateur = delta_pos_decel < delta_pos_tot

        #GESTION DE LA VITESSE EN X----------------------------------------

        if (current_velocity[0] - commanded_speed[0]) * sign(current_velocity[0] - commanded_speed[0]) > 0: # acceleration en x terminée
            if delta_pos_decel[0] - delta_pos_tot[0] < 0.01: # on doit rallentir
                next_speed[0] = current_velocity[0] - accel[0]*self.dt
            else: #on continue a vitesse constante
                next_speed[0] = current_velocity[0]
        else: # on doit continuer a accelerer
            next_speed[0] = current_velocity[0] + accel[0]*self.dt

        #GESTION DE LA VITESSE EN Y-----------------------------------------

        if (current_velocity[1] - commanded_speed[1]) * sign(current_velocity[1] - commanded_speed[1]) > 0: # acceleration en y terminée
            if delta_pos_decel[1] - delta_pos_tot[1] < 0.01: # on doit rallentir
                next_speed[1] = current_velocity[1] - accel[1]*self.dt
            else: #on continue a vitesse constante
                next_speed[1] = current_velocity[1]
        else: # on doit continuer a accelerer
            next_speed[1] = current_velocity[1] + accel[1]*self.dt
        # else:#on doit verifier quelle composante (x ou y) est limitée et sera en profil triangulaire.
        #     #print(accel * delta_pos_tot - self.current_velocity[0:2] ** 2, self.commanded_speed)
        #     vit_pointe = np.sqrt(accel * delta_pos_tot - self.current_velocity[0:2] ** 2 / 2 + self.commanded_speed ** 2 / 2)
        #     delta_pos_acc_temp = (vit_pointe ** 2 - self.current_velocity[0:2] ** 2) / (2 * accel)
        #     delta_pos_decel_temp = (vit_pointe ** 2 - self.target_velocity[0:2] ** 2) / (2 * accel)
        #     #print(vit_pointe, delta_pos_acc_temp, delta_pos_decel_temp)
        #     if not(comparateur[0] and comparateur[1]): # profil triangulaire en x et y
        #         delta_pos_acc = delta_pos_acc_temp
        #         delta_pos_decel = delta_pos_decel_temp
        #     elif not(comparateur[0]): # profil triangulaire en x et trapezoidal en y
        #         delta_pos_acc[0] = delta_pos_acc_temp[0]
        #         delta_pos_decel[0] = delta_pos_decel_temp[0]
        #     elif not(comparateur[1]): # profil trapezoidal en x et triangulaire en y
        #         delta_pos_acc[1] = delta_pos_acc_temp[1]
        #         delta_pos_decel[1] = delta_pos_decel_temp[1]
        #
        #     # GESTION DE LA VITESSE EN X----------------------------------------
        #
        #     if delta_pos_acc[0] < 0.001:  # acceleration en x terminée
        #         if delta_pos_decel[0] - delta_pos_tot[0] < 0.01:  # on doit rallentir
        #             next_speed[0] = self.current_velocity[0] - accel[0] * self.dt
        #         else:  # on continue a vitesse constante
        #             next_speed[0] = self.current_velocity[0]
        #     else:  # on doit continuer a accelerer
        #         next_speed[0] = self.current_velocity[0] + accel[0] * self.dt
        #
        #     # GESTION DE LA VITESSE EN Y-----------------------------------------
        #
        #     if delta_pos_acc[1] < 0.001:  # acceleration en y terminée
        #         if delta_pos_decel[1] - delta_pos_tot[1] < 0.01:  # on doit rallentir
        #             next_speed[1] = self.current_velocity[1] - accel[1] * self.dt
        #         else:  # on continue a vitesse constante
        #             next_speed[1] = self.current_velocity[1]
        #     else:  # on doit continuer a accelerer
        #         next_speed[1] = self.current_velocity[1] + accel[1] * self.dt
        print(current_velocity)
        next_speed = robot2fixed(next_speed, self.current_position[2])
        print(next_speed)

        return next_speed #mm/s juste en translaton

    def limit_acceleration(self, translation_cmd):
        current_acc = (translation_cmd - self.last_translation_cmd) / self.dt
        np.clip(current_acc, -self.setting.translation.max_acc, self.setting.translation.max_acc, out=current_acc)
        translation_cmd = self.last_translation_cmd + current_acc * self.dt
        self.last_translation_cmd = translation_cmd

        return translation_cmd

    def update_state(self, cmd):
        self.dt = self.ws.game_state.game.delta_t
        self.current_position = self.ws.game_state.game.friends.players[self.id].pose.conv_2_np()
        self.current_velocity = np.array(self.ws.game_state.game.friends.players[self.id].velocity)
        self.target_position = cmd.pose_goal.conv_2_np()
        path_speeds = cmd.path_speeds #une liste de scalaires représentant la norme max de la vitesse que doit avoir le robot
        print(path_speeds)
        self.target_velocity = path_speeds[1] * (self.target_position[0:2] - self.current_position[0:2])\
                               / np.linalg.norm(self.target_position[0:2] - self.current_position[0:2])

    def stop(self):
        self.last_translation_cmd = np.zeros(2)
        self.angle_controller.reset()
        self.x_controller.reset()
        self.y_controller.reset()


class PID(object):
    def __init__(self, kp: float, ki: float, kd: float, antiwindup_size=0):
        """
        Simple PID parallel implementation
        Args:
            kp: proportional gain
            ki: integral gain
            kd: derivative gain
            antiwindup_size: max error accumulation of the error integration
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd

        self.err_sum = 0
        self.last_err = 0

        self.antiwindup_size = antiwindup_size
        if self.antiwindup_size > 0:
            self.antiwindup_active = True
            self.old_err = np.zeros(self.antiwindup_size)
            self.antiwindup_idx = 0
        else:
            self.antiwindup_active = False

    def update(self, err: float) -> float:
        d_err = err - self.last_err
        self.last_err = err
        self.err_sum += err

        if self.antiwindup_active:
            self.err_sum -= self.old_err[self.antiwindup_idx]
            self.old_err[self.antiwindup_idx] = err
            self.antiwindup_idx = (self.antiwindup_idx + 1) % self.antiwindup_size

        return (err * self.kp) + (self.err_sum * self.ki) + (d_err * self.kd)

    def reset(self):
        if self.antiwindup_active:
            self.old_err = np.zeros(self.antiwindup_size)
        self.err_sum = 0


def get_control_setting(is_sim):
    if is_sim:
        translation = {"kp": 0.7, "ki": 0.005, "kd": 0.02, "antiwindup": 0,
                       "max_speed": 50, "max_acc": 100, "deadzone": 0.03}
        rotation = {"kp": 0.6, "ki": 0.2, "kd": 0.3, "antiwindup": 0,
                    "max_speed": 6, "max_acc": 4, "deadzone": 0}
    else:
        translation = {"kp": 0.000001, "ki": 0.000005, "kd": 0, "antiwindup": 0,
                       "max_speed": 2000, "max_acc": 1500, "deadzone": 30}
        rotation = {"kp": 1, "ki": 0.05, "kd": 0, "antiwindup": 0,
                    "max_speed": 6, "max_acc": 4, "deadzone": 0}
    control_setting = DotDict()
    control_setting.translation = DotDict(translation)
    control_setting.rotation = DotDict(rotation)
    return control_setting


def robot2fixed(vector: np.ndarray, angle: float) -> np.ndarray:
    tform = np.array(
        [[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    vector_temp = np.transpose(np.dot(tform, np.transpose(vector[0:2])))
    return vector_temp

if __name__ == "__main__":
    pass


def sign(x):
    if x > 0:
        return 1
    if x == 0:
        return 0
    return -1
