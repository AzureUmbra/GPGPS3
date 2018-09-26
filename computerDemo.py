from simpleControls import simpleRobot
from time import sleep


class interface:
    def __init__(self):
        self.commands = ['forward','backward','left','right','distance','head','gohome','light','eye','help','MADDUCKS']
        self.controls = ['DO','AGAIN','END','FORGET','FORGETLAST']
        self.admin = ['exit','shutdown','speed','limits','origin','edgeAdjust','edgeActive','help']
        self.adminMode = False
        self.program = []
        self.startUp()
        self.run()


    def getInput(self):
        return input('>>> ')


    def getAdmin(self):
        return input('#ADMIN# ')


    def adminParser(self, string):
        cmds = [j for j in [i.strip() for i in string.split()] if j != '']
        if len(cmds) == 0:
            return

        if cmds[0] not in self.admin:
            return 'Invalid Command'

        if cmds[0] == 'exit':
            self.adminMode = False
            print('\n' * 100)
            self.intro()
            return

        elif cmds[0] == 'shutdown':
            return True

        elif cmds[0] == 'speed':
            return self.robot.setSpeed(cmds[1])

        elif cmds[0] == 'limits':
            return self.robot.setTableLimits((int(cmds[1]),int(cmds[2])))

        elif cmds[0] == 'origin':
            return self.robot.setOrigin()

        elif cmds[0] == 'edgeAdjust':
            return self.robot.setEdgeSensor(int(cmds[1]))

        elif cmds[0] == 'edgeActive':
            return self.robot.setEdgeSensorState(bool(cmds[1]))

        elif cmds[0] == 'help':
            self.adminHelp()


    def parser(self, string):
        cmds = [j for j in [i.strip() for i in string.split()] if j != '']
        if len(cmds) == 0:
            return

        if cmds[0] == self.commands[-1]:
            self.adminMode = True
            return

        if cmds[0].lower() in self.commands:
            cmd = cmds[0].lower()

            if cmd == 'help':
                self.help()

            elif cmd == 'forward':
                try:
                    count = int(cmds[1])
                    return self.robot.forward(count)
                except:
                    return "I Don't Know That Number..."

            elif cmd == 'backward':
                try:
                    count = int(cmds[1])
                    return self.robot.backward(count)
                except:
                    return "I Don't Know That Number..."

            elif cmd == 'left':
                try:
                    count = int(cmds[1])
                    return self.robot.spinLeft(count)
                except:
                    return "I Don't Know That Number..."

            elif cmd == 'right':
                try:
                    count = int(cmds[1])
                    return self.robot.spinRight(count)
                except:
                    return "I Don't Know That Number..."

            elif cmd == 'distance':
                return self.robot.getDistance()

            elif cmd == 'gohome':
                print(self.robot.goHome())
                self.intro()
                return

            elif cmd == 'head':
                try:
                    count = int(cmds[1])
                    return self.robot.setServo(count)
                except:
                    return "I Don't Know That Number..."

            elif cmd == 'light':
                return self.robot.setBlinker(cmd[1],cmd[2])

            elif cmd == 'eye':
                try:
                    if type(cmd[2].split(',')[0]) is int and len(cmd[2].split(',')) == 3:
                        cmd[2] = tuple(cmd[2].strip('()').split(','))
                    return self.robot.setEye(cmd[1],cmd[2])
                except:
                    return "I Don't Know What You Mean..."


        elif cmds[0] in self.controls:
            cmd = cmds[0]

            if cmd == 'DO':
                if len(self.program) != 0:
                    return 'You are Already Giving Me Instructions...'
                else:
                    self.program.append('DO')

            if cmd == 'FORGET':
                self.program = []
                return 'I Forgot It All'

            if cmd == 'FORGETLAST':
                if len(self.program) >= 1:
                    self.program = self.program[:-1]
                    return 'I Forgot It'
                else:
                    return 'I have Nothing to Forget'

            if cmd == 'END':
                if len(self.program) >= 2:
                    self.program.append(1)
                    return 1
                elif len(self.program) == 1:
                    return "You havn't Given Me Instructions Yet"
                else:
                    return "You havn't Started a Program with DO"

            if cmd == 'AGAIN':
                if len(self.program) >= 2:
                    try:
                        count = int(cmds[1])
                        self.program.append(count)
                        return 1
                    except:
                        return "I Don't Know That Number..."
                elif len(self.program) == 1:
                    return "You havn't Given Me Instructions Yet"
                else:
                    return "You havn't Started a Program with DO"


        else:
            return "I Don't Know What You Mean..."



    def runner(self):
        print('Here I Go!')
        for i in range(self.program[-1]):
            for j in self.program[1:-1]:
                if j in self.commands[:-2]:
                    print(self.parser(j))
        self.program = []
        print('I Did It!')


    def run(self):
        self.intro()
        running = True
        while running:
            if self.adminMode:
                x = self.getAdmin()
                x = self.adminParser(x)
                if type(x) is str:
                    print(x)
                if x == True:
                    running = False

            else:
                x = self.getInput()
                x = self.parser(x)
                if type(x) is str:
                    print(x)
                elif type(x) is int:
                    if x == 1:
                        self.runner()

        print('System Shutting Down...')
        self.robot.egpg.stop()
        sleep(1)
        self.robot.setServo(0)
        sleep(1)
        self.robot.setBlinker('both','off')
        sleep(1)
        self.robot.setEye('both','off')
        sleep(1)
        print('Goodbye!')


    def intro(self):
        print('Hello! My name is Dex!')
        print('I need you to help me drive around!')
        print("Type HELP if you need me to show you my language!")
        print('Lets Go!')


    def help(self):
        print('Here is what I understand:\n')
        print("gohome -\t I'll come back to my home spot")
        print("forward # -\t I'll drive # cm forward, just pick a number for #")
        print("backward # -\t I'll drive # cm backward, just pick a number for #")
        print("left # -\t I'll turn # degrees left, just pick a number for #")
        print("right # -\t I'll turn # degrees right, just pick a number for #")
        print("distance -\t I'll tell you the nearest object I can see")
        print("head # -\t I'll turn my head, -90 is full left and 90 is full right\n")
        print("light left/right/both on/off - Pick a side and a status and I'll light up")
        print("\tExample: light left on - I'll turn my left light on\n")
        print("eye left/right/both color -\t Pick a eye and a color, and I'll change my eyes")
        print("\tExample: left red - My left eye will light up red")
        print("\tExample: both 255,128,0 - Both my eyes will be a mix of red and green")
        print("\tThis is called RGB, the 1st number is red, the 2nd green, and the 3rd blue")
        print("\tYou can pick any number between 0-255 for the colors, and I'll mix them\n")
        print("\nI can also do many things at once!\n")
        print("DO -\t\t Anything you type after this I'll wait until you tell me to start")
        print("END -\t\t This tells me to start doing what you said")
        print("AGAIN # -\t Type this and pick a number for # and I'll do it that many times")
        print("FORGET -\t I'll forget everything you told me after and including DO")
        print("FORGETLAST -\t I'll forget the last thing you told me")
        print("\nHere's an example:")
        print("\tDO\n\tforward 10\n\tright 90\n\tforward 5\n\tEND")
        print("Type DO, and I'll wait until you type END, and then I'll drive forward 10cm,")
        print("turn 90 degrees right, and drive another 5cm forward")
        print("\nHere is one more example:")
        print("\tDO\n\tforward 10\n\tright 90\n\tforward 10\n\tright 90\n\tforward 10\n\tright 90\n\tforward 10\n\tright 90\n\tAGAIN 3")
        print("Type DO, and I'll wait just like before. But instead of doing it once like with END,")
        print("I'll do it 3 times because you said AGAIN 3. Can you figure out what I would do? Why don't you try it?")


    def startUp(self):
        print('\n'*100)
        print('333TRS GoPiGo3 Demo')
        print('Contact 2LT Gareth Price for Issues')
        print('(419) 341-6105')
        print('\n\n\n')
        sleep(3)
        print('Instantiating Robot...Standby')
        speed = int(input('Max Robot Speed (default: 300): '))
        servo = input('Head Servo Active (y/n): ').lower()
        if servo == 'y':
            servoMin = int(input('Min Servo Limit (default: 700): '))
            servoMax = int(input('Max Servo Limit (default: 2000): '))
        else:
            servoMax, servoMin = None, None
        edgeSensor = input('Edge Sensor Active (y/n): ').lower()
        edgeSensor = True if edgeSensor == 'y' else False
        print('\nTable Limits are in Centimeters')
        print('They are measured from the center axle of the robot')
        print('Ensure you account for the size of the robot when deciding limits!')
        print('\nPlace the Robot at the Lower-Left of the Table')
        print('Enter 0 for both for No Limits')
        x = int(input('Enter the Length of the Table (in front of robot): '))
        y = int(input('Enter the Width of the Table (right of robot): '))
        self.robot = simpleRobot(speed,(servoMin,servoMax),edgeSensor,(x,y))
        print('\n\n\nRobot Ready\n\n')
        print(self.robot._checkSetup())
        print("\nType 'MADDUCKS' at the prompt for admin functions")
        print('Screen clearing in 5',end='')
        for i in range(5):
            print('.',end='',flush=True)
            sleep(1)
        print('\n'*100)


    def adminHelp(self):
        self.admin = ['exit', 'shutdown', 'speed', 'limits', 'origin', 'edgeAdjust', 'edgeActive']
        print("exit - \t\t\tLeaves Admin Mode")
        print("shutdown - \t\tTerminates Robot Operations")
        print("speed int - \t\tSets the robot speed (default:300)")
        print("limits int int - \tSets the table limits in cm, forward then right, 0 0 specifies no limits")
        print('origin - \t\tTells the robot that you have moved it back the the origin')
        print('edgeAdjust int - \tAdjusts the threshold for a edge being detected in mm greater than startup height (default:100)')
        print('edgeActive bool - \tActivate or Deactivate the edge sensor')
        print('\n\nContact 2LT Gareth Price at (419) 341-6105 with questions.')


if __name__ == '__main__':
    interface = interface()