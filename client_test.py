import cv2
import numpy as np
import client

''' Test parse image'''
def test_imageParse():
    img = np.zeros((500, 500, 3), dtype = 'uint8')
    img = cv2.circle(img, (200, 200), 5, (255, 255, 255), -1)
    assert client.imageParse is client.imageParse