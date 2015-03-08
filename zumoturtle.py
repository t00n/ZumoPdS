import socket

try:
    HOST = 'localhost'    # The remote host
    PORT = 6571             # The same port as used by the server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    def forward(length):
        print "  forward", length
        sock.sendall("fw %d" % length)
        sock.read(1024)

    def backward(length):
        print " backward", length
        sock.sendall("bw %d" % length)
        sock.read(1024)

    def turnLeft(angle):
        print " turnLeft", angle
        sock.sendall("tl %d" % angle)
        sock.read(1024)

    def turnRight(angle):
        print "turnRight", angle
        sock.sendall("tr %d" % angle)
        sock.read(1024)

    def setSpeed(speed):
        print " setSpeed", speed
        sock.sendall("ss %d" % speed)
        sock.read(1024)

except:
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
