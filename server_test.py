import server

''' Test ball functions '''
def test_BouncingBall():
    ball = server.BouncingBall()
    assert ball.Height == 540
    assert ball.Width == 960

def test_OutBound():
    ball = server.BouncingBall()
    assert ball.Outbound(ball.Width,2000)

def test_ballBounce():
    ball = server.BouncingBall()
    ball.BouncingBall()
    assert ball.xCoord == 65

''' Test Frame Construction '''
def test_FrameConstruction():
    ball = server.BouncingBall()
    track = server.FrameConstruction(ball)
    assert track.x == 60
    assert track.y == 60

''' Test Computer Error '''
def test_ComputeError():
    assert server.computeErrors(1,1,1,1) is None