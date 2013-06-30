import sys
#avoid generating the .pyc files
sys.dont_write_bytecode = True

import viz
import vizact
import vizjoy
import vizproximity
from string import upper, lower
import Factory
import Interaction
import Window
import Avatar
import StateMachine
import LogParser

viz.go(viz.FULLSCREEN)

viz.phys.enable()
#viz.MainView.setPosition(-10,2,-5)
#viz.MainView.setEuler(-90,0,0)
#viz.fov(60)
#viz.collision(viz.ON)
#viz.clearcolor(viz.SKYBLUE)

#DEFINE VARIABLES
MACHINERY = {0: ('waterPipe'),
			 #1: ('boiler', 'engine', 'lavalR', 'millR', 'pressR', 'pumpR', 'loader', 'lavalL', 'millL', 'pumpL', 'pressL', 'oilPump', 'scale')}
			 1: ('millL', 'millR', 'lavalL', 'lavalR', 'scale')}
EYEHEIGHT = 1.75
DEVICE = 'XBOX'

studyMode = 1	#set True for experiment

##############################################
### MAKE THE INTERFACE AND DIFFERENT VIEWS ###
##############################################

gPlayers = {}		#dictionaty with player, joystick, and avatar classes
gPlayerData = {1: {'name': 'Player 1', 'colors': [[197, 106, 183], [97, 50, 83]], 'pos': [-15,EYEHEIGHT,0]},
               2: {'name': 'Player 2', 'colors': [[83, 171, 224], [36, 70, 90]], 'pos': [-10,EYEHEIGHT,0]},
               3: {'name': 'Player 3', 'colors': [[255, 189, 0], [135, 100, 0]], 'pos': [-5,EYEHEIGHT,0]}}
	
def splitViews ():
	global olivePress, floorMap, playerByView

	# set the four different views in seperate windows (3 players and the map)
	floorMap = Window.PlayerView(winPos=[0.5,1])
	p1 = Window.PlayerView(view=viz.MainView, win=viz.MainWindow, winPos=[0,1], player=1, data=gPlayerData[1], fact=olivePress, sm=FSM, fmap=floorMap)
	# assign the joystick to player 1
	j1 = Interaction.Joystick(p1._window, p1, DEVICE)
	# set the avatar for player 1
	a1 = Avatar.Avatar(p1._view, gPlayerData[1]['colors'], EYEHEIGHT)
	players = [[p1, j1, a1]]
	if condition > 0:	#if more the 3P condition was chosen (condition=1)
		p2 = Window.PlayerView(winPos=[0,.5], player=2, data=gPlayerData[2], fact=olivePress, sm=FSM, fmap=floorMap)
		j2 = Interaction.Joystick(p2._window, p2, DEVICE)
		a2 = Avatar.Avatar(p2._view, gPlayerData[2]['colors'], EYEHEIGHT)
		p3 = Window.PlayerView(winPos=[0.5,.5], player=3, data=gPlayerData[3], fact=olivePress, sm=FSM, fmap=floorMap)
		j3 = Interaction.Joystick(p3._window, p3, DEVICE)
		a3 = Avatar.Avatar(p3._view, gPlayerData[3]['colors'], EYEHEIGHT)
		players.append([p2, j2, a2])
		players.append([p3, j3, a3])
	# make a list of all the players and set the initial view positions
	playerByView = {}	#dictionary of players by view {view1: p1, view1:p2, view3:p3}
	for i,p in enumerate(players):
		playNum = i+1
		player, joy, avatar = p[0], p[1], p[2]
		gPlayers[playNum] = {'player': player, 'joy': joy, 'avatar': avatar}
		#hide avatars from their window and the map; render map avatar only on map
		avatar._avatar.renderToAllWindowsExcept([player._window, floorMap._window])
		avatar._mapAva.renderOnlyToWindows([floorMap._window])
		playerByView[player._view] = player
	olivePress.factory.renderToAllWindowsExcept([floorMap._window])
	
vizact.onkeydown('v', splitViews)

def checkCollabActivity ():
	pickingObjs = {}
	for p in gPlayers.values():
		player = p['player']
		if player._picking != None:
			pickingObjs[player] = player._picking
	if len(pickingObjs) < 1:
		return
	# get the players with the same picking objects
	objByPlayer = {}
	for pl, obj in pickingObjs.iteritems():
		objByPlayer.setdefault(obj, []).append(pl)
	# change the color according to how many interact with the same object
	for plrs in objByPlayer.values():
		if len(plrs) == 1:
			plrs[0].ChangePickColor('1P')
		else:
			for p in plrs:
				p.ChangePickColor(str(len(plrs))+'P')

vizact.onupdate(0, checkCollabActivity)

###################################
## TIMER FOR DISPLAYING THE TIME ##
###################################
def setTimer():
	global timerTicks, time
	if not isinstance(timerTicks, float):
		return
	ticks = int(viz.tick() - timerTicks)
	if ticks < 60:
		sec = ticks
		min = 0
	else:
		sec = ticks % 60
		min = ticks / 60
	if sec < 10:
		sec = '0'+str(sec)
	if min < 10:
		min = '0'+str(min) 
	time = str(min) + ':' + str(sec)
	#time.message(str(min) + ':' + str(sec))    

def startTimer():
    global timerTicks
    timerTicks = viz.tick()
    vizact.ontimer(0, setTimer)

vizact.onkeydown(viz.KEY_BACKSPACE, startTimer)

	
##############################
## STATES for STATE MACHINE ##
##############################

def loadMachFSM_Xl():
	import xlrd	#load the library for reading Excel files
	global FSM, STATES
	#load state machine from an external file
	FSM = {}
	STATES = {}
	workbook = xlrd.open_workbook('OLiVE_StateMachine.xlsx')
	#Get the first sheet in the workbook by index
	sheet1 = workbook.sheet_by_name('FSM'+str(trial))
	r = 0
	for rowNumber in range(sheet1.nrows):
		r += 1
		if r == 1: continue	#skip the title line
		stateData = sheet1.row_values(rowNumber)
		state = upper(stateData[0])
		#add each machine as a separate instance in FSM, and dictionary in STATES
		m = stateData[0].split('/')[0]
		FSM.setdefault(m, StateMachine.StateMachine(m))
		STATES.setdefault(m, {})
		#add the data in list format to the STATES of machine m
		data = dict(func=stateData[1], inputs={})
		STATES[m].setdefault(state, data)
		#load the states in the state machine
		FSM[m].add_state(state, eval(data['func']))
		# set start and end states (start state set by SyncFactoryStates during initialize)
		#FSM[m].add_state("Start", start)
		FSM[m].add_state("End", None, end_state=True)
		#FSM[m].set_start('START')
		#set the inputs subdictionary with: input:{next state, output, info}
		if stateData[3] == '':
			stateData[3] = None
		inputs = dict(next=stateData[3], output=stateData[4].split('; '), info=stateData[5].split(' $ '))
		if inputs['output'] == ['']: 
			del inputs['output'][0]
		if inputs['info'] == ['']: 
			del inputs['info'][0]
		STATES[m][state]['inputs'][stateData[2]] = inputs
	
def loadFactFSM_Xl():
	import xlrd	#load the library for reading Excel files
	global FaSM, FaSTATES
	#load state machine from an external file
#	FaSM = StateMachine.StateMachine()
	FaSTATES = {}
	workbook = xlrd.open_workbook('OLiVE_StateMachine.xlsx')
	#Get the first sheet in the workbook by index
	sheet1 = workbook.sheet_by_name('FaSM'+str(trial))
	r = 0
	for rowNumber in range(sheet1.nrows):
		r += 1
		if r == 1: continue	#skip the title line
		stateData = sheet1.row_values(rowNumber)
		state = upper(stateData[0])
		machStates = stateData[2].split('; ')
#		data = dict(func=stateData[1], inputs={})
		FaSTATES.setdefault(state, machStates)
	print FaSTATES

def ReloadFSM():
	loadMachFSM_Xl()
#	loadFactFSM_Xl()
#	(actions, message) = SyncFactoryStates ('FACTORY/START')
#	gPlayers[1]['player'].BroadcastActionsMessages(actions, message)

#vizact.onkeydown('r', ReloadFSM)

def MachineState (mach, state, inp, sync=False):
	global STATES
	
	print "State:",state,"Input:",inp
	#check if this input is defined for this state
	if STATES[mach][state]['inputs'].has_key(inp):
		output = STATES[mach][state]['inputs'][inp]['output']
		info   = STATES[mach][state]['inputs'][inp]['info']
		nextSt = STATES[mach][state]['inputs'][inp]['next']
	else:
		nextSt, output, info = None, [], []
		print "This input is not defined!"
	# create a copy of output and info to avoid alterning the original STATES
	output2 = list(output)
	info2 = list(info)
	# change remaining machine states if this is an entry input
	# and this function was not called through SynchFactoryStates
	if inp == 'entry' and sync == True:
		act, mess = SyncFactoryStates(state)
	try:
		# add the new actions/messages returned from syncing other SMs
		output2 += act
		info2 += mess
		print "Machine state returns:", nextSt, output2, info2
	except:
		pass
	return nextSt, (output2, info2)

def SyncFactoryStates (state):
	global FaSTATES
	print "------------SYNCRONIZING MACHINES-------------"
	actions, messages = [], []
	if FaSTATES.has_key(state):
		for st in FaSTATES[state]:
			newState = None
			mach = st.split('/')[0]
			#skip this machine if not in the FSM
			if not FSM.has_key(mach):
				continue
			if ':' in st:
				stOR = st.split('#')
				for stat in stOR:
					s = stat.split(':')
					mach2 = s[1].split('/')[0]	#allow comparison of different machines' states
					if FSM[mach2].currentState == upper(s[1]):
						newState = s[0]
						break
			else:
				if FSM[mach].currentState != upper(st):
					newState = st
			#print "MACHINE:", mach	
			try:	#change machine to the new state, if there is one defined
				olivePress.machines[mach]	#this is used to prevent code running for machines not loaded
				print upper(newState), "-> new state of machine:", mach 
				FSM[mach].set_start(newState)
				(a, m) = FSM[mach].evaluate_state('entry', synch=False)
				actions  += a
				messages += m
			except:
				pass
	print "----------------------------------------------"
	return actions, messages

def getFaStates ():
	global FSM
	for m in FSM.keys():
		print m, "->", FSM[m].currentState
		
#######################
### INITIALIZE GAME ###
#######################

def AddProximitySensors():
	manager = vizproximity.Manager()
#	manager.setDebug(viz.ON)
	#Add line below so proximity shape does not interfere with picking
#	manager.getDebugNode().disable([viz.PICKING,viz.INTERSECTION])
	manager.setDebugColor(viz.RED)
	manager.setDebugActiveColor(viz.YELLOW)
	for p in gPlayers.values():
		target = vizproximity.Target(p['player']._view)
		manager.addTarget(target)
	# add the stairs as sensors to increase step size
	sensor_stairL = vizproximity.Sensor(vizproximity.RectangleArea([1,.5]), source=olivePress.factory.getChild('stairL-GEODE'))
	sensor_stairR = vizproximity.Sensor(vizproximity.RectangleArea([1,.5]), source=olivePress.factory.getChild('stairR-GEODE'))
	manager.addSensor(sensor_stairL)
	manager.addSensor(sensor_stairR)
	manager.onEnter(sensor_stairL, EnterStairs)
	manager.onExit(sensor_stairL, ExitStairs)
	manager.onEnter(sensor_stairR, EnterStairs)
	manager.onExit(sensor_stairR, ExitStairs)
	# add machine sensors to capture when player approaches one
	sensors = {}
	for m, mach in olivePress.machines.iteritems():
		machSensor = vizproximity.Sensor(mach.proximityData[0], source=mach.proximityData[1])
		manager.addSensor(machSensor)
		manager.onEnter(machSensor, EnterMachine, m)
		manager.onExit(machSensor, ExitMachine, m)
		sensors[m] = machSensor

def EnterStairs(e):
	view = e.target.getSourceObject()
	playerByView[view].ChangeStepSize(0.35)

def ExitStairs(e):
	view = e.target.getSourceObject()
	playerByView[view].ChangeStepSize(0.1)

def EnterMachine(e, mach):
	view = e.target.getSourceObject()
	playerByView[view].ApproachMachine(mach)

def ExitMachine(e, mach):
	view = e.target.getSourceObject()
	playerByView[view].LeaveMachine(mach)
	

##############################################
## TIMER EXPIRATION: DEFINED IN FSM_ACTIONS ##
		
def timerExpire(id):
	print "expiring...", id
	pl = 1	#this is the default player for issuing timer-expiration-based actions
	# TIMERS FOR BOILER
	if id == 5:
		(actions, message) = FSM['boiler'].evaluate_state('anim-finished')
	if id in [10, 15, 20]:	# timers for boiler alerts
		(actions, message) = FSM['boiler'].evaluate_state(str(id)+'-mins-later')
		
	# TIMERS FOR MILLS [millL: 76-81, millR: 82-87]
	elif id in [76, 82]:	# timer for mill loading expiration
		(actions, message) = FSM['mill'+chr(id)].evaluate_state('anim-finished')
	elif id in range(77, 88): 
		#77: time for dilusion, 78: thick alert, 79: ready to remove, 80: very hot warning 
		animsL = {77: 'dilute', 78: 'thick', 79: 'ready', 80: 'hot', 81: 'wasted'}
		animsR = {83: 'dilute', 84: 'thick', 85: 'ready', 86: 'hot', 87: 'wasted'}
		id, code = getTimerIDCode(id, animsL, animsR)
		(actions, message) = FSM['mill'+chr(id)].evaluate_state('paste-'+code)
	
	# Timers for millR
	elif id == 600:			# tranfer tank animation expired (millR)
		(actions, message) = FSM['millR'].evaluate_state('transfer-done')
	elif id == 601:			# reset mill to empty state (millR)
		(actions, message) = FSM['millR'].evaluate_state('mill-reset')
		
	# TIMERS FOR PRESSES [pumpL: 576-580, pumpR: 582-586]
	elif id in [576, 582]:	# timer for press releasing animation expiration
		(actions, message) = FSM['press'+chr(id-500)].evaluate_state('anim-finished')
	elif id in range(577, 588): 
		#577: time to fillup, 578: pump 1500psi, 579: pump 4000psi, 580: bypass valve closed, 581: oilPump started
		animsL = {577: 'fillup', 578: 'start', 579: 'finish', 580: 'reset', 581: 'oilPumping'}
		animsR = {583: 'fillup', 584: 'start', 585: 'finish', 586: 'reset', 587: 'oilPumping'}
		id, code = getTimerIDCode(id, animsL, animsR)
		(actions, message) = FSM['press'+chr(id)].evaluate_state('press-'+code)

	# TIMERS FOR PUMPS [pumpL: 177-181, pumpR: 183-187]
	elif id in [176, 182]:	# timer for pump damage expiration
		(actions, message) = FSM['pump'+chr(id-100)].evaluate_state('anim-finished')
	elif id in range(177, 188):	# timers for pump animations
		animsL = {177: 'good', 178: 'safe', 179: 'done', 180: 'high', 181: 'max'}
		animsR = {183: 'good', 184: 'safe', 185: 'done', 186: 'high', 187: 'max'}
		id, code = getTimerIDCode(id, animsL, animsR)
		(actions, message) = FSM['pump'+chr(id)].evaluate_state('pressure-'+code)
	
	# TIMERS FOR LAVALS [lavalL: 477-481, lavalR: 483-487]
	elif id in [476, 482]:	# timer for laval damage expiration
		(actions, message) = FSM['laval'+chr(id-400)].evaluate_state('anim-finished')
	elif id in range(477, 488):	# timers for laval animations
		animsL = {477: 'start', 478: 'done', 479: 'critical', 480: 'max'}
		animsR = {483: 'start', 484: 'done', 485: 'critical', 486: 'max'}
		id, code = getTimerIDCode(id, animsL, animsR)
		(actions, message) = FSM['laval'+chr(id)].evaluate_state('separation-'+code)
		
	# TIMER FOR LOADER
	elif id in [201,202,203]:	# timer for picking mat expiration
		pl = id - 200	#encoding player number in timer id
		(actions, message) = FSM['loader'].evaluate_state('mat-picked')
		
	# TIMERS FOR OILP PUMP
	elif id in [701, 702]:	# timer for oil pump expiration
		anims = {701: 'tanks', 702: 'lavals'}
		(actions, message) = FSM['oilPump'].evaluate_state(anims[id]+'-filled')
		
	# TIMERS FOR SCALE
	elif id in [801, 802, 803]:	# timer for scale expiration
		anims = {801: 'pitcher', 802: 'reminder', 803: 'finished'}
		(actions, message) = FSM['scale'].evaluate_state('weigh-'+anims[id])
		
	# TIMERS FOR WATER PIPE [PRACTICE]
	elif id in range(1000, 1005):	# timer for scale expiration
		anims = {1000: 'waitAnim', 1001: 'done', 1002: 'high', 1003: 'max'}
		(actions, message) = FSM['waterPipe'].evaluate_state('water-'+anims[id])
		
	# TIMER FOR EXPIRATION FOR ENABLING PLAYER 1 TO EXECUTE MULTI-INPUT ACTION
	elif id == 1100:
		if condition == 0:	#check if 1P condition
			(actions, message) = ([], '')
		
	#tell player 1 to broadcast messages and actions
	gPlayers[pl]['player'].BroadcastActionsMessages(actions, message)
		
viz.callback(viz.TIMER_EVENT, timerExpire)

def getTimerIDCode (id, anL, anR):
	if id in anL: 
		code = anL[id]
		id = 76
	else: 
		code = anR[id]
		id = 82
	return id, code
	

def onExit():
	import vizinput
#	vizinput.message('Thank you for playing the Olive Oil Game!!!')
	if studyMode and trial:	#log data only for main trial
		LogParser.storeLogData(FSM, gPlayers, condition, group)

viz.callback(viz.EXIT_EVENT, onExit) 

def initialize ():
	global olivePress, floorMap, inputPanel, names
	
	#remove input panel and store player names
	try:
		for p in range(condition*2+1):
			if names[p].getMessage() != '':
				gPlayerData[p+1]['name'] = names[p].getMessage()
		inputPanel.remove()
	except:
		pass
	#add the factory
	olivePress = Factory.Factory()
	#load the state machine files
	loadMachFSM_Xl()
	loadFactFSM_Xl()
	#add machinery and other stuff to factory
	olivePress.AddMachinery(MACHINERY[trial])
	olivePress.AddAllTools()
	olivePress.AddOtherStuff()
	#split the views according to players
	splitViews()
	AddProximitySensors()
	#initiate the factory states
	(actions, message) = SyncFactoryStates ('FACTORY/START')
	gPlayers[1]['player'].BroadcastActionsMessages(actions, message)

vizact.onkeydown('i', initialize)

#####################################
## EXPERIMENT CONDITIONS AND INPUT ##
#####################################

def displayInputPanel():
	global inputPanel, names
	
	inputPanel = viz.addGUIGroup()
	names = []
	pl = range(condition*2+1)
	pl.reverse()
	for i,p in enumerate(pl):
		name = viz.addTextbox()
		title = viz.addText('Player %s name:'%str(i+1), viz.SCREEN)
		title.fontSize(24)
		title.addParent(inputPanel)
		title.setPosition([.4, .53+.1*p, 0])
		name.setPosition([.5, .5+.1*p, 0])
		name.addParent(inputPanel)
		names.append(name)
	startB = viz.addButtonLabel('START')
	startB.setPosition(.5,.4)
	startB.addParent(inputPanel)
	vizact.onbuttonup(startB, initialize)
	
if studyMode:
	trial = viz.choose('Choose practice or main trial:',['practice', 'trial'])
	condition = viz.choose('Choose study condition:',['1P', '3P'])
	if trial:
		group = viz.input('Choose group number:', '')
		displayInputPanel()
	else:
		initialize()
else:
	condition = 0	#0->'1P', 1->'3P'
	trial = 1		#1->full factory & logging, 0->practice
	initialize()
	
#----------------------------------------------------------------
def sendEventToMachine (mach, action):
	(mActions, mMessage) = FSM[mach].evaluate_multi_input(action, gPlayers[1]['player'], True)
	gPlayers[1]['player'].BroadcastActionsMessages(mActions, mMessage)

def changeFSMState (mach, newState):
	FSM[mach].set_start(newState)
	sendEventToMachine(mach, 'entry')