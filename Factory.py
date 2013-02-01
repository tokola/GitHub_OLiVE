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
		self.toolsData = {'wrench': [[16.75,1.5,5],[30,0,0], True], 'shovel': [[15,0.5,7.55],[0,-80,0],False], 
				          'hammer': [[16.75,1.5,4],[45,0,0], True], 'match':[[16.75,1.5,6.1],[45,0,0],True],
						  'belt':   [[13.38,1.56,7.7],[0,90,0],False]}
		self.machines = {}		#e.g. {'engine': <engine obj>
		self.wheels = {}		#e.g. {'mill': [<mill wheel1>, <mill wheel2>]
		self.belts = {}			#e.g. {'laval': [<laval wheel1>, <laval wheel2>]
		self.components = {}	#e.g. {'engine': ['valve']}
		self.componentPos = {}	#e.g. {<valve obj>: [10, 2, -4]}
		self.tools = {}
		self.started = False
		
	def AddMachinery(self, *args):
		if 'engine' in args:	#ADD THE ENGINE
			self.engine = Machinery.Engine(self.factory, [0.58, .6, 2.97], [-90,0,0])
			self.machines['engine'] = self.engine
			wheel_engine=viz.add('models/objects/wheel.ive', parent=self.factory, cache=viz.CACHE_CLONE)
			wheel_engine.setPosition(0.75,5.77,-7.143)
			self.wheels['engine'] = [wheel_engine]
			belt_engine=self.factory.add('models/objects/belt_engine.ive')
			belt_engine.setPosition(0.75,5.77,-7.143)
			belt_engine.setEuler(0,27.1,0)
			self.belts['engine'] = [belt_engine]
		if 'boiler' in args:	#ADD THE BOILER
			self.boiler = Machinery.Boiler(self.factory, [7.1,0,0])
			self.machines['boiler'] = self.boiler
		if 'mill' in args:		# ADD THE 2 MILLS
			millL = Machinery.Mill(self.factory, [-24.7,0,6.5], [0,0,0], 'L')
			millR = Machinery.Mill(self.factory, [-3.7,0,6.5], [45,0,0], 'R')
			self.machines['millR'] = millR
			self.machines['millL'] = millL
			# wheels and belts
			wheel_millR = viz.add('models/objects/wheel.ive', parent=self.factory, cache=viz.CACHE_CLONE)
			wheel_millR.setPosition(-1.6,5.77,-7.143)
			belt_millR = self.factory.add('models/objects/belt_mill.ive')
			belt_millR.setPosition(-1.6,5.77,-7.143)
			belt_millR.setEuler(0,11.4,0)
			self.wheels['millR'] = [wheel_millR]
			self.belts['millR'] = [belt_millR]
			gear_millR = belt_millR.getChild('motion gear')
			gear_millR.center(0,0,13.953)
			wheel_millL = viz.add('models/objects/wheel.ive', parent=self.factory, cache=viz.CACHE_CLONE)
			wheel_millL.setPosition(-26.8,5.77,-7.143)
			self.wheels['millR'].append(gear_millR)
			belt_millL = self.factory.add('models/objects/belt_mill.ive')
			belt_millL.setPosition(-26.8,5.77,-7.143)
			belt_millL.setEuler(0,11.4,0)
			self.wheels['millL'] = [wheel_millL]
			self.belts['millL'] = [belt_millL]
			gear_millL = belt_millL.getChild('motion gear')
			gear_millL.setEuler(180,0,0)
			gear_millL.center(0,0,13.953)
			self.wheels['millL'].append(gear_millL)
		if 'pump' in args:		#ADD THE 2 PUMPS
			self.pumpL = Machinery.Pump(self.factory, [-17,2.8,-6.5], [-90,0,0])
			self.machines['pumpL'] = self.pumpL
			base1=self.factory.add('models/objects/concrete base.ive')
			base1.setPosition(-17.5,0,-6.5)
			base1.scale(.2,.2,.2)
			self.pumpR = Machinery.Pump(self.factory, [-20.3,2.8,-6.5], [-90,0,0])
			self.machines['pumpR'] = self.pumpR
			base2=self.factory.add('models/objects/concrete base.ive')
			base2.setPosition(-20.8,0,-6.5)
			base2.scale(.2,.2,.2)
			# wheels and belts
			wheel_pumpL = viz.add('models/objects/wheel.ive', parent=self.factory, cache=viz.CACHE_CLONE)
			wheel_pumpL.setPosition(-16.77,5.77,-7.143)
			belt_pumpL = self.factory.add('models/objects/belt_pump.ive')
			belt_pumpL.setPosition(-16.77,5.77,-7.143)
			belt_pumpL.setEuler(0,85.5,0)
			self.wheels['pumpL'] = [wheel_pumpL]
			self.belts['pumpL']  = [belt_pumpL]
			wheel_pumpR = viz.add('models/objects/wheel.ive', parent=self.factory, cache=viz.CACHE_CLONE)
			wheel_pumpR.setPosition(-20.1,5.77,-7.143)
			belt_pumpR = self.factory.add('models/objects/belt_pump.ive')
			belt_pumpR.setPosition(-20.1,5.77,-7.143)
			belt_pumpR.setEuler(0,85.5,0)
			self.wheels['pumpR'] = [wheel_pumpR]
			self.belts['pumpR']  = [belt_pumpR]
		if 'press' in args:	#ADD THE 2 PRESSES
			self.pressL = Machinery.Press(self.factory, [-17.4,0,6.5], [180,0,0])
			self.pressR = Machinery.Press(self.factory, [-14.4,0,6.5], [180,0,0])
			self.machines['pressL'] = self.pressL
			self.machines['pressR'] = self.pressR
		if 'laval' in args:		#ADD THE 2 LAVALS
			self.lavalR = Machinery.Laval(self.factory, [-7.65,0,-5.81], [180,0,0])
			self.machines['lavalR'] = self.lavalR
			self.lavalL = Machinery.Laval(self.factory, [-4.65,0,-5.81], [180,0,0])
			self.machines['lavalL'] = self.lavalL
			# wheels and belts
			wheel_lavalL = viz.add('models/objects/wheel.ive', parent=self.factory, cache=viz.CACHE_CLONE)
			wheel_lavalL.setPosition(-4, 5.77, -7.143)
			belt_lavalL = viz.add('models/objects/belt_laval.ive', parent=self.factory, cache=viz.CACHE_CLONE)
			belt_lavalL.setPosition(-3.95, 0.893, -6.992)
			self.wheels['lavalL'] = [wheel_lavalL]
			self.belts['lavalL']  = [belt_lavalL]
			wheel_lavalR = viz.add('models/objects/wheel.ive', parent=self.factory, cache=viz.CACHE_CLONE)
			wheel_lavalR.setPosition(-7,5.77,-7.143)
			belt_lavalR = viz.add('models/objects/belt_laval.ive', parent=self.factory, cache=viz.CACHE_CLONE)
			belt_lavalR.setPosition(-6.95, 0.893, -6.992)
			self.wheels['lavalR'] = [wheel_lavalR]
			self.belts['lavalR']  = [belt_lavalR]
				
		#get all components from machines and store them in factory.components
		self.AddComponentsToFactory()
		
	def AddComponentsToFactory(self):
		for m in self.machines.values():
			try:
				for cName, cObj in m.components.iteritems():
					self.components[cName] = cObj
				for cObj, cPos in m.componentPos.iteritems():
					self.componentPos[cObj] = cPos
			except:
				pass
	
	def AddOtherStuff(self):
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
		self.tools[tool] = self.factory.add('models/objects/tool_'+tool+'.ive')
		self.tools[tool].setPosition(self.toolsData[tool][0])
		self.tools[tool].setEuler(self.toolsData[tool][1])
		if self.toolsData[tool][2]:	#no physics for the shovel
			self.tools[tool].collideBox()
		
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
			if  self.belts.has_key(m):	#check if this machine has wheels
				for b in self.belts[m]:
					if m == 'lavalL':
						global matrix1, matrix2, belt, timer
						matrix1 = vizmat.Transform()
						matrix2 = vizmat.Transform()
						belt = b
						timer = vizact.ontimer(.01, self.TurnBelt)
					
	def TurnBelt(self):
		#belt=oliveFactory.belts['lavalL'][0]
		global matrix1, matrix2, belt
		matrix1.postTrans(0,.04,0)
		matrix2.postTrans(0,-.04,0)
		belt.texmat(matrix1,'belt1',0)
		belt.texmat(matrix2,'belt2',0)
		
	def StopFactory(self):
		self.started = False
		for m, machine in self.machines.iteritems():
			machine.Stop()
			if  self.wheels.has_key(m):
				for w in self.wheels[m]:
					w.endAction()
		
	def RemoveFactory (self):
		self.factory.remove(children = True)
		
if __name__ == '__main__':
	viz.go()

	viz.phys.enable()
	viz.eyeheight = 2.0
	viz.MainView.setPosition(-10,2,-5)
	#viz.MainView.setEuler(-90,0,0)
	#viz.fov(60)
	#viz.collision(viz.ON)
	viz.clearcolor(viz.SKYBLUE)
	
	oliveFactory = Factory()
	oliveFactory.AddMachinery('laval')
	oliveFactory.AddAllTools()