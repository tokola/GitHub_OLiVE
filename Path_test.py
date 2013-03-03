import viz

viz.go()

sackItem = viz.add('models/objects/sack.osgb')

def AnimateSack():
		
	sack = sackItem.getChild('sack')
	sack_path = sackItem.getChild('path1R').copy()
#	sack_path.setAnimationLoopMode(0)
	sack.setParent(sack_path, node='path1R')