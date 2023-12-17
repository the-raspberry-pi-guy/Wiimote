#include <WiFi.h>
#include <WiFiUdp.h>
#include "Freenove_4WD_Car_For_ESP32.h"
#include "Freenove_4WD_Car_WiFi.h"
#include <WiFiClient.h>
#include <WiFiAP.h>
#include <Arduino.h>

#define OBSTACLE_DISTANCE      55
#define OBSTACLE_DISTANCE_LOW  35
int distance[4];     //Storage of ultrasonic data

const int UDP_TX_PACKET_MAX_SIZE = 1024;
String CmdArray[8];
int paramters[8];
bool videoFlag = 0;
bool moving = false;
bool scanEnabled = true;

unsigned int localPort = 4000;  // local port to listen on

// buffers for receiving and sending data
char packetBuffer[UDP_TX_PACKET_MAX_SIZE + 1];  // buffer to hold incoming packet,
char ReplyBuffer[] = "acknowledged\r\n";        // a string to send back

WiFiUDP Udp;

void WiFi_Init() {
  ssid_Router     =   "Stoltzfus-2G";    //Modify according to your router name
  password_Router =   "Farhills";    //Modify according to your router password
  ssid_AP         =   "Sunshine";    //ESP32 turns on an AP and calls it Sunshine
  password_AP     =   "Sunshine";    //Set your AP password for ESP32 to Sunshine
  frame_size      =    FRAMESIZE_CIF;//400*296
}

WiFiServer server_Cmd(4000);



void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Buzzer_Setup();           //Buzzer initialization
  
  WiFi_Init();              //WiFi paramters initialization
  WiFi_Setup(0);            //Start AP Mode
  server_Cmd.begin(4000);   //Start the command server
  
  Ultrasonic_Setup();
  PCA9685_Setup();          //PCA9685 initialization
  Light_Setup();            //Light initialization
  Track_Setup();            //Track initialization

  disableCore0WDT();        //Turn off the watchdog function in kernel 0
  xTaskCreateUniversal(loopTask_WTD, "loopTask_WTD", 8192, NULL, 0, NULL, 0);
  Servo_2_Angle(105);
  Udp.begin(localPort);
}

void Get_Command(String inputStringTemp)
{
  int string_length = inputStringTemp.length();
  for (int i = 0; i < 8; i++) {//Parse the command received by WiFi
    int index = inputStringTemp.indexOf(INTERVAL_CHAR);
    if (index < 0) {
      if (string_length > 0) {
        CmdArray[i] = inputStringTemp;         //Get command
        paramters[i] = inputStringTemp.toInt();//Get parameters
      }
      break;
    }
    else {
      string_length -= index;                                //Count the remaining words
      CmdArray[i] = inputStringTemp.substring(0, index);     //Get command
      paramters[i] = CmdArray[i].toInt();                    //Get parameters
      inputStringTemp = inputStringTemp.substring(index + 1);//Update string
    }
  }
}
void loop() {
  // if there's data available, read a packet
  int packetSize = Udp.parsePacket();
  if (packetSize) {
    // read the packet into packetBufffer
    int n = Udp.read(packetBuffer, UDP_TX_PACKET_MAX_SIZE);
    packetBuffer[n] = 0;
    Serial.println(packetBuffer);//Print out the command received by WiFi
        String inputStringTemp = packetBuffer;
        Get_Command(inputStringTemp);
        if (CmdArray[0] == CMD_BUZZER) //Buzzer control command
        {
          Buzzer_Variable(paramters[1], paramters[2]);}
        if (CmdArray[0] == CMD_MOTOR) {//Network control car movement command
          Car_SetMode(0);
          if (paramters[1] == 0 && paramters[3] == 0){
            Motor_Move(0, 0, 0, 0);//Stop the car
            moving = false;}
          else {//If the parameters are not equal to 0
            Motor_Move(paramters[1], paramters[1], paramters[3], paramters[3]);
            if (paramters[1] >= 150 && paramters[3] >= 150)
              moving = true;
            }
        }
        if (CmdArray[0] == CMD_SERVO) {//Network control servo motor movement command
          if (paramters[1] == 0)
            Servo_1_Angle(paramters[2]);
          else if (paramters[1] == 1)
            Servo_2_Angle(paramters[2]);
        }
        if (CmdArray[0] == CMD_USONIC) {
            if (scanEnabled) {
              scanEnabled = false;
              char replyBuff = 'd';
              Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
              Udp.write(replyBuff);
              Udp.endPacket();
            }
            else {
              scanEnabled = true;  
              char replyBuff = 'e';
              Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
              Udp.write(replyBuff);
              Udp.endPacket();
            }
        }
        if (CmdArray[0] == CMD_CAR_MODE) { //Car command Mode
          Car_SetMode(paramters[1]);
        }
        //Clears the command array and parameter array
        memset(CmdArray, 0, sizeof(CmdArray));
        memset(paramters, 0, sizeof(paramters));
      }
      else {
        if (moving && scanEnabled) {
          if (Get_Sonar() < OBSTACLE_DISTANCE_LOW) {
            Motor_Move(0, 0, 0, 0);
            moving = false;
            }
          }
        }
      Car_Select(carFlag);//ESP32 Car mode selection function
    }
