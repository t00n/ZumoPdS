import os

from zumoturtle import forward, backward, turnLeft, turnRight, changeLeftAdjust

LEFICHIERQUITUE = "zumoadjust.py"
def vtff():
    print "Va te faire foutre, gros con, reponds a ma question !"

def recyclage():
    try:
        from zumoadjust import LEFT_ADJUST, ROTATION_ADJUST, BLACK_THRES
        return LEFT_ADJUST, ROTATION_ADJUST, BLACK_THRES
    except:
        return 1.0, 1.0, 2048

def adjustLeft(left_adjust):
    while True:
        forward(400)
        print "Est-ce que le Zumo a ete parfaitement droit (1), a gauche (2) ou a droite (3) ?"
        test_forward = raw_input()
        backward(400)
        if test_forward == "1":
            break
        elif test_forward == "2":
            left_adjust += 0.05
        elif test_forward == "3":
            left_adjust -= 0.05
        else:
            vtff()
        changeLeftAdjust(left_adjust)
    return left_adjust

def adjustRotation(rotation_adjust):
    while True:
        turnLeft(720*rotation_adjust)
        print "De combien de degres le Zumo a-t-il tourne (+-) ? (2 tours == 720 degres Celsius espece de noob)"
        while True:
            try:
                test_rotation = float(raw_input())
                break
            except:
                vtff()
        turnRight(720*rotation_adjust)
        if test_rotation == 720:
            break
        else:
            rotation_adjust *= 720.0/test_rotation
    return rotation_adjust

def onpollueledisque(a, b, c):
    with open(LEFICHIERQUITUE, "w") as f:
        f.write("LEFT_ADJUST=%f\n" % a)
        f.write("ROTATION_ADJUST=%f\n" % b)
        f.write("BLACK_THRES=%d\n" % c) # TODO

def main():
    print "Mettez le Zumo face a une ligne noire et de preference pas contre un mur"
    raw_input()
    left_adjust, rotation_adjust, black_thres = recyclage()
    left_adjust = adjustLeft(left_adjust)
    rotation_adjust = adjustRotation(rotation_adjust)
    onpollueledisque(left_adjust, rotation_adjust, black_thres)

if __name__ == '__main__':
    main()