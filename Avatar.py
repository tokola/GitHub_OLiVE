import viz
import vizact
import Robot
import vizshape

class Avatar():
	"""This is the Avatar class"""
	def __init__ (self, view, color):
		self._view = view
#		self._player_matrix = viz.Matrix() #self.view.getMatrix()
		self._avatar = Robot.Steve()
		self._avatar.disable([viz.INTERSECTION, viz.PICKING], op=viz.OP_ROOT)
		self._avatar.head.setScale([1.5,1.5,1.5])
		self._avatar.body_root.setScale([1.5,1.5,1.5])
		#self._avatar.disable(viz.PHYSICS)
		bodyColor = [float(c)/255 for c in color[0]]
		shadeColor= [float(c)/255 for c in color[1]]
		self._avatar.setBodyColor(bodyColor)
		self._avatar.setShadeColor(shadeColor)
#		self._avatar.setTracker(self._player_matrix)
		self._avatar.setTracker(viz.link(self._view, viz.NullLinkable,offset=[0,-0.25,0]))
		# add the representation on the map
		self._mapAva = viz.addTexQuad(size=.75)
		#self._mapAva = vizshape.addSphere(.5,10,10)
		self._mapAva.texture(viz.addTexture('textures/mapAva_icon.png'),'',0)
		self._mapAva.color(bodyColor)
		self._updateFunc = vizact.onupdate(0, self.UpdatePlayer)
		
	def UpdatePlayer(self):
#		self._view.setPosition([self._view.getPosition()[0], 1.82, self._view.getPosition()[2]])
		pos = self._view.getPosition(viz.VIEW_ORI)
		eul = self._view.getEuler(viz.VIEW_ORI)
#		quat= self._view.getQuat(viz.VIEW_ORI)
#		self._player_matrix.setPosition(pos)
#		self._player_matrix.setQuat(quat)
		self._mapAva.setPosition(pos[0], 0.5, pos[2])
		self._mapAva.setEuler(eul[0], 90, eul[2])
		#self._player_matrix = self._view.getMatrix(viz.VIEW_ORI)
		
		
if __name__ == '__main__':

    viz.setMultiSample(2)
    viz.go()

    ground = viz.addChild('ground.osgb')