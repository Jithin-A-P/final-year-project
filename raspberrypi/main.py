#!/usr/bin/python3

import cv2
import os
import time
import serial
import itertools
import sys
import numpy as np
from threading import Thread
from picamera2 import Picamera2, Preview
from server import Server
from keras.models import load_model
from http.server import HTTPServer

isWaiting = False # Global variable to control the loading animation

def start_server():
    httpd = HTTPServer(('0.0.0.0', 8000), Server)
    print('HTTP Server started on port 8000')
    httpd.serve_forever()

def init_cam():
    os.environ["LIBCAMERA_LOG_LEVELS"] = "3"
    Picamera2.set_logging(Picamera2.ERROR)
    picam2 = Picamera2()
    camera_config = picam2.create_still_configuration(main={"size": (1920, 1080)}, lores={"size": (320, 240)}, display="lores")
    picam2.configure(camera_config)
    if len(sys.argv) > 1:
        if sys.argv[1] == '--show-preview':
            picam2.start_preview(Preview.QTGL)
    picam2.start()
    time.sleep(0.5)
    print('Camera initialized\n')
    return picam2

def capture_image(picam2):
    picam2.capture_file('image.jpg')
    image = cv2.imread('image.jpg')
    image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)
    image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)
    return (image / 127.5) - 1

def loading_animation():
    global isWaiting
    isWaiting = True
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if not isWaiting:
            break
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write('\b')

def main():
    global isWaiting
    print('Automatic Shopping Cart\n')
    ser = serial.Serial('/dev/ttyS0', 9600)
    print('UART initialized with baudrate of 9600')
    model = load_model('keras_model.h5', compile=False)
    print('ML model loaded')
    Thread(target=start_server, daemon=True).start()
    labels = open('labels.txt', 'r').readlines()
    picam2 = init_cam()
    
    while True:
        print('Waiting for weight change ', end='')
        Thread(target=loading_animation, daemon=True).start()
        weight = ''
        while isWaiting:
            if ser.in_waiting > 0:
                c = ser.read()
                if c == b'R':
                    ser.write(b'X')
                    Server.clear_products()
                    continue
                if c == b'W':
                    c = ser.read()
                    while c != b'g':
                        weight += c.decode()
                        c = ser.read()
                    isWaiting = False
                    break

        weight = int(weight)     
        print('\rCapturing and processing image ', end='')
        Thread(target=loading_animation, daemon=True).start()
        image = capture_image(picam2)
        probabilities = model.predict(image)
        isWaiting = False
        product_idx = int(np.argmax(probabilities))
        ser.write(str(product_idx).encode())
        Server.add_product(product_idx, weight)
        time.sleep(0.2)
        print("\r", end='')
        print(labels[np.argmax(probabilities)])

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nTerminated !!!')
        raise SystemExit