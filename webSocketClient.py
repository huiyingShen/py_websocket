import websocket
import _thread
import time

# def on_message(ws, message):
#     print(message)

# def on_error(ws, error):
#     print(error)

# def on_close(ws, close_status_code, close_msg):
#     print("### closed ###")

# def on_open(ws):
#     print("Opened connection")

def test0():
    def on_message(ws, message):
        print(message)

    def on_error(ws, error):
        print(error)

    def on_close(ws, close_status_code, close_msg):
        print("### closed ###")

    def on_open(ws):
        print("Opened connection")

    websocket.enableTrace(True)
    # ws = websocket.WebSocketApp("wss://api.gemini.com/v1/marketdata/BTCUSD",
    ws = websocket.WebSocketApp("ws://34.237.62.252:8001",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)

    ws.run_forever(dispatcher=rel)  # Set dispatcher to automatic reconnection
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()

def getClient(host,port, trace = False):
    def on_message(ws, message):
        print(message)

    def on_error(ws, error):
        print(error)

    def on_close(ws, close_status_code, close_msg):
        print("### closed ###")

    def on_open(ws):
        print("Opened connection")

    if trace: websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://" + host + ":" + str(port),
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    return ws

def test1():
    host,port = "34.237.62.252",8001
    ws = getClient(host,port, trace=False)
    ws.run_forever()  # Set dispatcher to automatic reconnection
    
    ws1 = getClient(host,port, trace=False)
    ws1.run_forever()  # Set dispatcher to automatic reconnection

    
    import time
    for cnt in range(10):
        ws.send("hello,  New Landmark Data, please: " + str(cnt))
        time.sleep(1)

    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()

if __name__ == "__main__":
    test1()