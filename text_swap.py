import viz
import vizact
import vizinfo

viz.setMultiSample(4)
viz.fov(60)
viz.go()

#vizinfo.InfoPanel()
#
FRAME_RATE  = 30        # in Hertz

#Create cycle of textures
movieImages = viz.cycle( [ viz.addTexture('textures/Seq/TestTexture_00%d.jpg' % i) for i in range(1,98) ] )

#Add and position the movie screen
screen = viz.addTexQuad()
screen.setPosition([0, 1.82, 1.5])
screen.setScale([4.0/3, 1, 1])

#Setup timer to swap texture at specified frame rate
def NextMovieFrame():
    screen.texture(movieImages.next())

vizact.ontimer(1.0/FRAME_RATE, NextMovieFrame)