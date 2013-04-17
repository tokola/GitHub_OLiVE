import viz
import vizact

class FSM_Actions ():
	"""This class contains all the actions - it is the PlayerView's subclass"""	
	def __init__(self):
		pass
		#self.recipient = fact
		#self.player = play
	

	def execute_actions (self, actList):
		# check if this is a valid list and if it contains at least one action
		try:
			if len(actList) > 0:
				print self._name.getMessage(), "executing...", actList
				ex = True
			else:
				ex = False
		except:
			ex = False
			pass
		
		if not ex: return
		#action list
		for action in actList:
			if action == 'detaching_laval_belt':
				self._factory.lavalL.detachBelt()
			elif 'attaching_belt' in action:	#has * at the end
				if not '*' in action:	#execute the action only the first time
					print "ATTACHING BELTTTTTTTTTTT by", self._name.getMessage()
					self._factory.lavalL.attachBelt()
				if self._selected == 'belt':#the one holding the belt should...	
					self.DropObject(False)	#drop it without putting in back in place
			elif action == 'turning_valve_on':
				self._factory.factory.addAction(vizact.call(self._factory.engine.E_openValve, 3))
			elif action == 'turning_valve_off':
				self._factory.factory.addAction(vizact.call(self._factory.engine.E_closeValve, 3))
			elif action == 'loading_boiler':
				self._factory.boiler.openCloseHatch(True)
				self._factory.factory.addAction(vizact.waittime(2))
				self._factory.factory.addAction(vizact.call(self._factory.boiler.coalAction, 1))
				#self._factory.factory.addAction(vizact.waittime(1))
				#self._factory.factory.addAction(vizact.call(self._factory.boiler.coalAction, 2))
			elif action == 'starting_timer':
				viz.starttimer(10, 300, 0)	#timer for the first warning
				viz.starttimer(15, 400, 0)	#timer for the second warning
				viz.starttimer(20, 450, 0)	#timer for stopping factory
			elif action == 'stopping_timer':
				viz.killtimer(10)
				viz.killtimer(15)
				viz.killtimer(20)
			elif action == 'starting_engine':
				self._factory.factory.addAction(vizact.waittime(3))	#wait for valve animation
				self._factory.factory.addAction(vizact.call(self._factory.StartFactory))
			elif action == 'stopping_engine':
				self._factory.StopFactory()
			elif 'pressure' in action:
				#get the pressure and send it as an argument to boiler
				pressure = action.rpartition('_')[2][:-3]
				self._factory.boiler.changePressure(int(pressure))
			elif action == 'lighting_furnace':	#coals appear inside furnace and light up
				self._factory.boiler.coalAction(2)
			elif action == 'dying_away_fire':	#fire dies away and coals are wasted
				self._factory.boiler.coalAction(3)
			elif action == 'renewing_fire':	#fire dies away and coals are wasted
				self._factory.boiler.coalAction(4)
			elif action == 'exhausting_fire':	#fire dies away and coals are wasted
				self._factory.boiler.coalAction(5)
			elif 'loading_mill' in action:	#has * at the end
				if '*' in action:	#don't let the second player execute the action again
					return
				LR = action[-1:]
				print "ACTION", action, LR
				viz.starttimer(ord(LR), 5, 0)	#timer while loading the olives L:76, R:82
				mill = 'mill'+ LR
				sackID = action[-2:]
				exec('self._factory.'+mill+'.SackAnim(\"'+sackID+'\")')
			elif 'starting_crash' in action:
				LR = action[-1:]
				mill = 'mill'+ LR
				exec('self._factory.'+mill+'.OlivesToPaste()')
			elif 'pouring_paste' in action:
				LR = action[-1:]
				mill = 'mill'+ LR
				viz.starttimer(ord(LR), 5, 0)	#timer while pouring the paste L:76, R:82
				exec('self._factory.'+mill+'.PasteInTank()')
			elif 'wasting_paste' in action:
				LR = action[-1:]
				mill = 'mill'+ LR
				exec('self._factory.'+mill+'.WastingPaste()')
			elif 'transfering_tank' in action:
				LR = action[-1:]
				mill = 'mill'+ LR
				viz.starttimer(ord(LR), 3, 0)	#timer while transferring the tank L:76, R:82
				exec('self._factory.'+mill+'.MovingTank()')
			elif 'resetting_mill' in action:
				LR = action[-1:]
				mill = 'mill'+ LR
				viz.starttimer(ord(LR), 1, 0)	#timer while resetting mill L:76, R:82
				exec('self._factory.'+mill+'.MovingTank()')
			elif 'timerM' in action:
				LR = action[-1:]
				action = action.replace(LR, '')	#delete the last character
				timerTag = action.partition('_')[2]
				timerCode = action.partition('_')[0][-1:]	#1=set timer, 0=kill timer
				#e.g., (1,5) -> set timer id=77 (76+1) or id=83 (82+1) for 5 secs
				timers = {'dilute':(1,20), 'thick':(2,10), 'ready':(3,10), 'hot':(4,15), 'wasted':(5,25)}
				if int(timerCode) == 1:
					viz.starttimer(ord(LR)+timers[timerTag][0], timers[timerTag][1], 0)
				else:
					viz.killtimer(ord(LR)+timers[timerTag][0])
			########## LOADER ACTIONS ##############
			elif action == 'serving_mat':
				self._factory.loader.matOnTable()
			elif 'getting_pulp' in action:
				amount = int(action[-2:])
				self._factory.loader.pulpInTank(amount)
			elif action == 'scooping_pulp':
				self._factory.loader.pulpInTank(-.5)
				self._CanFull(True)	# sent to player holding can
			elif action == 'removing_pulp':
				self._factory.loader.pulpInTank(-1)
			elif action == 'loading_mat':
				self._factory.loader.loadMat()
				self._CanFull(False)	# sent to player holding can
			elif action == 'mat_as_tool':
				matObj = self._factory.loader.components['mat']
				self._factory.AddMatAsTool('mat', matObj)
			######## PRESS ACTIONS ###############
			elif 'loading_press' in action:
				LR = action[-1:]
				press = 'press'+ LR
				exec('self._factory.'+press+'.LoadMat()')
#			elif 's-timer' in action:
#				timerID = action.rpartition('_')[2]
#				viz.starttimer(int(timerID), 5, 0)
				
			# ALERTS ON MACHINERY
			elif 'error' in action:
				mach = action.partition('_')[2]
				machPos = self._factory.machines[mach].object.getPosition()
				errorCode = action.partition('_')[0][-1:]	#1=error on, 0=error off
				self._mapWin.ShowErrorOnMap(mach, machPos, int(errorCode))