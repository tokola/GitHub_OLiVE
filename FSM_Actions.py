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
			elif 'attaching_belt' in action:
				self._factory.lavalL.attachBelt()
				if self._selected == 'belt':
					self.DropObject(False)	#drop object without putting in back in place
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
				LR = action[-2:-1]
				viz.starttimer(ord(LR), 5, 0)	#timer while loading the olives L:76, R:82
				mill = 'mill'+ LR
				sackID = action[-3:-1]
				exec('self._factory.'+mill+'.SackAnim(\"'+sackID+'\")')
			elif 'starting_crash' in action:
				LR = action[-1:]
				mill = 'mill'+ LR
				exec('self._factory.'+mill+'.OlivesToPaste()')
			elif 'pouring_paste' in action:
				LR = action[-1:]
				mill = 'mill'+ LR
				exec('self._factory.'+mill+'.PasteInTank()')
			elif 'wasting_paste' in action:
				LR = action[-1:]
				mill = 'mill'+ LR
				exec('self._factory.'+mill+'.WastingPaste()')
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
			
			# ALERTS ON MACHINERY
			elif 'error' in action:
				mach = action.partition('_')[2]
				machPos = self._factory.machines[mach].object.getPosition()
				errorCode = action.partition('_')[0][-1:]	#1=error on, 0=error off
				self._mapWin.ShowErrorOnMap(mach, machPos, int(errorCode))