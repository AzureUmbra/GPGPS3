from ps3Controller import PS3
import gopigo3
import easygopigo3
from time import sleep
import math
from random import random, randint

class ps3GoPiGo:
    def __init__(self,delay):
        self.mode = 0
        self.controller = PS3(delay)
        self.motors = motorController()
        self.headActive = False
        self.headAngle = 0
        self.count = 0

    def run(self):
        done = False
        rangeLock = False
        range = 999999
        while not done:
            self.controller.update()

            if self.mode != 0 and self.controller.buttons['select'] == 1:
                self.mode = 0
                print('MODE: 0')
                self.motors.led(0,0,0,4)
            elif self.mode == 0:
                if self.controller.buttons['cross'] == 1:
                    self.mode = 1
                    print('MODE: 1')
                    self.motors.led(0, 0, 128, 4)
                elif self.controller.buttons['triangle'] == 1:
                    self.mode = 2
                    print('MODE: 2')
                    self.motors.led(0, 128, 0, 4)
                elif self.controller.buttons['circle'] == 1 and not self.headActive:
                    self.mode = 3
                    print('MODE: 3')
                    self.motors.led(128, 0, 0, 4)
                elif self.controller.buttons['square'] == 1 and not self.headActive:
                    print('MODE: 4')
                    self.motors.driveAuto(self.controller)
                    print('Self Drive Done!\nMODE: 0')

            if self.mode == 0:
                self.motors.motors(0,0)
            elif self.mode == 1:
                self.motors.driveModThresholdCircle(self.controller.axes['leftH'], self.controller.axes['leftV'])
            elif self.mode == 2:
                self.motors.driveTank(self.controller.axes['leftV'],self.controller.axes['rightV'])
            elif self.mode == 3:
                self.count += 1
                if self.count > 10:
                    range = self.motors.ranging()
                    print(range)
                    self.count = 0
                if range < 100 and not rangeLock:
                    rangeLock = True
                elif range > 300 and rangeLock:
                    rangeLock = False
                if rangeLock:
                    self.motors.motors(-100,-100)
                    self.motors.led(128, 0, 0, 0)
                    self.motors.led(128, 0, 0, 1)
                else:
                    self.motors.led(0, 0, 0, 0)
                    self.motors.led(0, 0, 0, 1)
                    self.motors.driveModThresholdCircle(self.controller.axes['leftH'], self.controller.axes['leftV'],0.1+(float(range-100)/2150))


            if self.controller.buttons['up'] == 1 and self.mode != 3:
                self.headActive = True
            if self.controller.buttons['down'] == 1:
                self.headActive = False
                self.motors.head(0)
                self.motors.rangeLights(True)

            if self.headActive:
                self.motors.head(round(self.controller.axes['rightH'],2))
                # if (1.0+self.controller.axes['l2'])/2.0 > 0.1 and self.headAngle > -90:
                #     self.headAngle -= ((1.0+self.controller.axes['l2'])/2.0)/5
                # elif (1.0+self.controller.axes['r2'])/2.0 > 0.1 and self.headAngle < 90:
                #     self.headAngle += ((1.0+self.controller.axes['r2'])/2.0)/5
                # self.motors.head(self.headAngle)
                self.count += 1
                if self.count > 10:
                    self.motors.rangeLights()
                    self.count = 0
            sleep(0.08)



class motorController:

    def __init__(self,speedLimit=300,axisLimit=1.0):
        self.minSpeed = -(speedLimit)
        self.maxSpeed = speedLimit
        self.minAxis = -(axisLimit)
        self.maxAxis = axisLimit

        self.gpg = gopigo3.GoPiGo3()
        self.egpg = easygopigo3.EasyGoPiGo3()
        self.distSensor = self.egpg.init_distance_sensor()
        self.head(0)
        self.curColor = 0

    def driveModThresholdCircle(self,x,y,mut=1.0):
        mut = 1.0 if mut > 1.0 else mut
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
        self.motors(left*mut,right*mut)

    def driveAuto(self,control):
        run = True
        mode = 0
        count = -1
        while run:
            control.update()
            if control.buttons['start'] == 1:
                run = False
            count += 1
            if count == 2:
                count = 0
            if count == 0:
                self.gpg.set_led(self.gpg.LED_EYE_LEFT,128,0,0)
                self.gpg.set_led(self.gpg.LED_EYE_RIGHT, 0, 0, 128)
            elif count == 1:
                self.gpg.set_led(self.gpg.LED_EYE_LEFT, 0, 0, 128)
                self.gpg.set_led(self.gpg.LED_EYE_RIGHT, 128, 0, 0)
            if mode == 0:
                dist = self.ranging()
                if dist < 150:
                    self.motors(0,0)
                    mode = 1
                elif 2300 > dist > 150:
                    speed = 100 + (200*(float(dist-150)/2150))
                    self.motors(speed,speed)
                else:
                    self.motors(300,300)
            elif mode == 1:
                if randint(0,100) > 50:
                    self.motors(-100,100)
                else:
                    self.motors(100,-100)
                mode = 2
            elif mode == 2:
                dist = self.ranging()
                if dist > 500:
                    sleep(0.25)
                    self.motors(0,0)
                    mode = 0
            sleep(0.08)
        self.gpg.set_led(self.gpg.LED_EYE_LEFT, 0, 0, 0)
        self.gpg.set_led(self.gpg.LED_EYE_RIGHT, 0, 0, 0)


    def driveTank(self,x,y):
        left = self.toSpeed(x)
        right = self.toSpeed(y)
        self.motors(left,right)

    def motors(self,left,right):
        self.gpg.set_motor_dps(self.gpg.MOTOR_LEFT, int(left))
        self.gpg.set_motor_dps(self.gpg.MOTOR_RIGHT, int(right))
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
        angle = int(self.scale(angle,-1,1,2000,700))
        self.gpg.set_servo(self.gpg.SERVO_1,angle)

    def ranging(self):
        return self.distSensor.read_mm()
    def rangeLights(self,off=False):
        if off:
            self.led(0,0,0,0)
            self.led(0,0,0,1)
        else:
            rnge = self.ranging()
            print(rnge)
            if rnge >= 2000:
                r,g,b=0,0,128
                newColor = 0
            elif 2000 > rnge >= 1000:
                r,g,b = 0,128,0
                newColor = 1
            elif 1000 > rnge >= 500:
                r,g,b = 64,128,0
                newColor = 2
            elif 500 > rnge >= 100:
                r,g,b = 128,128,0
                newColor = 3
            elif 100 > rnge >= 50:
                r,g,b = 128,64,0
                newColor = 4
            elif 50 > rnge:
                r,g,b = 128,0,0
                newColor = 5
            if self.curColor != newColor:
                self.curColor = newColor
                self.led(r,g,b,0)
                self.led(r,g,b,1)

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