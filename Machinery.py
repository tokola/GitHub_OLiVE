import viz
import vizmat
import vizact
import vizproximity

viz.go()

SOUNDS_ENABLED = 0

class Pump():
	"""This is the Pump class"""
	def __init__(self, factory, pos, eul, LR, faClass):
		self.object = factory.add('models/pump.ive')
		self.object.setScale(.0014,.0014,.0014)
		self.object.setPosition(pos)
		self.object.setEuler(eul)
		self.LR = LR
		self.faClass = faClass	#the factory class used to get the belts
		base = factory.add('models/objects/concrete base.ive')
		base.setPosition(pos[0]-.5,0,pos[2])
		base.scale(.2,.2,.2)
		#Add individual objects (wheel, shaft, connection rods, pistons)
		wheel = self.object.add('models/pump_wheels.ive', pos=(-243.232,-372.44,311.102))
		self.gear = wheel.getChild('mainGear')
		self.crazy = wheel.getChild('crazyWheel')
		self.shaft = self.object.add('models/pump_crankshaft.ive', pos=(13.245,-196.394,738.167))
		self.rodL = self.object.add('models/pump_conrodL.ive', pos=(13.245,-196.394,738.167))
		self.rodL.center(0,-514.739,-539.148)
		self.rodR = self.object.add('models/pump_conrodR.ive', pos=(13.245,-196.394,738.167))
		self.rodR.center(0,-448.407, -237.04)
		self.pistonL = self.object.add('models/pump_pistonL.ive', pos=(13.245,-196.394,738.167))
		self.pistonR = self.object.add('models/pump_pistonR.ive', pos=(13.245,-196.394,738.167))
		# load other moving parts
		self.gauge = self.object.getChild('gaugeNeedle')
		self.gauge.center(229.246, -654.955, 642.767)
		self.bar = self.object.getChild('pressureBar')
		self.bar.center(44.983, -813.081, 413.712)
		self.barRod = self.object.getChild('pressureRod')
		self.barRod.center(-50.902, -862.024, 426.787)
		self.getComponents()
		#this is called by the AddProximitySensors() of the main module
		self.proximityData = (vizproximity.RectangleArea([16,20]), base)
		
	def getComponents (self):
		self.components = {}
		self.componentPos = {}
		valve = self.object.getChild('bypassValve')
		valve.center(169.156, -858.204, 350.093)
		self.components['bypass'+self.LR] = valve
		self.componentPos[valve] = self.object.getPosition()
		guide = self.object.getChild('beltGuide')
		self.components['guide'+self.LR] = guide
		self.componentPos[guide] = self.object.getPosition()
		
	def ChangeGuide (self, dir):	#dir=1 -> move right, -1 -> move left
		guide = self.components['guide'+self.LR]
		pos = guide.getPosition()
		newPos = [pos[0], pos[1], pos[2]+100*dir]
		self.faClass.belts['pump'+self.LR].MoveBelt(dir, .135)
		guide.addAction(vizact.moveTo(newPos, time=2, interpolate=vizact.easeInOut))
	
	def TurnValve (self, dir):
		self.components['bypass'+self.LR].addAction(vizact.spin(1*dir,0,0,360,3))
		
	def ChangePressure(self, pressure, duration):
		self.gauge.endAction()
		angle = int(pressure) * 0.06
		ease = vizact.easeInOutCubic
		# spin to 180 degrees first, because spinTo chooses the shortest path (CCW in this case)
		if angle == 0:
			incPress = vizact.spinTo(euler=[0, 180, 0], time=2, interpolate=vizact.easeIn)
			self.gauge.addAction(incPress)
			ease = vizact.easeOut
		incPress = vizact.spinTo(euler=[0, angle, 0], time=int(duration), interpolate=ease)
		self.gauge.addAction(incPress)
	
	def LiftBar (self, flag):
		self.bar.addAction(vizact.spinTo(euler=[0,0,-20*flag], time=5, interpolate=vizact.easeOut))
		self.barRod.addAction(vizact.moveTo([0,40*flag,0], time=5, interpolate=vizact.easeOut))
		
	def StartCrazy (self):
		self.crazy.addAction(vizact.spin(0,0,1, 90,viz.FOREVER))
		
	def StopCrazy (self):
		self.crazy.endAction()
		
	def SetMotion (self):
		#reset component position
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
		self.gear.addAction(vizact.spin(0,0,1, 90,viz.FOREVER))
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
		
	def EndMotion (self):
		self.gear.endAction()
		self.shaft.endAction()
		self.rodL.endAction()
		self.rodR.endAction()
		self.pistonL.endAction()
		self.pistonR.endAction()
	
	def Start (self):
		self.StartCrazy()
		
	def Stop (self):
		self.StopCrazy()
		self.EndMotion()
		
		
class Mill ():
	"""This is the Mill class"""
	def __init__(self, factory, pos, eul, LR):	#LR='L' or 'R'
		self.object = factory.add('models/mill.osgb')
		self.object.setPosition(pos)
		self.object.setEuler(eul)
		self.LR = LR
		self.factory = factory
		dirs = {'L': 1, 'R': -1}	#direction of rotation according to mill
		self.direction = dirs[LR]
		#get the nodes used for animation
		self.rotationAxis = self.object.getChild('rotation_axis')
		self.tankPulp = self.object.getChild('pulp')
		self.tankPulp.pick_parent = True	#used in the Player.CheckPickObject() function
		self.pourPulp = self.object.getChild('pourPulp')
		self.pourPulp.alpha(0)
		self._usedSackCounter = 0
		self.getComponents()
		#this is called by the AddProximitySensors() of the main module
		self.proximityData = (vizproximity.CircleArea(3), self.object)
	
	def getComponents (self):
		self.components = {}
		self.componentPos = {}
		millPos = self.object.getPosition()
		self.wheels = self.object.getChild('wheels')
		self.components['wheels'+self.LR] = self.wheels
		self.wL = self.wheels.getChild('WheelL')
		self.wL.pick_parent = True	#used in the Player.CheckPickObject() function
		self.wR = self.wheels.getChild('WheelR')
		self.wR.pick_parent = True	#used in the Player.CheckPickObject() function
		self.componentPos[self.wheels] = [millPos[0], millPos[1]+1, millPos[2]]
		# Add the paste
		self.mixedPulp = self.object.getChild('mixedPulp')
#		self.mixedPulp.enable(viz.SAMPLE_ALPHA_TO_COVERAGE)
#		self.mixedPulp.disable(viz.BLEND)
#		self.mixedPulp.drawOrder(-10, node='olives')	#make sure olives are drawn first
		self.mixedPulp.getChild('olives').setAnimationSpeed(.75)
		self.mixedPulp.setPosition(0,-.35,0)
		self.mixedPulp.setScale(.85,1,.85)
		justPaste = self.mixedPulp.insertGroupBelow('paste')
		justPaste.alpha(0)
		justPaste.visible(0)
		self.components['paste'+self.LR] = justPaste
		self.componentPos[justPaste] = [millPos[0], millPos[1]+1, millPos[2]]
		# Add the hatch
		hatch = self.object.getChild('hatch')
		hatch.center(.28, .879, -.907)
		self.components['hatch'+self.LR] = hatch
		self.componentPos[hatch] = [millPos[0]+.28, millPos[1]+.879, millPos[2]-.907]
		# Add the tank
		tank = self.object.getChild('tank')
		tank.center(.373, .252, -1.03)
		self.components['tank'+self.LR] = tank
		self.componentPos[tank] = [millPos[0]+.373, millPos[1]+1, millPos[2]-1.03]
		#once the following line is called the tank stops reacting to intersections
		#self.componentPos[tank] = self.object.getChild('tank-GEODE').getPosition(viz.ABS_GLOBAL)
		self.AddSacks()
	
	def AddSacks (self):
		self.sackItem = viz.add('models/objects/sack'+self.LR+'.osgb')
		#The alpha is being applied as part of the material, but both sacks use the same material. 
		#Vizard preserves material instancing by default, but you can break the instancing using...
		self.sackItem.hint(viz.COPY_SHARED_MATERIAL_HINT)
		self.sackItem.alpha(0, 'sack_pouring')
		self.sackPour = self.sackItem.getChild('sack_pouring')
		self.sackPour.center(-3.905, 1.504, 8.611)
		sack_path = self.sackItem.getChild('path1'+self.LR)
		sack_path.setAnimationLoopMode(0)
		sack_path.setAnimationSpeed(0)
		sack_path = self.sackItem.getChild('path2'+self.LR)
		sack_path.setAnimationLoopMode(0)
		sack_path.setAnimationSpeed(0)
		#create a new group below 'sack' and adopt its children to keep pivot point
		sack1 = self.sackItem.insertGroupBelow('sack1'+self.LR)
		sack2 = self.sackItem.insertGroupBelow('sack2'+self.LR)
		self.components['sack1'+self.LR] = sack1
		self.components['sack2'+self.LR] = sack2
		if self.LR == 'R':
			self.componentPos[sack1] = [-1.4, 2, 9.5]
			self.componentPos[sack2] = [-1.4, 2, 10.7]
		else:
			self.componentPos[sack1] = [-26.4, 2, 10.27]
			self.componentPos[sack2] = [-26.4, 2, 11.43]
		
	def SackAnim (self, sid):	#sid is the sack id: {1R, 2R, 1L, or 2L}
		self._usedSackCounter += 1
		sack = self.components['sack'+sid]
		self.sack_path = self.sackItem.getChild('path'+sid).copy()
		sack.setParent(self.sack_path, node='path'+sid)
		self.sack_path.setAnimationSpeed(1)
		sack.addAction(vizact.waittime(3))	#wait for sack animation
		endAnimSignal = vizact.signal()
		trig = endAnimSignal.trigger
		hide = vizact.method.visible(0)
		sack.addAction(vizact.parallel(hide, trig))
		self.sackPour.addAction(endAnimSignal.wait)	# wait for animation before pouring starts
		self.sackPour.addAction(vizact.method.alpha(1, node='sack_bent'))
		self.sackPour.addAction(vizact.spinTo(euler=[0,-45,0], time=.75, interpolate=vizact.easeInStrong))
		self.sackPour.addAction(vizact.fadeTo(1, begin=0, time=.5, node='olive_flow'))
		loadSignal = vizact.signal()
		self.sackPour.addAction(loadSignal.trigger)
		self.sackPour.addAction(vizact.waittime(5))
		self.sackPour.addAction(vizact.fadeTo(0, time=.5))
		self.sackPour.addAction(vizact.method.setEuler([0,0,0]))	# put it back standing
		self.mixedPulp.addAction(loadSignal.wait)	# wait for olive pouring before pulp appears
		self.mixedPulp.addAction(vizact.method.visible(1))
		#self.mixedPulp.addAction(vizact.fadeTo(1, begin=0, time=1, node='olives'))
		move = vizact.moveTo([0, 0, 0], time=5)
		resize = vizact.sizeTo([1, 1, 1], time=5, interpolate=vizact.easeIn)
		self.mixedPulp.addAction(vizact.parallel(move, resize))
		self.sack_path.addAction(loadSignal.wait)
		self.sack_path.addAction(vizact.method.setAnimationSpeed(-100))	#put sack back
	
	def OlivesToPaste (self):
		justPaste = self.components['paste'+self.LR]
		#adjust draw order to make sure the paste is transparent
		self.mixedPulp.setTransparentDrawOrder(node='paste')
		justPaste.addAction(vizact.method.visible(1))
		justPaste.addAction(vizact.fadeTo(1, begin=0, time=30, interpolate=vizact.easeInCubic))
			
	def WastePaste (self):
		self.mixedPulp.addAction(vizact.fadeTo(0, time=1))
		self.mixedPulp.addAction(vizact.method.setScale(.85,1,.85))
		self.mixedPulp.addAction(vizact.method.setPosition(0,-.35,0))
		self.mixedPulp.addAction(vizact.method.visible(1))
		self.mixedPulp.addAction(vizact.method.alpha(1, node='olives'))
	
	def ReplenishSacks (self):	#replenish sacks every two that are wasted
		if not (self._usedSackCounter % 2):
			self.components['sack1'+self.LR].visible(1)
			self.components['sack2'+self.LR].visible(1)
		
	def PasteInTank (self):
		hatch = self.components['hatch'+self.LR]
		hatch.addAction(vizact.moveTo([.3-.275, .976-.879, -0.956+.907], time=1, interpolate=vizact.easeInOut))
		hatch.addAction(vizact.waittime(1))
		openSignal = vizact.signal()
		hatch.addAction(openSignal.trigger)
		# code for pouring animation
		self.pourPulp.addAction(openSignal.wait)
		self.pourPulp.addAction(vizact.fadeTo(1, time=.5))
		self.pourPulp.addAction(vizact.waittime(5))
		self.pourPulp.addAction(vizact.fadeTo(0, time=.5))
		self.tankPulp.addAction(openSignal.wait)
		self.tankPulp.addAction(vizact.waittime(.5))
		self.tankPulp.addAction(vizact.moveTo([0,.4,0], time=5, interpolate=vizact.easeOut))
		self.mixedPulp.addAction(openSignal.wait)
#		self.mixedPulp.addAction(vizact.fadeTo(0, time=5))
		move = vizact.moveTo([0, -.28, 0], time=5, interpolate=vizact.easeOut)
		resize = vizact.sizeTo([.85,1,.85], time=5, interpolate=vizact.easeOut)
		self.mixedPulp.addAction(vizact.parallel(move, resize))
		
	def MoveTank (self):
		#change tank and cart animation depending on mill
		if self.LR == 'L':
			offset = .50
			self.cart = self.factory.add('models/objects/cart.osgb', pos = [-23.835,0,3.97])
		else:
			offset = 0
			self.cart = self.factory.add('models/objects/cart.osgb', pos = [-5.2166,0,4.448])
		self.cart.setEuler(360*offset,0,0)	#millL: rotate 180 deg
		cTank = self.cart.insertGroupBelow('tank')
		cTank.visible(0)
		cTank.alpha(0, node='pourPulp')
		tank = self.components['tank'+self.LR]
		tank.addAction(vizact.moveTo([-0.25+offset,0,-.5], time=1, interpolate=vizact.easeInOutSine))
		tank.addAction(vizact.moveTo([-0.25+offset,.5,-.5], time=.5, interpolate=vizact.easeInOutSine))
		tank.addAction(vizact.spinTo(euler=[60-270*offset,0,0], time=.5))	#millL: rotate -75 deg
		tank.addAction(vizact.moveTo([offset,.5,-1.5], time=1, interpolate=vizact.easeInOutSine))
		tank.addAction(vizact.moveTo([offset,.2,-1.5], time=.5, interpolate=vizact.easeInSine))
		waitLoad = vizact.signal()
		tank.addAction(waitLoad.trigger)
		tank.addAction(vizact.method.visible(0))
		cTank.addAction(waitLoad.wait)
		cTank.addAction(vizact.method.visible(1))
		self.cart.addAction(waitLoad.wait)
		self.cart.addAction(vizact.call(self.PlayAudio, 'cart_roll', self.cart, viz.PLAY))
		self.cart.addAction(vizact.spinTo(euler=[-20+440*offset,0,0], time=.5))	#millL: rotate to 200 deg
		moveCart = vizact.moveTo([-14.65-4.9*offset, 0, .75], time=3, interpolate=vizact.easeInOut)
		rotateCart = vizact.spinTo(euler=[0+360*offset,0,0], time=3)	#millL: rotate to 180 deg
		self.cart.addAction(vizact.parallel(moveCart, rotateCart))
		waitMove = vizact.signal()
		self.cart.addAction(waitMove.trigger)
		cTank.addAction(waitMove.wait)
		cTank.addAction(vizact.moveTo([0,1,-0.1], time=1))
		cTank.addAction(vizact.spinTo(euler=[0,-90,0], time=1))
		cTank.addAction(vizact.fadeTo(1, time=.5, node='pourPulp'))
		cTank.addAction(vizact.fadeTo(0, time=3, node='pulp', interpolate=vizact.easeInExp))
		cTank.addAction(vizact.fadeTo(0, time=.5, node='pourPulp'))
		
	def ResetMill (self):
		hatch = self.components['hatch'+self.LR]
		hatch.addAction(vizact.moveTo([0,0,0], time=1, interpolate=vizact.easeInOut))
		self.tankPulp.setPosition(0,0,0)
		self.components['paste'+self.LR].alpha(0)
		self.components['paste'+self.LR].visible(0)
		tank = self.components['tank'+self.LR]
		tank.setPosition(0,0,0)
		tank.setEuler(0,0,0)
		tank.alpha(0)
		tank.addAction(vizact.method.visible(1))
		tank.addAction(vizact.fadeTo(1, begin=0, time=.5))
		self.tankPulp.setPosition(0,0,0)
		self.cart.getChild('pourPulp').remove()
		self.cart.getChild('pulp').remove()
		self.cart.addAction(vizact.fadeTo(0, time=.5))
		self.cart.addAction(vizact.method.remove())
	
	def Damage (self, flag):
		if flag:
			self.smoke = self.object.add('models/objects/smoke_trail.osg')
			self.smoke.setPosition(0,2,0)
		else:
			self.smoke.remove()
			
	def Start (self):
		self.PlayAudio('mill_grind')
		self.rotationAxis.addAction(vizact.spin(0,1,0,35*self.direction,viz.FOREVER))
		self.wheels.addAction(vizact.spin(0,1,0,35*self.direction,viz.FOREVER))
		self.wL.addAction(vizact.spin(1,0,0,35*self.direction,viz.FOREVER))
		self.wR.addAction(vizact.spin(1,0,0,35*(-self.direction),viz.FOREVER))
		
	def Stop (self):
		self.AdjustAudio(0)
		self.rotationAxis.endAction()
		self.wheels.endAction()
		self.wL.endAction()
		self.wR.endAction()
	
	def PlayAudio (self, audio, obj=None, mode=viz.LOOP):
		if not SOUNDS_ENABLED:
			return
		if obj == None:
			obj = self.object
		sound = obj.playsound('sounds/'+audio+'.wav', mode)
		sound.minmax(5,40)
		if mode == viz.LOOP: #constant machine loop
			self.sound = sound
	
	def AdjustAudio (self, mode): #0-1->volume value, 0->stop
		if not SOUNDS_ENABLED:
			return
		if mode>0:
			self.sound.volume(mode)
		else:
			self.sound.stop()
			
		
class Engine ():
	"""This is the Engine class"""
	def __init__(self, factory, pos, eul):
		self.object = factory.add('models/engine.osgb')
		self.object.setPosition(pos)
		self.object.setEuler(eul)
		self.engine_system = self.object.getChild('rotation_system')
		self.piston = self.object.insertGroupBelow('piston')
		self.rod = self.object.insertGroupBelow('rod')
#		self.rod.setParent(self.piston)
		self.crankshaft = self.object.getChild('crankshaft')
		#the cap is hiden inside the crankshaft and is used to let the rod follow it
		self.cap = self.object.insertGroupBelow('cap')
		self.watt = self.object.insertGroupBelow('watt_regulator')
		self.spool = self.object.insertGroupBelow('karouli')
		self.getComponents()
		#this is called by the AddProximitySensors() of the main module
		base = self.object.insertGroupBelow('middle_base')
		self.proximityData = (vizproximity.RectangleArea([20,8]), base)

	#Get the engine working
	def Start (self):
		self.PlayAudio('steam_engine')
		self.engine_system.addAction(vizact.spin(0,0,1, 90,viz.FOREVER))
		self.watt.addAction(vizact.spin(0,0,1, 90, viz.FOREVER))
		self.spool.addAction(vizact.spin(0,1,0, 90, viz.FOREVER))
		try:
			self.capPrevZPos = self.cap.getPosition(viz.ABS_GLOBAL)[2]
			self._updateFunc.setEnabled(viz.ON)
		except AttributeError:
			self._updateFunc = vizact.onupdate(0, self.update)
	
	def update(self):
		#make the connecting rod look at the cap every frame
		mat = self.rod.getMatrix(viz.ABS_GLOBAL)
#		mat.setTrans( mat.preMultVec( 0,0,-.5) )
		pos = mat.getPosition()
		#look at the cap; eye=rod pos, look at=cap, up vector when engine not rotated is [0,0,1]
		mat.makeLookAt( pos, self.cap.getPosition(viz.ABS_GLOBAL),[1,0,0])
		mat.preEuler([-100.85,0,0])
		self.rod.setQuat( mat.getQuat(), viz.ABS_GLOBAL )
		#now push the piston up
		pistonPos = self.piston.getPosition()
		capShift = self.capPrevZPos - self.cap.getPosition(viz.ABS_GLOBAL)[2]
		self.piston.setPosition(pistonPos[0]-capShift*2.534443502684017, 0, 0)
		self.capPrevZPos = self.cap.getPosition(viz.ABS_GLOBAL)[2]
#		if self.cap.getPosition(viz.ABS_GLOBAL)[2] < 2.66814:
#			print "cap left most: ", self.cap.getPosition(viz.ABS_GLOBAL)[2], self.piston.getPosition()[0]
#		if self.cap.getPosition(viz.ABS_GLOBAL)[2] > 3.2718:
#			print "cap right most: ", self.cap.getPosition(viz.ABS_GLOBAL)[2], self.piston.getPosition()[0]	
	
	def Stop (self):
		self.AdjustAudio(0)
		self.engine_system.endAction()
		self.spool.endAction()
		self.watt.endAction()
		self._updateFunc.setEnabled(viz.OFF)
		
	def getComponents (self):
		self.components = {}
		self.componentPos = {}
		valve = self.object.insertGroupBelow('valve')
		valveBox = valve.add('box.wrl',alpha=0,scale=valve.getBoundingBox().size)
		valveBox.pick_parent = True
		self.components['valve'] = valve
		self.componentPos[valve] = [1.563+.58, .6+.475, 2.97-2.76]
		
	def E_openValve (self, time):
		self.components['valve'].addAction(vizact.spin(0,1,0,360,time))
		
	def E_closeValve (self, time):
		self.components['valve'].addAction(vizact.spin(0,1,0,-360,time))
		
	def PlayAudio (self, audio, obj=None, mode=viz.LOOP):
		if not SOUNDS_ENABLED:
			return
		if obj == None:
			obj = self.object
		sound = obj.playsound('sounds/'+audio+'.wav', mode)
		sound.minmax(3,30)
		if mode == viz.LOOP: #constant machine loop
			self.sound = sound
	
	def AdjustAudio (self, mode): #0-1->volume value, 0->stop
		if not SOUNDS_ENABLED:
			return
		if mode>0:
			self.sound.volume(mode)
		else:
			self.sound.stop()
			
		
class Press ():
	"""This is the Press class"""
	def __init__(self, factory, pos, eul, LR):
		self.object = factory.add('models/press.osgb')
		self.object.setPosition(pos)
		self.object.setEuler(eul)
		self.LR = LR
		self.oilGathered = self.object.getChild('PressVertDrop')
		self.oilGathered.visible(0)
		self.oilGathered.alpha(0)
		self.mats = self.object.getChild('elaiopana')
		self.mats.visible(0)
		self.mats.alpha(0)
#		self.mats.enable(viz.SAMPLE_ALPHA_TO_COVERAGE)
#		self.mats.disable(viz.BLEND)
		self.oilStrain = self.object.getChild('matOil')
		self.oilStrain.drawOrder(50)
		self.oilStrain.visible(0)
		self.oilStrain.alpha(0)
		self.oilDrop = self.object.getChild('OilDropD')
		self.oilDrop.visible(0)
		self.oilDrop.alpha(0)
		self.mat = self.object.getChild('matOnTray')
		self.mat.visible(0)
		self.mat.alpha(0)
		self.oilSurface = self.object.getChild('oilSurface')
		self.oilSurface.setPosition(0,-.22,0)
		self.piston = self.object.getChild('pressPiston')
		#for storing the loaded mats (objects)
		self.loadedMats = []
		self.getComponents()
		#this is called by the AddProximitySensors() of the main module
		self.proximityData = (vizproximity.RectangleArea([3,4]), self.object)
	
	def getComponents (self):
		self.components = {}
		self.componentPos = {}
		pressTray = self.object.getChild('press_tray')
		pos = self.object.getPosition()
		self.components['tray'+self.LR] = pressTray
		self.componentPos[pressTray] = [pos[0], pos[1]+1.5, pos[2]]
	
	def LoadMat (self):
		self.mat2 = self.mat.copy()
		self.mat2.setParent(self.components['tray'+self.LR])
		self.mat2.pick_parent = True		#used in the Player.CheckPickObject() function
		counter = len(self.loadedMats)
		self.loadedMats.append(self.mat2)
		self.mat2.setPosition(0, .24+.01*counter, .01, viz.ABS_PARENT)
		self.mat2.addAction(vizact.method.visible(1))
		self.mat2.addAction(vizact.fadeTo(1, begin=0, time=.5))
		counter += 1
		return counter
			
	def FillUp (self):
		for m in self.loadedMats:
			m.addAction(vizact.fadeTo(0, time=.25))
			m.addAction(vizact.method.remove())
		self.mats.addAction(vizact.method.visible(1))
		self.mats.addAction(vizact.fadeTo(1, begin=0, time=.5))
	
	def RestoreMats (self):
		self.oilStrain.visible(0)
		self.mats.addAction(vizact.fadeTo(0, time=1))
		self.mats.addAction(vizact.method.visible(0))
		self.mats.addAction(vizact.method.setScale(1,1,1))
		self.loadedMats = []
		
	def Pressing (self):
		# start moving the piston upwards (not sure why it's working with Z value)
		self.piston.addAction(vizact.moveTo([0,1.2,0], time=60, interpolate=vizact.easeOutCubic))
		stopStrain=vizact.signal()	# signal when the straining finished (60 secs)
#		self.mats.addAction(startSqueeze.trigger)
		self.mats.addAction(vizact.sizeTo([1,.5,1], time=60, interpolate=vizact.easeOutCubic))
		self.mats.addAction(stopStrain.trigger)
		# oil straining starts 2'' after squeezing starts and stops 3'' after squeezing stops
		self.oilStrain.addAction(vizact.waittime(2))	# start straining after 2 secs
		startSqueeze = vizact.signal()	# signal when straining starts
		self.oilStrain.addAction(startSqueeze.trigger)
		self.oilStrain.addAction(vizact.method.visible(1))
		self.oilStrain.addAction(vizact.fadeTo(1, begin=0, time=1))
		self.oilStrain.addAction(stopStrain.wait)
		self.oilStrain.addAction(vizact.fadeTo(0, time=3))
		# oil gathering starts when mats reach the top and finishes 5'' after strain is over
		self.oilGathered.addAction(startSqueeze.wait)
		self.oilGathered.addAction(vizact.method.visible(1))
		self.oilGathered.addAction(vizact.fadeTo(1, begin=0, time=5))
		startDrop = vizact.signal()	# signal when the drop should start (5'' after oil gathered)
		self.oilGathered.addAction(startDrop.trigger)
		self.oilGathered.addAction(stopStrain.wait)
		self.oilGathered.addAction(vizact.waittime(5))	# wait 5 more secs for gathered oil to drop
		self.oilGathered.addAction(vizact.fadeTo(0, time=1))
		self.oilGathered.addAction(vizact.method.visible(0))
		# oil drop stars 5'' after oil is gathered and finishes 5'' after strain is over
		self.oilDrop.addAction(startDrop.wait)	# start drop and tank filling after 5 secs
		self.oilDrop.addAction(vizact.method.visible(1))
		self.oilDrop.addAction(vizact.fadeTo(1, begin=0, time=1))
		self.oilDrop.addAction(stopStrain.wait)
		self.oilDrop.addAction(vizact.waittime(5))
		self.oilDrop.addAction(vizact.fadeTo(0, time=1))
		self.oilDrop.addAction(vizact.method.visible(0))
		# oil in can starts filling up when oil drop starts (45'')
		self.oilSurface.addAction(startDrop.wait)
		self.oilSurface.addAction(vizact.moveTo([0,0,0], time=45))
	
	def Releasing (self, dur):
		self.piston.addAction(vizact.moveTo([0,0,0], time=dur, interpolate=vizact.easeOut))
		self.mats.addAction(vizact.sizeTo([1,.75,1], time=dur, interpolate=vizact.easeOutCubic))
	
	def Damage (self, flag):
		if flag:
			self.smoke = self.object.add('models/objects/smoke_trail.osg')
			self.smoke.setPosition(0,3.5,.25)
		else:
			self.smoke.remove()
		
	def PumpOil (self):
		self.oilSurface.addAction(vizact.moveTo([0,-.22,0], time=30))
		
	#Get the engine working
	def Start (self):
		pass
		
	#Get the engine working
	def Stop (self):
		pass
		

class Loader ():
	"""This is the loading table class"""
	def __init__(self, FAClass, factory, pos, eul):
		self.object = factory.add('models/loader.ive')
		self.faClass = FAClass
		self.object.setPosition(pos)
		self.object.setEuler(eul)
		self.object.getChild('can').remove()
		self.PulpLevel = 0
		#this is called by the AddProximitySensors() of the main module
		self.proximityData = (vizproximity.RectangleArea([5,5]), self.object)
		self.getComponents()
		
	def getComponents (self):
		self.components = {}
		self.componentPos = {}
		mat = self.object.getChild('mat')
		mat.hint(viz.COPY_SHARED_MATERIAL_HINT)
		self.paste1 = mat.getChild('Paste')
		self.paste1.pick_parent = True	#when picked highlight its parent instead of object
		self.paste1.visible(0)
		self.paste1.alpha(0)
		self.paste2 = mat.getChild('FlatPaste')
		self.paste2.pick_parent = True
		self.paste2.visible(0)
		self.components['mat'] = mat
		mat.visible(0)
		pos = self.object.getPosition(viz.ABS_GLOBAL)
		self.componentPos[mat] = [pos[0]+.523, pos[1]+1.159, pos[2]+.49]
		tankPaste = self.object.insertGroupBelow('pasteSurface')
		self.components['pulp'] = tankPaste
		self.componentPos[tankPaste] = [pos[0]+.698, pos[1]+.123, pos[2]-1.087]
		matPile = self.object.getChild('EmptyMats')
		self.components['matPile'] = matPile
		self.componentPos[matPile] = [pos[0]-1.064, pos[1]+1, pos[2]+.484]
	
	def FillMat (self):
		self.paste1.setPosition(0,0,0)
		self.paste2.setPosition(0,-.02,0)
		self.paste1.addAction(vizact.method.visible(1))
		self.paste1.addAction(vizact.fadeTo(1, time=.5))
		self.paste1.addAction(vizact.moveTo([0,-.1,0], time=2))
		self.paste2.addAction(vizact.waittime(1))
		self.paste2.addAction(vizact.method.visible(1))
		self.paste2.addAction(vizact.moveTo([0,0,0], time=2))
	
	def MatOnTable (self):
		mat = self.components['mat']
		mat.setPosition(1.58,0.3,0, viz.REL_PARENT)
		mat.addAction(vizact.method.visible(1))
		mat.addAction(vizact.moveTo([0,0.3,0], time=1, interpolate=vizact.easeInCircular))
		mat.addAction(vizact.moveTo([0,0,0], time=.5, interpolate=vizact.easeOutCircular))
		
	def PulpInTank (self, inOut):	# >0 -> add, <0 -> subtract
		self.PulpLevel += inOut
		amount = self.PulpLevel * .05
		pulp = self.components['pulp']
		move = vizact.moveTo([0,amount,0], time=3)
		resize = vizact.sizeTo([1+amount/4,1,1+amount/2], time=3)
		pulp.addAction(vizact.parallel(move, resize))
	
	def PickMat(self):
		mat = self.components['mat']
		self.paste1.visible(0)
		self.paste1.alpha(0)
		self.paste2.visible(0)
		mat.visible(0)
		mat.setPosition([0,0,0], viz.REL_PARENT)
		
	def Start (self):
		pass
		
	def Stop (self):
		pass
		
class Laval ():
	"""This is the Laval class"""
	def __init__(self, factory, pos, eul, LR, faClass):
		self.object = factory.add('models/laval.osgb')
		self.object.setPosition(pos)
		self.object.setEuler(eul)
		self.LR = LR
		self.faClass = faClass	#the factory class used to get the belts
		base = factory.add('models/objects/concrete base.ive')
		base.setPosition(pos[0]-.02, pos[1], pos[2]+.05)
		base.scale(.12,.1,.25)
		self.belt = self.object.getChild('belt_laval')
		self.faClass.belts['laval'+self.LR] = Belt(self.belt)
		self.power_wheel = self.object.getChild('powerW')
		self.power_wheel.center(-.393, .643, .048)
#		self.gauge = self.object.getChild('gauge')
		#insert group right below gauge transform since the OFFSET and GEODE subobjects are not pivoted correctly.
		self.gauge = self.object.insertGroupBelow('gauge')
		self.oil = self.object.getChild('oil')
		self.oil.hint(viz.COPY_SHARED_MATERIAL_HINT)
		self.oil.alpha(0)
		self.water = self.object.getChild('water')
		self.water.hint(viz.COPY_SHARED_MATERIAL_HINT)
		self.water.alpha(0)
		self.getComponents()
		#this is called by the AddProximitySensors() of the main module
		self.proximityData = (vizproximity.RectangleArea([2,4]), self.object)

	def getComponents (self):
		self.components = {}
		self.componentPos = {}
		handle = self.object.getChild('handle')
		handle.center(-.47, .834, 0.197)
		lavalPos = self.object.getPosition()
		self.components['handle'+self.LR] = handle
		self.componentPos[handle] = [lavalPos[0]+.5, lavalPos[1]+.5, lavalPos[2]]
		pitcher = self.object.getChild('pitcher')
		self.components['pitcher'+self.LR] = pitcher
		self.componentPos[pitcher] = [lavalPos[0]+.215, lavalPos[1]+.689, lavalPos[2]-.505]
		self.wheel = self.object.getChild('wheel')
		self.wheel.center(-.352, 1.251, 2.388)
		self.crazy_wheel = self.object.getChild('crazyW')
		self.crazy_wheel.center(-.393, .643, .048)
		if self.LR == 'R':
			self.components['wheel'] = self.wheel
			self.componentPos[self.wheel] = [lavalPos[0]+.35, lavalPos[1]+1.25, lavalPos[2]-2.4]
			self.components['crazyW'] = self.crazy_wheel
			self.componentPos[self.crazy_wheel] = [lavalPos[0]+.5, lavalPos[1]+.5, lavalPos[2]]
	
	def DetachBelt (self):
		self.belt.visible(0)
		
	def AttachBelt (self):
		self.belt.addAction(vizact.fadeTo(1, begin=0, time=1))
		self.belt.visible(1)
#		self.faClass.belts['laval'+self.LR] = Belt(self.belt)
		
	def StartSeparation (self, start):
		self.oil.addAction(vizact.fadeTo(start, time=.5))
		self.water.addAction(vizact.fadeTo(start, time=.5))
		if start == 1:
			pitcher = self.components['pitcher'+self.LR]
			oilSurf = pitcher.getChild('oilSurface')
			oilSurf.addAction(vizact.moveTo([0,.5,0], time=10))
	
	def MovePitcher (self, t):
		pitcher = self.components['pitcher'+self.LR]
		posX = self.object.getPosition()[0]
		off = 0		#this is the offset for the left DeLaval's pitcher
		if self.LR == 'R':
			off = .5
		pitcher.addAction(vizact.moveTo([posX,0,-4], time=2*t/10, interpolate=vizact.easeInOut, mode=viz.ABS_GLOBAL))
		pitcher.addAction(vizact.moveTo([-2.5,0,-5], time=5*t/10, interpolate=vizact.easeInOut, mode=viz.ABS_GLOBAL))
		pitcher.addAction(vizact.moveTo([-2.5-off,0,-6.8+off], time=3*t/10, interpolate=vizact.easeInOut, mode=viz.ABS_GLOBAL))
		pitcher.addAction(vizact.moveTo([-2.5-off,-0.08,-6.8+off], time=.2, mode=viz.ABS_GLOBAL))
		pitcher.addAction(vizact.moveTo([-2.5-off,-0.1, -6.8+off], time=2, interpolate=vizact.easeInOutCircular, mode=viz.ABS_GLOBAL))
		
	def ChangePressure(self, pressure, duration):
		self.gauge.endAction()
		#dict of tuples (degrees of rotation, anim duration) for every pressure value
		angle = int(pressure) * 0.3
		ease = vizact.easeInOutCubic
		# spin to 180 degrees first, because spinTo chooses the shortest path (CCW in this case)
		if angle == 0:
			incPress = vizact.spinTo(euler=[180, 0, 0], time=2, interpolate=vizact.easeIn)
			self.gauge.addAction(incPress)
			ease = vizact.easeOut
		incPress = vizact.spinTo(euler=[angle, 0, 0], time=int(duration), interpolate=ease)
		self.gauge.addAction(incPress)
		
	def Damage (self, flag):
		if flag:
			self.smoke = self.object.add('models/objects/smoke_trail.osg')
			self.smoke.setPosition(0,1,0)
			self.smoke.setScale(.25,.25,.25)
		else:
			self.smoke.remove()
			
	def ChangeGuide (self, dir):	#dir=1 -> move right, -1 -> move left
		if dir > 0:
			self.PlayAudio('laval_start', self.object, viz.PLAY)
		else:
			self.AdjustAudio(0)
			self.PlayAudio('laval_stop', self.object, viz.PLAY)
		guide = self.components['handle'+self.LR]
		pos = guide.getPosition()
		newPos = [pos[0]+.25*dir, pos[1], pos[2]]
		self.faClass.belts['laval'+self.LR].MoveBelt(-dir, .09)
		guide.addAction(vizact.moveTo(newPos, time=2, interpolate=vizact.easeInOut))
		if dir > 0:
			guide.addAction(vizact.call(self.StopCrazy))
			guide.addAction(vizact.call(self.SetMotion))
		else:
			guide.addAction(vizact.call(self.StartCrazy))
			guide.addAction(vizact.call(self.EndMotion))
			
	def StartCrazy (self):
		self.crazy_wheel.addAction(vizact.spin(1,0,0, 90,viz.FOREVER))
		
	def StopCrazy (self):
		self.crazy_wheel.endAction()
		
	def SetMotion (self):
		self.power_wheel.addAction(vizact.call(self.PlayAudio, 'laval_separate'))
		self.power_wheel.addAction(vizact.spin(1,0,0, 90,viz.FOREVER))
		
	def EndMotion (self):
		self.power_wheel.endAction()
		
	def Start (self):
		self.StartCrazy()
		self.wheel.addAction(vizact.spin(1,0,0, 90,viz.FOREVER))
		
	def Stop (self):
		self.StopCrazy()
		self.EndMotion()
		self.wheel.endAction()
		
	def PlayAudio (self, audio, obj=None, mode=viz.LOOP):
		if not SOUNDS_ENABLED:
			return
		if obj == None:
			obj = self.object
		sound = obj.playsound('sounds/'+audio+'.wav', mode)
		sound.minmax(5,30)
		if mode == viz.LOOP: #constant machine loop
			self.sound = sound
	
	def AdjustAudio (self, mode): #0-1->volume value, 0->stop
		if not SOUNDS_ENABLED:
			return
		if mode>0:
			self.sound.volume(mode)
		else:
			self.sound.stop()
			
		
class OilPump ():
	"""This is the Oil Pump class"""
	def __init__(self, factory, pos, eul, faClass):
		self.object = factory.add('models/oil_pump.osgb')
		self.object.setPosition(pos)
		self.object.setEuler(eul)
		self.faClass = faClass
		base = factory.add('models/objects/concrete base.ive')
		base.setPosition(pos[0]+0.12, pos[1]-.3, pos[2]+0.02)
		base.scale(.07,.1,.08)
		self.crankshaft = self.object.getChild('crankshaft001')
		self.crankshaft.center(-.292, .638, -.026)
		self.rod = self.object.insertGroupBelow('rod001')
		self.cap = self.object.insertGroupBelow('cap001')
		self.wheelP = self.object.getChild('wheelP')
		self.wheelP.center(.149, .638, -.026)
		self.wheelC = self.object.getChild('wheelC')
		self.wheelC.center(.244, .638, -.026)
		self.oilDrop = self.object.getChild('oilDrop')
		self.oilDrop.alpha(0)
		self.faClass.belts['oilPump'] = Belt(self.object.getChild('belt_oil'))
		self.getComponents()
		#this is called by the AddProximitySensors() of the main module
		self.proximityData = (vizproximity.CircleArea(1.2), self.object)
		
	def getComponents (self):
		self.components = {}
		self.componentPos = {}
		handle = self.object.getChild('handle')
		self.components['handle'] = handle
		self.componentPos[handle] = self.object.getPosition()
	
	def ChangeGuide (self, dir):	#dir=1 -> move right, -1 -> move left
		dir = -dir
		handle = self.components['handle']
		pos = handle.getPosition()
		newPos = [pos[0]+.095*dir, pos[1], pos[2]]
		self.faClass.belts['oilPump'].MoveBelt(-dir, .095)
		handle.addAction(vizact.moveTo(newPos, time=2, interpolate=vizact.easeInOut))
		if dir < 0:
			handle.addAction(vizact.call(self.StopCrazy))
			handle.addAction(vizact.call(self.SetMotion))
		else:
			handle.addAction(vizact.call(self.StartCrazy))
			handle.addAction(vizact.call(self.EndMotion))
	
	def OilPourInLavals (self, flag):
		self.oilDrop.addAction(vizact.fadeTo(flag, time=.5))
#		if not flag: self.oilDrop.visible(0)
		
	def StartCrazy (self):
		self.wheelC.addAction(vizact.spin(1,0,0, 90,viz.FOREVER))
		
	def StopCrazy (self):
		self.wheelC.endAction()
		
	def SetMotion (self):
		self.PlayAudio('pump_oil')
		self.wheelP.addAction(vizact.spin(1,0,0, 90,viz.FOREVER))
		self.crankshaft.addAction(vizact.spin(1,0,0, 152,viz.FOREVER))
#		self.crankshaft.addAction(vizact.spin(0,0,1, 90,viz.FOREVER))
		try:
			self.capPrevYPos = self.cap.getPosition(viz.ABS_GLOBAL)[1]
			self._updateFunc.setEnabled(viz.ON)
		except AttributeError:
			self._updateFunc = vizact.onupdate(0, self.update)
			
	def EndMotion (self):
		self.AdjustAudio(0)
		self.wheelP.endAction()
		self.crankshaft.endAction()
		
	def update(self):
		#make the connecting rod look at the cap every frame
		mat = self.rod.getMatrix(viz.ABS_GLOBAL)
#		mat.setTrans( mat.preMultVec( 0,0,-.5) )
		pos = mat.getPosition()
		mat.makeLookAt( pos, self.cap.getPosition(viz.ABS_GLOBAL),[1,0,0])
		mat.preEuler([0,90,9.25])
		self.rod.setQuat( mat.getQuat(), viz.ABS_GLOBAL )
		#now push the rod up
		rodPos = self.rod.getPosition()
		capShift = self.capPrevYPos - self.cap.getPosition(viz.ABS_GLOBAL)[1]
		self.rod.setPosition(0, rodPos[1]-capShift, 0)
		self.capPrevYPos = self.cap.getPosition(viz.ABS_GLOBAL)[1]
		
	def Start (self):
		self.StartCrazy()
		
	def Stop (self):
		self.StopCrazy()
		self.EndMotion()
	
	def PlayAudio (self, audio, obj=None, mode=viz.LOOP):
		if not SOUNDS_ENABLED:
			return
		if obj == None:
			obj = self.object
		sound = obj.playsound('sounds/'+audio+'.wav', mode)
		sound.minmax(5,30)
		if mode == viz.LOOP: #constant machine loop
			self.sound = sound
	
	def AdjustAudio (self, mode): #0-1->volume value, 0->stop
		if not SOUNDS_ENABLED:
			return
		if mode>0:
			self.sound.volume(mode)
		else:
			self.sound.stop()
			
		
class Boiler ():
	"""This is the Boiler class"""
	def __init__(self, factory, pos):
		self.object = factory.add('models/boiler.ive')
		self.hatch = (self.object.insertGroupBelow('HatchDoorL'), self.object.insertGroupBelow('HatchDoorR'))
		self.gauge = self.object.insertGroupBelow('velona')
		fire = viz.add('textures/fire.mov', loop=1, play=1)
		self.fire = viz.addTexQuad(texture=fire, pos=[.15,1.2,0], size=1.2, alpha=0)
		self.fire.setParent(self.object)
		self.fire.visible(0)
		self.object.setPosition(pos)
		self.getComponents()
		#this is called by the AddProximitySensors() of the main module
		self.proximityData = (vizproximity.RectangleArea([5,5]), self.object)
		
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
		
	def ChangePressure(self, pressure, duration):
		self.gauge.endAction()
		angle = int(pressure) * 2.25
		ease = vizact.easeInOutCubic
		# spin to 180 degrees first, because spinTo chooses the shortest path (CCW in this case)
		if angle == 270:
			incPress = vizact.spinTo(euler=[0,0,-180], time=int(duration)*2/3, interpolate=vizact.easeInCubic)
			duration = int(duration)*1/3
			self.gauge.addAction(incPress)
			ease = vizact.easeOutCubic
		incPress = vizact.spinTo(euler=[0,0,-angle], time=int(duration), interpolate=ease)
		self.gauge.addAction(incPress)
		
	def OpenCloseHatch(self, open):	#open=True or False
		if open:
			self.PlayAudio('boiler_load', self.components['coal'], viz.PLAY)
		angle = 120 * open
		openLeft = vizact.spinTo(euler=[angle,0,0], time=2, interpolate=vizact.easeOut)
		openRight = vizact.spinTo(euler=[-angle,0,0], time=2, interpolate=vizact.easeOut)
		self.hatch[0].addAction(openLeft)
		self.hatch[1].addAction(openRight)
		
	def CoalAction(self, act):	#act=1->load, 2->light, 3->waste
		coalFurnace = self.components['coalfurnace']
		if act == 1:	#fade in the coals
			coalFurnace.addAction(vizact.method.visible(1))
			coalFurnace.addAction(vizact.fadeTo(1, begin=0, time=1))
		elif act == 2:	#turn coals red and light fire
			self.PlayAudio('boiler_light', coalFurnace, viz.PLAY)
			fireSignal = vizact.signal()
			coalFurnace.addAction(vizact.fadeTo(viz.RED, time=1))
			coalFurnace.addAction(fireSignal.trigger)
			cPos = coalFurnace.getPosition()
			coalFurnace.addAction(vizact.moveTo([cPos[0],cPos[1],cPos[2]+.1],time=.5))
			self.fire.addAction(fireSignal.wait)
			self.fire.addAction(vizact.method.visible(1))
			self.fire.addAction(vizact.fadeTo(0.75, time=1))
			self.fire.addAction(vizact.waittime(4))
			self.fire.addAction(vizact.call(self.PlayAudio, 'boiler_furnace'))
		elif act == 3:	#fade out the coals and fire
			self.AdjustAudio(.5)
			coalFurnace.addAction(vizact.fadeTo(0.25, time=.5))
			self.fire.addAction(vizact.fadeTo(0.25, time=.5))
		elif act == 4:	#light up the coals and fire again
			self.AdjustAudio(1)
			coalFurnace.addAction(vizact.fadeTo(1, time=.5))
			self.fire.addAction(vizact.fadeTo(.75, time=.5))
		elif act == 5:	#fade out the coals and fire completely
			self.AdjustAudio(0)
			self.AdjustAudio(1)
			coalFurnace.addAction(vizact.fadeTo(0, time=.5))
			coalFurnace.addAction(vizact.method.setPosition([0,0,0]))
			coalFurnace.addAction(vizact.method.color(viz.GRAY))
			coalFurnace.addAction(vizact.method.visible(0))
			self.fire.addAction(vizact.fadeTo(0, time=.5))
			self.fire.addAction(vizact.method.visible(0))
	
	def PlayAudio (self, audio, obj=None, mode=viz.LOOP):
		if not SOUNDS_ENABLED:
			return
		if obj == None:
			obj = self.object
		sound = obj.playsound('sounds/'+audio+'.wav', mode)
		sound.minmax(5,30)
		if mode == viz.LOOP: #constant machine loop
			self.sound = sound
	
	def AdjustAudio (self, mode): #0-1->volume value, 0->stop
		if not SOUNDS_ENABLED:
			return
		if mode>0:
			self.sound.volume(mode)
		else:
			self.sound.stop()

class Scale ():
	"""This is the Laval class"""
	def __init__(self, factory, pos, eul):
		self.object = factory.add('models/scale.ive')
		self.object.setPosition(pos)
		self.object.setEuler(eul)
		self.base = self.object.getChild('base')
		self.needle = self.object.insertGroupBelow('gauge')
		#this is called by the AddProximitySensors() of the main module
		self.proximityData = (vizproximity.RectangleArea([2.5,2.5]), self.object)
		
	def WeighPitcher (self, duration, amount):
		self.base.addAction(vizact.move(0,-0.01,0, time=duration))
		angle = amount * 0.6
		self.needle.addAction(vizact.spin(0,120,0, speed=angle/duration, dur=duration))
		
	def Start (self):
		pass
		
	def Stop (self):
		pass

		
class Belt ():
	"""This is the Belt class"""
	def __init__(self, obj):
		self.belt = obj
		self.belt.setAnimationSpeed(0)
#		self.matrix1 = vizmat.Transform()
#		self.matrix2 = vizmat.Transform()
#		self.timer = vizact.ontimer(.01, self.TurnBelt)
#		self.timer.setEnabled(viz.OFF)
	
	def Start(self):
		self.belt.setAnimationSpeed(1)
#		self.timer.setEnabled(viz.ON)		
	
	def Stop(self):
		self.belt.setAnimationSpeed(0)
#		self.timer.setEnabled(viz.OFF)
		
	def TurnBelt(self):
		self.matrix1.postTrans(0,.04,0)
		self.matrix2.postTrans(0,-.04,0)
		self.belt.texmat(self.matrix1,'belt1',0)
		self.belt.texmat(self.matrix2,'belt2',0)
		
	def MoveBelt (self, dir, dist):
		pos = self.belt.getPosition()
		newPos = [pos[0]-dist*dir, pos[1], pos[2]]
		self.belt.addAction(vizact.moveTo(newPos, time=2, interpolate=vizact.easeInOut))
		

class WaterPipe ():
	"""This is the WaterPipe class used for practice"""
	def __init__(self, factory, pos, eul):
		self.object = factory.add('models/waterPipe.ive')
		self.object.setPosition(pos)
		self.object.setEuler(eul)
		self.pipe = self.object.getChild('missingPipe')
		#this is called by the AddProximitySensors() of the main module
		self.proximityData = (vizproximity.RectangleArea([2.5,2.5]), self.object)
		self.getComponents()
		
	def getComponents (self):
		self.components = {}
		self.componentPos = {}
		valve = self.object.insertGroupBelow('valve')
		self.components['valve'] = valve
		objPos = self.object.getPosition()
		self.componentPos[valve] = [objPos[0],1.5,objPos[2]]
		elbow = self.object.getChild('elbow')
		self.components['elbow'] = elbow
		objPos = self.object.getPosition()
		self.componentPos[elbow] = [objPos[0],1,objPos[2]]
		ferrule = self.object.getChild('ferrule')
		self.components['ferrule'] = ferrule
		objPos = self.object.getPosition()
		self.componentPos[ferrule] = [objPos[0],1,objPos[2]]
	
	def DetachPipe (self):
		self.pipe.visible(0)
		
	def AttachPipe (self):
		self.pipe.addAction(vizact.fadeTo(1, time=1))
		self.pipe.visible(1)
	
	def OpenValve (self, time):
		self.components['valve'].addAction(vizact.spin(0,0,1,360,time))
		
	def CloseValve (self, time):
		self.components['valve'].addAction(vizact.spin(0,0,1,-360,time))
	
	def Damage (self, flag):
		if flag:
			self.smoke = self.object.add('models/objects/smoke_trail.osg')
			self.smoke.setPosition(0,1.5,0)
			self.smoke.setScale(.25,.25,.25)
		else:
			self.smoke.remove()
			
	def Start (self):
		pass
		
	def Stop (self):
		pass

	
if __name__ == '__main__':
	import vizcam
	
	viz.setMultiSample(8)
	viz.go()
	
	ground = viz.addChild('ground.osgb')
	#engine = Engine(ground, [0.58, 1, 2.97], [-90,0,0])	#476 drawables
	#vizact.onkeydown('e', engine.Start)
	#vizact.onkeydown('r', engine.Stop)
	
	
#	pump = Pump(ground, [5, 2, 10], [90,0,0], 'L', None)	#43 drawables
#	press = Press(ground, [5, 1, 2.97], [0,0,0], 'L')	#32 drawables
	boiler = Boiler(ground, [15, 0, 2.97])	#219 drawables
#	laval = Laval(ground, [10, 0, 2.97], [-90,0,0], 'L' ,None)	#35 drawables
#	mill = Mill(ground, [5, 0, 2.97], [-90,0,0], 'L')	#150 drawables
	
	cam = vizcam.PivotNavigate(distance=2)
	cam.centerNode(boiler.object)
	
#	OilPump = OilPump(ground, [0, 1, 10], [180,0,0], False)	#29 drawables
#	vizact.onkeydown('s', OilPump.SetMotion)
#	vizact.onkeydown('d', OilPump.EndMotion)
#	cam = vizcam.PivotNavigate(distance=2)
#	cam.centerNode(OilPump.rod)