import viz
import vizact
import vizjoy
from string import upper, lower
import Factory
#import Machinery
import Interaction
import Window
import Avatar
import StateMachine

viz.go()

viz.phys.enable()
#viz.MainView.setPosition(-10,2,-5)
#viz.MainView.setEuler(-90,0,0)
#viz.fov(60)
#viz.collision(viz.ON)
viz.clearcolor(viz.SKYBLUE)

#ADD FACTORY
olivePress = Factory.Factory()
MACHINERY = ('boiler', 'engine', 'lavalL', 'millR', 'pressR')
EYEHEIGHT = 1.5

### MAKE THE DIFFERENT VIEWS ###

gPlayers = {}
gPlayerData = {1: {'name': 'Takis', 'colors': [[197, 106, 183], [97, 50, 83]], 'pos': [-15,EYEHEIGHT,0]},
               2: {'name': 'Anna', 'colors': [[83, 171, 224], [36, 70, 90]], 'pos': [-10,EYEHEIGHT,0]},
               3: {'name': 'Matzourana', 'colors': [[255, 189, 0], [135, 100, 0]], 'pos': [-5,EYEHEIGHT,0]}}

def splitViews ():
	global floorMap

	# set the four different views in seperate windows (3 players and the map)
	floorMap = Window.PlayerView(winPos=[0.5,1])
	p1 = Window.PlayerView(view=viz.MainView, win=viz.MainWindow, winPos=[0,1], player=1, name=gPlayerData[1]['name'], fact=olivePress, sm=FSM, fmap=floorMap)
	p2 = Window.PlayerView(winPos=[0,.5], player=2, name=gPlayerData[2]['name'], fact=olivePress, sm=FSM, fmap=floorMap)
	p3 = Window.PlayerView(winPos=[0.5,.5], player=3, name=gPlayerData[3]['name'], fact=olivePress, sm=FSM, fmap=floorMap)
	# set the initial view positions
	for i,p in {1:p1,2:p2,3:p3}.iteritems():
		p._view.setPosition(gPlayerData[i]['pos'])
		p._view.collision(viz.ON)
		p._view.eyeheight(EYEHEIGHT)
		p._view.stepsize(.35)
	# assign the joystick to each player
	j2 = Interaction.Joystick(p2._window, p2)
	j3 = Interaction.Joystick(p3._window, p3)
	# set the avatar for each player
	a1 = Avatar.Avatar(p1._view, gPlayerData[1]['colors'])
	a2 = Avatar.Avatar(p2._view, gPlayerData[2]['colors'])
	a3 = Avatar.Avatar(p3._view, gPlayerData[3]['colors'])
	# make a list of all the players
	gPlayers[1] = {'player': p1, 'joy': None, 'avatar': a1}
	gPlayers[2] = {'player': p2, 'joy': j2, 'avatar': a2}
	gPlayers[3] = {'player': p3, 'joy': j3, 'avatar': a3}
	for p in gPlayers.values():
		av = p['avatar']
		av._avatar.renderToAllWindowsExcept([p['player']._window, floorMap._window])
		av._mapAva.renderOnlyToWindows([floorMap._window])
	#p2.AddToToolbox('wrench')
	#p2.AddToToolbox('hammer')
	#p2.AddToToolbox('shovel')
	
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
	# chnage the color according to how many interact with the same object
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

############################
## PARSE LOGFILE FROM FSM ##
############################

def parseLogFile (parser):
	log = FSM.log
	if parser == 'time':
		output = []
		for p,data in log.iteritems():
			for e in data:
				output.append((e[2], p, e[0], e[1]))
		output.sort()
	# Output log in readable format
	for i in output:
		print "Time Stamp: %s | %s performed %s and caused actions: %s" %(i[0], i[1], i[2], str(i[3]))
		
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
	sheet1 = workbook.sheet_by_name('FSM')
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
		inputs = dict(next=stateData[3], output=stateData[4].split('; '), info=stateData[5].split('; '))
		if inputs['output'] == ['']: 
			del inputs['output'][0]
		if inputs['info'] == ['']: 
			del inputs['info'][0]
		STATES[m][state]['inputs'][stateData[2]] = inputs
		
	#print STATES
	
def loadFactFSM_Xl():
	import xlrd	#load the library for reading Excel files
	global FaSM, FaSTATES
	#load state machine from an external file
#	FaSM = StateMachine.StateMachine()
	FaSTATES = {}
	workbook = xlrd.open_workbook('OLiVE_StateMachine.xlsx')
	#Get the first sheet in the workbook by index
	sheet1 = workbook.sheet_by_name('FaSM')
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

def start (*args):	
	print "Game started!"
	m = args[0]
	return m+'/idle', ([], None)

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
	# change remaining machine states if this is an entry input
	# and this function was not called through SynchFactoryStates
	if inp == 'entry' and sync == True:
		act, mess = SyncFactoryStates(state)
	try:
		output += act
		info += mess
		print "Machine state returns:", nextSt, output, info
	except:
		pass
	return nextSt, (output, info)

def SyncFactoryStates (state):
	global FaSTATES
	print "------------SYNCRONIZING MACHINES-------------"
	actions, messages = [], []
	if FaSTATES.has_key(state):
		for st in FaSTATES[state]:
			newState = None
			mach = st.split('/')[0]
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

def initialize ():
	global floorMap
	
	loadMachFSM_Xl()
	loadFactFSM_Xl()
	splitViews()
	
	olivePress.AddMachinery(MACHINERY) #, 'mill', 'pump', 'press')
	olivePress.AddAllTools()
	olivePress.factory.renderToAllWindowsExcept([floorMap._window])
	
	(actions, message) = SyncFactoryStates ('FACTORY/START')
	#(actions, message) = FSM['boiler'].evaluate_state("START")
	#(actions, message) = FSM['engine'].evaluate_state("START")
	gPlayers[1]['player'].BroadcastActionsMessages(actions, message)

vizact.onkeydown('i', initialize)
vizact.onkeydown('s', olivePress.StartFactory)


initialize()


def timerExpire(id):
	if id in [10, 15, 20]:	# timers for boiler alerts
		(actions, message) = FSM['boiler'].evaluate_state(str(id)+'-mins-later')
	elif id in [76, 82]:	# timer for mill loading expiration
		(actions, message) = FSM['mill'+chr(id)].evaluate_state('anim-finished')
	elif id in [77, 83]:	# timer for paste to be diluted
		if id < 82: id = 76
		else: id = 82
		(actions, message) = FSM['mill'+chr(id)].evaluate_state('paste-dilute')
	elif id in [78, 84]:	# timer for paste being too thick (display warning)
		if id < 82: id = 76	# Left Mill
		else: id = 82		# Right Mill
		(actions, message) = FSM['mill'+chr(id)].evaluate_state('paste-thick')
	elif id in [79, 85]:	# timer for paste being ready
		if id < 82: id = 76
		else: id = 82
		(actions, message) = FSM['mill'+chr(id)].evaluate_state('paste-ready')
	elif id in [80, 86]:	# timer for paste being too hot (display warning)
		if id < 82: id = 76
		else: id = 82
		(actions, message) = FSM['mill'+chr(id)].evaluate_state('paste-hot')
	elif id in [81, 87]:	# timer for paste being wasted
		if id < 82: id = 76
		else: id = 82
		(actions, message) = FSM['mill'+chr(id)].evaluate_state('paste-wasted')
	#tell player 1 to broadcast messages and actions
	gPlayers[1]['player'].BroadcastActionsMessages(actions, message)
		
viz.callback(viz.TIMER_EVENT, timerExpire)

def applyNormalToMillR():
#	kazani=olivePress.machines['millR'].object.getChild('kazani')
	kazani=viz.add('models/tank.osgb')
	normal=viz.add('models/images/PRITSINIA_NORMAL_2.tga')
	diffuse=viz.add('models/images/kazani_unfolded.tga')
	kazani.bumpmap(normal,'',0)
	kazani.texture(diffuse,'',1)
	kazani.color(1,1,1)
	
def applyNormalToPumpL():
	global tank
	tank=viz.add('models/pump_tank.ive')
	tank.setPosition(-5,2,0)
	tank.setScale(.1,.1,.1)
	#tank=olivePress.machines['pumpL'].object.getChild('water tank')
	normal=viz.add('models/images/testNormal.jpg')
	diffuse=viz.add('models/images/Roiled Concrete.tga')
	tank.bumpmap(normal,'',0)
	tank.texture(diffuse,'',1)
	tank.color(1,1,1)