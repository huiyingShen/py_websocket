import threading
from msClient import TheClient

class Simple_Client:
    def __init__(self):
        self.pnts_sav = [[1021, 118],[451, 139], [447, 583],[1066, 566],[483, 289], [884, 497]]
        self.scale = 0.667
        self.ws = TheClient("34.237.62.252",8001,trace = False, on_message=self.on_message).ws
        threading.Thread(target=self.ws.run_forever).start()
        threading.Thread(target=self.sendDataLoop).start()


    def sendDataLoop(self):
        from time import sleep
        print("starting sendOldLoop(), ...")
        while True:
            sleep(5*60)
            self.sendSaved()
            
    def sendSaved(self):
        print("sendSaved(), ...,")
        h = 722
        jnk = "" 
        for p in self.pnts_sav:
            x,y = h-p[1], p[0]
            jnk += '\n{} {}'.format(x/self.scale, y/self.scale)
        print(jnk[1:])
        self.ws.send(f"New Landmark Data:" + jnk[1:])

    def on_message(self, ws,txt):
        if len(txt) < 100:
            print("MainWindow.on_mmessage, txt = ", txt)
        else:
            print("len = ",len(txt))
            print("txt[:100] = ",txt[:100])
            s = txt[:100]+"_test"
            pos = s.find(' - ')
            print("pos = ", pos)
            print(txt[pos+3:100])

if __name__ == '__main__':
    Simple_Client()