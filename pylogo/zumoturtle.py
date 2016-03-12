
try:
    from zumoadjust import ROTATION_ADJUST, LEFT_ADJUST, BLACK_THRES
except:
    ROTATION_ADJUST = 1.0
    LEFT_ADJUST = 1.0
    BLACK_THRES = 2048

try:
    import socket
    import atexit
    import time
    HOST = 'localhost'
    PORT = 6571
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    atexit.register(sock.close)

    def send_cmd(cmd, param):
        param = int(param)
        cmdbytes = [ord(cmd), (param>>24)&0xff, (param>>16)&0xff, (param>>8)&0xff, param&0xff]
        sock.sendall(''.join(map(chr, cmdbytes)))
        resbuf = ""
        got = sock.recv(1)
        while got != '\n':
            resbuf += got
            got = sock.recv(1)
        return resbuf.strip()

    def forward(length):
        send_cmd("f", length)

    def backward(length):
        send_cmd("b", length)

    def turnLeft(angle):
        send_cmd("l", angle*ROTATION_ADJUST)

    def turnRight(angle):
        send_cmd("r", angle*ROTATION_ADJUST)

    def changeLeftAdjust(ratio):
        send_cmd("c", int(ratio*1000))

    def playMusic():
        send_cmd("p", 0)

    def getGroundSensor(index):
        time.sleep(0.001)
        res = 4294967295
        while res == 4294967295:
            res = int(send_cmd("s", index))
            time.sleep(0.001)
        return res

    def getGroundSensorSum():
        return int(send_cmd("a", 0))
        
    def groundPurple():
        return groundPurpleRight() or groundPurpleCenter() or groundPurpleLeft()

    def groundBlack():
        return groundBlackRight() or groundBlackCenter() or groundBlackLeft()

    def groundPurpleRight():
        return getGroundSensor(5) < BLACK_THRES

    def groundBlackRight():
        return getGroundSensor(5) >= BLACK_THRES

    def groundPurpleLeft():
        return getGroundSensor(0) < BLACK_THRES

    def groundBlackLeft():
        return getGroundSensor(0) >= BLACK_THRES

    def groundPurpleCenter():
        return getGroundSensor(1) < BLACK_THRES or getGroundSensor(2) < BLACK_THRES or getGroundSensor(4) < BLACK_THRES

    def groundBlackCenter():
        return getGroundSensor(1) >= BLACK_THRES or getGroundSensor(2) >= BLACK_THRES or getGroundSensor(4) >= BLACK_THRES

    # adapt left/right motors speed for each robot    
    changeLeftAdjust(LEFT_ADJUST)
    
except Exception as err:
    print "\033[33;1m[WARNING]\033[0m No Arduino YUN Bridge:", str(err)

    def do_print(text):
        def f(*args):
            print text, args
            return 0
        return f

    for f in ('forward', 'backward', 'turnLeft', 'turnRight', 'getGroundSensor', 'playMusic', 'getGroundSensorSum'):
        globals()[f] = do_print(f)
