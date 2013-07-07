import viz
import vizact
from collections import OrderedDict
from operator import itemgetter
from weakref import WeakValueDictionary
import sys
import vizmat
import vizinfo
import viztask
import vizdlg
import vizproximity
import textwrap
import fnmatch
import FSM_Actions
from LogParser import sgetGameLoadingTime

GRABDIST = 2	# The threashold for grabbing/interacting with items

class PlayerView(FSM_Actions.FSM_Actions):
	"""This is the class for making a new view"""
	
	PLAYERS = WeakValueDictionary()	#holds all player instances (used by FSM_Actions)
	SOUNDS = {'score1':viz.addAudio('sounds/score1.wav'), 'score0':viz.addAudio('sounds/score0.wav'),
			  'alert':viz.addAudio('sounds/alert.wav')}
	
	def __init__(self, view=None, win=None, winPos=[], player=None, fact=None, data=None, sm=None, fmap=None):
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
		#check if this is a player window
		if player in [1,2,3]:
			self.PLAYERS[player] = self	#list of all player instances (used by FSM_Actions)
			self._name = data['name']
			self._view.setPosition(data['pos'])
			self._view.stepSize(0.1)
			self._view.collisionBuffer(0.25)
			self._view.getHeadLight().disable()
			self._window.clearcolor(viz.SKYBLUE)
			self.AddPanel()
			#reset other variables
			self._toolbox = OrderedDict()
			self._selected = None	#object name being currently held/selected
			self._holding = None	#object being currently held/selected
			self._picking = None	#object name being intersected by cursor
			self._iMach = None		#machine interacting with (one of its components)
			self._nearMachine = None#machine being near to (based on proximity)
			self._updateAlerts = []	#a list of tuples (machine, error) for checking the alert update
			self._factory = fact	#factory object
			self.AddToToolbox('hand')
			self._fsm = sm			#FSM with all machine states
			self._mapWin = fmap		#the map (storing all alerts and messages)
			self._pressed = False	#True is player presses a button
			self._pickcolor = viz.GREEN
			self._feedback = None	#feedback message as result of interaction (not in FSM)
			self._iLog = []			#for logging picked and dropped tools from inventory
			self._proxLog = []		#for logging proximity to machines (enter, exit)
			self._pLog = []			#for logging position data
			self._collabAction = ''	#stores the collab action in 1P mode
			self.LoadToolTips()
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
		
	
	#######################################
	### RECEIVED FROM PROXIMITY SENSORS ###
		
	def ChangeStepSize(self, step):
		self._view.stepSize(step)

	def ApproachMachine(self, machine):
#		print "Player", self._name.getMessage(), "approached", machine
		self._nearMachine = machine
		self.LogProximity(machine, 1)
		if self._mapWin._messages.has_key(machine):
			mes = self._mapWin._messages[machine]
			self.DisplayAlert(mes)
			if not self._alertPanel.getPanelVisible():
				self._alertPanel.setPanelVisible(1)
		
	def LeaveMachine(self, machine):
#		print "Player", self._name.getMessage(), "left", machine
		self._nearMachine = None
		self.LogProximity(machine, 0)
		if self._mapWin._alerts.has_key(machine):
			self._alertPanel.setIconTexture(self._alertIcons['a'])
			self._alertPanel.setPanelVisible(0)
	
	def CheckForAlertNearMachine(self, *args):
		#stores the machine and error code to check in the next simulation step (frame)
		#this makes sure that the map messages are updated by the DisplayGlobalMessages function first...
		if len(args) > 1:
			self._updateAlerts.append(args)	#args =(machine, error)
			return
		#...before updating the messages and alert icons with the following code (executed by Update)
		#the index of the alert from the _updateAlerts list is passed as an argument
		ind = args[0]
		machine, error = self._updateAlerts[ind][0], self._updateAlerts[ind][1]
		if machine == self._nearMachine:
			if error > 0:	#a new error appeared so update alert panel
				mes = self._mapWin._messages[machine]
				self.DisplayAlert(mes)
			else:	#an error ceized so reset the icon of the alert panel
				self._alertPanel.setIconTexture(self._alertIcons['a'])
			#show or hide the alert panel
			self._alertPanel.setPanelVisible(error)	
		
	###############################
	### ONLY FOR THE MAP WINDOW ###
	
	def AddMap (self):
		self.flmap=viz.add('models/floor_map.IVE')
		self.flmap.texture(viz.addTexture('textures/map_view.png'),'',0)
		self.flmap.setPosition(0, .01, 0)
		#self.flmap.setScale(1, 1, 1.1)
		self.flmap.renderOnlyToWindows([self._window])
		self.bg = viz.addTexQuad(parent=viz.ORTHO, scene=self._window)
		self.CreateInfoPanels()
		self.CreateScorePanel()
		
	def CreateInfoPanels (self):
		#add the alert messages panel
		self._alertPanel = vizinfo.InfoPanel('Factory Alerts', window=self._window, align=viz.ALIGN_LEFT_BOTTOM)
		self._alertPanel.getPanel().fontSize(14)
		self._alertPanel.getPanel().setCellPadding(5)
		self._alertPanel.getPanel().setMargin(1)
		self._alertIcons = {'a': viz.add('textures/alert_icon.png'), 'w': viz.add('textures/danger_icon.png')}
		self._alertPanel.setIconTexture(self._alertIcons['a'])
		self._alertThemes = {'a': viz.getTheme(), 'w': viz.getTheme()}
		self._alertThemes['a'].borderColor = (.5,0.5,0,1)
		self._alertThemes['w'].borderColor = (.5,0,0,1)
		self._alertPanel.setPanelVisible(0)
		#add the info messages panel
		self._infoPanel = vizinfo.InfoPanel('Welcome to the Olive Oil Production Factory', window=self._window, align=viz.ALIGN_LEFT_TOP)
		self._infoPanel.getPanel().fontSize(14)
		self._infoPanel.getPanel().setCellPadding(5)
		self._infoPanel.getPanel().setMargin(1)
		self._infoPanel.setIconTexture(viz.add('textures/info_icon.png'))
		self._infoTheme = viz.getTheme()
		self._infoTheme.borderColor = (0,0,.5,1)
		self._infoPanel.getPanel().setTheme(self._infoTheme)
		self._infoTimer = vizact.ontimer2(10, 1, self.ShowInfoPanel, False)

	def CreateScorePanel(self):
		self._newScore = None	#holds the temp score after each update
		self._scorePanel = vizdlg.GridPanel(window=self._window, skin=vizdlg.ModernSkin, 
					spacing=-10, align=vizdlg.ALIGN_RIGHT_TOP, margin=0)
		row1text = viz.addText('Points')
		row1text.font("Segoe UI")
		self._scoreIcon = viz.addTexQuad(size=25, texture=viz.add('textures/star_yellow_256.png'))
		self._score= viz.addText('000')
		self._score.font("Segoe UI")
		self._score.alignment(viz.ALIGN_RIGHT_BASE)
		self._scorePanel.addRow([self._scoreIcon, row1text, self._score])
		row2text = viz.addText('Olive Oil (lbs)   ')
		row2text.font("Segoe UI")
		self._oilIcon = viz.addTexQuad(size=25, texture=viz.add('textures/oil_icon.png'))
		self._oil= viz.addText('000')
		self._oil.font("Segoe UI")
		self._oil.alignment(viz.ALIGN_RIGHT_BASE)
		self._scorePanel.addRow([self._oilIcon, row2text, self._oil])
		self._scorePanel.setCellAlignment(vizdlg.ALIGN_RIGHT_TOP)
		#place the score board at the top right corner of the window
		viz.link(self._window.RightTop, self._scorePanel, offset=(-10,-45,0))
		
	def ShowTotalScore (self):
		#add third row with the total score if not added already
		try:
			self._total.alignment(viz.ALIGN_RIGHT_BASE)
		except:
			row3text = viz.addText('Total points')
			row3text.font("Segoe UI")
			row3icon = viz.addTexQuad(size=25, texture=viz.add('textures/total_icon.png'))
			self._total= viz.addText('000')
			self._total.font("Segoe UI")
			self._total.alignment(viz.ALIGN_RIGHT_BASE)
			self._scorePanel.addRow([row3icon, row3text, self._total])
		
	def IncreaseOilTotal (self, dur, amount):
		score = int(self._score.getMessage())
		oil = int(self._oil.getMessage())
		total = int(self._total.getMessage())
		oilCounter = vizact.mix(oil, oil+amount, time=dur)
		totalCounter = vizact.mix(total, total+score*amount, time=dur)
		self._total.addAction(vizact.call(self.CounterIncrease, self._total, totalCounter))
		self._oil.addAction(vizact.call(self.CounterIncrease, self._oil, oilCounter))
	
	def CounterIncrease (self, counter, val):
		counter.message(str(int(val)))
		
	def UpdateScore(self, points):
		curScore = int(self._score.getMessage())
		if self._newScore == None:	#this ensures correct update of the score
			self._newScore = curScore + points
		else:
			self._newScore += points
		self.SOUNDS['score'+str(int(points>0))].play()
		resize = vizact.sizeTo([1.5-(points<0),1.5-(points<0),0], time=.25)	#resizes to .5 if deducting points
		color = [viz.RED, viz.GREEN][points>0]
		fade = vizact.fadeTo(color, time=.25)
		self._scoreIcon.addAction(vizact.parallel(resize, fade))
		waitAnim = vizact.signal()
		self._scoreIcon.addAction(waitAnim.trigger)
		self._score.addAction(waitAnim.wait)
		self._score.addAction(vizact.method.message(str(self._newScore)))
		self._score.addAction(vizact.call(self.resetNewScore))
		resize = vizact.sizeTo([1,1,0], time=.25)
		fade = vizact.fadeTo(viz.YELLOW, time=.25)
		self._scoreIcon.addAction(vizact.parallel(resize, fade))
	
	def resetNewScore (self):
		self._newScore = None
	
	def GameFinish (self, delay):
		self.info = vizinfo.add('Congratulations!')
		self.info.visible(0)
		self.info.icon(viz.add('textures/c-olive_icon.png'))
		self.info.add(viz.TEXT3D, 'You have finished the game \nproducing %s lbs of olive oil. \n' % self._oil.getMessage())
		self.info.add(viz.TEXT3D, 'Your team statistics are:')
		self.info.translate(0.1,0.95)
		self.info.alignment(vizinfo.UPPER_LEFT)
		self.info.scale(2.4,2.6)
		self.info.messagecolor(100,100,0)
		self.info.bgcolor(viz.BLACK, 0.8)
		self.info.bordercolor([100,100,0], .9)
		points = self.info.add(viz.TEXQUAD, 'Total points: %s' % self._total.getMessage())
		points.texture(viz.add('textures/total_icon.png'))
		time = self.info.add(viz.TEXQUAD, 'Time taken: %s' % self.ConvertTime(viz.tick()))
		time.texture(viz.add('textures/time_icon.png'))
		self.info.shrink()
		#hide all other panels
		self._scorePanel.visible(0)
		self._infoPanel.visible(0)
		self._alertPanel.visible(0)
		for p in self.PLAYERS.values():
			p._infoPanel.visible(0)
			p._alertPanel.visible(0)
			p._hud.visible(0)
		time.addAction(vizact.waittime(delay))
		time.addAction(vizact.call(self.info.visible, 1))
		time.addAction(vizact.waittime(.5))
		time.addAction(vizact.call(self.info.expand))
	
	def ConvertTime(self, time):
		time = round(time, 2)
		mins = int(time/60)
		secs = int(time%60)
		return str(mins)+'\''+str(secs)+'\'\''
		
	def ShowInfoPanel(self, flag, map=False):
		self._infoPanel.setPanelVisible(flag)
		self._infoTimer.setEnabled(0)
		if flag:
			#show alert panel for 10 secs and then dismiss it
			self._infoTimer = vizact.ontimer2(10, 1, self.ShowInfoPanel, False)
			try:	#this runs only for players having a _mapWin property
				self._infoPanel.setText(self._mapWin._infoPanel.getText())
			except:
				pass
		#RUNS ONLY FROM MAP: update the info panels of the remaining players
		if map:
			for p in self.PLAYERS.values():
				p.ShowInfoPanel(flag)
		
	def ShowErrorOnMap(self, machine, mPos, flag):
		if flag == 0:	#remove error if there is one for this machine
			if self._alerts.has_key(machine):
				self._alerts[machine].remove()
				del self._alerts[machine]
				del self._messages[machine]
		else:	#add or update the alert icon in every other case
			#aPos = self._window.worldToScreen(mPos)
			#newAlert = viz.addTexQuad(parent=viz.ORTHO, scene=self._window, size=50, pos=aPos)
			#add new alert if there is NOT one already for this machine
			alertSymbols = {1:'a', 2:'w'}
			if not self._alerts.has_key(machine):
				self.SOUNDS['alert'].play()
				newAlert = viz.addTexQuad(size=1.25)
				newAlert.texture(self._alertIcons[alertSymbols[flag]])
				newAlert.renderOnlyToWindows([self._window])
				newAlert.setPosition(mPos[0], 0, mPos[2])
				newAlert.setEuler(0, 90, 0)
				self._alerts[machine] = newAlert
			else:	#update the machine error if an alert if already defined
				self._alerts[machine].texture(self._alertIcons[alertSymbols[flag]])
		#show or hide the alert panel depending on the current alerts
		self._alertPanel.setPanelVisible(len(self._alerts)>0)
		if len(self._alerts) == 0:
			self._alertPanel.setIconTexture(self._alertIcons['a'])
		
	def AddAvatars (self):
		self.avatars = []
		for p in range(3):
			sphere = vizshape.addSphere(.65,10,10)
			self.avatars.append(sphere)
	
	def UpdateAlerts (self, mes):
		# update the icon on the map and the message queue
		try:
			text = mes.split('/')[2]
			# parse message for different types (i-> info, a->alert)
			if mes.split('/')[0] == 'i' > 1:	#this is the info (not added to _messages)
				mach = 'info'
				self._infoPanel.setText(text)
				self.ShowInfoPanel(True, map=True)
			else: 	#this is the alert or warning (added to _messages)
				atype= mes.split('/')[0]
				mach = mes.split('/')[1]
				self._messages[mach] = atype+'^'+text
				self.DisplayAlert(text)
			# print "MESSAGES", self._messages
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
			# this is void since the info message is not stored in the _messages anymore
			if self._cycler == 'info' and len(self._messages) > 1:
				del self._messages['info']
			ind = items.index(self._cycler)
			ind += 1
			if ind > len(items)-1:
				self._cycler = items[0]
			else:
				self._cycler = items[ind]
			#print "[TRY] Cycler returned from GetMessage:", self._cycler	
		except:
			self._cycler = items[len(items)-1]
			#print "[EXCEPT] Cycler returned from GetMessage:", self._cycler
		return self._cycler
		
	def CycleAlertsTask (self):
		self._cycler = None		#the next item in the list to display (starts with last)
		fade_out = vizact.fadeTo(0, 1, time=0.5, interpolate=vizact.easeOutStrong)
		fade_in = vizact.fadeTo(1, 0, time=0.5, interpolate=vizact.easeOutStrong)
		#set all alerts on map to 100% opaque so that they don't stay semi-transparent
		for i in [a for m, a in self._alerts.iteritems() if m != 'info']:
			a.alpha(1)
		while True:
			data = yield viztask.waitDirector(self.GetNextMessage)
			nextKey = data.returnValue
			if nextKey == 'info':	#not verified anymore because info not in _messages
				self._infoPanel.setText(self._messages[nextKey])
			else:
				self.DisplayAlert(self._messages[nextKey])
			if nextKey != 'info':
				alertObj = self._alerts[nextKey]
				yield viztask.addAction(alertObj, fade_out)
				yield viztask.addAction(alertObj, fade_in)
				yield viztask.addAction(alertObj, fade_out)
				yield viztask.addAction(alertObj, fade_in)
				yield viztask.addAction(alertObj, fade_out)
				yield viztask.addAction(alertObj, fade_in)
				yield viztask.addAction(alertObj, fade_out)
				yield viztask.addAction(alertObj, fade_in)
			else:
				yield viztask.waitTime(5)
	
	def DisplayAlert (self, tex):
		typ = tex.split('^')[0]
		tex = tex.split('^')[1]
		self._alertPanel.setIconTexture(self._alertIcons[typ])
		self._alertPanel.getPanel().setTheme(self._alertThemes[typ])
		self._alertPanel.setText(tex)
		
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
		#add the user feedback message
		self._message = viz.addText('', viz.ORTHO, self._window)
		self._message.alignment(viz.ALIGN_LEFT_TOP)
		self._message.font("Segoe UI")
		self._message.color(viz.BLACK)
		self._message.fontSize(13)
		self._message.resolution(.5)
		self._message.setScale(1.5,.75,1)
		self._message.setPosition(-80,32,0)
		self._message.setParent(self._hud)
		#add the collab icon
		self._collabTextures = [viz.add('textures/collab0.png'), viz.add('textures/collab1.png')]
		self._collabIcon = viz.addTexQuad(parent=viz.ORTHO, scene=self._window, size=150)
		self._collabIcon.texture(self._collabTextures[0])
		self._collabIcon.setParent(self._hud)
		self._collabIcon.drawOrder(20)
		self._collabIcon.setPosition(0, -65, 10)
		self._collabIcon.setScale(1,.4,1)
		self._collabIcon.alpha(0)
		self.ResizePanel()
		#add the info panels
		self.CreateInfoPanels()
		
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
		self.LogPosition()
		if self._window.getSize(viz.WINDOW_ORTHO) <> self._size:
			self._size = self._window.getSize(viz.WINDOW_ORTHO)
			if self._player in [1,2,3]:
				self.ResizePanel()
		# Check if the cursor intersects with an object
		if isinstance(self._player, int):
			self.CheckPickObject()
		# Check if the player should check for updated alerts according to proximity to machinery
		if len(self._updateAlerts) > 0:
			for a, c in reversed(list(enumerate(self._updateAlerts))):
				self.CheckForAlertNearMachine(a)
				del self._updateAlerts[a]
	
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
			if getattr(toolObj, 'pick_parent', False):
				toolObj = toolObj.getParents()[0]
#			print "TOOL interecting: ", toolObj
			# RULE: ALL OBJECTS RESPOND TO HELD ITEMS; tools turn red, components turn green (1P) or orange(2-3P)
			if self._selected == 'hand':				
				#print "Obj colliding", toolObj
				if toolObj in self._factory.tools.values() and self.WithinReach(toolObj):
					self._picking = toolObj
					self._picking.color(viz.RED, op=viz.OP_OVERRIDE)
				elif toolObj in self._factory.components.values() and self.WithinReach(toolObj, True, 2):
					self._picking = toolObj
					self._picking.color(self._pickcolor, op=viz.OP_OVERRIDE)
				else:
					self.ResetPick()
			elif self._selected != None:
				# check if the picked object is a factory component and light it green if it is
				if toolObj in self._factory.components.values() and self.WithinReach(toolObj, True, 2.5):
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
		if len(self._toolbox) < 4:
			if tool == 'mat' and 'mat' in self._toolbox:
				self._feedback = 'oneOnly'
				return False
			obj = viz.addTexQuad(parent=viz.ORTHO, scene=self._window, size=75)
			obj.setParent(self._hud)
			obj.setPosition(-60+len(self._toolbox)*45, 60, 0)
			obj.setScale(1,.4,1)
			tool = self._factory.FilterAddedTool(tool)	# adds 'ful' for 'can' if full
			textur = viz.addTexture('textures/tool_'+tool+'.png', useCache=True)
			textur_sel = viz.addTexture('textures/tool_'+tool+'_sel.png', useCache=True)
			obj.texture(textur)
			self._toolbox[tool] = {'obj': obj, 'tex': textur, 'sel': textur_sel}
			return True
		else:
			self._feedback = 'inventory'
			self.DisplayLocalMessage('inventory')
		
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
	def SelectTool(self, prevNext):	#-1 for previous, 1 for next, or tool name
		self.ResetPick()
		if isinstance(prevNext, str):	#this is a tool name, so select it in the toolbox
			self.ZoomIcon(prevNext, 1)
			return
		if self._selected == None:
			if prevNext == 1:
				self.ZoomIcon('hand', 1)
			else:
				lastTool = next(reversed(self._toolbox))
				self.ZoomIcon(lastTool, 1)
		else:
			if len(self._toolbox) >= 1 :
				toolNo = self._toolbox.keys().index(self._selected)
				if toolNo + prevNext > len(self._toolbox) - 1:
#					self.ZoomIcon('hand', 1)	#recursive tool selection
					self.ZoomIcon(None, 1)		#deselect last tool
				elif toolNo + prevNext < 0:
					self.ZoomIcon(None, 1)		#deselect first tool
#					self.ZoomIcon(self._toolbox.keys()[len(self._toolbox)-1], 1)	#recursive tool selection
				else:
					self.ZoomIcon(self._toolbox.keys()[toolNo + prevNext], 1)
	
	def ZoomIcon (self, icon, inOut=0):	# 1 for in, 0 for out
		if inOut:
			if self._selected != None:	#zoom out the previously selected icon
				self.ZoomIcon(self._selected, 0)
			self._selected = icon
			if self._selected != None:
				self._toolbox[icon]['obj'].setScale(1.1,.45,1)
				self._toolbox[icon]['obj'].texture(self._toolbox[icon]['sel'])
		else:
			self._toolbox[icon]['obj'].setScale(1,.4,1)
			self._toolbox[icon]['obj'].texture(self._toolbox[icon]['tex'])
			
	def HoldObject(self, obj=None):
		if obj == None:
			obj = self._selected
		self.LetObject()
		if self._selected == None:	#No object selected (at the end of the list)
			return False
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
#		if not press:	#don't run this script because release should also run evaluate_multi_user
#			return
		try:
			if self._picking != None:
				#check if the user is interacting with a tool or machine component
				if self._picking in self._factory.tools.values():
					# get the tool name (key) from the object to be picked (value) from the tools list (dict)
					tool = [key for key, value in self._factory.tools.iteritems() if value == self._picking][0]
					if self.AddToToolbox(tool):
						self.LogInventory(tool, 1)
						self.RemoveFromWorld()
						return tool	#return tool name to enable immediate tool holding
						
				elif self._picking in self._factory.components.values():
					# get the component name from the object to be picked from the factory components list
					held = self._selected
					comp = [key for key, value in self._factory.components.iteritems() if value == self._picking][0]
					pressOrRelease = {True:'Interacting with', False:'Releasing'}[press]
					print "%s %s on %s" %(pressOrRelease, held, comp)
					self._iMach = self._factory.componentPar[comp]
					(mActions, mMessage, mCollab) = self._fsm[self._iMach].evaluate_multi_input(held+'_'+comp+self._collabAction, self, self._pressed)
					self.BroadcastActionsMessages(mActions, mMessage, (held, comp), mCollab)
					#sys.exit()	#still goes to except after executing else(?)
		except AttributeError:
			pass #print "No object under cursor!"
		else:
			pass

	def DropObject (self, putBack=True, matOnTray=False):
		if self._holding != None:
			if self._selected == 'hand':
				print "Cannot drop my hand!"
				return
			elif self._selected == 'mat' and not matOnTray:
				self._feedback = 'noDrop'
				return
			toolToDrop = self._selected
			self.LogInventory(toolToDrop, 0)
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
		self._factory.AddTool(dropped)
		
	########################################################
	## SENDING ACTIONS AND MESSAGES TO FSM_ACTIONS MODULE ##
	
	def BroadcastActionsMessages (self, acts, mess, interact=None, collab=False): #interact is tuple (tool, comp)
		#execute action sequence (subclass function)	
		self.execute_actions(acts)
		if collab:
			self.DisplayCollabBonus()
		#this executes when no messages exist and interaction excludes hand_mat picked
		#because there is a mat pick check with delay (0.1sec) for action 'picking_mat'
		if mess == [] and interact != None and self._feedback != 'picked':
			#_feedback is updated by the actions in the previous function call
			self.DisplayLocalMessage(self._feedback, interact)
		self._feedback = None
		alertsUpdated = False	#ensures alerts are updated in every case
		#check if the message is a local (user-only) or global message (all users)
		for m in mess:
			if m == None:
				continue
			if m.rpartition('/')[1] == '':		#if there is no slash in the message
				self.DisplayLocalMessage(m)		#display message on player's window
			else:
				alertsUpdated = True
				self.DisplayGlobalMessage(m)	#display message on map  (subclass function)
		#update the alerts cycling in case there is error0 and have not been updated before
		if not alertsUpdated and len(fnmatch.filter(acts, 'error0*'))>0:
			self.DisplayGlobalMessage('')
		
	def DisplayGlobalMessage (self, mes):
		self._mapWin.UpdateAlerts(mes)
		
	def DisplayLocalMessage(self, mes, toolComp=None):
		try:	#deactivate the previously enabled timer
			self._localTimer.setEnabled(False)
		except:
			pass
		if mes == None:	#no feedback defined for this action
			if toolComp[0] == 'hand':
				mes = self.tooltips['hand_use'] % self.tooltips[toolComp[1]]
			else:
				mes = self.tooltips['tool_use'] % (self.tooltips[toolComp[0]], self.tooltips[toolComp[1]])
		elif len(mes.split(' ')) == 1:	#if only one word is passed
			mes = self.tooltips[mes]
		
		mes = '\n'.join(textwrap.wrap(mes, 18))
		self._message.message(mes)
		self._localTimer = vizact.ontimer2(10, 1, self.DismissMessage)
		
	def DismissMessage (self):
		self._message.message('')
	
	def DisplayCollabBonus (self):
		self._collabIcon.endAction()
		self._collabIcon.alpha(1)
		self._collabIcon.texture(self._collabTextures[1])
		self._collabIcon.addAction(vizact.fadeTo(0, begin=1, time=3, interpolate=vizact.easeInCubic))
		
	def EnablePlayer1ForMultiInput (self, secInput):
		if self._player == 1 and len(self.PLAYERS) == 1 and self._collabAction == '':
			self._collabAction = ', '+secInput	#add second action for 1P conditions
			self._collabIcon.texture(self._collabTextures[0])
			self._collabIcon.addAction(vizact.fadeTo(0, begin=1, time=5, interpolate=vizact.easeInCircular))
			self._collabTimer = vizact.ontimer2(5, 1, self.DisablePlayer1ForMultiInput)
			print "PLAYER1: Preparing to execute multi-input action!"
			
	def DisablePlayer1ForMultiInput (self):
		self._collabAction = ''
	
	def LoadToolTips (self):	#load tool explanations from an external file
		import xlrd	#load the library for reading Excel files
		self.tooltips = {}
		workbook = xlrd.open_workbook('OLiVE_StateMachine.xlsx')
		#Get the first sheet in the workbook by name
		sheet1 = workbook.sheet_by_name('tools')
		for rowNumber in range(sheet1.nrows):
			rowData = sheet1.row_values(rowNumber)
			self.tooltips[rowData[0]] = rowData[1]
		#print self.tooltips
	
	###########################################
	### LOGGING USER ACTIONS IN THE FACTORY ###
	
	def LogInventory (self, tool, pickDrop):
		timeStamp = round(viz.tick()-sgetGameLoadingTime(False),2)
		self._iLog.append((timeStamp, self._player, tool, pickDrop))
		#pd = ['dropped', 'picked'][pickDrop]
		#print "Time %s: player %s %s the %s" % (round(viz.tick(),2), self._player, pd, tool)
		
	def LogProximity (self, mach, inOut):
		timeStamp = round(viz.tick()-sgetGameLoadingTime(False),2)
		self._proxLog.append((timeStamp, self._player, mach, inOut))
		
	def LogPosition (self):
		timeStamp = round(viz.tick()-sgetGameLoadingTime(False),2)
		#record player position every 1 second
		if viz.tick() % 1 <= viz.getFrameElapsed():
			self._pLog.append((timeStamp, self._view.getPosition()[0], self._view.getPosition()[2]))
		
if __name__ == '__main__':

	viz.setMultiSample(8)
	viz.go()
	
	ground = viz.addChild('ground.osgb')
	
	floorMap = PlayerView(winPos=[0.5,1])