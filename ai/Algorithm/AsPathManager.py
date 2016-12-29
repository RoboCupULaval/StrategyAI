#pylint: skip-file

from ai.Algorithm.IntelligentModule import Pathfinder
from ai.Algorithm.Astar.AsPosition import AsPosition
from ai.Algorithm.Astar.AsGraph import AsGraph
import math

class AsPathManager(Pathfinder):

    def __init__(self, p_worldstate):

        super().__init__(p_worldstate)

        self.TopLeftCorner = AsPosition(-4500,3000)
        self.DownRigthCorner = AsPosition(4500,-3000)
        self.RobotRadius = 100 # real radius is 90, 100 help avoid collision and make it easier to find interval
        self.PreciseInterval = 100
        self.ImpreciseInterval = 200
        self.MaxDist = math.sqrt((self.DownRigthCorner.x - self.TopLeftCorner.x)**2 + (self.TopLeftCorner.y - self.DownRigthCorner.y)**2)

        self.preciseGraph = AsGraph(self.TopLeftCorner, self.DownRigthCorner, self.RobotRadius, self.PreciseInterval)
        self.impreciseGraph = AsGraph(self.TopLeftCorner, self.DownRigthCorner, self.RobotRadius, self.ImpreciseInterval)

    def getAllAsPath(self, startPosList, endPosList, obstacleList):

        allAsPathList = []
        nbPath = len(startPosList)

        for i in range(0, nbPath, 1):

            graph = self.impreciseGraph
            endPos = endPosList[i]
            startPos = startPosList[i]
            totalDist = startPos.getDist(endPos)

            if (totalDist < (self.MaxDist / 3)):
                graph = self.preciseGraph

            if (totalDist > self.PreciseInterval * 10):
                ratio = math.fabs((self.PreciseInterval * 10) / totalDist)
                xPos = startPos.x + ((endPos.x - startPos.x) * ratio)
                yPos = startPos.y + ((endPos.y - startPos.y) * ratio)
                endPos = AsPosition(xPos, yPos)

            updatedObstacleList = list(obstacleList)
            for j in range(0, nbPath, 1):
                if (j != i):
                    updatedObstacleList.append(startPosList[j])

            allAsPathList += [graph.aStarPath(startPos, endPos, updatedObstacleList)]


        return allAsPathList
    
    def update(self):
        """
            Prepare le pathfinder pour retourner les paths voulues. ie.
            calcule toutes les paths activés
        :return:
        """
        team = self.ws.game_state.my_team
        commands = self.ws.play_state.current_ai_commands
        nbRobot = len(team.players)

        for i in range(0, nbRobot, 1):
            dest, kick = commands[i]

    def get_path(self, robot_id=None, target=None):
        """
            Si l'ID est précisé, retourne la liste des *Pose* pour le chemin
            de ce robot. Autrement, retourne le dictionnaire.

            :param robot_id: int entre 0 à 11 représentant les robots de
                             l'équipe alliée
            :param target: LEGACY -> a etre supprimer dans versin future.
            :return: { id : [Pose, Pose, ...] } || [Pose, Pose, ...]
        """

    def get_next_point(self, robot_id=None):
        """
            Si l'ID est précisé, retourne le prochain point *Pose* pour le
            chemin de ce robot. Autrement, retourne dictionaire des
            prochains points avec clé l'id des robots.
            :param robot_id: int entre 0 à 11 représentant l'id des robots de
                             l'équipe alliée
            :return: {id : Pose, ... }
        """


