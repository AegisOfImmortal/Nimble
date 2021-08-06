''' 2. Client python program '''

import cv2
import numpy as np
from multiprocessing import Process, Queue, Value
import argparse
import asyncio
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
from aiortc.contrib.signaling import BYE, TcpSocketSignaling, add_signaling_arguments

class FrameTransport(MediaStreamTrack):

    '''5. Transmit images (frames) using MediaStreamTrack'''

    kind = "video"
    def __init__(self, track):
        super().__init__()
        self.track = track

    async def recv(self):

        '''
        Waits for the frame to receive
            output: the frame received
        '''

        frame = await self.track.recv()
        return frame

async def consume_signaling(pc, signaling):
    '''
    Utility function to keep signal receive port and offer-answer active
    Taken from aiortc client example
    Also awaits answer
    '''
    while True:
        obj = await signaling.receive()

        if isinstance(obj, RTCSessionDescription):
            await pc.setRemoteDescription(obj)
            if obj.type == "offer":
                await pc.setLocalDescription(await pc.createAnswer())
                await signaling.send(pc.localDescription)
        elif isinstance(obj, RTCIceCandidate):
            await pc.addIceCandidate(obj)
        elif obj is BYE:
            print("Exiting")
            break

def imageParse(queue, X, Y):
    '''
    9. Parse the image and determine the current location of the ball
    input:
        queue: multiprocessing queue where parsed images are sorted 
        X: multiprocessing.value storage of X coords
        Y: multiprocessing.value storage of Y coords
    10. Store computed coordinates as values
    '''
    img = queue.get()
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray_image, 127, 255, 0)
    M = cv2.moments(thresh)
    if (M["m00"] != 0):
        X.value = int(M["m10"] / M["m00"])
        Y.value = int(M["m01"] / M["m00"])

async def analyzeTrack(pc, track):
    '''
    8. Send recieved image to process_a using queue
    '''
    localVideo = FrameTransport(track)
    dc = pc.createDataChannel('coords')

    X = Value('i', 0)
    Y = Value('i', 0)
    process_q = Queue()

    '''
    6. Display received images using opencv
    7. Starts a new process_a
    11. Send coodinates from the values of process_a
    '''

    while(True):
        try:
            process_a = Process(target = imageParse, args = (process_q, X, Y))
            process_a.start()
            frame = await localVideo.recv()

            img = frame.to_ndarray(format="bgr24")
            cv2.imshow("Client Feed", img)
            cv2.waitKey(1)
            process_q.put(img)
            process_a.join()
            dc.send("coords:" + str(X.value) + "," + str(Y.value))
        except Exception as e:
            print(e)



async def main(pc, signaling):
    '''
    3. Using aiortc built-in TcpSocketSignaling
    b. Receive aiortc offer and create answer
    Input
        pc: RTC remote Peer Connection
        signaling : TcpSocketSignaling object

    '''
    params = await signaling.connect()

    @pc.on("track")
    async def on_track(track):
        print("Track %s received" % track.kind)
        await analyzeTrack(pc, track)

    @pc.on("datachannel")
    def on_datachannel(channel):
        print(channel, "-", "created by remote party")

        @channel.on("message")
        def on_message(message):
            print(channel, "<", message)

    await consume_signaling(pc, signaling)


if __name__ == "__main__":
    print("Client started")
    parser = argparse.ArgumentParser(description="Ball Position Detector - Client")

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
        loop.run_until_complete(cv2.destroyAllWindows())