import viz
import vizact
import vizjoy
from string import upper
import Factory
#import Machinery
import Interaction
import Window
import Avatar
import StateMachine

viz.go()

viz.phys.enable()
viz.eyeheight = 1.5
#viz.MainView.setPosition(-10,2,-5)
#viz.MainView.setEuler(-90,0,0)
#viz.fov(60)
#viz.collision(viz.ON)
viz.clearcolor(viz.SKYBLUE)

#ADD FACTORY
olivePress = Factory.Factory()

def initialize ():
	global floorMap
	
	olivePress.AddMachinery()
	olivePress.AddAllTools()
	olivePress.factory.renderToAllWindowsExcept([floorMap._window])

vizact.onkeydown('i', initialize)
vizact.onkeydown('s', olivePress.StartFactory)

### MAKE THE DIFFERENT VIEWS ###

gPlayers = {}
gPlayerData = {1: {'name': 'Takis', 'colors': [[197, 106, 183], [97, 50, 83]]},
               2: {'name': 'Anna', 'colors': [[83, 171, 224], [36, 70, 90]]},
               3: {'name': 'Matzourana', 'colors': [[255, 189, 0], [135, 100, 0]]}}

def splitViews ():
	global floorMap

	# set the four different views in seperate windows (3 players and the map)
	floorMap = Window.PlayerView(winPos=[0.5,1])
	p1 = Window.PlayerView(view=viz.MainView, win=viz.MainWindow, winPos=[0,1], player=1, name=gPlayerData[1]['name'], fact=olivePress, sm=fsm, fmap=floorMap)
	p2 = Window.PlayerView(winPos=[0,.5], player=2, name=gPlayerData[2]['name'], fact=olivePress, sm=fsm, fmap=floorMap)
	p3 = Window.PlayerView(winPos=[0.5,.5], player=3, name=gPlayerData[3]['name'], fact=olivePress, sm=fsm, fmap=floorMap)
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
		av._avatar.renderToAllWindowsExcept([p['player']._window])
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
	log = fsm.log
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

def loadStateMachine():
	global fsm, steamSM
	
	fsm = StateMachine.StateMachine()
	
	#load state machine from an external file
	steamSM = {}
	file = open('OLiVE_StateMachine.txt', 'r')
	l = 0
	#dictionary with states: {<state>:{'func':<function>, 'inputs':{'entry':{'output':[<actions>], 'info':[<messages>]}
	#															   {<input1>:{'output':[<actions>], 'info':[<messages>]}
	for line in file:
		l = l + 1
		if l == 1: continue	#skip the title line
		stateData = line.split('\t')
		state = upper(stateData[0])
		if state != '':
#			data = dict(func=stateData[1], entryM=stateData[2].split('; '), entryA=stateData[3].split('; '))
			data = dict(func=stateData[1], inputs={})
			steamSM.setdefault(state, data)
#			if steamSM[state]['entryA'] == ['']: del steamSM[state]['entryA'][0]
#			if steamSM[state]['entryM'] == ['']: del steamSM[state]['entryM'][0]
			fsm.add_state(state, eval(data['func']))
			#set the inputs subdictionary with: input:{next state, output, info}
			mes = stateData[5]
			if mes == ['']: 
				del mes[0]
			else:
				if '"' in mes:
					mes = eval(mes)
			if stateData[3] == '':
				stateData[3] = None
			inputs = dict(next=stateData[3], output=stateData[4].split('; '), info=mes.split('; '))
			if inputs['output'] == ['']: del inputs['output'][0]
#			steamSM[state].setdefault('inputs', {})
			steamSM[state]['inputs'][stateData[2]] = inputs
	print steamSM
	file.close()
	#load state machine manually
#	fsm.add_state("Boiler-off/empty", Boiler_empty, [], ["a/The olive press does not have power!"])
#	fsm.add_state("Boiler-off/loaded", Boiler_loaded, ['loading_boiler'], ["i/Great! The boiler is being loaded with coal"])
#	fsm.add_state("Boiler-on", Boiler_working, ['increasing_pressure', 'starting_timer'], ["i/Good! You started steam supply to the engine"])
#	fsm.add_state("Boiler-low-pressure", Boiler_pressure, ['dropping_pressure', 'error-low-pressure'], ["a/Beware! Boiler pressure is low"])
#	fsm.add_state("Boiler-on/empty", Boiler_on_empty, ['dropping_pressure', 'stopping_engine'], ["a/The boiler stopped working due to inadequate steam pressure!"])
	# set start and end states
	fsm.add_state("Idle", idle)
	fsm.add_state("game finished", None, end_state=True)
	exec("fsm.set_start('Idle')")
	#fsm.set_start('Idle')

vizact.onkeydown('m', loadStateMachine)

def idle (*args):
	print "Game started!"
	return 'Boiler-off/empty', ([], None)

def Steam_Prod (state, inp):
	global steamSM
	
	print "State:",state,"Input:",inp 
	output = steamSM[state]['inputs'][inp]['output']
	info   = steamSM[state]['inputs'][inp]['info']
	nextSt = steamSM[state]['inputs'][inp]['next']
	print nextSt, (output, info)
	return nextSt, (output, info)
	
#def Boiler_empty (*args):
#	# If all args are received this is the entry condition of the state
#	# otherwise check the input for this state
#	mInput = args[0]
#	if mInput == 'shovel_coal':
#		mes = "You are shoveling coal in the boiler, which is necessary for its operation"
#		return 'Boiler-off/loaded', ([], [mes])
#	elif mInput == 'hand_valve':
#		mes = "The boiler is still empty, so there is no need to allow steam supply to the engine"
#		return None, ([], [mes])
##	if mInput == 'shovel_coal':
##		mes = "You need someone to hammer the coal as well (if that makes sense!)"
#		return None, ([], [mes])
#	if mInput == 'hammer_coal':
#		mes = "You need someone to shovel the coal as well (doh!)"
#		return None, ([], [mes])
#	return None, ([], None)
#			
#def Boiler_loaded (*args):
#	mInput = args[0]
#	if mInput == 'hand_valve':
#		mes = "This valve allows flow of steam from the boiler to the engine"
#		return 'Boiler-on', (['turning_valve_on'], [mes])
#	elif mInput == 'shovel_coal':
#		mes = "The steam pressure is in good levels, so you don't need to load more coal"
#		return None, ([], [mes])
#	return None, ([], None)
#
#def Boiler_working (*args):
#	mInput = args[0]
#	if mInput == 'hand_valve':
#		mes = "Steam supply is already on; you should better not turn off the engine!"
#		return None, ([], [mes])
#	elif mInput == 'shovel_coal':
#		mes = "Boiler has enough pressure, so you don't need to load more coal"
#		return None, ([], [mes])
#	elif mInput == '10_mins_later':
#		return 'Boiler-low-pressure', ([], None)
#	return None, ([], None)
#	
#def Boiler_pressure (*args):
#	mInput = args[0]
#	if mInput == 'hand_valve':
#		mes = "Steam supply is already on; you should better not turn off the engine!"
#		return None, ([], [mes])
#	elif mInput == 'shovel_coal':
#		mes = ["i/Good! Steam supply is back to normal", "The boiler needs coal quite often to keep it running"]
#		return 'Boiler-on', (['stopping_timer'], mes)
#	elif mInput == '15_mins_later':
#		mes = "a/Danger! Boiler pressure is very low which may lead to machine shutdown!"
#		return None, (['dropping_pressure'], [mes])
#	elif mInput == '20_mins_later':
#		return 'Boiler-on/empty', (['stopping_timer'], None)
#	return None, ([], None)
#	
#def Boiler_on_empty (*args):
#	mInput = args[0]
#	if mInput == 'hand_valve':
#		mes = "Good! You can now ignite the boiler again"
#		return 'Boiler-off/empty', (['turning_valve_off'], [mes])
#	elif mInput == 'shovel_coal':
#		mes = "You need to turn the vale off first before igniting the boiler"
#		return None, ([], [mes])
#	return None, ([], None)
#	
#def Engine_on (*args):
#	#Referenced as a callback in FSM file but not used in the scenario
#	pass
	
#######################
### INITIALIZE GAME ###
#######################

loadStateMachine()
splitViews()
initialize()

(actions, message) = fsm.evaluate_state("START")
gPlayers[1]['player'].BroadcastActionsMessages(actions, message)

def timerExpire(id):
	if id in [10, 15, 20]:
		(actions, message) = fsm.evaluate_state(str(id)+'_mins_later')
		gPlayers[1]['player'].BroadcastActionsMessages(actions, message)
		
viz.callback(viz.TIMER_EVENT, timerExpire)