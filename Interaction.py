import viz
import vizact
import vizjoy
import math
from LowPassDynamicFilter import LowPassDynamicFilter
from Vector3 import Vector3

MOVE_SPEED = .1  #5
TURN_SPEED = 1   #10
CURSOR_SPEED = .1
FPS = 60

class Joystick(viz.EventClass):
    """This is the Joystick Interacion class"""
    def __init__ (self, win, PlayViewObj=None):
        self.joystick = vizjoy.add()
        self.view = win.getView()
        self.window = win
        self.toolActive = 0
        self.moveCursor = False
        self._updateFunc = vizact.onupdate(0, self.UpdateJoystick)
        self.filter = LowPassDynamicFilter(0.5, 5, 10.0, 200.0)
        self.player = PlayViewObj
        #Call super class constructor to create different callbacks for every joystick
        viz.EventClass.__init__(self)
        self.callback(vizjoy.BUTTONDOWN_EVENT, self.joydown)
        self.callback(vizjoy.BUTTONUP_EVENT, self.joyup)
        self.callback(vizjoy.HAT_EVENT, self.joyhat)
        #set the PlayerView instance items controlled by the joystick
        
    def UpdateJoystick(self):
        global v1, v2, v3, v4
        #Get the joystick position
        x,y,z = self.joystick.getPosition()
        twist = self.joystick.getTwist()
        
        #Move the viewpoint forward/backward based on y-axis value
        if abs(y) > 0.2:
            self.view.move([0,0,MOVE_SPEED * -y], viz.BODY_ORI)
            #self.view.move([0,0,viz.elapsed() * MOVE_SPEED * -y], viz.BODY_ORI)

        #Move the viewpoint left/right based on x-axis value
        if abs(x) > 0.2:
            self.view.setEuler([TURN_SPEED * x,0,0], viz.BODY_ORI,viz.REL_PARENT)
            #self.view.setEuler([viz.elapsed() * TURN_SPEED * x,0,0], viz.BODY_ORI,viz.REL_PARENT)
        
        #Tilt the head up and down until 45 degrees
#        if abs(twist) > 0.2: #Make sure value is above a certain threshold
#            if abs(self.view.getEuler()[1])<=45:
#                self.view.setEuler([0,twist,0],viz.HEAD_ORI,viz.REL_PARENT)
#        else:
#            self.view.setEuler([0,0,0],viz.HEAD_ORI,viz.ABS_PARENT)
        #Tilt the head up and down until 45 degrees
        if abs(twist) < .104 :
            twist = 0
        newTwist = self.filter.Apply(Vector3(0, twist, 0), FPS)
        #if abs(twist) > 0.05: #Make sure value is above a certain threshold
        self.view.setEuler([0,newTwist.y*60,0],viz.HEAD_ORI,viz.ABS_PARENT)
        
        #Move the cursor towards the direction of the cross buttons (hat)
        if isinstance(self.moveCursor, list):
            # prevent the cursor from moving outside of the window
            objPos = self.toolActive.getDst().getPosition()
            objPos[0] += self.moveCursor[0]
            objPos[1] += self.moveCursor[1]
            if self.moveCursor[0] < 0 and self.window.worldToScreen(objPos)[0] <= .05:
                self.moveCursor[0] = 0
            if self.moveCursor[0] > 0 and self.window.worldToScreen(objPos)[0] >= .95:
                self.moveCursor[0] = 0
            if self.moveCursor[1] < 0 and self.window.worldToScreen(objPos)[1] <= .05:
                self.moveCursor[1] = 0
            if self.moveCursor[1] > 0 and self.window.worldToScreen(objPos)[1] >= .95:
                self.moveCursor[1] = 0
            self.toolActive.preTrans(self.moveCursor)
            
        # Check for button presses
#        try:
#            len(self.player._toolbox) > 0
#            if self.joystick.isButtonDown(1):
#                self.player.SelectItem(-1)
#                toolLink = self.player.HoldObject()
#                self.ControlObject(toolLink)
#            if self.joystick.isButtonDown(3):
#                self.player.SelectItem(1)
#                toolLink = self.player.HoldObject()
#                self.ControlObject(toolLink)
##            if e.button == 2:
##                toolLink = self.player.HoldObject()
##                self.ControlObject(toolLink)
#            if self.joystick.isButtonDown(4):
#                self.player.DropObject()
#            if self.joystick.isButtonDown(2):
#                self.player.PickObject()
#        except AttributeError:
#            pass
            
    
    def joydown(self, e):
        if e.joy != self.joystick:
            return
        try:
            len(self.player._toolbox) > 0
            if e.button in [1, 5]:
                self.player.SelectItem(-1)
                toolLink = self.player.HoldObject()
                self.ControlObject(toolLink)
            if e.button in [3, 6]:
                self.player.SelectItem(1)
                toolLink = self.player.HoldObject()
                self.ControlObject(toolLink)
            if e.button == 4:
                self.player.DropObject()
            if e.button in [2, 7, 8, 11, 12]:
                self.player.PickObject(True)
            if e.button == 9:
                self.player.HideShowHUD()
        except AttributeError:
            pass
        #print e.button

    def joyup(self, e):
        if e.joy != self.joystick:
            return
        try:
            if e.button in [2, 11, 12]:
                self.player.PickObject(False)
        except AttributeError:
            pass
        
    def joyhat(self, e):
        # e.hat		- new hat value
        # e.oldHat	- old hat value
        if e.joy != self.joystick:
            return
        if not isinstance(self.toolActive, int):
            self.moveCursor = True
            if e.hat >= 0:
                deg = e.hat
                x = y = 0
                if deg > 180:
                    deg = deg - 360
                #check y move
                if abs(deg) < 90:
                    y = 1
                elif abs(deg) > 90:
                    y = -1
                #check x move
                if deg < 0:
                    x = -1
                elif 180 > deg > 0:
                    x = 1
                speed = viz.elapsed() * CURSOR_SPEED
                
                self.moveCursor = [speed * x, speed * y, 0]
            else:
                self.moveCursor = False
    
    def ControlObject (self,obj):
        self.toolActive = obj
    
if __name__ == '__main__':

    viz.setMultiSample(2)
    viz.go()

    ground = viz.addChild('ground.osgb')
    
    joy1 = Joystick(viz.MainWindow)
    