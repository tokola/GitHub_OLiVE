import viz

viz.go()

sackItem = viz.add('models/objects/sack2.osgb')
sack_path = sackItem.getChild('path'+'1R').copy()
sack_path.setAnimationLoopMode(0)
sack_path.setAnimationSpeed(0)
	
def AnimateSack():
	#create a new group below 'sack' and adopt its children
	sack = sackItem.insertGroupBelow('sack')
#	sack.setEuler(90,0,0)
	sack.setParent(sack_path, node='path'+'1R')
	sack_path.setAnimationSpeed(1)