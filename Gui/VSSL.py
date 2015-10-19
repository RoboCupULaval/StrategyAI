import sys, math
from PyQt4 import QtGui, QtCore

class MainLoop(QtCore.QThread):
    updateField = QtCore.pyqtSignal()

    def __init__(self, target):
        super(MainLoop, self).__init__()
        self.target = target

    def run(self):
        run_loop = self.target
        emit_signal = self.updateField.emit
        while True:  # TODO: Replace with a loop that will stop when the game is over
            run_loop()
            emit_signal()

class FieldDisplay(QtGui.QWidget):
    #TODO: Make the gui be based on the current window size.

    def __init__(self, game_thread, game, vision, command_sender):
        super(FieldDisplay, self).__init__()

        self._thread = MainLoop(game_thread)
        self._thread.updateField.connect(self.refresh)

        self.game = game
        self.vision = vision
        self.command_sender = command_sender

        self.ratio = 1.0
        self.fieldOffsetX = 700
        self.fieldOffsetY = 700

        self.fieldWidth = 9000;
        self.fieldHeight = 6000;

        self._thread.start()

        self.initUI()

    def setRatio(self, ratio):
        self.ratio = ratio

        self.ratioWidth = self.fieldWidth / self.ratio
        self.ratioHeight = self.fieldHeight / self.ratio

        self.ratioFieldOffsetX = self.fieldOffsetX / self.ratio
        self.ratioFieldOffsetY = self.fieldOffsetY / self.ratio

    def atRatio(self, value):
        return value / self.ratio

    def initUI(self):
        self.setGeometry(200, 200, 1011, 720)

        self.setRatio((6000 + self.fieldOffsetY * 2) / 720)

        self.ratioHeight = self.fieldHeight / self.ratio
        self.setWindowTitle('SSL Visualizer')

        self.redPen = QtGui.QPen(QtGui.QColor(255, 0, 0), 3, QtCore.Qt.SolidLine)
        self.whitePen = QtGui.QPen(QtGui.QColor(255, 255, 255), 3, QtCore.Qt.SolidLine)
        self.blackPen = QtGui.QPen(QtGui.QColor(0, 0, 0), 3, QtCore.Qt.SolidLine)
        self.grayPenFat = QtGui.QPen(QtGui.QColor(50, 50, 50, 200), 10, QtCore.Qt.SolidLine)
        self.grayPenFat.setCapStyle(QtCore.Qt.RoundCap)
        self.transPen = QtGui.QPen(QtGui.QColor(0, 0, 0, 0), 3, QtCore.Qt.SolidLine)

        self.show()


    def closeEvent(self, e):
        global playAll
        playAll = False

    def resizeEvent(self, e):
        print ("Current new size: {}, {}".format(e.size().width(), e.size().height()))
        ratioX = ((self.fieldWidth + self.fieldOffsetX * 2) / (e.size().width()))
        ratioY = ((self.fieldHeight + self.fieldOffsetY * 2) / (e.size().height()))
        print ("RatioX: {}".format(ratioX))
        print ("RatioY: {}".format(ratioY))

        self.setRatio(max(ratioX, ratioY))

        pass

    def moveBall(self, x, y, vx, vy):
        packet = self.command_sender.get_new_packet()

        packet.replacement.ball.x = x
        packet.replacement.ball.y = y
        packet.replacement.ball.vx = vx
        packet.replacement.ball.vy = vy

        print ("Moving ball! {}, {}".format(packet.replacement.ball.x, packet.replacement.ball.y))
        self.command_sender.send_packet(packet)

    def mousePressEvent(self, e):
        self.moveBall(e.x() * self.ratio / 1000 - 10400 / 1000 / 2, -e.y() * self.ratio / 1000 + 7400 / 1000 / 2, 0, 0)

    def mouseMoveEvent(self, e):
        self.moveBall(e.x() * self.ratio / 1000 - 10400 / 1000 / 2, -e.y() * self.ratio / 1000 + 7400 / 1000 / 2, 0, 0)

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)

        self.drawField(qp)
        qp.end()

    def drawField(self, qp):
        qp.setPen(self.blackPen)

        qp.setFont(QtGui.QFont('SansSerif', 20))

        color = QtGui.QColor(0, 0, 0)
        color.setNamedColor('#d4d4d4')

        qp.setBrush(QtGui.QColor(0, 155, 0, 150))
        qp.drawRect(0, 0, self.ratioWidth + self.fieldOffsetX * 2 / self.ratio, self.ratioHeight + self.fieldOffsetY * 2 / self.ratio)
        qp.setBrush(QtGui.QColor(0, 155, 0, 200))
        qp.setPen(self.transPen)
        qp.drawRect(self.ratioFieldOffsetX - self.atRatio(250), self.ratioFieldOffsetY - self.atRatio(250), self.ratioWidth + self.atRatio(500), self.ratioHeight + self.atRatio(500))
        qp.setPen(self.whitePen)
        qp.drawRect(self.ratioFieldOffsetX, self.ratioFieldOffsetY, self.ratioWidth, self.ratioHeight)

        qp.setPen(self.whitePen)
        qp.drawLine(self.ratioFieldOffsetX + self.ratioWidth / 2, self.ratioFieldOffsetY, self.ratioFieldOffsetX + self.ratioWidth / 2, self.ratioFieldOffsetY + self.ratioHeight)
        qp.drawLine(self.ratioFieldOffsetX, self.ratioFieldOffsetY + self.ratioHeight / 2, self.ratioFieldOffsetX + self.ratioWidth, self.ratioFieldOffsetY + self.ratioHeight / 2)
        qp.setBrush(QtGui.QColor(255, 255, 255, 0))
        circleSize = 500 / self.ratio
        qp.drawEllipse(self.ratioFieldOffsetX + self.ratioWidth / 2 - circleSize, self.ratioFieldOffsetY + self.ratioHeight / 2 - circleSize, circleSize * 2, circleSize * 2)

        qp.drawArc(self.ratioFieldOffsetX - circleSize * 2, self.ratioFieldOffsetY + self.ratioHeight / 2 - circleSize * 2 - self.atRatio(250), circleSize * 4, circleSize * 4, 0, 90 * 16)
        qp.drawArc(self.ratioFieldOffsetX - circleSize * 2, self.ratioFieldOffsetY + self.ratioHeight / 2 - circleSize * 2 + self.atRatio(250), circleSize * 4, circleSize * 4, 0, -90 * 16)

        qp.drawArc(self.ratioFieldOffsetX + self.ratioWidth - circleSize * 2, self.ratioFieldOffsetY + self.ratioHeight / 2 - circleSize * 2 - self.atRatio(250), circleSize * 4, circleSize * 4, 180 * 16, -90 * 16)
        qp.drawArc(self.ratioFieldOffsetX + self.ratioWidth - circleSize * 2, self.ratioFieldOffsetY + self.ratioHeight / 2 - circleSize * 2 + self.atRatio(250), circleSize * 4, circleSize * 4, 180 * 16, 90 * 16)

        qp.drawLine(self.ratioFieldOffsetX + circleSize * 2, self.ratioFieldOffsetY + self.ratioHeight / 2 - self.atRatio(250), self.ratioFieldOffsetX + circleSize * 2, self.ratioFieldOffsetY + self.ratioHeight / 2 + self.atRatio(250))
        qp.drawLine(self.ratioFieldOffsetX + self.ratioWidth - circleSize * 2, self.ratioFieldOffsetY + self.ratioHeight / 2 - self.atRatio(250), self.ratioFieldOffsetX + self.ratioWidth - circleSize * 2, self.ratioFieldOffsetY + self.ratioHeight / 2 + self.atRatio(250))

        goalSize = 1000
        qp.setPen(self.redPen)
        qp.drawLine(self.ratioFieldOffsetX - self.atRatio(180), self.ratioFieldOffsetY - self.atRatio(goalSize / 2) + self.ratioHeight / 2, self.ratioFieldOffsetX - self.atRatio(180), self.ratioFieldOffsetY + self.atRatio(goalSize / 2) + self.ratioHeight / 2)
        qp.drawLine(self.ratioFieldOffsetX - self.atRatio(180), self.ratioFieldOffsetY - self.atRatio(goalSize / 2) + self.ratioHeight / 2, self.ratioFieldOffsetX, self.ratioFieldOffsetY - self.atRatio(goalSize / 2) + self.ratioHeight / 2)
        qp.drawLine(self.ratioFieldOffsetX - self.atRatio(180), self.ratioFieldOffsetY + self.atRatio(goalSize / 2) + self.ratioHeight / 2, self.ratioFieldOffsetX, self.ratioFieldOffsetY + self.atRatio(goalSize / 2) + self.ratioHeight / 2)

        qp.drawLine(self.ratioFieldOffsetX + self.atRatio(180) + self.ratioWidth, self.ratioFieldOffsetY - self.atRatio(goalSize / 2) + self.ratioHeight / 2, self.ratioFieldOffsetX + self.atRatio(180) + self.ratioWidth, self.ratioFieldOffsetY + self.atRatio(goalSize / 2) + self.ratioHeight / 2)
        qp.drawLine(self.ratioFieldOffsetX + self.atRatio(180) + self.ratioWidth, self.ratioFieldOffsetY - self.atRatio(goalSize / 2) + self.ratioHeight / 2, self.ratioFieldOffsetX + self.ratioWidth, self.ratioFieldOffsetY - self.atRatio(goalSize / 2) + self.ratioHeight / 2)
        qp.drawLine(self.ratioFieldOffsetX + self.atRatio(180) + self.ratioWidth, self.ratioFieldOffsetY + self.atRatio(goalSize / 2) + self.ratioHeight / 2, self.ratioFieldOffsetX + self.ratioWidth, self.ratioFieldOffsetY + self.atRatio(goalSize / 2) + self.ratioHeight / 2)

        qp.setPen(self.blackPen)

        robotSize = 180 / self.ratio
        index = 0
        for i in self.vision.get_latest_frame().detection.robots_yellow:

            self.drawRobot(qp, 255, 255, 0, i, index, robotSize)

            index += 1

        index = 0
        for i in self.vision.get_latest_frame().detection.robots_blue:

            self.drawRobot(qp, 0, 0, 255, i, index, robotSize)

            index += 1

        qp.setPen(self.blackPen)
        qp.setBrush(QtGui.QColor(255, 69, 0, 200))
        ballSize = 10
        ballX = self.atRatio(self.vision.get_latest_frame().detection.balls[0].x) + (self.ratioFieldOffsetX + self.ratioWidth / 2)
        ballY = self.atRatio(-self.vision.get_latest_frame().detection.balls[0].y) + (self.ratioFieldOffsetY + self.ratioHeight / 2)
        #print ("Ball x: {} and y: {}".format(ballX, ballY))
        qp.drawEllipse(ballX - (ballSize / 2), ballY - (ballSize / 2), ballSize, ballSize)

    def drawRobot(self, qp, r, g, b, robot, index, robotSize):
        qp.setPen(self.blackPen)
        centerX = self.atRatio(robot.x) + (self.ratioFieldOffsetX + self.ratioWidth / 2)
        centerY = self.atRatio(-robot.y) + (self.ratioFieldOffsetY + self.ratioHeight / 2)
        qp.setBrush(QtGui.QColor(r, g, b, 70))
        qp.drawEllipse(centerX - robotSize, centerY - robotSize, robotSize * 2, robotSize * 2)
        qp.setBrush(QtGui.QColor(r, g, b, 200))
        qp.drawEllipse(centerX - robotSize / 2, centerY - robotSize / 2, robotSize, robotSize)


        indexLabel = "{}".format(index)
        fm = QtGui.QFontMetrics(QtGui.QFont('SansSerif', 20))
        labelWidth = fm.width(indexLabel)
        labelHeight = fm.height() - 11 #Hard coded for this font.
        labelX = centerX - labelWidth / 2
        labelY = centerY + labelHeight / 2

        qp.setBrush(QtGui.QColor(0, 0, 0, 150))
        qp.drawRect(labelX, labelY, labelWidth, -labelHeight)

        qp.setPen(self.whitePen)
        qp.drawText(QtCore.QPointF(labelX, labelY), indexLabel)
        index += 1

        x1, y1 = self.followAngle(-robot.orientation, centerX, centerY, robotSize)
        x2, y2 = self.followAngle(-robot.orientation, centerX, centerY, robotSize * 2)
        #qp.setPen(self.grayPenFat)
        #qp.drawLine(x1, y1, x2, y2)

        qp.setPen(self.blackPen)
        qp.drawLine(x1, y1, x2, y2)



    def drawPoints(self, qp):
        qp.setPen(QtCore.Qt.red)
        size = self.size()

        for i in range(1000):
            x = random.randint(1, size.width()-1)
            y = random.randint(1, size.height()-1)
            qp.drawPoint(x, y)

    def refresh(self):
        self.update()

    def slopeFromAngle(self, angle):
        if angle == math.pi + math.pi / 2:
            angle += 0.01
        elif angle == math.pi / 2:
            angle -= 0.01

        return math.tan(angle - math.pi)

    def pointsOnLine(self, slope, x, y, distance):
        b = y - slope * x
        r = math.sqrt(1 + slope * slope)

        newX1 = (x + (distance / r))
        newY1 = (y + ((distance * slope) / r))

        newX2 = (x + ((-distance) / r))
        newY2 = (y + (((-distance) * slope) / r))

        return ((newX1, newY1), (newX2, newY2))

    def followAngle(self, angle, x, y, distance):
        slope = self.slopeFromAngle(angle)
        coord1, coord2 = self.pointsOnLine(slope, x, y, distance)

        side = (angle - math.pi / 2) % (math.pi * 2)
        if (side < math.pi):
            return coord2
        else:
            return coord1
