﻿import viz
import vizmat
import vizact

viz.go()

class Pump():
	"""This is the Pump class"""
	def __init__(self, factory, pos, eul, LR, faClass):
		self.object = factory.add('models/pump.ive')
		self.object.setScale(.0014,.0014,.0014)
		self.object.setPosition(pos)
		self.object.setEuler(eul)
		self.LR = LR
		self.faClass = faClass	#the factory class used to get the belts
		#fix swlinaki
		#self.object.getChild('swlinaki').setPosition(0,20,-40)
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
		
	def getComponents (self):
		self.components = {}
		self.componentPos = {}
		valve = self.object.getChild('bypassValve')
		valve.center(169.156, -858.204, 350.093)
		self.components['bypass'] = valve
		self.componentPos[valve] = self.object.getPosition()
		guide = self.object.getChild('beltGuide')
		self.components['guide'] = guide
		self.componentPos[guide] = self.object.getPosition()
		
	def ChangeGuide (self, dir):	#dir=1 -> move right, -1 -> move left
		guide = self.components['guide']
		pos = guide.getPosition()
		newPos = [pos[0], pos[1], pos[2]+100*dir]
		self.faClass.belts['pump'+self.LR].MoveBelt(dir)
		guide.addAction(vizact.moveTo(newPos, time=2, interpolate=vizact.easeInOut))
	
	def TurnValve (self, dir):
		self.components['bypass'].addAction(vizact.spin(1*dir,0,0,360,3))
	
	def IncreasePressure (self):
		self.bar.addAction(vizact.call(self.ChangePressure, 1500))
		self.bar.addAction(vizact.waittime(15))
		self.bar.addAction(vizact.call(self.ChangePressure, 2000))
		
	def ChangePressure(self, pressure):
		self.gauge.endAction()
		#dict of tuples (degrees of rotation, anim duration) for every pressure value
		presToAngle = {4500: (270,30), 4000: (240,60), 1500: (90,10), 0:(0,5)}
		angle = presToAngle[pressure][0]
		duration = presToAngle[pressure][1]
		ease = vizact.easeInOutCubic
		# spin to 180 degrees first, because spinTo chooses the shortest path (CCW in this case)
		if angle == 0:
			incPress = vizact.spinTo(euler=[0, 180, 0], time=2, interpolate=vizact.easeIn)
			self.gauge.addAction(incPress)
			ease = vizact.easeOut
		incPress = vizact.spinTo(euler=[0, angle, 0], time=duration, interpolate=ease)
		self.gauge.addAction(incPress)
	
	def LiftBar (self, flag):
		self.bar.addAction(vizact.spinTo(euler=[0,0,-20*flag], time=5, interpolate=vizact.easeOut))
		self.barRod.addAction(vizact.moveTo([0,40*flag,0], time=5, interpolate=vizact.easeOut))
		
	def StartCrazy (self):
		self.crazy.addAction(vizact.spin(0,0,1, 76,viz.FOREVER))
		
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
		self.gear.addAction(vizact.spin(0,0,1, 76,viz.FOREVER))
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
		self.object.setScale(.32,.32,.32)
		self.object.setPosition(pos)
		self.object.setEuler(eul)
		dirs = {'L': 1, 'R': -1}	#direction of rotation according to mill
		self.direction = dirs[LR]
		#self.wheels = self.object.getChild('wheels')
		#self.wheels.setCenter(0,3.954,0)
		#self.object.getChild('wheels').remove()
		#get the nodes used for animation
		self.rotationAxis = self.object.getChild('rotation_axis')
		self.wheels=self.object.add('models/mill_wheels.ive', pos=[0,3.964,0])
		self.wL = self.wheels.getChild('WheelL')
		self.wR = self.wheels.getChild('WheelR')
		self.tankPulp = self.object.getChild('pulp')
		self.pourPulp = self.object.getChild('pourPulp')
		self.pourPulp.alpha(0)
		self.getComponents()
	
	def getComponents (self):
		self.components = {}
		self.componentPos = {}
		# Add the paste
#		self.object.getChild('mixedPulp').remove()
#		self.mixedPulp = self.object.add('models/objects/paste_mixed.osgb', pos=[0, 0, 0])
		self.mixedPulp = self.object.getChild('mixedPulp')
		self.mixedPulp.enable(viz.SAMPLE_ALPHA_TO_COVERAGE)
		self.mixedPulp.disable(viz.BLEND)
		self.mixedPulp.drawOrder(-10, node='olives')	#make sure olives are drawn first
		self.mixedPulp.getChild('olives').setAnimationSpeed(.75)
#		self.mixedPulp.alpha(0)
#		self.mixedPulp.visible(0)
		self.mixedPulp.setPosition(0,-1,0)
		self.mixedPulp.setScale(.85,1,.85)
		justPaste = self.mixedPulp.getChild('paste')
		justPaste.alpha(0)
		justPaste.visible(0)
		self.components['paste'] = justPaste
		self.componentPos[justPaste] = self.object.getPosition()
		# Add the hatch
		hatch = self.object.getChild('hatch')
		hatch.center(.916, 2.681, -2.885)
		self.components['hatch'] = hatch
		millPos = self.object.getPosition()
		self.componentPos[hatch] = [millPos[0]+.916/3, millPos[1]+2.681/3, millPos[2]-2.885/3]
		# Add the tank
		tank = self.object.getChild('tank')
		tank.center(1.147, .779, -3.165)
		self.components['tank'] = tank
		self.componentPos[tank] = [millPos[0]+1.147/3, millPos[1]+.779/3, millPos[2]-3.165/3]
		# Add the sacks
		self.sackItem = viz.add('models/objects/sackR.osgb')
		#The alpha is being applied as part of the material, but both sacks use the same material. 
		#Vizard preserves material instancing by default, but you can break the instancing using...
		self.sackItem.hint(viz.COPY_SHARED_MATERIAL_HINT)
		self.sackItem.alpha(0, 'sack_pouring')
		self.sackPour = self.sackItem.getChild('sack_pouring')
		self.sackPour.center(-3.905, 1.504, 8.611)
		#add sacks to the components and componentPos
		sackR1 = self.sackItem.getChild('sack1R')
		sackR2 = self.sackItem.getChild('sack2R')
		self.components['sack1R'] = sackR1
		self.components['sack2R'] = sackR2
		self.componentPos[sackR1] = [-1.692, 1.502, 9.963]
		self.componentPos[sackR2] = [-1.692, 1.502, 11.121]
		sack_path = self.sackItem.getChild('path1R')
		sack_path.setAnimationLoopMode(0)
		sack_path.setAnimationSpeed(0)
		sack_path = self.sackItem.getChild('path2R')
		sack_path.setAnimationLoopMode(0)
		sack_path.setAnimationSpeed(0)
		
	def SackAnim (self, sid):	#sid is the sack id: {1R, 2R, 1L, or 2L}
		sack = self.components['sack'+sid]
		self.sack_path = self.sackItem.getChild('path'+sid).copy()
		#create a new group below 'sack' and adopt its children to keep pivot point
		sack = self.sackItem.insertGroupBelow('sack'+sid)
		sack.setParent(self.sack_path, node='path'+sid)
		self.sack_path.setAnimationSpeed(1)
		sack.addAction(vizact.waittime(3))	#wait for sack animation
		endAnimSignal = vizact.signal()
		trig = endAnimSignal.trigger
		fade = vizact.method.alpha(0)
		sack.addAction(vizact.parallel(fade, trig))
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
	
	def OlivesToPaste (self):
		justPaste = self.components['paste']
		justPaste.addAction(vizact.method.visible(1))
		justPaste.addAction(vizact.fadeTo(1, begin=0, time=30, interpolate=vizact.easeInCubic))
			
	def WastePaste (self):
		self.mixedPulp.drawOrder(0, node='olives')
		self.mixedPulp.addAction(vizact.fadeTo(0, time=1))
		self.mixedPulp.addAction(vizact.method.drawOrder(-10))
		
	def PasteInTank (self):
		hatch = self.components['hatch']
		hatch.addAction(vizact.moveTo([.97-.917, 3.102-2.681, -3.095+2.885], time=1, interpolate=vizact.easeInOut))
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
		self.tankPulp.addAction(vizact.moveTo([0,1,0], time=5, interpolate=vizact.easeOut))
		self.mixedPulp.addAction(openSignal.wait)
#		self.mixedPulp.addAction(vizact.fadeTo(0, time=5))
		move = vizact.moveTo([0, -1, 0], time=5)
		resize = vizact.sizeTo([.85,1,.85], time=5, interpolate=vizact.easeOut)
		self.mixedPulp.addAction(vizact.parallel(move, resize))
		
	def MovingTank (self):
		pass
	
	def ResetMill (self):
		hatch = self.components['hatch']
		hatch.addAction(vizact.moveTo([0,0,0], time=1, interpolate=vizact.easeInOut))
		self.tankPulp.setPosition(0,0,0)
		self.components['paste'].alpha(0)
		self.components['paste'].visible(0)
		
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
		self.object = factory.add('models/press2.osgb')
		#self.object.setScale(.045,.045,.045)
		self.object.setPosition(pos)
		self.object.setEuler(eul)
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
		self.oilSurface.setPosition(0,-.165,0)
		self.piston = self.object.getChild('pressPiston')
		#for storing the loaded mats (objects)
		self.loadedMats = []
		self.getComponents()
	
	def getComponents (self):
		self.components = {}
		self.componentPos = {}
		pressTray = self.object.getChild('press_tray')
		pos = self.object.getPosition()
		self.components['tray'] = pressTray
		self.componentPos[pressTray] = [pos[0], pos[1]+1.5, pos[2]]
	
	def LoadMat (self):
		mat = self.mat.copy()
		mat.setParent(self.object)
		counter = len(self.loadedMats)
		self.loadedMats.append(mat)
		mat.setPosition(0, .05*counter, 0)
		mat.addAction(vizact.method.visible(1))
		mat.addAction(vizact.fadeTo(1, begin=0, time=.5))
		counter += 1
		if counter == 1:
			return True
			
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
		self.piston.addAction(vizact.moveTo([0,0,.25], time=60, interpolate=vizact.easeOutCubic))
		self.mats.addAction(vizact.waittime(10))	# start straining after 10 secs
		reachTop = vizact.signal()	# signal when mats have reached the top
		stopStrain=vizact.signal()	# signal when the straining finished (60 secs)
		self.mats.addAction(reachTop.trigger)
		self.mats.addAction(vizact.sizeTo([1,1,.62], time=50, interpolate=vizact.easeOutCubic))
		self.mats.addAction(stopStrain.trigger)
		# oil straining starts when mats reach the top and stops 3'' after strain is over
		self.oilStrain.addAction(reachTop.wait)
		self.oilStrain.addAction(vizact.method.visible(1))
		self.oilStrain.addAction(vizact.fadeTo(1, begin=0, time=1))
		self.oilStrain.addAction(stopStrain.wait)
		self.oilStrain.addAction(vizact.fadeTo(0, time=3))
		# oil gathering starts when mats reach the top and finishes 5'' after strain is over
		self.oilGathered.addAction(reachTop.wait)
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
#		table = self.object.getChild('Table')
#		table.collideBox()
		self.getComponents()
		
	def getComponents (self):
		self.components = {}
		self.componentPos = {}
		mat = self.object.getChild('mat')
		mat.hint(viz.COPY_SHARED_MATERIAL_HINT)
		mat.getChild('Paste').visible(0)
		mat.getChild('Paste').alpha(0)
		mat.getChild('FlatPaste').visible(0)
		self.components['mat'] = mat
		mat.visible(0)
		pos = mat.getPosition(viz.ABS_GLOBAL)
		self.componentPos[mat] = [pos[0]-1.952, pos[1]+1.159, pos[2]-2.62]
		tankPaste = self.object.getChild('pasteSurface')
		tankPaste.center(1.777,.123,4.198)
		self.components['pulp'] = tankPaste
		self.componentPos[tankPaste] = [pos[0]-1.777, pos[1]+.123, pos[2]-4.198]
		matPile = self.object.getChild('EmptyMats')
		self.components['matPile'] = matPile
		self.componentPos[matPile] = [pos[0]-3.539, pos[1]+.159, pos[2]-2.575]
	
	def FillMat (self):
		mat = self.components['mat']
		matPaste = mat.getChild('Paste')
		matFlatPaste = mat.getChild('FlatPaste')
		matFlatPaste.setPosition(0,-.02,0)
		matPaste.setPosition(0,0,0)
		matPaste.addAction(vizact.method.visible(1))
		matPaste.addAction(vizact.fadeTo(1, time=.5))
		matPaste.addAction(vizact.moveTo([0,-.1,0], time=2))
		matFlatPaste.addAction(vizact.waittime(1))
		matFlatPaste.addAction(vizact.method.visible(1))
		matFlatPaste.addAction(vizact.moveTo([0,0,0], time=2))
#		matFlatPaste.addAction(vizact.call(self.faClass.AddMatAsTool, 'mat', mat))
	
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
		move = vizact.moveTo([0,amount,0], time=1)
		resize = vizact.sizeTo([1+amount/4,1,1+amount/2], time=1)
		pulp.addAction(vizact.parallel(move, resize))
	
	def PickMat(self):
		mat = self.components['mat']
		mat.getChild('Paste').visible(0)
		mat.getChild('Paste').alpha(0)
		mat.getChild('FlatPaste').visible(0)
		mat.visible(0)
		mat.setPosition([0,0,0], viz.REL_PARENT)
		
	def Start (self):
		pass
		
	def Stop (self):
		pass
		
class Laval ():
	"""This is the Laval class"""
	def __init__(self, factory, pos, eul):
		self.object = factory.add('models/laval.ive')
		self.object.setPosition(pos)
		self.object.setEuler(eul)
		base = factory.add('models/objects/concrete base.ive')
		base.setPosition(pos[0]+0.01, pos[1], pos[2]-0.15)
		base.scale(.085,.1,.12)
		self.belt = self.object.getChild('belt_laval')
		self.power_wheel = self.object.getChild('powerW')
		self.power_wheel.center(-.393, .643, .048)
		self.getComponents()

	def getComponents (self):
		self.components = {}
		self.componentPos = {}
		self.wheel = self.object.getChild('wheel')
		self.wheel.center(-.352, 1.251, 2.388)
		self.components['wheel'] = self.wheel
		lavalPos = self.object.getPosition()
		self.componentPos[self.wheel] = [lavalPos[0]+.56, lavalPos[1]+.9, lavalPos[2]-1.174]
		self.crazy_wheel = self.object.getChild('crazyW')
		self.crazy_wheel.center(-.393, .643, .048)
		self.components['crazyW'] = self.crazy_wheel
		self.componentPos[self.crazy_wheel] = [lavalPos[0]+.5, lavalPos[1]+.5, lavalPos[2]]
		handle = self.object.getChild('handle')
		handle.center(-.47, .834, 0.197)
		self.components['handle'] = handle
		self.componentPos[handle] = [lavalPos[0]+.5, lavalPos[1]+.5, lavalPos[2]]
		
	#Get the engine working
	def Start (self):
		self.crazy_wheel.addAction(vizact.spin(1,0,0, 76,viz.FOREVER))
		self.wheel.addAction(vizact.spin(1,0,0, 76,viz.FOREVER))
		
	def Stop (self):
		self.crazy_wheel.endAction()
		self.wheel.endAction()
	
	def detachBelt (self):
		self.belt.visible(0)
		
	def attachBelt (self):
		self.belt.addAction(vizact.fadeTo(1, begin=0, time=1))
		self.belt.visible(1)

class OilPump ():
	"""This is the Oil Pump class"""
	def __init__(self, factory, pos, eul):
		self.object = factory.add('models/oil_pump.ive')
		self.object.setPosition(pos)
		self.object.setEuler(eul)
		base = factory.add('models/objects/concrete base.ive')
		base.setPosition(pos[0]+0.12, pos[1]-.3, pos[2]+0.02)
		base.scale(.07,.1,.08)
		self.cyl = self.object.getChild('cylinder')
		self.cyl.center(-.292, .638, -.026)
		self.rod = self.object.getChild('rod')
		self.rod.center(-.428, .642, -.104)
		link = viz.link(self.cyl, self.rod)
	
	def Start(self):
		pass
		
	def Stop(self):
		pass
		
class Boiler ():
	"""This is the Boiler class"""
	def __init__(self, factory, pos):
		self.object = factory.add('models/boiler.ive')
		self.hatch = (self.object.getChild('HatchDoorL'), self.object.getChild('HatchDoorR'))
		self.hatch[0].center(-.247, 1.494, -.253)
		self.hatch[1].center(.536, 1.504, -.242)
		self.gauge = self.object.getChild('velona')
		self.gauge.center(.25, 2.776, .248)
		fire = viz.add('textures/fire.mov', loop=1, play=1)
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
		
	def ChangePressure(self, pressure):
		self.gauge.endAction()
		presToAngle = {4500: 270, 3000: 180, 1500: 90, 0:0}
		angle = presToAngle[pressure]
		ease = vizact.easeInOutCubic
		# spin to 180 degrees first, because spinTo chooses the shortest path (CCW in this case)
		if angle == 270:
			incPress = vizact.spinTo(euler=[0,0,-180], time=5, interpolate=vizact.easeInCubic)
			self.gauge.addAction(incPress)
			ease = vizact.easeOutCubic
		incPress = vizact.spinTo(euler=[0,0,-angle], time=15, interpolate=ease)
		self.gauge.addAction(incPress)
		
	def OpenCloseHatch(self, open):	#open=True or False
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
			fireSignal = vizact.signal()
			coalFurnace.addAction(vizact.fadeTo(viz.RED, time=2))
			coalFurnace.addAction(fireSignal.trigger)
			cPos = coalFurnace.getPosition()
			coalFurnace.addAction(vizact.moveTo([cPos[0],cPos[1],cPos[2]+.1],time=.5))
			self.fire.addAction(fireSignal.wait)
			self.fire.addAction(vizact.method.visible(1))
			self.fire.addAction(vizact.fadeTo(0.5, time=1))
		elif act == 3:	#fade out the coals and fire
			coalFurnace.addAction(vizact.fadeTo(0.25, time=.5))
			self.fire.addAction(vizact.fadeTo(0.25, time=.5))
		elif act == 4:	#light up the coals and fire again
			coalFurnace.addAction(vizact.fadeTo(1, time=.5))
			self.fire.addAction(vizact.fadeTo(.5, time=.5))
		elif act == 5:	#fade out the coals and fire completely
			coalFurnace.addAction(vizact.fadeTo(0, time=.5))
			coalFurnace.addAction(vizact.method.setPosition([0,0,0]))
			coalFurnace.addAction(vizact.method.color(viz.GRAY))
			coalFurnace.addAction(vizact.method.visible(0))
			self.fire.addAction(vizact.fadeTo(0, time=.5))
			self.fire.addAction(vizact.method.visible(0))


#class Tanks ():
#	"""This is the Laval class"""
#	def __init__(self, factory, pos, eul):
#		self.object = factory.add('models/tanks.ive')
#		self.object.setPosition(pos)
#		self.object.setEuler(eul)

		
class Belt ():
	"""This is the Belt class"""
	def __init__(self, obj):
		self.belt = obj
		self.matrix1 = vizmat.Transform()
		self.matrix2 = vizmat.Transform()
		self.timer = vizact.ontimer(.01, self.TurnBelt)
		self.timer.setEnabled(viz.OFF)
	
	def Start(self):
		self.timer.setEnabled(viz.ON)		
	
	def Stop(self):
		self.timer.setEnabled(viz.OFF)
		
	def TurnBelt(self):
		self.matrix1.postTrans(0,.04,0)
		self.matrix2.postTrans(0,-.04,0)
		self.belt.texmat(self.matrix1,'belt1',0)
		self.belt.texmat(self.matrix2,'belt2',0)
		
	def MoveBelt (self, dir):
		pos = self.belt.getPosition()
		newPos = [pos[0]-.135*dir, pos[1], pos[2]]
		self.belt.addAction(vizact.moveTo(newPos, time=2, interpolate=vizact.easeInOut))