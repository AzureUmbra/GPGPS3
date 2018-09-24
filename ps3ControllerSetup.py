from pygame.locals import *
import pygame
from time import sleep
from pickle import load,dump



class PS3Layout:
    def __init__(self,preActive=False):
        if preActive == False:
            pygame.init()
            pygame.joystick.init()
            self.joy = pygame.joystick.Joystick(0)
            self.joy.init()
        else:
            self.joy = preActive
        self.buttons = {}
        self.axes = {}


    def getControllerLayout(self):
        try:
            with open('ps3Layout.p','rb') as f:
                layout = load(f)
                self.buttons = layout[0]
                self.axes = layout[1]
        except:
            print('No Valid Layout Found')
            print('Starting Layout Configuration')
            self.createControllerLayout()
            dump([self.buttons,self.axes],open('ps3Layout.p','wb'))
        return self.buttons, self.axes


    def createControllerLayout(self):
        self.buttons = {'ps3': -1, 'start': -1, 'select': -1, 'up': -1, 'down': -1, 'left': -1, 'right': -1, 'r1': -1,
                        'r2': -1, 'r3': -1, 'l1': -1, 'l2': -1, 'l3': -1, 'cross': -1, 'square': -1, 'triangle': -1,
                        'circle': -1}
        self.axes = {'leftH': -1, 'rightH': -1, 'leftV': -1, 'rightV': -1, 'invert':{'leftH': -1, 'leftV': -1,
                     'rightH': -1, 'rightV': -1} }

        for key, value in self.buttons.items():
            print('Press the ' + key + ' Button Now...')
            done = False
            while not done:
                for event in pygame.event.get():
                    if event.type == pygame.JOYBUTTONDOWN:
                        for i in range(self.joy.get_numbuttons()):
                            if self.joy.get_button(i) == 1:
                                self.buttons[key] = i
                                done = True
            print('Button ' + key + ' Successfully Mapped!')

        self.axes = {'leftH': 0, 'rightH': 3, 'leftV': 1, 'rightV': 4, 'l2':2, 'r2':5, 'invert': {'leftH': 0, 'leftV': 1,
                                                                                      'rightH': 0, 'rightV': 1, 'l2':0, 'r2':0}}
        # tempAxesNames = {'Left Stick- Right':'leftH','Left Stick- Up':'leftV','Right Stick- Right':'rightH','Right Stick- Up':'rightV'}
        # for key, value in tempAxesNames.items():
        #     print('Move the ' + key + ' Now...')
        #     done = False
        #     while not done:
        #         for event in pygame.event.get():
        #             if event.type == pygame.JOYAXISMOTION:
        #                 for i in range(self.joy.get_numaxes()):
        #                     val = self.joy.get_axis(i)
        #                     if abs(val) >= 0.8:
        #                         self.axes[value] = i
        #                         self.axes['invert'][value] = 1 if val < 0 else 0
        #                         done = True
        #     print('Axis ' + key + ' Successfully Mapped!')
        #     sleep(2)

        print('Mapping Completed Successfully')


if __name__ == '__main__':
    pass