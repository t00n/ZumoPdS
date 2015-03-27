#include <ZumoMotors.h>
#include <QTRSensors.h>
#include <ZumoReflectanceSensorArray.h>
#include <Console.h>
#include <ZumoBuzzer.h>

/* Adjust coef for left/right motors not running at the same speed */
float leftAdjust = 1.00;

/* Motors base speed */
static int speed = 200;

/* Ground sensors result array */
static unsigned int groundSensors[6];

ZumoMotors motors;
ZumoReflectanceSensorArray reflectArray(ZUMO_SENSOR_ARRAY_DEFAULT_EMITTER_PIN);
ZumoBuzzer buzzer;

/* Helper to set motors speeds */
static inline uint32_t setSpeeds(float left, float right, int wait){
    motors.setSpeeds(left*speed*leftAdjust, right*speed/leftAdjust);
    delay(wait);
    motors.setSpeeds(0, 0);
    return 0;
}

/* Wit for a character to be available on console */
static inline void waitConsole(){
    while (! (Console.connected() && Console.available()));
}

/* Invocable function */
typedef struct LOGO_cmd_t {
    char name;
    uint32_t(*procedure)(uint32_t);
} LOGO_cmd;

/* Running command */
struct {
    char name;
    uint32_t param;
} currentCommand;

uint32_t   forward(uint32_t len){return setSpeeds( 1.08,  1, 10+5*len);}
uint32_t  backward(uint32_t len){return setSpeeds(-1.15, -1, 10+5*len);}
uint32_t  turnLeft(uint32_t len){return setSpeeds(-1,  1, 10+3.85*len);}
uint32_t turnRight(uint32_t len){return setSpeeds( 1, -1, 10+3.98*len);}
uint32_t playMusic(uint32_t unused){
    buzzer.play("! T220 L8 O4 C4F.C16FA O5 C4 R8 C16D16 C O4 A# A G A4");
    return 0;
}

uint32_t getGroundSensor(uint32_t index){
    if (index < 6){
        reflectArray.read(groundSensors);
        return groundSensors[index];
    }
    return -1;
}

uint32_t getGroundSensorSum(uint32_t unused){
    uint32_t res = 0;
    reflectArray.read(groundSensors);
    for (int i=0; i<6; i++)
        res += groundSensors[i];
    return res;
}

uint32_t changeLeftAdjust(uint32_t ratio){
    uint32_t res = 0;
    leftAdjust = ((float) ratio)/1000.0;
    return res;
}

/* Robot interface */
#define N_Commands sizeof(Commands)/sizeof(LOGO_cmd)
LOGO_cmd Commands[] = {
    {'f', forward},
    {'b', backward},
    {'l', turnLeft},
    {'r', turnRight},
    {'s', getGroundSensor},
    {'a', getGroundSensorSum},
    {'p', playMusic},
    {'c', changeLeftAdjust}
};

/* Read command from console into currentCommand */
void readCommand(){
    waitConsole();
    currentCommand.name = Console.read();
    currentCommand.param = 0;
    for (int i=0; i<4; i++){
        waitConsole();
        if (i > 0)
            currentCommand.param <<= 8;
        currentCommand.param += Console.read();
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
        if (Commands[i].name == currentCommand.name){
            uint32_t res = Commands[i].procedure(currentCommand.param);
            Console.println(res);
            return;
        }
    }
}
