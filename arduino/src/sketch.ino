#include <ZumoMotors.h>
#include <Console.h>

float leftAdjust = 1.08;
static int speed = 150;
ZumoMotors motors;

typedef struct LOGO_cmd_t {
    char *name;
    void(*procedure)(long);
} LOGO_cmd;

void forward(long len){
    motors.setSpeeds(speed*leftAdjust, speed);
    delay(1000 * len / speed);
    motors.setSpeeds(0, 0);
}

void backward(long len){
    motors.setSpeeds(-speed*leftAdjust, -speed);
    delay(1000 * len / speed);
    motors.setSpeeds(0, 0);
}

void turnLeft(long len){
    motors.setSpeeds(-speed*leftAdjust, speed);
    delay(1000 * len / speed);
    motors.setSpeeds(0, 0);
}

void turnRight(long len){
    motors.setSpeeds(speed*leftAdjust, -speed);
    delay(1000 * len / speed);
    motors.setSpeeds(0, 0);
}

void setSpeed(long newSpeed){
    if (0 < speed && speed < 500)
        speed = newSpeed;
}

LOGO_cmd Commands[] = {
    {"forward", forward}, {"fw", forward},
    {"backward", backward}, {"bw", backward},
    {"turnLeft", turnLeft}, {"tl", turnLeft},
    {"turnRight", turnRight}, {"tr", turnRight},
    {"setSpeed", setSpeed}, {"ss", setSpeed}
};

void setup(){
    Bridge.begin();
    Console.begin();
    while (! Console);
}

bool executeCommand(char *command){
    char *operand = strchr(command, ' ');
    if (operand == NULL)
        return false;

    while (*operand == ' '){
        *operand = '\0';
        operand++;
    }

    char *end = NULL;
    long value = strtol(operand, &end, 10);
    if (end == operand)
        return false;

    for (int i=0; i<sizeof(Commands)/sizeof(LOGO_cmd); i++){
        if (strcmp(Commands[i].name, command) == 0){
            Commands[i].procedure(value);
            return true;
        }
    }
    return false;
}

int buflen = 0;
char buffer[128] = {'\0'};

void loop(){
    if (Console.connected() && Console.available()){
        if (buflen < sizeof(buffer)-1){
            buffer[buflen] = Console.read();
        } else {
            memset(buffer, 0, sizeof(buffer));
            buflen = 0;
        }
        buflen++;
        if (buffer[buflen-1] == '\n'){
            buffer[buflen] = '\0';
            if (executeCommand(buffer)){
                Console.print("# => ");
                Console.println(buffer);
            }
            memset(buffer, 0, sizeof(buffer));
            buflen = 0;
        }
    }
}
