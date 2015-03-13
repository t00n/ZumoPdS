#include <ZumoMotors.h>
#include <Console.h>

float leftAdjust = 1.04;
static int speed = 150;
ZumoMotors motors;

static inline void setSpeeds(int left, int right, int wait){
    motors.setSpeeds(left*speed*leftAdjust, right*speed/leftAdjust);
    delay(5*wait);
    motors.setSpeeds(0, 0);
}

static inline void waitConsole(){
    while (! (Console.connected() && Console.available()));
}

typedef struct LOGO_cmd_t {
    char name;
    void(*procedure)(uint32_t);
} LOGO_cmd;

struct {
    char name;
    uint32_t param;
} command;

void   forward(uint32_t len){setSpeeds( 1,  1, len);}
void  backward(uint32_t len){setSpeeds(-1, -1, len);}
void  turnLeft(uint32_t len){setSpeeds(-1,  1, len);}
void turnRight(uint32_t len){setSpeeds( 1, -1, len);}

#define N_Commands sizeof(Commands)/sizeof(LOGO_cmd)
LOGO_cmd Commands[] = {
    {'f', forward},
    {'b', backward},
    {'l', turnLeft},
    {'r', turnRight}
};

void readCommand(){
    waitConsole();
    command.name = Console.read();
    command.param = 0;
    for (int i=0; i<4; i++){
        waitConsole();
        if (i > 0)
            command.param <<= 8;
        command.param += Console.read();
    }
}

void setup(){
    Bridge.begin();
    Console.begin();
    while (! Console);
}

void loop(){
    readCommand();
    for (int i=0; i<N_Commands; i++){
        if (Commands[i].name == command.name){
            Commands[i].procedure(command.param);
            Console.println(command.name);
            return;
        }
    }
}
