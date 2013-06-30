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
    def __init__ (self, win, PlayViewObj=None, device='RUMBLEPAD'):
        self.joystick = vizjoy.add()
        self.view = win.getView()
        self.window = win
        self.toolActive = 0
        self.moveCursor = False 
        self.filter = LowPassDynamicFilter(0.5, 5, 10.0, 200.0)
        self.player = PlayViewObj
        #Call super class constructor to create different callbacks for every joystick
        viz.EventClass.__init__(self)
        self.callback(vizjoy.BUTTONDOWN_EVENT, self.joydown)
        self.callback(vizjoy.BUTTONUP_EVENT, self.joyup)
        self.callback(vizjoy.HAT_EVENT, self.joyhat)
        #decide the button actions based on the joystick
        self._updateFunc = vizact.onupdate(0, self.UpdateJoystick)
        if 'Rumblepad' in self.joystick.getName():
            self.device = 'RUMBLEPAD'
            self.actions = {'prev':[1,5], 'next':[3,6], 'pick':[2, 7, 8, 11, 12], 'drop':4, 'hud':9}
        elif 'Xbox' in self.joystick.getName():
            self.device = 'XBOX'
            self.actions = {'prev':[3], 'next':[2], 'pick':[1, 9, 10, 5, 6], 'drop':4, 'hud':7}
            self.triggerActive = True   #False after trigger buttons are pressed
            #Create a callback to handle the expiring trigger (de)activation events
            self.callback(viz.TIMER_EVENT, self.timerExpire)
        else:
            self.device = 'XBOX'
            print "UNIDENTIFIED JOYSTICK"
        
    def UpdateJoystick(self):
        #Get the joystick position
        x,y,z = self.joystick.getPosition()
        rx,ry,rz = self.joystick.getRotation()
        twist = {'RUMBLEPAD': rz, 'XBOX': ry}[self.device]
        # twist = self.joystick.getTwist()
        # slider = self.joystick.getSlider()
        
        #Move the viewpoint forward/backward based on y-axis value
        if abs(y) > 0.2:
            self.view.move([0,0,MOVE_SPEED * -y], viz.BODY_ORI)
            #self.view.move([0,0,viz.elapsed() * MOVE_SPEED * -y], viz.BODY_ORI)

        #Move the viewpoint left/right based on x-axis value
        if abs(x) > 0.2:
            self.view.setEuler([TURN_SPEED * x,0,0], viz.BODY_ORI,viz.REL_PARENT)
            #self.view.setEuler([viz.elapsed() * TURN_SPEED * x,0,0], viz.BODY_ORI,viz.REL_PARENT)
        
        #Yaw the head left and right based on rx-axis value
#        if abs(rx) > 0.2:
#            self.view.setEuler([TURN_SPEED * rx,0,0], viz.BODY_ORI,viz.REL_PARENT)
#            #self.view.setEuler([viz.elapsed() * TURN_SPEED * rx,0,0], viz.BODY_ORI,viz.REL_PARENT)
        
        #Tilt the head up and down until 60 degrees
        if abs(twist) < .104 :
            twist = 0
        newTwist = self.filter.Apply(Vector3(0, twist, 0), FPS)
        #if abs(twist) > 0.05: #Make sure value is above a certain threshold
        self.view.setEuler([0,newTwist.y*60,0],viz.HEAD_ORI,viz.ABS_PARENT)
        #Move the cursor towards the direction of the cross buttons (hat)        
        self.MoveCursor()
        #Check if the Xbox analog trigger was pressed and change the tool accordingly
        if self.device == 'XBOX':
            self.CheckTrigger()
        
    def UpdateJoystickRev(self):
        #Get the joystick position
        x,y,z = self.joystick.getPosition()
        rx,ry,rz = self.joystick.getRotation()
        twist = {'RUMBLEPAD': z, 'XBOX': y}[self.device]
        # twist = self.joystick.getTwist()
        
        #Move the viewpoint forward/backward based on y-axis value
        if abs(ry) > 0.2:
            self.view.move([0,0,MOVE_SPEED * -ry], viz.BODY_ORI)
            #self.view.move([0,0,viz.elapsed() * MOVE_SPEED * -ry], viz.BODY_ORI)

        #Move the viewpoint left/right based on x-axis value
        if abs(rx) > 0.2:
            self.view.setEuler([TURN_SPEED * rx,0,0], viz.BODY_ORI,viz.REL_PARENT)
            #self.view.setEuler([viz.elapsed() * TURN_SPEED * rx,0,0], viz.BODY_ORI,viz.REL_PARENT)

        #Tilt the head up and down until 45 degrees
        if abs(twist) < .15 :
            twist = 0
        newTwist = self.filter.Apply(Vector3(0, twist, 0), FPS)
        #if abs(twist) > 0.05: #Make sure value is above a certain threshold
        self.view.setEuler([0,newTwist.y*60,0],viz.HEAD_ORI,viz.ABS_PARENT)
        #Move the cursor towards the direction of the cross buttons (hat)        
        self.MoveCursor()
        
    def MoveCursor (self):
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
    
    def CheckTrigger(self):
        if self.joystick.getSlider() < -.25 and self.triggerActive:
            self.triggerActive = False
            self.starttimer(1, .25, 0)
            self.SelectTool(1)
            return
        if self.joystick.getSlider() > .25 and self.triggerActive:
            self.triggerActive = False
            self.starttimer(-1, .25, 0)
            self.SelectTool(-1)
            
    def timerExpire (self, num):
        self.killtimer(num)
        self.triggerActive = True
        
    def joydown(self, e):
        if e.joy != self.joystick:
            return
        try:
            print e.button
            len(self.player._toolbox) > 0
            if e.button in self.actions['prev']:
                self.SelectTool(-1)
            if e.button in self.actions['next']:
                self.SelectTool(1)
            if e.button in self.actions['pick']:
                picked = self.player.PickObject(True)
                if isinstance(picked, str): #if tool name returned
                    self.SelectTool(picked)
            if e.button == self.actions['drop']:
                self.player.DropObject()
            if e.button == self.actions['hud']:
                self.player.HideShowHUD()
        except AttributeError:
            pass
        #print e.button

    def joyup(self, e):
        if e.joy != self.joystick:
            return
        try:
            if e.button in self.actions['pick']:
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
    
    #gets a link of the held tool to the center of the viewpoint
    def SelectTool(self, prevNextTool): #prevNextTool=1,-1 or tool name
        self.player.SelectTool(prevNextTool)
        toolLink = self.player.HoldObject()
        if toolLink != False:
            self.toolActive = toolLink
                    
if __name__ == '__main__':

    viz.setMultiSample(2)
    viz.go()

    ground = viz.addChild('ground.osgb')
    
    joy1 = Joystick(viz.MainWindow)
    