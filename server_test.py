import server

def test_BouncingBall():
    try:
        ball = server.BouncingBall()
        print(ball.Height)
        print(ball.Width)
    except ValueError:
        pass
