import traceback

try:
    import socket
    import atexit
    HOST = 'localhost'
    PORT = 6571
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    atexit.register(sock.close)

    def send_cmd(cmd, param):
        param = int(param)
        cmdbytes = [ord(cmd), (param>>24)&0xff, (param>>16)&0xff, (param>>8)&0xff, param&0xff]
        sock.sendall(''.join(map(chr, cmdbytes)))
        while sock.recv(1) != '\n':
            pass

    def forward(length):
        send_cmd("f", length)

    def backward(length):
        send_cmd("b", length)

    def turnLeft(angle):
        send_cmd("l", angle)

    def turnRight(angle):
        send_cmd("r", angle)

except Exception as err:
    print "\033[33;1m[WARNING]\033[0m No Arduino YUN Bridge:", str(err)

    def forward(length):
        print "  forward", length

    def backward(length):
        print " backward", length

    def turnLeft(angle):
        print " turnLeft", angle

    def turnRight(angle):
        print "turnRight", angle
