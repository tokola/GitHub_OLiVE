import viz
from string import upper

class StateMachine ():
	def __init__(self, mach=None):
		self.handlers = {}	# stores the state callbacks
		self.messages = {}	# stores the messages to appear on the player's panel
		self.actions  = {}	# stores the actions to be executed on event trigger
		self.currentState = None
		self.endStates = []
		self.inputs = {}	#stores inputs from different players
		self.log = {}		#stores user interaction data {user:[(trigger, actions, time)}
		self.sLog= {}		#stores machine state changes {time:[state, trigger, new state]}
		self.machine = mach	#the machine of this specific FSM

	def add_state(self, state, handler, end_state=0):
		state = upper(state)
		self.handlers[state] = handler
#		self.actions[state] = actions
#		self.messages[state] = message
		if end_state:
			self.endStates.append(state)

	def set_start(self, state):
		self.currentState = upper(state)

	def evaluate_state(self, eInput, synch=True):
		try:
			handler = self.handlers[self.currentState]
		except:
			raise AttributeError("Must call .set_start() before .evaluate()")

		if not self.endStates:
			raise AttributeError("At least one state must be an end_state")
		
		prevState = self.currentState
		
		# This is the callback of the function passed when loading the state machine;
		# cargo is used to carry a tuple with actions and messages (<actionList>, <messageList>);
		# synch is a boolean for defining if the callback function (MachineState) 
		# will try to synch with the factory and is FALSE only for 'entry' inputs
		# which are invoked from the SyncFactoryStates function
		(newState, cargo) = handler(self.machine, self.currentState, eInput, synch)
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
				(voidState, cargo) = handler(self.machine, self.currentState, 'entry', synch)
				# append entry actions to the ones triggered by the state change
				actions = actions + cargo[0]
				# if the new state has an entry message (cargo[1]) defined... 
				if cargo[1] != None:
					try:	#check if the event returned any messages (exception for messages=[])
						#if they are not defined by the event (2 messages already) or there is not an alert type
						if len(messages) < 2 and not ('/' in str(messages[0]).partition('/')):	
							messages = messages + cargo[1]	#when the messages are lists
					except:
						messages = cargo[1]
		#log the time and state change caused by the input
		self.log_state_change(prevState, eInput, actions)
		
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
		# make a trigger from all the players' inputs, e.g. {1:'hand_coal', 2:'hand_hammer'}
		sortInputs = self.inputs.values()
		sortInputs.sort()	#inputs should be recorded in alphabetical order in Excel
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
		#actions with * at the end will be broadcast to all players involved in the action
		acti = [a.split('*')[0] for a in act if '*' in a]
		if len(acti) > 0:
			return acti
		
	def log_user_data (self, user_input, actions):
		for u, i in user_input.iteritems():
			self.log.setdefault(u._player, []).append((i, actions, round(viz.tick(), 2)))
		#print "Log file:", self.log
		
	def log_state_change (self, oldState, trigger, actions):
		self.sLog[round(viz.tick(),2)] = [oldState, trigger, self.currentState, actions]
		#print "Time: %s State: %s, Input: %s, New state: %s" % (round(viz.tick(),2), prevState, eInput, self.currentState)
		
if __name__ == '__main__':
	viz.go()
				
	fsm=StateMachine()