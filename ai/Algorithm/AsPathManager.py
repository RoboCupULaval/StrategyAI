#pylint: skip-file
import time

from ai.Algorithm.IntelligentModule import Pathfinder
from ai.Algorithm.Astar.AsPosition import AsPosition
from ai.Algorithm.Astar.AsObstacle import AsObstacle
from ai.Algorithm.Astar.AsGraph import AsGraph
from RULEngine.Util.Position import Position
import math

class AsPathManager(Pathfinder):

    def __init__(self, p_worldstate, simulation):

        super().__init__(p_worldstate)

        self.TopLeftCorner = AsPosition(-5000, 3500)
        self.DownRigthCorner = AsPosition(5000, -3500)

        if (simulation):
            self.robot_radius = 250 # real radius is 90, 125 help avoid collision and make it easier to find interval
            self.precise_interval = 125
            self.imprecise_interval = 200
        else:
            self.robot_radius = 125
            self.precise_interval = 200
            self.imprecise_interval = 500

        self.MaxDist = math.sqrt((self.DownRigthCorner.x - self.TopLeftCorner.x)**2 + (self.TopLeftCorner.y - self.DownRigthCorner.y)**2)

        self.preciseGraph = AsGraph(self.TopLeftCorner, self.DownRigthCorner, self.robot_radius, self.precise_interval)
        self.impreciseGraph = AsGraph(self.TopLeftCorner, self.DownRigthCorner, self.robot_radius, self.imprecise_interval)
        self.last_update = time.time()

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

            if (totalDist > self.precise_interval * 10):
                ratio = math.fabs((self.precise_interval * 10) / totalDist)
                xPos = startPos.x + ((endPos.x - startPos.x) * ratio)
                yPos = startPos.y + ((endPos.y - startPos.y) * ratio)
                endPos = AsPosition(xPos, yPos)

            updatedObstacleList = list(obstacleList)
            for j in range(0, nbPath, 1):
                if (j != i):
                    updatedObstacleList.append(AsObstacle(startPosList[j]))

            allAsPathList += [graph.aStarPath(startPos, endPos, updatedObstacleList)]


        return allAsPathList

    def getAsPath(self, startPos, endPos, obstacleList):

        graph = self.impreciseGraph
        totalDist = startPos.getDist(endPos)

        if (totalDist < (self.MaxDist / 3)):
            graph = self.preciseGraph

        if (totalDist > self.precise_interval * 10):
            ratio = math.fabs((self.precise_interval * 10) / totalDist)
            xPos = startPos.x + ((endPos.x - startPos.x) * ratio)
            yPos = startPos.y + ((endPos.y - startPos.y) * ratio)
            endPos = AsPosition(xPos, yPos)

        asPath = graph.aStarPath(startPos, endPos, obstacleList)

        return asPath
    
    def update(self):
        """
            Prepare le pathfinder pour retourner les paths voulues. ie.
            calcule toutes les paths activés
        :return:
        """
        now = time.time()
        delta_t = now - self.last_update

        # if delta_t < 0.1:
        #    return None
        self.last_update = now

        game_state = self.ws.game_state
        commands = self.ws.play_state.current_ai_commands
        keyToCalculate = []
        startPosList = []
        endPosList = []
        obstacleList = []

        idList = []

        for key, command in commands.items():
            if (command.pathfinder_on):

                idList.append(command.robot_id)
                keyToCalculate.append(key)
                position = game_state.get_player_position(command.robot_id)
                startPosList.append(AsPosition(position.x, position.y))
                position = command.pose_goal.position
                endPosList.append(AsPosition(position.x, position.y))

        if (len(keyToCalculate) > 0):

            opponentTeam = game_state.other_team.players
            for id in opponentTeam:
                position = game_state.get_player_position(id, False)
                obstacleList.append(AsPosition(position.x, position.y))

            allPath = self.getAllAsPath(startPosList, endPosList, obstacleList)

            for i in range(0, len(keyToCalculate), 1):
                self.paths[idList[i]] = allPath[i]
                position = allPath[i][0]
                commands[keyToCalculate[i]].pose_goal.position.x = position.x
                commands[keyToCalculate[i]].pose_goal.position.y = position.y


    def get_path(self, robot_id=None, target=None):
        """
            Si l'ID est précisé, retourne la liste des *Pose* pour le chemin
            de ce robot. Autrement, retourne le dictionnaire.

            :param robot_id: int entre 0 à 11 représentant les robots de
                             l'équipe alliée
            :param target: LEGACY -> a etre supprimer dans versin future.
            :return: { id : [Pose, Pose, ...] } || [Pose, Pose, ...]
        """

        game_state = self.ws.game_state
        obstacleList = []
        opponentTeam = game_state.other_team.players
        ourTeam = game_state.my_team.players

        for id in opponentTeam:
            player = game_state.get_player(id, False)
            position = player.pose.position
            vector = player.velocity
            obstacle = AsObstacle(AsPosition(position.x, position.y), vector)
            obstacleList.append(obstacle)

        for id in ourTeam:
            if (id != robot_id):
                player = game_state.get_player(id, True)
                position = player.pose.position
                vector = player.velocity
                obstacle = AsObstacle(AsPosition(position.x, position.y), vector)
                obstacleList.append(obstacle)

        currentRobotPos = game_state.get_player_position(robot_id)
        startAsPos = AsPosition(currentRobotPos.x, currentRobotPos.y)
        endAsPos = AsPosition(target.position.x, target.position.y)

        robotAsPath = self.getAsPath(startAsPos, endAsPos, obstacleList)
        robotPosPath = []

        for i in range(0, len(robotAsPath), 1):
            tempAsPos = robotAsPath[i]
            robotPosPath += [Position(tempAsPos.x, tempAsPos.y)]

        return robotPosPath


    def get_next_point(self, robot_id=None):
        """
            Si l'ID est précisé, retourne le prochain point *Pose* pour le
            chemin de ce robot. Autrement, retourne dictionaire des
            prochains points avec clé l'id des robots.
            :param robot_id: int entre 0 à 11 représentant l'id des robots de
                             l'équipe alliée
            :return: {id : Pose, ... }
        """
        asPath = self.paths[robot_id]
        
        return Position(asPath[0].x, asPath[0].y)

