#include <ZumoMotors.h>
#include <Console.h>

/* Speeds, in motors unit */
#define ULTRAFAST 400
#define FAST 300
#define SLOW 200

ZumoMotors motors;

void setup(){
    // initialize serial communication:
    Bridge.begin();
    Console.begin();
    while (!Console);
    Console.println("Welcome to ZumoRobot");
}

void loop(){
    if (Console.available()){
        switch (Console.read()) {
            case 'F':
            case 'f':
                motors.setSpeeds(SLOW, SLOW);
                delay(250);
                break;
            case 'B':
            case 'b':
                motors.setSpeeds(-SLOW, -SLOW);
                delay(250);
                break;
            case 'L':
            case 'l':
                motors.setSpeeds(-SLOW, SLOW);
                delay(250);
                break;
            case 'R':
            case 'r':
                motors.setSpeeds(SLOW, -SLOW);
                delay(250);
                break;
        }
    }
    motors.setSpeeds(0, 0);
}
