import gopigo3,easygopigo3
from time import sleep
from math import sin, cos, radians, sqrt, atan2, degrees


class simpleRobot():

    def __init__(self, maxSpeed=300, servo=(None,None), edgeSensor=False, tableLimits=(0,0)):
        self.gpg = gopigo3.GoPiGo3()
        self.egpg = easygopigo3.EasyGoPiGo3()
        self.maxSpeed =maxSpeed

        self.setEye('both','Off')
        self.egpg.open_eyes()

        self.setup = ""

        if servo != (None,None):
            self.servoLimits = [servo[0],servo[1]]
            self.setup += 'Servo Active\n'
            try:
                self.distanceSensor = self.egpg.init_distance_sensor()
                self.setup += 'Distance Sensor Active\n'
            except:
                self.setup += '***Distance Sensor Non-Functional***\n'
                self.distanceSensor = None
        else:
            self.servoLimits = None
            self.setup += '***Servo Non-Functional***'

        if edgeSensor:
            try:
                self.edgeSensor = self.egpg.init_distance_sensor()
                self.edgeLimit = self.edgeSensor.read_mm() + 100
                self.setup += 'Edge Sensor Active at ' + str(self.edgeLimit) + '\n'
            except:
                self.setup += '***Edge Sensor Non-Functional***\n'
                self.edgeSensor = None

        if tableLimits != (0,0):
            self.tableLimits = tableLimits
            self.position = [0,0]
            self.angle = 0
            self.setup += 'Table Limits Set to ' + str(self.tableLimits) + '\n'
        else:
            self.tableLimits = None
            self.setup += '***Table Limits Set to Unlimited***'

        self.setup += 'Setup Complete\n'


    def goHome(self):
        if self._getEdge():
            self.backward(5)
        dist = sqrt(self.position[0] ** 2 + self.position[1] ** 2)
        angle = degrees(atan2(self.position[1], self.position[0])) + 180
        if angle - self.angle >= 180:
            self.spinRight(self.angle - angle)
        else:
            self.spinLeft(self.angle - angle)
        limit = self.tableLimits
        edge = self.edgeSensor
        self.edgeSensor = None
        self.tableLimits = None
        self.forward(dist)
        self.spinRight(self.angle + (360 - self.angle))
        self.edgeSensor = edge
        self.tableLimits = limit
        return "I'm Home!"


    def forward(self, dist):
        if not self._checkTable(dist):
            return 'That Will Drive Me Off the Edge!'
        if self._getEdge():
            return "I'm Livin' on the Edge!"

        mm = dist * 10
        deg = self._mmToDeg(mm)
        startLeft = self.egpg.get_motor_encoder(self.egpg.MOTOR_LEFT)
        startRight = self.egpg.get_motor_encoder(self.egpg.MOTOR_RIGHT)
        self.egpg.drive_cm(dist,blocking=False)
        success = self._checkEdge(startLeft+deg,startRight+deg)
        if success:
            self._setPosition(dist)
            return 'I Drove Forward ' + str(dist) + ' cm'
        else:
            total = self._degToMm(self.egpg.get_motor_encoder(self.egpg.MOTOR_LEFT) - startLeft)
            self._setPosition(total)
            return 'That Was Close!\n I Drove Forward ' + str(round(total,2)) + ' cm'




    def backward(self, dist):
        dist = -dist
        if not self._checkTable(dist):
            return 'That Will Drive Me Off the Edge!'

        mm = dist * 10
        deg = self._mmToDeg(mm)
        startLeft = self.egpg.get_motor_encoder(self.egpg.MOTOR_LEFT)
        startRight = self.egpg.get_motor_encoder(self.egpg.MOTOR_RIGHT)
        self.egpg.drive_cm(dist,blocking=False)
        success = self._checkEdge(startLeft + deg, startRight + deg,stop=False)
        self._setPosition(dist)
        return 'I Drove Backward ' + str(dist) + ' cm'


    def turnLeft(self, angle=90, offset=0):
        if self.tableLimits is not None:
            return "I'm Sorry Dave, I'm Afraid I Can't Do That"
        else:
            pass


    def turnRight(self, angle=90, offset=0):
        if self.tableLimits is not None:
            return "I'm Sorry Dave, I'm Afraid I Can't Do That"
        else:
            pass


    def spinLeft(self, angle=90.0):
        angle = -angle
        if self._getEdge():
            return "I'm Livin' on the Edge!"

        deg = self._mmToDeg(self._wheelTravel(angle))
        startLeft = self.egpg.get_motor_encoder(self.egpg.MOTOR_LEFT)
        startRight = self.egpg.get_motor_encoder(self.egpg.MOTOR_RIGHT)
        self.egpg.turn_degrees(angle,blocking=False)
        success = self._checkEdge(startLeft + deg, startRight - deg)
        if success:
            self._setAngle(angle)
            return 'I Turned Left ' + str(angle) + ' degrees'
        else:
            total = self._bodyAngle(self._degToMm(self.egpg.get_motor_encoder(self.egpg.MOTOR_LEFT) - startLeft))
            self._setAngle(total)
            return 'That Was Close!\n I Turned Left ' + str(round(total,2)) + ' degrees'



    def spinRight(self, angle=90.0):
        if self._getEdge():
            return "I'm Livin' on the Edge!"

        deg = self._mmToDeg(self._wheelTravel(angle))
        startLeft = self.egpg.get_motor_encoder(self.egpg.MOTOR_LEFT)
        startRight = self.egpg.get_motor_encoder(self.egpg.MOTOR_RIGHT)
        self.egpg.turn_degrees(angle,blocking=False)
        success = self._checkEdge(startLeft + deg, startRight - deg)
        if success:
            self._setAngle(angle)
            return 'I Turned Right ' + str(angle) + ' degrees'
        else:
            total = self._bodyAngle(self._degToMm(self.egpg.get_motor_encoder(self.egpg.MOTOR_LEFT) - startLeft))
            self._setAngle(total)
            return 'That Was Close!\n I Turned Right ' + str(round(total,2)) + ' degrees'


    def getDistance(self):
        if self.distanceSensor is None:
            return "I Can't See Anything"

        dist = self.distanceSensor.read_mm()/10
        return 'I see something ' + str(round(dist,2)) + ' cm away'


    def setServo(self, angle=0):
        if self.servoLimits is None:
            return 'That Will Make Me Dizzy'

        if angle > self.servoLimits[1] or angle < self.servoLimits[0]:
            return "My Head Doesn't Turn That Far!"

        ang = int(self._scale(angle, -90, 90, self.servoLimits[1], self.servoLimits[0]))
        self.gpg.set_servo(self.gpg.SERVO_1, ang)
        return 'I Turned My Head to ' + str(angle) + ' Degrees'


    def setBlinker(self, id, state):
        if state.lower() == 'on':
            if id.lower() == 'both':
                self.egpg.blinker_on(0)
                self.egpg.blinker_on(1)
                return 'I Turned Both My Lights On'
            elif id.lower() == 'left':
                self.egpg.blinker_on(1)
                return 'I Turned My Left Light On'
            elif id.lower() == 'right':
                self.egpg.blinker_on(0)
                return 'I Turned My Right Light On'
        elif state.lower() == 'off':
            if id.lower() == 'both':
                self.egpg.blinker_off(0)
                self.egpg.blinker_off(1)
                return 'I Turned Both My Lights Off'
            elif id.lower() == 'left':
                self.egpg.blinker_off(1)
                return 'I Turned My Left Light Off'
            elif id.lower() == 'right':
                self.egpg.blinker_off(0)
                return 'I Turned My Right Light Off'
        return "I Don't Know What You Mean..."




    def setEye(self, id, color):
        color = color.lower()
        colors = {'red':(255,0,0),'green':(0,255,0),'blue':(0,0,255),'pink':(255,0,255),'cyan':(0,255,255),'yellow':(255,255,0),'white':(255,255,255),'off':(0,0,0)}
        good = False
        colorWord = ''
        if type(color) is str and color in colors.keys():
            colorWord = color
            color = colors[color]
            good = True
        elif type(color) is tuple and len(color) == 3:
            good = True
            colorWord = 'This Cool Color'
            for i in color:
                if i < 0 or i > 255:
                    good = False

        if not good:
            return "I Don't Know That Color"

        colorWord = colorWord.capitalize()
        if id.lower() == 'left':
            self.egpg.set_left_eye_color(color)
            return 'My Left Eye is Now ' + colorWord
        elif id.lower() == 'right':
            self.egpg.set_right_eye_color(color)
            return 'My Right Eye is Now ' + colorWord
        elif id.lower() == 'both':
            self.egpg.set_eye_color(color)
            return 'Both My Eyes are Now ' + colorWord
        return 'I Only Have 2 Eyes'



    ### HELPER FUNCTIONS ###


    def _getEdge(self):
        if self.edgeSensor is None:
            return False

        if self.edgeSensor.read_mm() >= self.edgeLimit:
            return True
        else:
            return False


    def _checkSetup(self):
        return self.setup


    def _checkEdge(self,tgtLeft, tgtRight,stop=True):
        while not self.egpg.target_reached(tgtLeft, tgtRight):
            if self._getEdge():
                self.setEye('BOTH','Red')
                if stop:
                    self.egpg.stop()
                    return False
            else:
                self.setEye('BOTH', 'Off')
            sleep(0.01)
        return True


    def _checkTable(self,dist):
        if self.tableLimits is None:
            return True

        x = dist * cos(radians(self.angle))
        y = dist * sin(radians(self.angle))
        x += self.position[0]
        y += self.position[1]

        if x > self.tableLimits[0] or y > self.tableLimits[1] or x < 0 or y < 0:
            return False
        else:
            return True

    def _setPosition(self,dist):
        if self.tableLimits is not None:
            x = dist * cos(radians(self.angle))
            y = dist * sin(radians(self.angle))
            self.position[0] += x
            self.position[1] += y

    def _setAngle(self, angle):
        test = self.angle + angle
        while test >= 360:
            test -= 360
        while test < 0:
            test += 360
        self.angle = test

    def _mmToDeg(self, mm):
        return (mm / self.egpg.WHEEL_CIRCUMFERENCE) * 360

    def _degToMm(self, deg):
        return (deg / 360) * self.egpg.WHEEL_CIRCUMFERENCE

    def _wheelTravel(self, deg):
        return (self.egpg.WHEEL_BASE_CIRCUMFERENCE * deg) / 360

    def _bodyAngle(self, mm):
        return (mm * 360) / self.egpg.WHEEL_BASE_CIRCUMFERENCE

    def _scale(self,value,minInput,maxInput,minOutput,maxOutput):
        value = self._bound(value,minInput,maxInput)
        leftSpan = maxInput - minInput
        rightSpan = maxOutput - minOutput
        scalar = float(value - minInput) / float(leftSpan)
        return minOutput + (scalar * rightSpan)

    def _bound(self,value,min,max):
        if value > max:
            return max
        elif value < min:
            return min
        else:
            return value

    ### ADMIN FUNCTIONS ###


    def setSpeed(self, speed):
        self.egpg.set_speed(speed)
        return "Robot Speed Set to " + str(self.egpg.get_speed())

    def setTableLimits(self,tableLimits=(0,0)):
        if tableLimits != (0,0):
            self.tableLimits = tableLimits
            self.position = [0,0]
            self.angle = 0
            return "Table Limits Set to " + str(self.tableLimits) + "\nMove Robot to Origin"
        else:
            del self.position
            del self.angle
            self.tableLimits = None
            return "Table Limits Set to Unlimited"

    def setOrigin(self):
        self.position = [0,0]
        self.angle = 0
        return "Origin Reset\nMove Robot to Origin"

    def setEdgeSensor(self,offset=100):
        if self.edgeSensor is None:
            return "No Edge Sensor Exists"
        else:
            self.edgeLimit = self.edgeSensor.read_mm() + offset
            return 'Edge Sensor Active at ' + str(self.edgeLimit) + '\n'

    def setEdgeSensorState(self,active):
        if active and self.edgeSensor is None:
            try:
                self.edgeSensor = self.egpg.init_distance_sensor()
                self.edgeLimit = self.edgeSensor.read_mm() + 100
                return 'Edge Sensor Active at ' + str(self.edgeLimit) + '\n'
            except:
                self.edgeSensor = None
                return '***Edge Sensor Non-Functional***\n'
        elif not active and self.edgeSensor is not None:
            self.edgeSensor = None
            return 'Edge Sensor Disabled'
        else:
            return 'Invalid Command for Current Edge Sensor State'


if __name__ == '__main__':
    pass