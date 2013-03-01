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
				viz.starttimer(10, 30, 0)	#timer for the first warning
				viz.starttimer(15, 40, 0)	#timer for the second warning
				viz.starttimer(20, 45, 0)	#timer for stopping factory
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
			# ALERTS ON MACHINERY
			elif 'error' in action:
				mach = action.partition('_')[2]
				machPos = self._factory.machines[mach].object.getPosition()
				errorCode = action.partition('_')[0][-1:]	#1=error on, 0=error off
				self._mapWin.ShowErrorOnMap(mach, machPos, int(errorCode))