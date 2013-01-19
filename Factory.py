"""
Shows how to use a joystick or gamepad in your script.
Move the car with with the joystick and press any button to drop a duck.
"""

import viz
import vizact
import vizjoy
#import Pump, Mill, Engine, Press, Laval
import Machinery


class Factory ():
	'''This is the self.factory class'''
	
	#factory = viz.add('models/factory.osgb')
	
	def __init__ (self):
		self.factory = viz.add('models/factory.osgb')
		self.toolsData = {'wrench': [[16.75,1.5,5],[30,0,0], True], 'shovel': [[15,0.5,7.55],[0,-80,0],False], 
				'hammer': [[16.75,1.5,4],[45,0,0], True]}
		self.machines = []
		self.components = {}
		self.componentPos = {}
		self.tools = {}		
		
	def AddMachinery(self):
		#ADD THE ENGINE
		self.engine = Machinery.Engine(self.factory, [0.58, .6, 2.97], [-90,0,0])
		self.machines.append(self.engine)
		#ADD THE BOILER
		self.boiler = Machinery.Boiler(self.factory, [7.1,0,0])
		self.machines.append(self.boiler)
		# ADD THE 2 MILLS
#		self.mill_R = Machinery.Mill(self.factory, [-3.7,0,6.5], [45,0,0])
#		self.mill_L = Machinery.Mill(self.factory, [-24.7,0,6.5], [0,0,0])
#		#ADD THE 2 PUMPS
#		self.pump_L = Machinery.Pump(self.factory, [-17,2.8,-6.5], [-90,0,0])
#		base1=self.factory.add('models/objects/concrete base.ive')
#		base1.setPosition(-17.5,0,-6.5)
#		base1.scale(.2,.2,.2)
#		self.pump_R = Machinery.Pump(self.factory, [-20.3,2.8,-6.5], [-90,0,0])
#		base2=self.factory.add('models/objects/concrete base.ive')
#		base2.setPosition(-20.8,0,-6.5)
#		base2.scale(.2,.2,.2)
#		#ADD THE 2 PRESSES
#		self.press_L = Machinery.Press(self.factory, [-17.4,0,6.5], [180,0,0])
#		self.press_R = Machinery.Press(self.factory, [-14.4,0,6.5], [180,0,0])
#		#ADD THE 2 LAVALS
#		self.laval_R = Machinery.Laval(self.factory, [-7.7,0,-6.5], [180,0,0])
#		self.laval_R = Machinery.Laval(self.factory, [-4.7,0,-6.5], [180,0,0])
#		#WHEELS & BELS
		# Engine
		self.wheel_engine=self.factory.add('models/objects/wheel.ive')
		self.wheel_engine.setPosition(0.75,5.77,-7.143)
		belt_engine=self.factory.add('models/objects/belt_engine.ive')
		belt_engine.setPosition(0.75,5.77,-7.143)
		belt_engine.setEuler(0,27.1,0)
#		#Mills
#		self.wheel_millR = self.factory.add('models/objects/wheel.ive')
#		self.wheel_millR.setPosition(-1.6,5.77,-7.143)
#		belt_millR = self.factory.add('models/objects/belt_mill.ive')
#		belt_millR.setPosition(-1.6,5.77,-7.143)
#		belt_millR.setEuler(0,11.4,0)
#		self.gear_millR = belt_millR.getChild('motion gear')
#		self.gear_millR.center(0,0,13.953)
#	
#		self.wheel_millL = self.factory.add('models/objects/wheel.ive')
#		self.wheel_millL.setPosition(-26.8,5.77,-7.143)
#		belt_millL = self.factory.add('models/objects/belt_mill.ive')
#		belt_millL.setPosition(-26.8,5.77,-7.143)
#		belt_millL.setEuler(0,11.4,0)
#		self.gear_millL = belt_millL.getChild('motion gear')
#		self.gear_millL.setEuler(180,0,0)
#		self.gear_millL.center(0,0,13.953)
#		#Pumps
#		self.wheel_pumpL = self.factory.add('models/objects/wheel.ive')
#		self.wheel_pumpL.setPosition(-16.77,5.77,-7.143)
#		belt_pumpL = self.factory.add('models/objects/belt_pump.ive')
#		belt_pumpL.setPosition(-16.77,5.77,-7.143)
#		belt_pumpL.setEuler(0,85.5,0)
#	
#		self.wheel_pumpR = self.factory.add('models/objects/wheel.ive')
#		self.wheel_pumpR.setPosition(-20.1,5.77,-7.143)
#		belt_pumpR = self.factory.add('models/objects/belt_pump.ive')
#		belt_pumpR.setPosition(-20.1,5.77,-7.143)
#		belt_pumpR.setEuler(0,85.5,0)
		
		#get all components from machines and store them in factory.components
		self.AddComponentsToFactory()
		
	def AddComponentsToFactory(self):
		for m in self.machines:
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
		self.engine.startEngine()
		self.wheel_engine.addAction(vizact.spin(1,0,0, -76,viz.FOREVER))
#		self.mill_L.startMill(1)
#		self.wheel_millR.addAction(vizact.spin(1,0,0, -76,viz.FOREVER))
#		self.gear_millR.addAction(vizact.spin(1,0,0, -76,viz.FOREVER))
#		self.mill_R.startMill(-1)
#		self.wheel_millL.addAction(vizact.spin(1,0,0, -76,viz.FOREVER))
#		self.gear_millL.addAction(vizact.spin(1,0,0, 76,viz.FOREVER))
#		self.pump_L.startPump()
#		self.wheel_pumpL.addAction(vizact.spin(1,0,0, -76,viz.FOREVER))
#		self.pump_R.startPump()
#		self.wheel_pumpR.addAction(vizact.spin(1,0,0, -76,viz.FOREVER))
	
	def StopFactory(self):
		self.engine.stopEngine()
		self.wheel_engine.endAction()
		
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