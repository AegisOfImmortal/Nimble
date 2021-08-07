# Nimble Programming Challenge

This project intends to solve the problems given by Nimble Programming Challenge.

Server.py creates a running server that generates a green ball bouncing over a sacpe of 960*540, in a video stream of frames and will be sent to clients via aiortc TCPSocketSignaling.
Usage:

    python3 Server.py

Client.py creates a running client that will capture the boucing ball frames, display them via openCV, and then make a prediction of the ball's position based on the received frame, and stores the prediction in multiprocessing value which is later extracted and sent back to the server.
Usage:

    python3 Client.py

In the end the server will calculate the error with the prediction and actual position, and print the errors on the screen.
Unit tests has been provided and can be run seperately or all via

    pytest-3

Demo video, Docker Containers and minibuke has been provided.