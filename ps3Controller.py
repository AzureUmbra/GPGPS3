from pygame.locals import *
import pygame
from time import sleep
import math
from ps3ControllerSetup import PS3Layout
from copy import deepcopy
"""
PS3
    buttons:
        x-14
        s-15
        o-13
        t-12
        up-4
        down-6
        left-7
        right-5
        l1-10
        l2-8
        r1-11
        r2-9
        l3-1
        r3-2
        sel-0
        st-3
        ps3-16
    axis:
        right/lr-2
        right/ud-3
        left/ud-1
        left/lr-0
        
"""
class PS3:
    def __init__(self,delay = 0):
        pygame.init()
        pygame.joystick.init()
        self.joy = pygame.joystick.Joystick(0)
        self.joy.init()

        layout = PS3Layout(self.joy)
        self.buttonLayout, self.axisLayout = layout.getControllerLayout()
        self.buttons = deepcopy(self.buttonLayout)
        self.axes = deepcopy(self.axisLayout)
        del self.axes['invert']
        for i in self.buttons.keys():
            self.buttons[i] = 0
        for i in self.axes.keys():
            self.axes[i] = 0

        self.delay = delay/1000



    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYBUTTONUP:
                for i in self.buttonLayout.keys():
                    self.buttons[i] = self.joy.get_button(self.buttonLayout[i])
            elif event.type == pygame.JOYAXISMOTION:
                for i in self.axisLayout.keys():
                    if i != 'invert':
                        if self.axisLayout['invert'][i] == 0:
                            self.axes[i] = self.joy.get_axis(self.axisLayout[i])
                        else:
                            self.axes[i] = -self.joy.get_axis(self.axisLayout[i])
        sleep(self.delay)




    def zeroDist(self):
        print(math.sqrt((self.axes['leftH'])**2+(self.axes['leftV'])**2))

if __name__ == '__main__':
    p = PS3(50)
    p.update()
    while p.buttons['cross'] != 1:
        p.zeroDist()
        p.update()