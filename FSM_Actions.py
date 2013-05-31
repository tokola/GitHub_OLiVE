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
			########## ENGINE ACTIONS ##############
			if action == 'turning_valve_on':
				self._factory.factory.addAction(vizact.call(self._factory.engine.E_openValve, 3))
			elif action == 'turning_valve_off':
				self._factory.factory.addAction(vizact.call(self._factory.engine.E_closeValve, 3))
			elif action == 'starting_engine':
				self._factory.factory.addAction(vizact.waittime(3))	#wait for valve animation
				self._factory.factory.addAction(vizact.call(self._factory.StartFactory))
			elif action == 'stopping_engine':
				self._factory.StopFactory()
			########## BOILER ACTIONS ##############
			elif action == 'loading_boiler':
				self._factory.boiler.OpenCloseHatch(True)
				self._factory.factory.addAction(vizact.waittime(2))
				self._factory.factory.addAction(vizact.call(self._factory.boiler.CoalAction, 1))
				#self._factory.factory.addAction(vizact.waittime(1))
				#self._factory.factory.addAction(vizact.call(self._factory.boiler.CoalAction, 2))
			elif action == 'starting_timer':
				viz.starttimer(10, 300, 0)	#timer for the first warning
				viz.starttimer(15, 450, 0)	#timer for the second warning
				viz.starttimer(20, 600, 0)	#timer for stopping factory
			elif action == 'stopping_timer':
				viz.killtimer(10)
				viz.killtimer(15)
				viz.killtimer(20)
			elif 'pressure' in action:
				#get the pressure and send it as an argument to the machine specified by the first word
				machine = action.partition('_')[0]
				pressure = action.rpartition('_')[2][:-3]
				exec('self._factory.'+machine+'.ChangePressure(int('+pressure+'))')
			elif action == 'lighting_furnace':	#coals appear inside furnace and light up
				self._factory.boiler.CoalAction(2)
				self._factory.factory.addAction(vizact.waittime(2))
				self._factory.factory.addAction(vizact.call(self._factory.boiler.OpenCloseHatch, False))
			elif action == 'dying_away_fire':	#fire dies away and coals are wasted
				self._factory.boiler.CoalAction(3)
			elif action == 'renewing_fire':	#fire dies away and coals are wasted
				self._factory.boiler.CoalAction(4)
			elif action == 'exhausting_fire':	#fire dies away and coals are wasted
				self._factory.boiler.CoalAction(5)
				
			########## MILL ACTIONS ##############
			elif 'loading_mill' in action:	#has * at the end
				if not '*' in action:	#don't let the second player execute the animation again
					LR = action[-1:]
					viz.starttimer(ord(LR), 5, 0)	#timer while loading the olives -> anim-finished
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
				viz.starttimer(ord(LR), 5, 0)	#timer while pouring the paste -> anim-finished
				exec('self._factory.'+mill+'.PasteInTank()')
			elif 'wasting_paste' in action:
				LR = action[-1:]
				mill = 'mill'+ LR
				viz.starttimer(ord(LR), 3, 0)	#timer while wasting the paste -> anim-finished
				exec('self._factory.'+mill+'.WastePaste()')
			elif 'transferring_tank' in action:
				if not '*' in action:	#don't let the second player execute the animation again
					LR = action[-1:]
					mill = 'mill'+ LR
					viz.starttimer(ord(LR), 10, 0)	#timer while transferring the tank -> anim-finshed
					exec('self._factory.'+mill+'.MoveTank()')
			elif 'finishing_transfer' in action:
				LR = action[-1:]
				mill = 'mill'+ LR
				viz.starttimer(ord(LR), 4, 0)	#timer while big tank fills up -> anim-finshed
			elif 'resetting_mill' in action:
				LR = action[-1:]
				mill = 'mill'+ LR
				exec('self._factory.'+mill+'.ResetMill()')
			elif 'timerM' in action:
				LR = action[-1:]
				action = action.replace(LR, '')	#delete the last character
				timerTag = action.partition('_')[2]
				timerCode = action.partition('_')[0][-1:]	#1=set timer, 0=kill timer
				#e.g., (1,5) -> set timer id=77 (76+1) or id=83 (82+1) for 5 secs
				#wasted is called with thick and hot and needs to expire later
				timers = {'dilute':(1,30), 'thick':(2,30), 'ready':(3,45), 'hot':(4,30), 'wasted':(5,60)}
				if int(timerCode) == 1:
					viz.starttimer(ord(LR)+timers[timerTag][0], timers[timerTag][1], 0)
				else:
					viz.killtimer(ord(LR)+timers[timerTag][0])
					
			########## LOADER ACTIONS ##############
			elif action == 'serving_mat':
				self._factory.loader.MatOnTable()
			elif 'getting_pulp' in action:
				amount = int(action[-2:])
				self._factory.loader.PulpInTank(amount)
			elif action == 'scooping_pulp':
				self._factory.loader.PulpInTank(-.5)
				self._CanFull(True)	# sent to player holding can
			elif action == 'removing_pulp':
				self._factory.loader.PulpInTank(-1)
			elif 'filling_mat' in action:
				if not '*' in action:	#don't let the second player execute the action again
					self._factory.loader.FillMat()
				if self._selected == 'canful':	#the one holding the can should...
					self._CanFull(False)	#fill up the can
			elif action == 'picking_mat':
				self.AddToToolbox('mat')
				self._factory.loader.PickMat()
			elif action == 'mat_as_tool':
				matObj = self._factory.loader.components['mat']
				self._factory.AddMatAsTool('matP', matObj)
				
			######## PRESS ACTIONS ###############
			elif 'loading_press' in action:
				LR = action[-1:]
				press = 'press'+ LR
				fullPress = eval('self._factory.'+press+'.LoadMat()')
				if fullPress:
					viz.starttimer(ord(LR)+501, 1, 0)	#timer for filling up press	
			elif action == 'dropping_mat':
				self.DropObject(putBack=False)
			elif 'fillingup_press' in action:
				LR = action[-1:]					#L:76, R:82
				press = 'press'+ LR
				exec('self._factory.'+press+'.FillUp()')
			elif 'starting_press' in action:	# called from the pump
				LR = action[-1:]
				viz.starttimer(ord(LR)+502, 1, 0)	#timer for staring press
			elif 'finishing_press' in action:	# called from the pump
				LR = action[-1:]
				viz.starttimer(ord(LR)+503, 1, 0)	#timer for finishing press
			elif 'pumping_oil_press' in action:	# called from the oil pump
				LR = action[-1:]
				viz.starttimer(ord(LR)+505, 1, 0)	#timer for emptying the oil tanks
			elif 'resetting_press' in action:	# called from the pump
				LR = action[-1:]
				viz.starttimer(ord(LR)+504, 1, 0)	#timer for releasing press
			elif 'releasing_press' in action:	# used as delay to send the 'anim-finished' event
				LR = action[-1:]
				press = 'press'+ LR
				viz.starttimer(ord(LR)+500, 10, 0)
				exec('self._factory.'+press+'.Releasing(10)')
			elif 'pressing_press' in action:
				LR = action[-1:]
				press = 'press'+ LR
				exec('self._factory.'+press+'.Pressing()')
			elif 'removing_mats' in action:
				LR = action[-1:]
				press = 'press'+ LR
				exec('self._factory.'+press+'.RestoreMats()')
			elif 'emptying_oil' in action:
				LR = action[-1:]
				press = 'press'+ LR
				exec('self._factory.'+press+'.PumpOil()')
				
			######## PUMP ACTIONS ###############
			elif 'starting_pump' in action:
				LR = action[-1:]
				pump = 'pump'+ LR
				func = 'self._factory.'+pump+'.ChangeGuide, 1'
				exec('self._factory.factory.addAction(vizact.call('+func+'))')
				func = 'self._factory.'+pump+'.StopCrazy'
				exec('self._factory.factory.addAction(vizact.call('+func+'))')
				func = 'self._factory.'+pump+'.SetMotion'
				exec('self._factory.factory.addAction(vizact.call('+func+'))')
			elif 'stopping_pump' in action:
				LR = action[-1:]
				pump = 'pump'+ LR
				func = 'self._factory.'+pump+'.ChangeGuide, -1'
				exec('self._factory.factory.addAction(vizact.call('+func+'))')
				func = 'self._factory.'+pump+'.StartCrazy'
				exec('self._factory.factory.addAction(vizact.call('+func+'))')
				func = 'self._factory.'+pump+'.EndMotion'
				exec('self._factory.factory.addAction(vizact.call('+func+'))')
			elif 'opening_bypass' in action:
				LR = action[-1:]
				pump = 'pump'+ LR
				exec('self._factory.'+pump+'.TurnValve(1)')
			elif 'closing_bypass' in action:
				LR = action[-1:]
				pump = 'pump'+ LR
				exec('self._factory.'+pump+'.TurnValve(-1)')
			elif 'lifting_bar' in action:
				LR = action[-1:]
				pump = 'pump'+ LR
				exec('self._factory.'+pump+'.LiftBar(True)')
			elif 'dropping_bar' in action:
				LR = action[-1:]
				pump = 'pump'+ LR
				exec('self._factory.'+pump+'.LiftBar(False)')
			elif 'damaging_pump' in action:
				LR = action[-1:]
				pump = 'pump'+ LR
				viz.starttimer(ord(LR)+100, 3, 0)
			elif 'timerP' in action:
				LR = action[-1:]
				action = action.replace(LR, '')	#delete the last character
				timerTag = action.partition('_')[2]
				timerCode = action.partition('_')[0][-1:]	#1=set timer, 0=kill timer
				#e.g., (101,20) -> set timer id=177 (76+101) or id=184 (82+102) for 20 secs
				#safe+done=60 (the duration of the pressing animation)
				#10, 60, 30 secs should be also set in the pump's ChangePressure function 
				timers = {'good':(101,10), 'safe':(102,10), 'done':(103,50), 'high':(104,30), 'max':(105,30)}
				if int(timerCode) == 1:
					viz.starttimer(ord(LR)+timers[timerTag][0], timers[timerTag][1], 0)
				else:
					viz.killtimer(ord(LR)+timers[timerTag][0])
					
			######## OIL PUMP ACTIONS ###############
			elif action == 'start_pumping':
				self._factory.oilPump.ChangeGuide(1)
			elif action == 'stop_pumping':
				self._factory.oilPump.ChangeGuide(-1)
			elif action == 'filling_lavals':
				self._factory.oilPump.OilPourInLavals(1)
			elif action == 'emptying_tanks':
				self._factory.oilPump.OilPourInLavals(0)
			elif 'timerO' in action:
				timerTag = action.partition('_')[2]
				timerCode = action.partition('_')[0][-1:]	#1=set timer, 0=kill timer
				timers = {'tanks':(701,5), 'lavals':(702,10)}
				if int(timerCode) == 1:
					viz.starttimer(timers[timerTag][0], timers[timerTag][1], 0)
				else:
					viz.killtimer(timers[timerTag][0])

			######## LAVAL ACTIONS ###############
			elif action == 'detaching_laval_belt':
				self._factory.lavalR.DetachBelt()
			elif 'attaching_belt' in action:	#has * at the end
				if not '*' in action:	#execute the action only the first time
					print "ATTACHING BELTTTTTTTTTTT by", self._name.getMessage()
					self._factory.lavalR.AttachBelt()
				if self._selected == 'belt':#the one holding the belt should...	
					self.DropObject(False)	#drop it without putting in back in place
			elif 'starting_laval' in action:
				LR = action[-1:]
				laval = 'laval'+ LR
				exec('self._factory.'+laval+'.ChangeGuide(1)')
			elif 'stopping_laval' in action:
				LR = action[-1:]
				laval = 'laval'+ LR
				exec('self._factory.'+laval+'.ChangeGuide(-1)')
			elif 'starting_separation' in action:
				LR = action[-1:]
				laval = 'laval'+ LR
				exec('self._factory.'+laval+'.StartSeparation(1)')
			elif 'stopping_separation' in action:
				LR = action[-1:]
				laval = 'laval'+ LR
				exec('self._factory.'+laval+'.StartSeparation(0)')
			elif 'transferring_pitcher' in action:
				if not '*' in action:	#don't let the second player execute the animation again
					LR = action[-1:]
					laval = 'laval'+ LR
					viz.starttimer(400+ord(LR), 7, 0)	#timer while transferring the pitcher -> anim-finshed
					exec('self._factory.'+laval+'.MovePitcher(8)')
			elif 'timerL' in action:
				LR = action[-1:]
				action = action.replace(LR, '')	#delete the last character
				timerTag = action.partition('_')[2]
				timerCode = action.partition('_')[0][-1:]	#1=set timer, 0=kill timer
				#e.g., (401,10) -> set timer id=477 (76+401) or id=484 (82+402) for 10 secs
				#10, 30, 30 secs should be also set in the laval's ChangePressure function 
				timers = {'start':(401,10), 'done':(402,10), 'critical':(403,30), 'max':(404,30)}
				if int(timerCode) == 1:
					viz.starttimer(ord(LR)+timers[timerTag][0], timers[timerTag][1], 0)
				else:
					viz.killtimer(ord(LR)+timers[timerTag][0])
			
			######## SCALE ACTIONS ###############
			elif action == 'pitcher_on_scale':	# called from the lavals
				viz.starttimer(801, 1, 0)
			elif action == 'weighing_pitcher':
				self._factory.scale.WeighPitcher()
			elif action == 'finishing_production':
				viz.starttimer(802, 1, 0)
			elif action == 'finishing_game':
				print "GAME FINISHED with 400lbs produced!"
				
			# ALERTS ON MACHINERY
			elif 'error' in action:
				mach = action.partition('_')[2]
				machPos = self._factory.machines[mach].object.getPosition()
				errorCode = action.partition('_')[0][-1:]	#1=error on, 0=error off
				self._mapWin.ShowErrorOnMap(mach, machPos, int(errorCode))