from ps3Controller import PS3
import gopigo3
import easygopigo3
import time
import math

class ps3GoPiGo:
    def __init__(self,delay):
        self.mode = 0
        self.controller = PS3(delay)
        self.motors = motorController()
        self.headActive = False
        self.headAngle = 0

    def run(self):
        done = False
        while not done:
            self.controller.update()

            if self.mode != 0 and self.controller.buttons['select'] == 1:
                self.mode = 0
                print('MODE: 0')
            elif self.mode == 0:
                if self.controller.buttons['cross'] == 1:
                    self.mode = 1
                    print('MODE: 1')
                elif self.controller.buttons['triangle'] == 1:
                    self.mode = 2
                    print('MODE: 2')

            if self.mode == 0:
                self.motors.motors(0,0)
            elif self.mode == 1:
                self.motors.driveModThresholdCircle(self.controller.axes['leftH'], self.controller.axes['leftV'])
            elif self.mode == 2:
                self.motors.driveTank(self.controller.axes['leftV'],self.controller.axes['rightV'])

            if self.controller.buttons['square'] == 1:
                self.motors.ranging()
            if self.controller.buttons['up'] == 1:
                self.headActive = True
                self.motors.led(0,0,255,4)
            if self.controller.buttons['down'] == 1:
                self.headActive = False
                self.motors.led(0, 0, 0,4)
                self.motors.head(0)

            if self.headActive and self.mode != 2:
                #self.motors.head(round(self.controller.axes['rightH'],2))
                if (1.0+self.controller.axes['l2'])/2.0 > 0.1 and self.headAngle > -90:
                    self.headAngle -= round((1.0+self.controller.axes['l2'])/2.0,2)
                elif (1.0+self.controller.axes['r2'])/2.0 > 0.1 and self.headAngle < 90:
                    self.headAngle += round((1.0+self.controller.axes['r2'])/2.0,2)
                self.motors.head(self.headAngle)



class motorController:

    def __init__(self,speedLimit=255,axisLimit=1.0):
        self.minSpeed = -(speedLimit)
        self.maxSpeed = speedLimit
        self.minAxis = -(axisLimit)
        self.maxAxis = axisLimit

        self.gpg = gopigo3.GoPiGo3()
        self.egpg = easygopigo3.EasyGoPiGo3()
        self.distSensor = self.egpg.init_distance_sensor()
        self.head(0)

    def driveModThresholdCircle(self,x,y):
        r,theta = self.rTheta(x,y)
        left = int(round(self.scale(r,0.0,1.0,0,self.maxSpeed),0))
        right = left
        if 0 <= theta < 90:
            right = int(round(right * self.scale(theta,0,90,-1,1),0))
        elif 90 <= theta < 180:
            left = int(round(left * self.scale(theta,90,180,1,-1),0))
        elif 180 <= theta < 270:
            right = int(round(right * self.scale(theta,180,270,1,-1),0))
            left = -left
        else:
            right = -right
            left = int(round(left * self.scale(theta,270,360,-1,1),0))
        self.motors(left,right)

    def driveTank(self,x,y):
        left = self.toSpeed(x)
        right = self.toSpeed(y)
        self.motors(left,right)

    def motors(self,left,right):
        self.gpg.set_motor_dps(self.gpg.MOTOR_LEFT, left)
        self.gpg.set_motor_dps(self.gpg.MOTOR_RIGHT, right)
        #print('Left: ' + str(left) + ' Right: ' + str(right))

    def toSpeed(self,value):
        return int(round(self.scale(value,self.minAxis,self.maxAxis,self.minSpeed,self.maxSpeed),0))

    def bound(self,value,min,max):
        if value > max:
            return max
        elif value < min:
            return min
        else:
            return value

    def scale(self,value,minInput,maxInput,minOutput,maxOutput):
        value = self.bound(value,minInput,maxInput)
        leftSpan = maxInput - minInput
        rightSpan = maxOutput - minOutput

        # Convert the left range into a 0-1 range (float)
        scalar = float(value - minInput) / float(leftSpan)
        # Convert the 0-1 range into a value in the right range.
        return minOutput + (scalar * rightSpan)

    def rTheta(self,x,y):
        r = math.sqrt(((x)**2)+((y)**2))
        if x == 0 and y > 0:
            return [r, 90.0]
        elif x == 0 and y < 0:
            return [r,270.0]
        elif y == 0 and x >= 0:
            return [r,0.0]
        elif y == 0 and x < 0:
            return [r,180.0]
        else:
            if y > 0 and x > 0:
                return [r,math.degrees(math.atan(y / x))]
            elif y < 0 and x > 0:
                return [r,360.0 + math.degrees(math.atan(y / x))]
            else:
                return [r,180 + math.degrees(math.atan(y / x))]



    def head(self,angle):
        #700-2000
        angle = int(self.scale(angle,-90,90,2000,700))
        self.gpg.set_servo(self.gpg.SERVO_1,angle)

    def ranging(self):
        print(self.distSensor.read_mm())

    # def slewHead(self,rate,clockwise):
    #     if clockwise:
    #         self.headAngle = self.headAngle + rate + .5
    #     else:
    #         self.headAngle = self.headAngle - (rate + .5)
    #     print(self.headAngle)
    #     self.head(self.headAngle)

    def led(self,r,g,b,led):
        leds = [self.gpg.LED_EYE_LEFT,self.gpg.LED_EYE_RIGHT,self.gpg.LED_BLINKER_LEFT,self.gpg.LED_BLINKER_RIGHT,self.gpg.LED_WIFI]
        led = leds[led]
        self.gpg.set_led(led,r,g,b)


if __name__ == '__main__':
    client = ps3GoPiGo(50)
    client.run()
    # t = motorController()
    # t.driveTrueCircle((-0.5),.5)
    # x=math.sqrt(((-.5)**2)+(.5**2))
    # y=t.scale(x,0,1,-1,1)
    # print(t.toSpeed(y))
    # t.motors(106,180)