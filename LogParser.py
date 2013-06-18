﻿import viz
import vizact
import pickle
import fnmatch

viz.go()

##############################
## STORE AND PARSE LOG DATA ##
##############################

def storeLogData (FSM, players):
	output = []		#user interaction with machinery [(time, user, name, input, machine, actions), ...]
	output2 = []	#machine state changes [(time, machine, before, trigger, after, actions), ...]
	output3 = []	#user inventory changes [(time, user, tool, pickOrDrop), (), ...]
	output4 = []	#user proximity to machinery [(time, user, macine, enterOrLeave), (), ...]
	output5 = {}	#{user1: [(time1, posx1, posz1), ...], user2: [...]}
	for m in FSM.keys():
		#parse user log from state machines
		log = FSM[m].log		
		for p,data in log.iteritems():
			for e in data:	#e[0]-> input, e[1]-> actions, e[2] -> time stamp
				output.append((e[2], p, getPName(players, p), e[0], m, e[1]))
		#parse machine state changes
		slog = FSM[m].sLog
		for t,data in slog.iteritems():
			output2.append((t, m, data[0], data[1], data[2], data[3]))
	#consolidate inventory data from all players
	for p in players.values():
		output3 += p['player']._iLog
	#consolidate proximity data from all players
	for p in players.values():
		output4 += p['player']._proxLog
	#dictionary with position data per player
	for p, player in players.iteritems():
		output5[p] = player['player']._pLog
	#sort data according to time stamp			
	output.sort()
	output2.sort()
	saveLogFile('user', output)
	saveLogFile('state',output2)
	saveLogFile('inventory', output3)
	saveLogFile('proximity', output4)
	saveLogFile('position', output5)
	
def saveLogFile(kind, content):
	file = open('log_'+kind, 'w')
	pickle.dump(content, file)
	file.close()

def loadLogFile(kind):
	file = open('log_'+kind, 'r')
	log = pickle.load(file)
	file.close()
	return log
	
def printLogFile(parser):
	import time
	data = loadLogFile('user')
	# Output log in readable format: i[0]->time, i[1]->player, i[2]->name, i[3]->machine, i[4]->input, i[5]->actions
	if parser == 'time':
		data.sort(key=lambda tup: tup[0])
	elif parser == 'machine':
		data.sort(key=lambda tup: tup[4])
	elif parser == 'player':
		data.sort(key=lambda tup: tup[1])
	for i in data:
		if parser == 'time':
			print "Time Stamp: %s | P%s (%s) performed %s on machine %s and caused actions: %s" %(i[0], i[1], i[2], i[3], i[4], str(i[5]))
		elif parser == 'machine':
			print "Machine: %s | At %s player P%s (%s) performed %s and caused actions: %s" %(i[4], i[0], i[1],  i[2], i[3], str(i[5]))
		elif parser == 'player':
			print "Player%s: %s | At %s performed %s on machine %s and caused actions: %s" %(i[1],  i[2], i[0], i[3], i[4], str(i[5]))
	
def getPName (playerList, p):
	return playerList[p]['player']._name.getMessage()
	
def retrieveScoreProgress():
	data = loadLogFile('state')
	#convert tuples to list and make time a string to allow string search
	scoreEntries = [d for d in data if fnmatch.filter(d[5], 'score*')!=[]]
	print scoreEntries
	score = 0
	for s in scoreEntries:
		sc = fnmatch.filter(s[5], 'score*')[0].rpartition('[')[2][:-1]
		score += int(sc)
		print "Time: %s | Action: %s | Score: %s" % (s[0], s[5][0], score)

def setupPathView ():
	import vizcam
#	viz.MainWindow.ortho(-25,25,-15,20,-1,1)
	viz.MainView.setEuler(0,90,0)
	flmap=viz.add('models/floor_map.IVE')
	flmap.texture(viz.addTexture('textures/map_view.png'),'',0)
	cam = vizcam.PivotNavigate(distance=50)
	cam.centerNode(flmap)

vizact.onkeydown('s', setupPathView)

def playerAnimationPath (player):
	data = loadLogFile('position')[player]
	#Add the ball to animate
#	avatar = viz.addTexQuad(size=.75)
#	avatar.setEuler(0,90,0)
#	avatar.texture(viz.addTexture('textures/mapAva_icon.png'),'',0)
	avatar = viz.addChild('beachball.osgb', scale=[1.5,1.5,1.5])
	colors = [[197, 106, 183], [83, 171, 224], [255, 189, 0]]
	avatar.color([float(c)/255 for c in colors[player-1]])
	#Create the animation path
	path = viz.addAnimationPath()
	#Initialize an array of control points and add them to the path
	positions = [[p[1],0,p[2]] for p in data]
	for x,pos in enumerate(positions):
		path.addControlPoint(x+1,pos=pos)
	#Set the initial loop mode to circular
	path.setLoopMode(viz.LOOP)
	#Automatically rotate the path to face trajectory
	path.setAutoRotate(viz.ON)
	path.setRotateMode(viz.BEZIER)
	#Link the ball to the path
	viz.link(path, avatar)
	#Play the animation path
	path.play()

for p in [1,2,3]:
	vizact.onkeydown(str(p), playerAnimationPath, p)