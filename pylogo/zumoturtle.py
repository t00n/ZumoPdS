try:
    import socket
    import atexit
    HOST = 'localhost'
    PORT = 6571
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    atexit.register(sock.close)
    try:
        from zumoadjust import rotation_adjust
    except:
        rotation_adjust = 1.0

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
        send_cmd("l", angle*rotation_adjust)

    def turnRight(angle):
        send_cmd("r", angle*rotation_adjust)

    def getGroundSensor(index):
        return int(send_cmd("s", index))

except Exception as err:
    print "\033[33;1m[WARNING]\033[0m No Arduino YUN Bridge:", str(err)

    def do_print(text):
        def f(*args):
            print text, args
        return f

    for f in ('forward', 'backward', 'turnLeft', 'turnRight', 'getGroundSensor'):
        globals()[f] = do_print(f)
