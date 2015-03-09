import traceback

try:
    import socket
    HOST = 'localhost'
    PORT = 6571
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    def send_32u4(fmt, *args):
        sock.sendall((fmt+"\n") % args)
        while sock.recv(1) != "\n":
            pass

    def forward(length):
        send_32u4("fw %d\n", length)

    def backward(length):
        send_32u4("bw %d\n", length)

    def turnLeft(angle):
        send_32u4("tl %d\n", angle)

    def turnRight(angle):
        send_32u4("tr %d\n", angle)

    def setSpeed(speed):
        send_32u4("ss %d\n", speed)

except:
    traceback.print_exc()
    print "\033[33;1m[WARNING]\033[0m No Arduino YUN Bridge..."

    def forward(length):
        print "  forward", length

    def backward(length):
        print " backward", length

    def turnLeft(angle):
        print " turnLeft", angle

    def turnRight(angle):
        print "turnRight", angle

    def setSpeed(speed):
        print " setSpeed", speed
