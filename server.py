''' 1. Server python program '''

import cv2
import numpy as np
import argparse
import asyncio
from av import VideoFrame
from aiortc import VideoStreamTrack, RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
from aiortc.contrib.signaling import BYE, TcpSocketSignaling, add_signaling_arguments

class BouncingBall():
    ''' 4. Generates 2D image ball bouncing '''

    def __init__(self):
        ''' Initialization of Animation parameters '''

        self.WIDTH = 720
        self.HEIGHT = 480
        self.dx = 10
        self.dy = 10
        self.xCo = 240
        self.yCo = 240
        self.ballRad = 10
        self.ballColor = (0, 255, 0)
        self.i = 0
        self.predX = 0
        self.predY = 0

    def Inbound(self, maxBound, x):
        '''
        Inbound check for ball
        Input:
            maxBound: int for maximum coordinate
            x: int for coordinate to be checked
        Output:
            Inbound check True/False
            
        '''
        if (x >= maxBound or x <= 0):
            return True
        return False

    def BouncingBall(self):
        '''
        Creation of one new frame of ball bouncing
        Output;
            img: img frame in numpy array
            xCo,yCo; x,y coordinates

        '''
        img = np.zeros((self.HEIGHT, self.WIDTH, 3), dtype = 'uint8')
        if self.Inbound(self.WIDTH, self.xCo):
            self.dx *= -1
        if self.Inbound(self.HEIGHT, self.yCo):
            self.dy *= -1

        self.xCo += self.dx
        self.yCo += self.dy
        self.i += 1
        cv2.circle(img, (self.xCo, self.yCo), self.ballRad, self.ballColor, -1)
        return (img, self.xCo, self.yCo)

class FrameConstruct(VideoStreamTrack):
    '''
    5. Creates the bouncing ball and prepares for transfer to client
    Use the VideoStreamTrack class to package the frames

    '''

    kind = "video"

    def __init__(self, ball):
        ''' Initialization of Ball '''

        super().__init__()
        self.ball =  ball
        self.x = 0
        self.y = 0


    async def recv(self):
        ''' Image is packed into a frame '''

        pts, time_base = await self.next_timestamp()
        img, self.x, self.y = self.ball.BouncingBall()
        frame = VideoFrame.from_ndarray(img, format = "bgr24")
        frame.pts = pts
        frame.time_base = time_base
        return frame


async def consume_signaling(pc, signaling):
    '''
    Utility function to keep signal receive port and offer-answer active
    Taken from aiortc server example
    '''
    while True:
        obj = await signaling.receive()

        if isinstance(obj, RTCSessionDescription):
            await pc.setRemoteDescription(obj)
        elif isinstance(obj, RTCIceCandidate):
            await pc.addIceCandidate(obj)
        elif obj is BYE:
            print("Exiting")
            break


def computeErrors(x1, y1, x2, y2):
    ''' Calculates the difference (error) within coordinaties '''

    error = ((x1 - x2)**2 + (y1 - y2)**2)**(1/2)

    print("Real Center: " + str(x1) + ", " + str(y1))
    print("Pred Center: " + str(x2) + ", " + str(y2))
    print("Error: " + str(error))


async def main(pc, signaling):
    '''
    3. Using aiortc built-in TcpSocketSignaling
    a. Create aiortc offer and send to client
    Input
        pc: RTC remote Peer Connection
        signaling : TcpSocketSignaling object

    '''
    ball = BouncingBall()
    track = FrameConstruct(ball)
    params = await signaling.connect()

    dc = pc.createDataChannel('chat')

    @pc.on('icegatheringstatechange')
    def pcIceGatherStateChange():
        print('NEW Ice Gathering State %s' % pc.iceGatheringState)

    @pc.on('iceconnectionstatechange')
    def pcIceConnectionStateChange():
        print('NEW Ice Connection State %s' % pc.iceConnectionState)

    @pc.on('signalingstatechange')
    def pcSignalingStateChange():
        print('NEW Signaling State %s' % pc.signalingState)

    @pc.on('track')
    def pcTrack():
        print('NEW track %s' % track.id)

    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        async def on_message(message):
            '''12. Display received coordinates and compute error'''

            if (message.startswith("coords")):
                coords = message[7:].split(",")
                computeErrors(ball.xCo, ball.yCo, int(coords[0]), int(coords[1]))

    pc.addTrack(track)
    await pc.setLocalDescription(await pc.createOffer())
    await signaling.send(pc.localDescription)

    await consume_signaling(pc, signaling)


if __name__ == "__main__":
    print("Server started")
    parser = argparse.ArgumentParser(description="Ball Position Detector - Server")
    add_signaling_arguments(parser)

    args = parser.parse_args()

    signaling = TcpSocketSignaling(args.signaling_host, args.signaling_port)
    pc = RTCPeerConnection()


    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            main(pc, signaling)
        )
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(signaling.close())
        loop.run_until_complete(pc.close())
