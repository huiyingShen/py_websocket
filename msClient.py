import websocket
 
class TheClient:   
    def __init__(self,host,port, trace = True, on_message = None):
        websocket.enableTrace(trace)
        if on_message is None:
            self.ws = websocket.WebSocketApp("ws://" + host + ":" + str(port),
                                on_open=self.on_open,
                                on_message=self.on_message,
                                on_error=self.on_error,
                                on_close=self.on_close)
        else:
             self.ws = websocket.WebSocketApp("ws://" + host + ":" + str(port),
                                on_open=self.on_open,
                                on_message=on_message,
                                on_error=self.on_error,
                                on_close=self.on_close)           
                                
    def on_message(self, ws, txt):
        print("on_message:")
        if len(txt) < 100:
            print("txt = ", txt)
        else:
            print("len = ",len(txt))
            print("txt[:100] = ",txt[:100])
            s = txt[:100]+"_test"
            pos = s.find(' - ')
            print("pos = ", pos)
            print(txt[pos+3:100])
            try:
                self.b64toImg(txt[pos+3:])
                # transform = QTransform().rotate(-90)
                # self.loadImage(QPixmap("some_image.jpg").transformed(transform))
                # self.pnts = []
            except:
                pass

    def on_error(self, ws,error):
        print(error)

    def on_close(self, ws,close_status_code, close_msg):
        print("### closed ###")

    def on_open(self,ws):
        print("Opened connection")

    def b64toImg(self,imgstring, filename = 'some_image.jpg'):
        import base64
        imgdata = base64.b64decode(imgstring)
        with open(filename, 'wb') as f:
            f.write(imgdata)

    def send(self,txt):
        self.ws.send(txt)

def test0():
    import time,threading
    ws1 = TheClient("34.237.62.252",8001,trace = True)
    threading.Thread(target=ws1.ws.run_forever).start()

    ws2 = TheClient("34.237.62.252",8001,trace = True)
    threading.Thread(target=ws2.ws.run_forever).start()

    for i in range(10):
        ws1.send("hello from ms1: "  + str(i))
        time.sleep(5)
    time.sleep(60)


if __name__ == '__main__':
    test0()
