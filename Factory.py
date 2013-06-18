"""
Shows how to use a joystick or gamepad in your script.
Move the car with with the joystick and press any button to drop a duck.
"""

import viz
import vizact
import vizmat
import Machinery


class Factory ():
	'''This is the self.factory class'''
	
	#factory = viz.add('models/factory.osgb')
	
	def __init__ (self):
		self.factory = viz.add('models/factory.osgb')
		# list of tools with position, orientation data and boolean for physics enabled or not
		self.toolsData = {'wrench': [[16.75,1.5,5],[30,0,0], True], 'shovel': [[15,0.5,7.55],[0,-80,0],False], 
				          'hammer': [[16.75,1.5,4],[45,0,0], True], 'match':[[16.75,1.5,6.1],[45,0,0],True],
						  'belt':   [[13.38,1.56,7.7],[0,90,0],False], 'water': [[-2,0,5],[0,-90,0],True],
						  'can':    [[-15.5,1.1,1.65], [90,0,0], False], 'cart': [[12,.2,1], [90,-45,0], False]}
		self.itemsData = {'sack1R': [[-1.5,1.5,10], [90,0,0]], 'sack2R': [[-1.5,1.5,11.2], [90,0,0]]}
		self.machines = {}		#e.g. {'engine': <engine obj>, 'lavalL:<lavalL obj>}
		self.wheels = {}		#e.g. {'millR': [<mill wheel1>, <mill wheel2>]
		self.belts = {}			#e.g. {'lavalL': [<laval belt1 class>, <laval belt2 class>]
		self.components = {}	#e.g. {'engine': ['valve']}
		self.componentPos = {}	#e.g. {<valve obj>: [10, 2, -4]}
		self.componentPar = {}	#e.g. {'valve': 'engine', 'coal':'boiler'}
		self.tools = {}
		self.started = False
		self._canCond = False	#False-> empty can | True-> full can
		self.AddLights()
		
	def AddLights (self):
		light1 = self.AddLight([-20, 7, 0], viz.WHITE, viz.WHITE,0)	#hall 1
		light1 = self.AddLight([-9, 7, 0], viz.WHITE, viz.WHITE,0)	#hall 2
		light1 = self.AddLight([2, 7, 0], viz.WHITE, viz.WHITE,0)		#engine
		light1 = self.AddLight([7, 7, -5], viz.WHITE, viz.WHITE,0,0.25)		#boiler
		light1 = self.AddLight([14.5, 7, 3], viz.WHITE, viz.WHITE,0)	#warehouse
		
	def AddMachinery(self, args):
		if 'engine' in args:	#ADD THE ENGINE
			self.engine = Machinery.Engine(self.factory, [0.58, .6, 2.97], [-90,0,0])
			self.machines['engine'] = self.engine
			wheel_engine=viz.add('models/objects/wheel.ive', parent=self.factory, cache=viz.CACHE_CLONE)
			wheel_engine.setPosition(0.75,5.77,-7.143)
			self.wheels['engine'] = [wheel_engine]
			belt_engine=self.factory.add('models/objects/belt_engine.osgb')
			belt_engine.setPosition(0.75,5.77,-7.143)
			belt_engine.setEuler(0,27.1,0)
			self.belts['engine'] = Machinery.Belt(belt_engine)
			signE = self.factory.add('models/objects/sign.ive', euler=[-90,0,0],
			         texture=viz.addTexture('textures/sign_engine.png'), pos=[-.45,2.5,0])
			
		if 'boiler' in args:	#ADD THE BOILER
			self.boiler = Machinery.Boiler(self.factory, [7.1,0,0])
			self.machines['boiler'] = self.boiler
			signB = self.factory.add('models/objects/sign.ive',
			         texture=viz.addTexture('textures/sign_boiler.png'), pos=[5.8,2.2,0.02])
	
		if 'millL' in args:		# ADD THE LEFT MILL
			self.millL = Machinery.Mill(self.factory, [-24.7,0,6.5], [0,0,0], 'L')
			self.machines['millL'] = self.millL
			wheel_millL = viz.add('models/objects/wheel.ive', parent=self.factory, cache=viz.CACHE_CLONE)
			wheel_millL.setPosition(-26.8,5.77,-7.143)
			belt_millL = self.factory.add('models/objects/belt_mill.osgb')
			belt_millL.setPosition(-26.8,5.77,-7.143)
			belt_millL.setEuler(0,11.4,0)
			self.wheels['millL'] = [wheel_millL]
			self.belts['millL'] = Machinery.Belt(belt_millL)
			gear_millL = belt_millL.getChild('motion gear')
			gear_millL.setEuler(180,0,0)
			gear_millL.center(0,0,13.953)
			self.wheels['millL'].append(gear_millL)
			signM1 = self.factory.add('models/objects/sign.ive', cache=viz.CACHE_COPY, 
			         texture=viz.addTexture('textures/sign_mill1.png'), pos=[-23.6,2.5,7.78])
		if 'millR' in args:		# ADD THE RIGHT MILL
			self.millR = Machinery.Mill(self.factory, [-3.7,0,6.5], [45,0,0], 'R')
			self.machines['millR'] = self.millR
			# wheels and belts
			wheel_millR = viz.add('models/objects/wheel.ive', parent=self.factory, cache=viz.CACHE_CLONE)
			wheel_millR.setPosition(-1.6,5.77,-7.143)
			belt_millR = self.factory.add('models/objects/belt_mill.osgb', cache=viz.CACHE_CLONE)
			belt_millR.setPosition(-1.6,5.77,-7.143)
			belt_millR.setEuler(0,11.4,0)
			self.wheels['millR'] = [wheel_millR]
			self.belts['millR'] = Machinery.Belt(belt_millR)
			gear_millR = belt_millR.getChild('motion gear')
			gear_millR.center(0,0,13.953)
			self.wheels['millR'].append(gear_millR)
			signM2 = self.factory.add('models/objects/sign.ive', cache=viz.CACHE_COPY,
				pos=[-5,2.5,7.78], texture=viz.addTexture('textures/sign_mill2.png'))

		if 'pumpR' in args:		#ADD THE RIGHT PUMP
			self.pumpR = Machinery.Pump(self.factory, [-17,2.6,-6.5], [-90,0,0], 'R', self)
			self.machines['pumpR'] = self.pumpR
			# wheels and belts
			wheel_pumpR = viz.add('models/objects/wheel.ive', parent=self.factory, cache=viz.CACHE_CLONE)
			wheel_pumpR.setPosition(-16.83,5.77,-7.143)
			belt_pumpR = self.factory.add('models/objects/belt_pump.osgb')
			belt_pumpR.setPosition(-16.74,5.77,-7.143)
			belt_pumpR.setEuler(0,85.35,0)
			self.wheels['pumpR'] = [wheel_pumpR]
			self.belts['pumpR']  = Machinery.Belt(belt_pumpR)
			signU2 = self.factory.add('models/objects/sign.ive', cache=viz.CACHE_COPY,
				pos=[-17.5,3,-7.85], euler=[180,0,0], texture=viz.addTexture('textures/sign_pump2.png'))
		if 'pumpL' in args:		#ADD THE LEFT PUMP
			self.pumpL = Machinery.Pump(self.factory, [-20.3,2.6,-6.5], [-90,0,0], 'L', self)
			self.machines['pumpL'] = self.pumpL
			# wheels and belts
			wheel_pumpL = viz.add('models/objects/wheel.ive', parent=self.factory, cache=viz.CACHE_CLONE)
			wheel_pumpL.setPosition(-20.13,5.77,-7.143)
			belt_pumpL = self.factory.add('models/objects/belt_pump.osgb', cache=viz.CACHE_CLONE)
			belt_pumpL.setPosition(-20.04,5.77,-7.143)
			belt_pumpL.setEuler(0,85.35,0)
			self.wheels['pumpL'] = [wheel_pumpL]
			self.belts['pumpL']  = Machinery.Belt(belt_pumpL)
			signU1 = self.factory.add('models/objects/sign.ive', cache=viz.CACHE_COPY,
				pos=[-20.8,3,-7.85], euler=[180,0,0], texture=viz.addTexture('textures/sign_pump1.png'))
				
		if 'pressL' in args:	#ADD THE 2 PRESSES
			self.pressL = Machinery.Press(self.factory, [-17.4,0,6.5], [180,0,0], 'L')
			self.machines['pressL'] = self.pressL
			signP1 = self.factory.add('models/objects/sign.ive', cache=viz.CACHE_COPY,
			              pos=[-17.4,2.5,7.78], texture=viz.addTexture('textures/sign_press1.png'))
		if 'pressR' in args:
			self.pressR = Machinery.Press(self.factory, [-14.1,0,6.5], [180,0,0], 'R')
			self.machines['pressR'] = self.pressR
			signP2 = self.factory.add('models/objects/sign.ive', cache=viz.CACHE_COPY,
			              pos=[-14.1,2.5,7.78], texture=viz.addTexture('textures/sign_press2.png'))
	
		if 'loader' in args:	#ADD THE LOADING TABLE
			self.loader = Machinery.Loader(self, self.factory, [-14.1,0,5], [180,0,0])
			self.machines['loader'] = self.loader
			
		if 'lavalR' in args:		#ADD THE 2 LAVALS
			self.lavalR = Machinery.Laval(self.factory, [-7.8,0,-5], [180,0,0], 'R', self)
			self.machines['lavalR'] = self.lavalR
			signL2 = self.factory.add('models/objects/sign.ive', cache=viz.CACHE_COPY,
					pos=[-7.6,2.3,-6.23], euler=[180,0,0], texture=viz.addTexture('textures/sign_laval2.png'))
		if 'lavalL' in args:
			self.lavalL = Machinery.Laval(self.factory, [-10,0,-5], [180,0,0], 'L', self)
			self.machines['lavalL'] = self.lavalL
			signL1 = self.factory.add('models/objects/sign.ive', cache=viz.CACHE_COPY,
					pos=[-10.37,2.3,-6.23], euler=[180,0,0], texture=viz.addTexture('textures/sign_laval1.png'))
		
		if 'oilPump' in args:
			self.oilPump = Machinery.OilPump(self.factory, [-6.02,.25,-6.032], [180,0,0], self)
			self.machines['oilPump'] = self.oilPump
			self.pipe = self.factory.add('models/objects/pipe.ive')
			self.pipe.setPosition(-6.02,.26,-6.032)
			self.pipe.setEuler([180,0,0])
			self.signO = self.factory.add('models/objects/sign.ive', cache=viz.CACHE_COPY,
					pos=[-5.6,.95,-7.19], euler=[180,13,0], texture=viz.addTexture('textures/sign_oilPump.png'))
			
		if 'scale' in args:
			self.scale = Machinery.Scale(self.factory, [-3.02,0,-6.5], [180,0,0])
			self.machines['scale'] = self.scale
		# wheels and belts for the laval sub-system
		wheel_lavalUp = viz.add('models/objects/wheel.ive', parent=self.factory, cache=viz.CACHE_CLONE)
		wheel_lavalUp.setPosition(-5, 5.77, -7.143)
		wheel_lavalDn = viz.add('models/objects/wheel.ive', parent=self.factory, cache=viz.CACHE_CLONE)
		wheel_lavalDn.setPosition(-5, 1.251, -7.38)
		wheel_lavalDn.setScale(.75,.75,.75)
		belt_laval = viz.add('models/objects/belt_laval.osgb', parent=self.factory, cache=viz.CACHE_CLONE)
		belt_laval.setPosition(-4.95, 1.251, -7.38)
		self.wheels['laval'] = [wheel_lavalUp, wheel_lavalDn]
		self.belts['laval']  = Machinery.Belt(belt_laval)
				
		#get all components from machines and store them in factory.components
		self.AddComponentsToFactory()
		
	def AddComponentsToFactory(self):
		for mName, m in self.machines.iteritems():
			try:
				for cName, cObj in m.components.iteritems():
					self.components[cName] = cObj
					self.componentPar[cName] = mName
				for cObj, cPos in m.componentPos.iteritems():
					self.componentPos[cObj] = cPos
			except:
				pass
	
	def AddOtherStuff(self):
		#Add tanks
#		self.tanks = self.factory.add('models/objects/tanks.ive')
#		self.tanks.setPosition([-8.75,0,-7.2])
#		self.tanks.setScale(1.2, 1.2, 1.2)
		#Decorate self.factory
		table = self.factory.add('models/objects/table.ive')
		table.setPosition(-12,0,9.8)
		table.setScale(.1,.1,.1)
		table2 = self.factory.add('models/objects/table.ive')
		table2.setPosition(-16,0,9.8)
		table2.setScale(.1,.1,.1)
		boxes=self.factory.add('models/objects/boxes.ive')
		boxes.setScale(.1,.1,.1)
		boxes.setPosition(-10,0,6)
		vessel=self.factory.add('models/objects/wooden vessel.ive')
		vessel.setScale(.1,.1,.1)
		vessel.setPosition(-25.5,0,-6.5)
	

	def AddAllTools(self):
		global fToolsData, fTools
		for t in self.toolsData.keys():
			self.AddTool(t)
		table3 = self.factory.add('models/objects/table.ive')
		table3.setScale(.1,.1,.1)
		table3.setPosition(16.75,0,5)
		table3.setEuler(90,0,0)
		## Physics
		self.factory.getChild('floor').collidePlane()
		table3.collideBox()
	
	def AddTool(self, tool):
		tool = self.FilterAddedObj(tool)
		self.tools[tool] = self.factory.add('models/objects/tool_'+tool+'.ive')
		self.tools[tool].setPosition(self.toolsData[tool][0])
		self.tools[tool].setEuler(self.toolsData[tool][1])
		if self.toolsData[tool][2]:	#no physics for the shovel
			self.tools[tool].collideBox()
		if tool == 'can':
			self.tools[tool].getChild('pulp').visible(self._canCond)
		if tool == 'cart':
			self.tools[tool].setScale(2, 2, 2)
	
	def AddLight(self, pos, lightColor, glareColor, group, intensity=0.15):
		Light = viz.addLight(group=group)
		Light.position(0,0,0)
		Light.setPosition(pos)
		Light.color(lightColor)
		Light.linearattenuation(intensity)
		GlareQuad = viz.addTexQuad(parent=Light)
		GlareQuad.billboard()
		GlareQuad.color(glareColor)
		GlareQuad.disable(viz.LIGHTING)
		GlareQuad.setScale([0.2,0.2,0.2])
		return Light
	
	###### USED FOR TOOL MANIPULATION FROM THE LOADER ########
	def AddMatAsTool (self, tool, toolObj):
		print "ADDING ", tool, toolObj
		self.tools[tool] = toolObj
		self.tools[tool].setParent(self.factory)
		self.tools[tool].setPosition(self.loader.object.getPosition())
		self.tools[tool].setEuler(self.loader.object.getEuler())
		del self.components['mat']
	
	def SetCanFull (self, state):
		self._canCond = state
	
	def GetCanFull (self):
		return self._canCond
	
	# convert canful to can when object (model) is asked
	def FilterAddedObj (self, obj):
		if obj == 'canful':
			return 'can'
		else:
			return obj
	
	# convert can to canful when tool name is asked, if can if full with paste
	def FilterAddedTool (self, tool):
		if tool == 'can':
			# conditional expression for returning canful instead of can
			return ('canful' if self._canCond else 'can')
		else:
			return tool
			
	def StartFactory (self):
		if self.started:	#don't run the script again if the factory is aleady started
			return
			
		self.started = True
		for m, machine in self.machines.iteritems():
			machine.Start()
			#animate machinery wheels
			if  self.wheels.has_key(m):	#check if this machine has wheels
				for w in self.wheels[m]:
					rev = 1
					#reverse the gear & wheel rotation for the left mill
					if m == 'millL' and self.wheels[m].index(w) == 1:
						rev = -1
					w.addAction(vizact.spin(1,0,0, -76*rev,viz.FOREVER))
			#animate machinery belts
			self.belts['laval'].Start()
			if  self.belts.has_key(m):	#check if this machine has wheels
				b = self.belts[m]
#				if m == 'lavalR':
				b.Start()
		
	def StopFactory(self):
		self.started = False
		for m, machine in self.machines.iteritems():
			machine.Stop()
			if  self.wheels.has_key(m):
				for w in self.wheels[m]:
					w.endAction()
			#stop machinery belts
			self.belts['laval'].Stop()
			if  self.belts.has_key(m):	#check if this machine has wheels
				b = self.belts[m]
				b.Stop()
				
	def RemoveFactory (self):
		self.factory.remove(children = True)
		
	
if __name__ == '__main__':
	import vizcam
	viz.setMultiSample(8)
	viz.go()

	viz.phys.enable()
	viz.eyeheight(1.75)
	viz.MainView.setPosition(-10,2,-5)
	#viz.MainView.setEuler(-90,0,0)
	#viz.fov(60)
	#viz.collision(viz.ON)
	viz.clearcolor(viz.SKYBLUE)
	viz.MainView.getHeadLight().disable()
	
	machines = ('boiler') #, 'millL', 'pressR', 'loader', 'lavalL', 'lavalR', 'oilPump', 'scale')
#	machines = ('millR', 'millL', 'pressL', 'pressR', 'pumpL', 'pumpR', 'loader', 'lavalL', 'lavalR', 'oilPump', 'engine', 'boiler', 'scale')
	oliveFactory = Factory()
	oliveFactory.AddMachinery(machines)
	oliveFactory.AddAllTools()
#	oliveFactory.AddOtherStuff()
	
	# pivot around object
#	cam = vizcam.PivotNavigate(distance=5)
#	cam.centerNode(oliveFactory.millL.mixedPulp)
#	cam.centerNode(oliveFactory.pressR.mats)
#	cam.centerNode(oliveFactory.pumpR.object)
#	cam.centerNode(oliveFactory.lavalL.object)
#	cam.centerNode(oliveFactory.engine.object)
#	cam.rotateUp(30)