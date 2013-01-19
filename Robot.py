# Copyright (c) 2001-2013 WorldViz LLC.
# All rights reserved.
import viz
import vizact
import vizmat

# Name of different components of the model
_HEAD_NAME		= 'steve_head'
_BODY_NAME		= 'steve_body'
_BODY_YAW_NAME	= 'steve_body_yaw'
_BODY_COLOR		= 'white'
_EYE_COLOR		= 'black'
_OUTLINE_COLOR	= 'ink'
_SHADE_COLOR	= 'grey'

# Modes for linking tracker to body
BODY_TRACK_NONE		= 0
BODY_TRACK_YAW		= 1

class Steve(viz.VizNode):

	def __init__(self,**kw):

		# Initialize base class with model
		model = viz.addChild('steve.ive')
		model.setCenter(0,.3,0)
		viz.VizNode.__init__(self,model.id,**kw)

		# Get handle to head/body
		self.head = self.getChild(_HEAD_NAME)
		self.body = self.getChild(_BODY_YAW_NAME)
		self.body_root = self.getChild(_BODY_NAME)

		# Internal state variables
		self._updateFunc = None
		self._incrementFunc = None
		self._tracker = None
		self._trackerFlag = 0
		self._bodyTrackMode = BODY_TRACK_NONE
		self._bodyYawIncrement = 0.0
		self._bodyIncrementTime = 0.0
		self._lastBodyYaw = 0.0
		self._bodyDragPos = [0.0,0.0,0.0]

	def remove(self,*args,**kw):
		"""Remove the model"""

		# Remove update func
		if self._updateFunc is not None:
			self._updateFunc.remove()
			self._updateFunc = None
		self._incrementFunc = None

		# Remove components
		self.head.remove()
		self.body.remove()
		self.body_root.remove()

		# Remove base class
		viz.VizNode.remove(self,*args,**kw)

	def setBodyColor(self,color):
		"""Set color of body"""
		self.color(color,_BODY_COLOR)

	def getBodyColor(self):
		"""Get color of body"""
		return self.getColor(_BODY_COLOR)

	bodyColor = property(getBodyColor,setBodyColor,doc='Color of body')

	def setOutlineColor(self,color):
		"""Set color of outline"""
		self.color(color,_OUTLINE_COLOR)

	def getOutlineColor(self):
		"""Get color of outline"""
		return self.getColor(_OUTLINE_COLOR)

	outlineColor = property(getOutlineColor,setOutlineColor,doc='Color of outline')

	def setEyeColor(self,color):
		"""Set color of eye"""
		self.color(color,_EYE_COLOR)

	def getEyeColor(self):
		"""Get color of eye"""
		return self.getColor(_EYE_COLOR)

	eyeColor = property(getEyeColor,setEyeColor,doc='Color of eye')

	def setShadeColor(self,color):
		"""Set color of shade"""
		self.color(color,_SHADE_COLOR)

	def getShadeColor(self):
		"""Get color of shade"""
		return self.getColor(_SHADE_COLOR)

	shadeColor = property(getShadeColor,setShadeColor,doc='Color of shade')

	def setTracker(self,tracker,bodyTrackMode=BODY_TRACK_YAW,bodyDrag=True,bodyYawIncrement=0.0,bodyIncrementTime=1.0,priority=viz.PRIORITY_LINKS+1,flag=0):
		"""Set tracker for model"""

		# Clear existing update func
		if self._updateFunc is not None:
			self._updateFunc.remove()
			self._updateFunc = None
		self._incrementFunc = None

		# Save internal state variables
		self._tracker = tracker
		self._trackerFlag = flag
		self._bodyTrackMode = bodyTrackMode
		self._bodyYawIncrement = bodyYawIncrement
		self._bodyIncrementTime = bodyIncrementTime
		self._bodyDragPos = tracker.getPosition()

		# Reset root body orientation
		self.body_root.setQuat([0,0,0,1])

		# If no tracker, then reset body parts and return
		if tracker is None:
			m = viz.Matrix()
			self.head.setMatrix(m)
			self.body_root.setMatrix(m)
			self.body.setMatrix(m)
			return

		# Set position update function
		if bodyDrag:
			self._updatePosition = self._updatePositionDrag
		else:
			self._updatePosition = self._updatePositionNoDrag

		# Create update function callback
		if bodyTrackMode == BODY_TRACK_NONE:
			self._updateFunc = vizact.onupdate(priority,self._updateBodyTrackNone)
		elif bodyTrackMode == BODY_TRACK_YAW:
			if bodyYawIncrement > 0.0:
				yaw,pitch,roll = self._tracker.getEuler(self._trackerFlag)
				self._lastBodyYaw = yaw
				self.body.setEuler([yaw,0,0])
				self._updateFunc = vizact.onupdate(priority,self._updateBodyTrackYawIncrement)
			else:
				self._updateFunc = vizact.onupdate(priority,self._updateBodyTrackYaw)
		else:
			raise ValueError,'bodyTrackMode value is not recognized: ' + str(bodyTrackMode)

	def _updatePositionNoDrag(self):
		pos = self._tracker.getPosition(self._trackerFlag)
		self.head.setPosition(pos)
		self.body_root.setPosition(pos)

	def _updatePositionDrag(self):
		pos = self._tracker.getPosition(self._trackerFlag)
		self.head.setPosition(pos)
		self.body_root.setPosition(pos)

		SPEED_DAMPING = 2.0
		ANGLE_DAMPING = 0.4
		MAX_DIST = 0.5

		# Increment drag position towards actual position
		t = viz.clamp(viz.getFrameElapsed() * SPEED_DAMPING,0.0,1.0) - 1.0
		self._bodyDragPos = vizmat.Interpolate(self._bodyDragPos,pos,-(t*t*t*t-1.0))
		#self._bodyDragPos = vizmat.Interpolate(pos,self._bodyDragPos,SPEED_DAMPING)
		self._bodyDragPos[1] = pos[1]

		# Clamp drag distance to max value
		lookPos = viz.Vector(self._bodyDragPos) - pos
		if lookPos.length() > MAX_DIST:
			lookPos.setLength(MAX_DIST)
		lookPos[1] -= ANGLE_DAMPING

		# Have body root look at drag position
		m = viz.Matrix()
		m.makeVecRotVec([0,-1,0],lookPos)
		self.body_root.setQuat(m.getQuat())

	def _updateBodyTrackNone(self):
		"""Update just the head object"""

		quat = self._tracker.getQuat(self._trackerFlag)
		self.head.setQuat(quat)

		self._updatePosition()

	def _updateBodyTrackYaw(self):
		"""Update just the head object"""
		yaw,pitch,roll = self._tracker.getEuler(self._trackerFlag)
		self.body.setEuler([yaw,0,0])
		self.head.setEuler([yaw,pitch,roll])
		self._updatePosition()

	def _updateBodyTrackYawIncrement(self):
		"""Update just the head object"""
		yaw,pitch,roll = self._tracker.getEuler(self._trackerFlag)
		self.head.setEuler([yaw,pitch,roll])

		# Check if body needs to increment to current yaw
		if abs(yaw-self._lastBodyYaw) >= self._bodyYawIncrement:

			self._lastBodyYaw = yaw

			# Setup function that will animate body turning to new yaw
			begin = vizmat.EulerToQuat(self.body.getEuler()[0],0,0)
			end = vizmat.EulerToQuat(yaw,0,0)
			interpolate = vizact._createInterpolator(vizact.easeOutStrong,begin,end,base=vizmat.slerp)
			data = viz.Data(begin=begin,end=end,interpolate=interpolate,elapsed=0.0,duration=self._bodyIncrementTime)
			def _incrementYaw():

				data.elapsed += viz.getFrameElapsed()
				if data.elapsed >= data.duration:
					self.body.setQuat(data.end)
					return True

				self.body.setQuat(data.interpolate(data.begin,data.end,data.elapsed/data.duration))
				return False

			self._incrementFunc = _incrementYaw

		# If increment function is valid call it
		if self._incrementFunc is not None:
			if self._incrementFunc():
				self._incrementFunc = None

		self._updatePosition()

if __name__ == '__main__':

	viz.setMultiSample(8)
	viz.go()

	# Add model
	model = Steve()
	model.bodyColor = [1,0.8,0.8]
	model.eyeColor = [0.8,0,0]
	model.outlineColor = viz.WHITE
	model.shadeColor = [1,0.5,0.5]

	# Setup tracking for model
	import viztracker
	tracker = viztracker.Keyboard6DOF()

	# Orientation does not affect body
	#model.setTracker(tracker,bodyTrackMode=BODY_TRACK_NONE)

	# Yaw orientation is applied to body
	model.setTracker(tracker)

	# Body yaw is updated every specified increment
	#model.setTracker(tracker,bodyYawIncrement=90.0)

	# Setup camera navigation
	import vizcam
	bb = model.getBoundingSphere()
	cam = vizcam.PivotNavigate(center=bb.center,distance=bb.radius*2.5)
	viz.cam.setHandler(cam)

	# Setup environment
	viz.clearcolor(viz.GRAY)
	import vizshape
	vizshape.addGrid(color=[0.2]*3)

