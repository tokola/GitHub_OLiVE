import viz
import vizact
from collections import OrderedDict
from operator import itemgetter
import sys
import vizmat
import vizinfo
import viztask
import textwrap
import FSM_Actions

GRABDIST = 2	# The threashold for grabbing/interacting with items

class PlayerView(FSM_Actions.FSM_Actions):
	"""This is the class for making a new view"""
	def __init__(self, view=None, win=None, winPos=[], player=None, fact=None, name=None, sm=None, fmap=None):
		if view == None:
			view = viz.addView()
		self._view = view
		if win == None:
			win = viz.addWindow()
		self._window = win
		self._window.fov(60)
		self._window.setSize(.5,.5)
		self._window.setPosition(winPos)
		self._window.setView(self._view)
		self._size = self._window.getSize(viz.WINDOW_ORTHO)
		self._player = player
		self._name = name
		#check if this is a player window
		if player in [1,2,3]:
#			self._view.collision(viz.ON)
			self._view.stepSize(.35)
			self._view.collisionBuffer(0.25)
			self._view.getHeadLight().disable()
			self._window.clearcolor(viz.SKYBLUE)
			self.AddPanel()
			#reset other variables
			self._toolbox = OrderedDict()
			self._selected = None
			self._holding = None
			self._picking = None
			self._iMach = None		#machine interacting with (one of its components)
			self._factory = fact
			self.AddToToolbox('hand')
			self._fsm = sm
			self._mapWin = fmap
			self._pressed = False
			self._pickcolor = viz.GREEN
			#set an update function to take care of window resizing (priority=0)
			self._updateFunc = vizact.onupdate(0, self.Update)
			#FSM_Actions.FSM_Actions.__init__(self)
		else:	#this is the map view
			self._window.clearcolor([.3,.3,.3])
			self._window.ortho(-25,25,-15,20,-1,1)
			self._view.setPosition(-3.8,0,0)
			self._view.setEuler(0,90,0)
			self._alerts = {}
			self._messages = OrderedDict()
			self.AddMap()
		
	
	###############################
	### ONLY FOR THE MAP WINDOW ###
	
	def AddMap (self):
		self.flmap=viz.add('models/floor_map.IVE')
		self.flmap.texture(viz.addTexture('textures/map_view.png'),'',0)
		self.flmap.setPosition(0, .5, 0)
		#self.flmap.setScale(1, 1, 1.1)
		self.flmap.renderOnlyToWindows([self._window])
		self.bg = viz.addTexQuad(parent=viz.ORTHO, scene=self._window)
		#add the alert messages space
		self._alert = vizinfo.add( 'This example demonstrates the use of the vizinfo module.' )
		self._alert.icon(viz.add('textures/alert_icon.png'))
		self._alert.scale([1.1,1.2])
		self._alert.alignment(vizinfo.UPPER_LEFT)
		self._alert.translate( [.03, .1] )
		self._alertIcon = viz.add('textures/alert_icon.png')
		self._infoIcon = viz.add('textures/info_icon.png')

	def ShowErrorOnMap(self, machine, mPos, flag):
		if flag == 0:	#remove error if there is one for this machine
			if self._alerts.has_key(machine):
				self._alerts[machine].remove()
				del self._alerts[machine]
				del self._messages[machine]
		else:	#add new alert if there is NOT one already for this machine
			#aPos = self._window.worldToScreen(mPos)
			#newAlert = viz.addTexQuad(parent=viz.ORTHO, scene=self._window, size=50, pos=aPos)
			if not self._alerts.has_key(machine):
				newAlert = viz.addTexQuad(size=1.25)
				newAlert.texture(viz.addTexture('textures/alert_icon.png'))
				newAlert.renderOnlyToWindows([self._window])
				newAlert.setPosition(mPos[0], 0.5, mPos[2])
				newAlert.setEuler(0, 90, 0)
				self._alerts[machine] = newAlert
		
	def AddAvatars (self):
		self.avatars = []
		for p in range(3):
			sphere = vizshape.addSphere(.65,10,10)
			self.avatars.append(sphere)
	
	def UpdateAlerts (self, mes):
		# update the icon on the map and the message queue
		try:
			# parse message for different types (i-> info, a->alert)
			if len(mes.split('i/')) > 1:	#this is the info
				mac = 'info'
			elif len(mes.split('a/')) > 1:	#this is the alert
				mac = mes.split('/')[1]

			mes = mes.split('/')[2]
			self._alert.message(mes)
			self._messages[mac] = mes
		except:
			pass
		
		try:
			self._scheduler.kill()
		except:
			pass
		
		if len(self._messages) > 0:
			self._scheduler = viztask.schedule(self.CycleAlertsTask())
	
	def GetNextMessage (self):
		items = self._messages.keys()
		try:
			# display the info only once if there are alerts in the queue
			if self._cycler == 'info' and len(self._messages) > 1:
				del self._messages['info']
			ind = items.index(self._cycler)
			ind += 1
			if ind > len(items)-1:
				self._cycler = items[0]
			else:
				self._cycler = items[ind]
		except:
			self._cycler = items[len(items)-1]
		
		return self._cycler
		
	def CycleAlertsTask (self):
		self._cycler = None		#the next item in the list to display (starts with last)
		fade_out = vizact.fadeTo(0, 1, time=0.5, interpolate=vizact.easeOutStrong)
		fade_in = vizact.fadeTo(1, 0, time=0.5, interpolate=vizact.easeOutStrong)
		for i in [a for m, a in self._alerts.iteritems() if m != 'info']:
			a.alpha(1)
		while True:
			data = yield viztask.waitDirector(self.GetNextMessage)
			nextKey = data.returnValue
			self._alert.message(self._messages[nextKey])
			if nextKey == 'info':
				self._alert.icon(self._infoIcon)
				self._alert.bgcolor(.3,.3,1,.4)
				self._alert.bordercolor(0,0,.5,1)
			else:
				self._alert.icon(self._alertIcon)
				self._alert.bgcolor(.3,.3,0,.4)
				self._alert.bordercolor(.5,0.5,0,1)
			if nextKey != 'info':
				alertObj = self._alerts[nextKey]
				yield viztask.addAction(alertObj, fade_out)
				yield viztask.addAction(alertObj, fade_in)
				yield viztask.addAction(alertObj, fade_out)
				yield viztask.addAction(alertObj, fade_in)
				yield viztask.addAction(alertObj, fade_out)
				yield viztask.addAction(alertObj, fade_in)
			else:
				yield viztask.waitTime(5)
			
	##############################
	### FOR THE PLAYER WINDOWS ###
	
	def AddPanel(self):
		self._hud = viz.addGroup(viz.ORTHO, scene=self._window)
		panel = viz.addTexQuad(parent=viz.ORTHO, scene=self._window, size=200)
		panel.texture(viz.addTexture('textures/panel.png', useCache = True))
		panel.setParent(self._hud)
		self.tag = viz.addTexQuad(parent=viz.ORTHO, scene=self._window, size=200)
		self.tag.texture(viz.addTexture('textures/p'+str(self._player)+'_tag.png', useCache = True))
		self.tag.setParent(self._hud)
		#add the player name as a child of the panel
		self._name = viz.addText(self._name, panel)
		self._name.alignment(viz.ALIGN_CENTER_TOP)
		self._name.font("Segoe UI")
		self._name.color(viz.BLACK)
		self._name.fontSize(14)
		self._name.resolution(.5)
		self._name.setScale(1.5,.75,1)
		self._name.setPosition(3,92,0)
		self._name.setParent(self._hud)
		#add the message
		self._message = viz.addText('', viz.ORTHO, self._window)
		self._message.alignment(viz.ALIGN_LEFT_TOP)
		self._message.font("Segoe UI")
		self._message.color(viz.BLACK)
		self._message.fontSize(13)
		self._message.resolution(.5)
		self._message.setScale(1.5,.75,1)
		self._message.setPosition(-80,32,0)
		self._message.setParent(self._hud)
		self.ResizePanel()
	
	def ResizePanel(self):
		winSize = self._size
		#calculate size of panel according to 200x450pix for 1440x900pix window
		ySize = winSize[1]
		xSize = winSize[1] * float(200)/450
		xScale = xSize/200
		yScale = ySize/450*2.25
		self._hud.setScale(xScale, yScale, 1)
		self._hud.setPosition(winSize[0]-200*xScale/2, winSize[1]-200*yScale/2)
		
	def Update(self):
		if self._window.getSize(viz.WINDOW_ORTHO) <> self._size:
			self._size = self._window.getSize(viz.WINDOW_ORTHO)
			if self._player in [1,2,3]:
				self.ResizePanel()
		# Check if the cursor intersect with an object
		if isinstance(self._player, int):
			self.CheckPickObject()
	
	def CheckPickObject(self):
		if self._holding != None:
			cursorPos = self._window.windowToDisplay(self._window.worldToScreen(self._holding.getPosition()))
			objList = self._window.pick(info=False, pos=cursorPos, all=True)
			# check there are at least 3 objects intersecting (at least the first 2 are the cursor object itself)
			if len(objList) < 3:
				return
			#get rid of the holding object and its children and keep the first one found
			objList = [i for i in objList if (i != self._holding) and (not i in self._holding.getChildren())]
			#check if the list is empty (picking outside of the world)
			if len(objList) == 0:
				return
			toolObj = objList[0]
#			print "TOOL interecting: ", toolObj
			# RULE: ALL OBJECTS RESPOND TO HELD ITEMS; tools turn red, components turn green (1P) or orange(2-3P)
			if self._selected == 'hand':				
				#print "Obj colliding", toolObj
				if toolObj in self._factory.tools.values() and self.WithinReach(toolObj):
					self._picking = toolObj
					self._picking.color(viz.RED, op=viz.OP_OVERRIDE)
				elif toolObj in self._factory.components.values() and self.WithinReach(toolObj, True, 2.5):
					self._picking = toolObj
					self._picking.color(self._pickcolor, op=viz.OP_OVERRIDE)
				else:
					self.ResetPick()
			elif self._selected != None:
				# check if the picked object is a factory component and light it green if it is
				if toolObj in self._factory.components.values() and self.WithinReach(toolObj, True, 3):
					self._picking = toolObj
					self._picking.color(self._pickcolor, op=viz.OP_OVERRIDE)
				else:
					self.ResetPick()
	
	def WithinReach(self, obj, machPart = False, dist = GRABDIST):
		# get the component position if it's a machine part
		if machPart:
			objPos = self._factory.componentPos[obj]
		else:
			objPos = obj.getPosition(viz.ABS_GLOBAL)
		# check if you are in grabbing distance from the object
		if vizmat.Distance(objPos, self._view.getPosition()) < dist:
			#print "Can be reached!"
			return True
	
	def ChangePickColor (self, play):
		if play == '1P': self._pickcolor = viz.GREEN
		elif play == '2P': self._pickcolor = viz.ORANGE
		elif play == '3P': self._pickcolor = viz.PURPLE
		
	def ResetPick (self):
		try: 
			self._picking.clearAttribute(viz.ATTR_COLOR, op=viz.OP_OVERRIDE)
			self._picking = None
			if self._iMach != None:	# remove player from FSM's input list
				self._fsm[self._iMach].evaluate_multi_input(None, self, False)	
		except AttributeError:
			None
		
	### SETTING THE TOOLBOX ###
	def AddToToolbox (self, tool):
		obj = viz.addTexQuad(parent=viz.ORTHO, scene=self._window, size=75)
		obj.setParent(self._hud)
		obj.setPosition(-60+len(self._toolbox)*45, 60, 0)
		obj.setScale(1,.4,1)
		tool = self._factory.FilterAddedTool(tool)	# adds 'ful' for 'can' if full
		textur = viz.addTexture('textures/tool_'+tool+'.png', useCache=True)
		textur_sel = viz.addTexture('textures/tool_'+tool+'_sel.png', useCache=True)
		obj.texture(textur)
		self._toolbox[tool] = {'obj': obj, 'tex': textur, 'sel': textur_sel}
		
	def RemoveFromToolbox (self, tool=None):
		if tool == None:
			tool = self._selected
		self._toolbox[tool]['obj'].remove()
		del self._toolbox[tool]
		self._selected = None
		self.UpdateToolBox()
		
	def UpdateToolBox(self):
		i = 0
		for t in self._toolbox.values():
			t['obj'].setPosition(-60+i*45, 60, 0)
			i += 1
	
	### CALLED FROM THE FSM_ACTIONS ###
	def _CanFull (self, flag):
		if 'can' in self._toolbox.keys():
			self._holding.getChild('pulp').visible(flag)
			self.RemoveFromToolbox('can')
			self.AddToToolbox('canful')
			self.ZoomIcon('canful', 1)
			self._factory.SetCanFull(True)
		elif 'canful' in self._toolbox.keys():
			self._holding.getChild('pulp').visible(flag)
			self._factory.SetCanFull(False)
			self.RemoveFromToolbox('canful')
			self.AddToToolbox('can')
			self.ZoomIcon('can', 1)
		
	### SENT FROM THE JOYSTICK CLASS ###
	def SelectItem(self, prevNext):	#-1 for previous, 1 for next
		self.ResetPick()
		if self._selected == None:
			self.ZoomIcon('hand', 1)
		else:
			if len(self._toolbox) > 1 :
				toolNo = self._toolbox.keys().index(self._selected)
				if toolNo + prevNext > len(self._toolbox) - 1:
					self.ZoomIcon('hand', 1)
				elif toolNo + prevNext < 0:
					self.ZoomIcon(self._toolbox.keys()[len(self._toolbox)-1], 1)
				else:
					self.ZoomIcon(self._toolbox.keys()[toolNo + prevNext], 1)
	
	def ZoomIcon (self, icon, inOut=0):	# 1 for in, 0 for out
		if inOut:
			if self._selected != None:	#zoom out the previously selected icon
				self.ZoomIcon(self._selected, 0)
			self._selected = icon
			self._toolbox[icon]['obj'].setScale(1.1,.45,1)
			self._toolbox[icon]['obj'].texture(self._toolbox[icon]['sel'])
		else:
			self._toolbox[icon]['obj'].setScale(1,.4,1)
			self._toolbox[icon]['obj'].texture(self._toolbox[icon]['tex'])
			
	def HoldObject(self, obj=None):
		if obj == None:
			obj = self._selected
		self.LetObject()
		obj = self._factory.FilterAddedObj(obj)	#filters out 'ful' for the can
		self._holding = viz.add('models/objects/tool_'+obj+'.ive')
		self._holding.setScale(.075,.075,.075)
		self._holding.disable(viz.INTERSECTION)
		self._holding.renderOnlyToWindows([self._window])
		self._link = viz.link(self._view, self._holding)
		self._link.preTrans([0,0,.2])
		if obj != 'hand':
			self._link.preEuler([0,-90,0], viz.LINK_ORI_OP)
			self._link.preEuler([-30,0,0], viz.LINK_ORI_OP)
		if obj == 'can':
			self._holding.getChild('pulp').visible(self._factory.GetCanFull())
		# return the held object as a link
		return self._link
			
	def LetObject(self):
		if self._holding != None:
			self._holding.remove()
			self._holding = None
			
	def PickObject(self, press):
		# set the pressed status of the user's trigger
		self._pressed = press
		try:
			if self._picking != None:
				# TODO: Make a list of actions and triggers
				if self._picking in self._factory.tools.values():
					# get the tool name (key) from the object to be picked (value) from the tools list (dict)
					tool = [key for key, value in self._factory.tools.iteritems() if value == self._picking][0]
					print "Picking...", self._picking
					self.AddToToolbox(tool)
					self.RemoveFromWorld()
				elif self._picking in self._factory.components.values():
					# get the component name from the object to be picked from the factory components list
					held = self._selected
					comp = [key for key, value in self._factory.components.iteritems() if value == self._picking][0]
					print "Interacting with %s on %s" %(held, comp)
					self._iMach = self._factory.componentPar[comp]
					(mActions, mMessage) = self._fsm[self._iMach].evaluate_multi_input(held+'_'+comp, self, self._pressed)
					self.BroadcastActionsMessages(mActions, mMessage)
					#sys.exit()	#still goes to except after executing else(?)
		except AttributeError:
			pass #print "No object under cursor!"
		else:
			pass

	def DropObject (self, putBack=True):
		if self._holding != None:
			if self._selected == 'hand':
				print "Cannot drop my hand!"
				return
			toolToDrop = self._selected
			print "Dropped " + toolToDrop
			self.LetObject()
			self.ResetPick()
			self.RemoveFromToolbox()
			if putBack:
				self.AddToWorld(toolToDrop)
		
	def HideShowHUD (self):
		self._hud.visible(viz.TOGGLE)
	
	####################################
	### COMMUNICATION WITH THE WORLD ###
	
	def RemoveFromWorld (self):
		self._picking.remove()
		
	def AddToWorld (self, dropped):
		print self._selected, dropped
		self._factory.AddTool(dropped)
		
	########################################################
	## SENDING ACTIONS AND MESSAGES TO FSM_ACTIONS MODULE ##
	
	def BroadcastActionsMessages (self, acts, mess):
		#execute action sequence (subclass function)	
		self.execute_actions(acts)	
		#check if the message is a local (user-only) or global message (all users)
		for m in mess:
			if m == None:
				continue
			if m.rpartition('/')[1] == '':
				self.DisplayLocalMessage(m)		#display message on player's window
			else:
				self.DisplayGlobalMessage(m)	#display message on map  (subclass function)
	
	def DisplayGlobalMessage (self, mes):
		self._mapWin.UpdateAlerts(mes)
		
	def DisplayLocalMessage(self, mes):
		mes = '\n'.join(textwrap.wrap(mes, 18))
		self._message.message(mes)
		
if __name__ == '__main__':

	viz.setMultiSample(8)
	viz.go()
	
	ground = viz.addChild('ground.osgb')
	
	floorMap = PlayerView(winPos=[0.5,1])