import threading
import base64
from webSocketServerClient import getClient
from time import time,sleep

def b64toImg(imgstring):
    imgdata = base64.b64decode(imgstring)
    filename = 'some_image.jpg'  # I assume you have a way of picking unique filenames
    with open(filename, 'wb') as f:
        f.write(imgdata)

def test0():
    running = True
    def sending(ws):
        while running:
            ws.send(f"hello, time = {time()}")
            # print("sending...")
            sleep(5.0)
    def receiving(ws):
        while running:
            txt = ws.recv()
            if len(txt) < 100:
                print("txt = ", txt)
            else:
                print("txt[:100] = ",txt[:100])

    port = 8001
    sender = getClient(port=port)
    threading.Thread(target=sending, name='Ping Sender', args=(sender,)).start()
    receiver = getClient(port=port)
    receiving(receiver)

def test1():
    port = 8001
    sender = getClient(port=port)
    receiver = getClient(port=port)
    sender.send("image, please!")
    while True:
        txt = receiver.recv()
        if len(txt) < 100:
            print("txt = ", txt)
        else:
            print("txt[:100] = ",txt[:100])

if __name__=="__main__":
    test1()