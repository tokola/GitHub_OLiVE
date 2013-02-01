import viz
import vizact

viz.go()

class Pump():
	"""This is the Pump class"""
	def __init__(self, factory, pos, eul):
		self.object = factory.add('models/pump.ive')
		self.object.setScale(.0015,.0015,.0015)
		self.object.setPosition(pos)
		self.object.setEuler(eul)
		#fix swlinaki
		self.object.getChild('swlinaki').setPosition(0,20,-40)
		#Add individual objects (wheel, shaft, connection rods, pistons)
		self.wheel = self.object.add('models/pump_wheel.ive', pos=(-243.232,-372.44,311.102))
		self.shaft = self.object.add('models/pump_crankshaft.ive', pos=(13.245,-196.394,738.167))
		self.rodL = self.object.add('models/pump_conrodL.ive', pos=(13.245,-196.394,738.167))
		self.rodL.center(0,-514.739,-539.148)
		self.rodR = self.object.add('models/pump_conrodR.ive', pos=(13.245,-196.394,738.167))
		self.rodR.center(0,-448.407, -237.04)
		self.pistonL = self.object.add('models/pump_pistonL.ive', pos=(13.245,-196.394,738.167))
		self.pistonR = self.object.add('models/pump_pistonR.ive', pos=(13.245,-196.394,738.167))
		
	def Start (self):
		#reset component position
		self.wheel.setPosition(-243.232,-372.44,311.102)
		self.shaft.setPosition(13.245,-196.394,738.167)
		self.shaft.setEuler(0,0,0)
		self.rodL.setPosition(13.245,-196.394,738.167)
		self.rodR.setPosition(13.245,-196.394,738.167)
		self.rodL.setEuler(0,0,0)
		self.rodR.setEuler(0,0,0)
		self.pistonL.setPosition(13.245,-196.394,738.167)
		self.pistonR.setPosition(13.245,-196.394,738.167)
		self.pistonL.setEuler(0,0,0)
		self.pistonR.setEuler(0,0,0)
		#self.wheel.setEuler(0,0,0)
		self.wheel.addAction(vizact.spin(0,0,1, 76,viz.FOREVER))
		self.shaft.addAction(vizact.spin(0,0,1,-36,viz.FOREVER))
		#set the left rod's action (rotation and transform)
		moveRodUp = vizact.moveTo([13.245,-130,738.167], time=5)
		moveRodDown = vizact.moveTo([13.245,-196.394,738.167], time=5)
		rodLTransform = vizact.sequence([moveRodUp, moveRodDown], viz.FOREVER)
		spinRodFw = vizact.spin(0,0,1, 2, 2.5)
		spinRodBw = vizact.spin(0,0,1, -2, 2.5)
		rodLRotation = vizact.sequence([spinRodFw, spinRodBw, spinRodBw, spinRodFw], viz.FOREVER)
		rodLMotion = vizact.parallel(rodLTransform, rodLRotation)
		#set the right rod's action (rotation and transform)
		moveRodRUp = vizact.moveTo([13.245,-196.394,738.167], time=5)
		moveRodRDown = vizact.moveTo([13.245,-262,738.167], time=5)
		rodRTransform = vizact.sequence([moveRodRDown, moveRodRUp], viz.FOREVER)
		rodRRotation = vizact.sequence([spinRodBw, spinRodFw, spinRodFw, spinRodBw], viz.FOREVER)
		rodRMotion = vizact.parallel(rodRTransform, rodRRotation)
		# start moving the rods
		self.rodL.addAction(rodLMotion)
		self.rodR.addAction(rodRMotion)
		# start moving the pistons
		pistonLTransform = vizact.sequence([moveRodUp, moveRodDown], viz.FOREVER)
		self.pistonL.addAction(pistonLTransform)
		pistonRTransform = vizact.sequence([moveRodRDown, moveRodRUp], viz.FOREVER)
		self.pistonR.addAction(pistonRTransform)
		
	def Stop (self):
		self.wheel.endAction()
		self.shaft.endAction()
		self.rodL.endAction()
		self.rodR.endAction()
		self.pistonL.endAction()
		self.pistonR.endAction()
		
class Mill ():
	"""This is the Mill class"""
	def __init__(self, factory, pos, eul, LR):	#LR='L' or 'R'
		self.object = factory.add('models/mill.osgb')
		self.object.setScale(.32,.32,.32)
		self.object.setPosition(pos)
		self.object.setEuler(eul)
		dirs = {'L': 1, 'R': -1}	#direction of rotation according to mill
		self.direction = dirs[LR]
		#self.wheels = self.object.getChild('wheels')
		#self.wheels.setCenter(0,3.954,0)
		self.object.getChild('wheels').remove()
		self.wheels=self.object.add('models/mill_wheel.ive', pos=[0,3.964,0])
		#get the nodes used for animation
		self.rotationAxis = self.object.getChild('rotation_axis')
		self.wL = self.wheels.getChild('WheelL')
		self.wR = self.wheels.getChild('WheelR')
		
	def Start (self):
		self.rotationAxis.addAction(vizact.spin(0,1,0,35*self.direction,viz.FOREVER))
		self.wheels.addAction(vizact.spin(0,1,0,35*self.direction,viz.FOREVER))
		self.wL.addAction(vizact.spin(1,0,0,35*self.direction,viz.FOREVER))
		self.wR.addAction(vizact.spin(1,0,0,35*(-self.direction),viz.FOREVER))
		
	def Stop (self):
		self.rotationAxis.endAction()
		self.wheels.endAction()
		self.wL.endAction()
		self.wR.endAction()
		
class Engine ():
	"""This is the Engine class"""
	def __init__(self, factory, pos, eul):
		self.object = factory.add('models/engine.osgb')
		self.object.setPosition(pos)
		self.object.setEuler(eul)
		self.engine_system = self.object.getChild('rotation_system')
		self.getComponents()

	#Get the engine working
	def Start (self):
		self.engine_system.addAction(vizact.spin(0,0,1, 76,viz.FOREVER))
		
	def Stop (self):
		self.engine_system.endAction()
		
	def getComponents (self):
		self.components = {}
		self.componentPos = {}
		valve = self.object.getChild('valve')
		valve.center(-2.76,.475,-1.563)
		self.components['valve'] = valve
		self.componentPos[valve] = [1.563+.58, .6+.475, 2.97-2.76]
		
	def E_openValve (self, time):
		self.components['valve'].addAction(vizact.spin(0,0,1,360,time))
		
	def E_closeValve (self, time):
		self.components['valve'].addAction(vizact.spin(0,0,1,-360,time))
		
class Press ():
	"""This is the Press class"""
	def __init__(self, factory, pos, eul):
		self.object = factory.add('models/press.osgb')
		self.object.setScale(.045,.045,.045)
		self.object.setPosition(pos)
		self.object.setEuler(eul)

	#Get the engine working
	def Start (self):
		pass
		
	#Get the engine working
	def Stop (self):
		pass
		
		
class Laval ():
	"""This is the Laval class"""
	def __init__(self, factory, pos, eul):
		self.object = factory.add('models/laval.ive')
		self.object.setPosition(pos)
		self.object.setEuler(eul)
		self.power_wheel = self.object.getChild('power_wheel')
		self.power_wheel.center(-.507, .433, .067)
		self.wheel = self.object.getChild('wheel')
		self.wheel.center(-.556, .891, 1.174)
		self.belt = self.object.getChild('belt_laval')
		self.getComponents()

	def getComponents (self):
		self.components = {}
		self.componentPos = {}
		self.components['wheel'] = self.wheel
		lavalPos = self.object.getPosition()
		self.componentPos[self.wheel] = [lavalPos[0]+.56, lavalPos[1]+.9, lavalPos[2]-1.174]
		self.components['powerWheel'] = self.power_wheel
		self.componentPos[self.power_wheel] = [lavalPos[0]+.5, lavalPos[1]+.5, lavalPos[2]]
		
	#Get the engine working
	def Start (self):
		self.power_wheel.addAction(vizact.spin(1,0,0, 76,viz.FOREVER))
		self.wheel.addAction(vizact.spin(1,0,0, 76,viz.FOREVER))
		
	def Stop (self):
		self.power_wheel.endAction()
		self.wheel.endAction()
	
	def detachBelt (self):
		self.belt.visible(0)
		
	def attachBelt (self):
		self.belt.addAction(vizact.fadeTo(1, begin=0, time=1))
		self.belt.visible(1)
		
class Boiler ():
	"""This is the Boiler class"""
	def __init__(self, factory, pos):
		self.object = factory.add('models/boiler.ive')
		self.hatch = (self.object.getChild('HatchDoorL'), self.object.getChild('HatchDoorR'))
		self.hatch[0].center(-.247, 1.494, -.253)
		self.hatch[1].center(.536, 1.504, -.242)
		self.gauge = self.object.getChild('velona')
		self.gauge.center(.25, 2.776, .248)
		fire = viz.add('textures/fire.avi', loop=1, play=1)
		self.fire = viz.addTexQuad(texture=fire, pos=[7.2,1.2,0], alpha=0)
		self.fire.visible(0)
		self.object.setPosition(pos)
		self.getComponents()
		
	def Start (self):
		pass
		
	def Stop (self):
		pass
		
	def getComponents (self):
		self.components = {}
		self.componentPos = {}
		coal = self.object.getChild('coal')
		self.components['coal'] = coal
		coalLoad = self.object.getChild('coalInside')
		self.components['coalfurnace'] = coalLoad
		coalLoad.visible(0)
		coalLoad.alpha(0)
		boiPos = self.object.getPosition()
		self.componentPos[coal] = [boiPos[0]+1.5, boiPos[1]+.23, boiPos[2]-.6]
		self.componentPos[coalLoad] = boiPos
		
	def changePressure(self, pressure):
		self.gauge.endAction()
		presToAngle = {4500: 270, 3000: 180, 1500: 90, 0:0}
		angle = presToAngle[pressure]
		ease = vizact.easeInOut
		# spin to 180 degrees first, because spinTo chooses the shortest path (CCW in this case)
		if angle == 270:
			incPress = vizact.spinTo(euler=[0,0,-180], time=5, interpolate=vizact.easeIn)
			self.gauge.addAction(incPress)
			ease = vizact.easeOut
		incPress = vizact.spinTo(euler=[0,0,-angle], time=5, interpolate=ease)
		self.gauge.addAction(incPress)
		
	def openCloseHatch(self, open):	#open=True or False
		angle = 120 * open
		openLeft = vizact.spinTo(euler=[angle,0,0], time=2, interpolate=vizact.easeOut)
		openRight = vizact.spinTo(euler=[-angle,0,0], time=2, interpolate=vizact.easeOut)
		self.hatch[0].addAction(openLeft)
		self.hatch[1].addAction(openRight)
		
	def coalAction(self, act):	#act=1->load, 2->light, 3->waste
		coalFurnace = self.components['coalfurnace']
		if act == 1:	#fade in the coals
			coalFurnace.addAction(vizact.method.visible(1))
			coalFurnace.addAction(vizact.fadeTo(1, begin=0, time=1))
		elif act == 2:	#turn coals red and light fire
			fireSignal = vizact.signal()
			coalFurnace.addAction(vizact.fadeTo(viz.RED, time=2))
			coalFurnace.addAction(fireSignal.trigger)
			cPos = coalFurnace.getPosition()
			coalFurnace.addAction(vizact.moveTo([cPos[0],cPos[1],cPos[2]+.1],time=.5))
			self.fire.addAction(fireSignal.wait)
			self.fire.addAction(vizact.method.visible(1))
			self.fire.addAction(vizact.fadeTo(0.5, time=.5))
			self.fire.addAction(vizact.call(self.openCloseHatch, False))
		elif act == 3:	#fade out the coals and fire
			coalFurnace.addAction(vizact.fadeTo(0.25, time=.5))
			self.fire.addAction(vizact.fadeTo(0.25, time=.5))
		elif act == 4:	#fade out the coals and fire completely
			coalFurnace.addAction(vizact.fadeTo(0, time=.5))
			coalFurnace.addAction(vizact.method.setPosition([0,0,0]))
			coalFurnace.addAction(vizact.method.color(viz.GRAY))
			coalFurnace.addAction(vizact.method.visible(0))
			self.fire.addAction(vizact.fadeTo(0, time=.5))
			self.fire.addAction(vizact.method.visible(0))