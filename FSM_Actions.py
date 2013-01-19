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
				print self._name, "executing...", actList
				ex = True
			else:
				ex = False
		except:
			ex = False
			pass
		
		if not ex: return
		#action list
		for action in actList:
			if action == 'turning_valve_on':
				self._factory.factory.addAction(vizact.call(self._factory.engine.E_openValve, 3))
				self._factory.factory.addAction(vizact.waittime(3))
				self._factory.factory.addAction(vizact.call(self._factory.StartFactory))
			elif action == 'turning_valve_off':
				self._factory.factory.addAction(vizact.call(self._factory.engine.E_closeValve, 3))
			elif action == 'loading_boiler':
				print "ACTION: shoveling coal"
			elif action == 'increasing_pressure':
				self._factory.boiler.increasePressure(220)
			elif action == 'starting_timer':
				viz.starttimer(10, 10, 0)
				viz.starttimer(15, 15, 0)
				viz.starttimer(20, 20, 0)
			elif action == 'stopping_timer':
				viz.killtimer(10)
				viz.killtimer(15)
				viz.killtimer(20)
			elif action == 'stopping_engine':
				self._factory.StopFactory()
				print "stop factory"
			elif action == 'dropping_pressure':
				print 'drop pressure'