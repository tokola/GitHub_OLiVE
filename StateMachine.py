import viz
from string import upper

class StateMachine ():
	def __init__(self):
		self.handlers = {}	# stores the state callbacks
		self.messages = {}	# stores the messages to appear on the player's panel
		self.actions  = {}	# stores the actions to be executed on event trigger
		self.currentState = None
		self.endStates = []
		self.inputs = {}	#stores inputs from different players
		self.log = {}

	def add_state(self, state, handler, end_state=0):
		state = upper(state)
		self.handlers[state] = handler
#		self.actions[state] = actions
#		self.messages[state] = message
		if end_state:
			self.endStates.append(state)

	def set_start(self, state):
		self.currentState = upper(state)

	def evaluate_state(self, eInput):
		try:
			handler = self.handlers[self.currentState]
		except:
			raise AttributeError("Must call .set_start() before .evaluate()")

		if not self.endStates:
			raise AttributeError("At least one state must be an end_state")
			
		# This is the callback of the function passed when loading the state machine
		# cargo is used to carry a tuple with actions and messages (<actionList>, <message>)
		(newState, cargo) = handler(self.currentState, eInput)
		(actions, message) = cargo
		# make a list of message if the message received is a string
		if not isinstance(message, list):
			messages = [message]
		else:
			messages = message
		if newState != None:
			if upper(newState) in self.endStates:
				print "this is the end my friend"
				return
			else: #update current state and execute entry conditions
				self.currentState = upper(newState)
				handler = self.handlers[self.currentState]
				(voidState, cargo) = handler(self.currentState, 'entry')
				# append entry actions to the ones triggered by the state change
				actions = actions + cargo[0]
				# don't display entry message if there is already defined by state change (2 messages already)
				if cargo[1] != None and len(messages) < 2:
					messages = messages + cargo[1]	#when the messages are lists
					#messages.append(cargo[1])		#when the messages are strings
		
		return (actions, messages)
		#execute_actions(actions)		
		#print_message(message)
		

	#########################################################
	## MULTI-PLAYER : RECEIVING THE INPUT FROM THE PLAYERS ##
	
	def evaluate_multi_input (self, rInput, player, pressed):
		# add or delete a player in/from the inputs list according to button pressed/released
		if pressed:
			self.inputs[player] = rInput
		else:
			try:
				del self.inputs[player]
			except KeyError:
				pass
			return None, ([], None)
		# make a trigger from all the players' inputs
		sortInputs = self.inputs.values()
		sortInputs.sort()
		trigInput = ', '.join(sortInputs)
		
		(acts, mess) = self.evaluate_state(trigInput)
		# if an action was eventually performed, notify the remaining players
		if len(self.inputs) > 1 and len(acts) > 0:
			for p in self.inputs.keys():
				if p != player:
					actions = self.filterMultiActions(acts)
					p.BroadcastActionsMessages(actions, mess)
		# log the input of the player and the action performed
		self.log_user_data(self.inputs, acts)	
		# finally, return the actions,messages to the current player (last input)
		return (acts, mess)
	
	def filterMultiActions(self, act):
		#actions with * at the end will be broadcast to all players
		acti = [a.split('*')[0] for a in act if '*' in a]
		if len(acti) > 0:
			return acti
		
	def log_user_data (self, user_input, actions):
		for u, i in user_input.iteritems():
			self.log.setdefault(u._name.getMessage(), []).append((i, actions, round(viz.tick(), 2)))
		#print "Log file:", self.log
			
if __name__ == '__main__':
	viz.go()
	
	def idle (args):
		print "Game started!"
		return 'Boiler-off/empty', ([], None)
		
	def Boiler_empty (*args):
		# If all args are received this is the entry condition of the state
		# otherwise check the input for this state
		mInput = args[0]
		if mInput == 'shovel_coal':
			return 'Boiler-off/loaded', ([], None)
		elif mInput == 'turn_valve_boiler':
			mes = "The boiler is still empty"
			return None, ([], mes)
		#return None, 5
		
			
	def Boiler_loaded (*args):
		mInput = args[0]
		if mInput == 'turn_valve_boiler':
			return 'Boiler-on', (['turning_valve_on'], None)
		elif mInput == 'shovel_coal':
			mes = "The steam pressure is in good levels"
			return None, ([], mes)
	
	def Boiler_working (*args):
		mInput = args[0]
		if mInput == 'turn_valve_boiler':
			mes = "Steam supply is already on"
			return None, ([], mes)
		elif mInput == 'shovel_coal':
			mes = "Boiler has enough pressure"
			return None, ([], mes)
		elif mInput == '10_mins_later':
			return 'Boiler-low-pressure', ([], None)
	
	def Boiler_pressure (*args):
		mInput = args[0]
		if mInput == 'turn_valve_boiler':
			mes = "Steam supply is already on"
			return None, ([], mes)
		elif mInput == 'shovel_coal':
			mes = "Good! Steam supply is back to normal"
			return 'Boiler-on', ([], mes)
		elif mInput == '5_mins_later':
			mes = "Danger! Boiler pressure is very low"
			return None, (['dropping_pressure'], mes)
		elif mInput == '10_mins_later':
			return 'Boiler-on/empty', (['stopping_timer'], None)
			
	def Boiler_on_empty (*args):
		mInput = args[0]
		if mInput == 'turn_valve_boiler':
			mes = "Steam supply is already on"
			return 'Boiler-off/empty', ([], None)
		elif mInput == 'shovel_coal':
			mes = "You need to turn the vale off first"
			return None, ([], mes)
			
	def print_message (mes):
		try:
			print "Message:", mes
		except:
			pass
	
	def execute_actions (act):
		try:
			if len(act) > 0:
				print "Executing...", act
		except:
			pass
			
	fsm=StateMachine()
	fsm.add_state("Idle", idle)
	fsm.add_state("Boiler-off/empty", Boiler_empty, [], "The boiler is currently turned off")
	fsm.add_state("Boiler-off/loaded", Boiler_loaded, ['loading_boiler'], "Great! The boiler is being loaded with coal")
	fsm.add_state("Boiler-on", Boiler_working, ['increasing_pressure', 'starting_timer'], "Good! You started steam supply to the engine")
	fsm.add_state("Boiler-low-pressure", Boiler_pressure, ['dropping_pressure', 'error-low-pressure'], "Beware! Boiler pressure is low")
	fsm.add_state("Boiler-on/empty", Boiler_on_empty, ['dropping_pressure', 'stopping_engine'], "The boiler stopped working due to inadequate pressure!")
	fsm.add_state("game finished", None, end_state=True)
	fsm.set_start('Idle')
	#fsm.evaluate_state('start')