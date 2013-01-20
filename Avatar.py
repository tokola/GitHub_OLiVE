import viz
import vizact
import Robot
import vizshape

class Avatar():
	"""This is the Avatar class"""
	def __init__ (self, view, color):
		self._view = view
		self._player_matrix = viz.Matrix() #self.view.getMatrix()
		self._avatar = Robot.Steve()
		self._avatar.disable([viz.INTERSECTION, viz.PICKING], op=viz.OP_ROOT)
		self._avatar.head.setScale([2,2,2])
		self._avatar.body_root.setScale([2,2,2])
		#self._avatar.disable(viz.PHYSICS)
		bodyColor = [float(c)/255 for c in color[0]]
		shadeColor= [float(c)/255 for c in color[1]]
		self._avatar.setBodyColor(bodyColor)
		self._avatar.setShadeColor(shadeColor)
		self._avatar.setTracker(self._player_matrix)
		#self._avatar.setTracker(viz.link(self._avatar.body, viz.NullLinkable,offset=[0,-0.2,0]))
		# add the representation on the map
		self._mapAva = viz.addTexQuad(size=.75)
		#self._mapAva = vizshape.addSphere(.5,10,10)
		self._mapAva.texture(viz.addTexture('textures/mapAva_icon.png'),'',0)
		self._mapAva.color(bodyColor)
		self._updateFunc = vizact.onupdate(0, self.UpdatePlayer)
		
	def UpdatePlayer(self):
		pos = self._view.getPosition(viz.VIEW_ORI)
		quat= self._view.getQuat(viz.VIEW_ORI)
		eul = self._view.getEuler(viz.VIEW_ORI)
		self._player_matrix.setPosition(pos)
		self._player_matrix.setQuat(quat)
		self._mapAva.setPosition(pos[0], 0.5, pos[2])
		self._mapAva.setEuler(eul[0], 90, eul[2])
		#self._player_matrix = self._view.getMatrix(viz.VIEW_ORI)
		
#	def Update(self):
#		vizact.ontimer(0, self.UpdatePlayer)
		
		
if __name__ == '__main__':

    viz.setMultiSample(2)
    viz.go()

    ground = viz.addChild('ground.osgb')