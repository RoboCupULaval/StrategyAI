#Under MIT License, see LICENSE.txt
from AI.STP.Skill.SkillBase import SkillBase
from RULEngine.Util.Pose import Pose, Position
from RULEngine.Util.geometry import *
import math as m

LEN_VECTOR = 850
DST_SAFE = 650
AGL_FRONT = 0.90

__author__ = 'RoboCupULaval'


class sPath(SkillBase):
    def __init__(self):
        SkillBase.__init__(self, self.__class__.__name__)

    def act(self, pose_player, pst_target, pst_goal):
        botPose = Pose(Position(pose_player.position.x, pose_player.position.y), pose_player.orientation)
        return self._genRelativePose(Pose(pst_target, botPose.orientation), botPose)

    def _genRelativePose(self, pose_ref, pose_obj):
        agl = m.radians((get_angle(pose_obj.position, pose_ref.position) - pose_ref.orientation + 180)%360)
        dst = get_distance(pose_ref.position, pose_obj.position)
        nPstX = dst * m.cos(agl)
        nPstY = dst * m.sin(agl)
        #print(agl)
        print("DEBUG",m.degrees(agl))
        if nPstX > -DST_SAFE and not m.pi*AGL_FRONT < agl < 2*m.pi - m.pi*AGL_FRONT:
            if not -DST_SAFE < nPstY < DST_SAFE:
                return self.__moveRelativeBack(pose_obj)
            else:
                if nPstY > 0:
                    return self.__moveRelativeLeft(pose_obj)
                else:
                    return self.__moveRelativeRight(pose_obj)
        elif m.pi*AGL_FRONT < agl < 2*m.pi - m.pi*AGL_FRONT or -75 < nPstY < 75:
             return self.__moveRelativeFront(pose_obj)
        else:
            if nPstY > 0:
                return self.__moveRelativeRight(pose_obj)
            else:
                return self.__moveRelativeLeft(pose_obj)


    @staticmethod
    def __moveRelativeFront(pose, lenght=LEN_VECTOR):
        #print('Front')
        angle = m.radians(pose.orientation)
        pst_x = lenght * m.cos(angle) + pose.position.x
        pst_y = lenght * m.sin(angle) + pose.position.y
        return Pose(Position(pst_x, pst_y), angle)

    @staticmethod
    def __moveRelativeBack(pose, lenght=LEN_VECTOR):
        #print('Back')
        angle = m.radians(pose.orientation)
        pst_x = lenght * m.cos(angle + m.pi) + pose.position.x
        pst_y = lenght * m.sin(angle + m.pi) + pose.position.y
        return Pose(Position(pst_x, pst_y), angle)

    @staticmethod
    def __moveRelativeLeft(pose, lenght=LEN_VECTOR):
        #print('Left')
        angle = m.radians(pose.orientation)
        pst_x = lenght * m.cos(angle + m.pi/2.0) + pose.position.x
        pst_y = lenght * m.sin(angle + m.pi/2.0) + pose.position.y
        return Pose(Position(pst_x, pst_y), angle)

    @staticmethod
    def __moveRelativeRight(pose, lenght=LEN_VECTOR):
        #print('Right')
        angle = m.radians(pose.orientation)
        pst_x = lenght * m.cos(angle - m.pi/2.0) + pose.position.x
        pst_y = lenght * m.sin(angle - m.pi/2.0) + pose.position.y
        return Pose(Position(pst_x, pst_y), angle)

#if __name__ == '__main__':
#    sPath().act(Pose(Position(-255, -50), 0), Position(0, 0), Position(0, 0))