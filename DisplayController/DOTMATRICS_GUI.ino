//https://copynull.tistory.com/394 <Pin information>

#include <FrequencyTimer2.h>
#include <Wire.h>
#include <SPI.h>

int rows[] = {A0, 12, A2, 13, 5, A3, 7, 2};
int cols[] = {9, 8, 4, A1, 3, 10 ,11, 6};
byte HeaterLevelLast[8][8];


byte HeaterLevel0[8][8] = 
{
  {0, 0, 0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0, 0, 0},
};

byte HeaterLevel1[8][8] = 
{
  {0, 0, 0, 0, 0, 0, 0, 0},
  {0, 0, 0, 1, 1, 0, 0, 0},
  {0, 0, 1, 1, 1, 1, 0, 0},
  {0, 1, 1, 1, 1, 1, 1, 0},
  {0, 1, 1, 1, 1, 1, 1, 0},
  {0, 0, 1, 1, 1, 1, 0, 0},
  {0, 0, 0, 1, 1, 0, 0, 0},
  {0, 0, 0, 0, 0, 0, 0, 0},
};

byte HeaterLevel2[8][8] = 
{
  {0, 0, 0, 1, 1, 0, 0, 0},
  {0, 0, 1, 1, 1, 1, 0, 0},
  {0, 1, 1, 1, 1, 1, 1, 0},
  {1, 1, 1, 1, 1, 1, 1, 1},
  {1, 1, 1, 1, 1, 1, 1, 1},
  {0, 1, 1, 1, 1, 1, 1, 0},
  {0, 0, 1, 1, 1, 1, 0, 0},
  {0, 0, 0, 1, 1, 0, 0, 0},
};

byte HeaterLevel3[8][8] = 
{
  {0, 0, 1, 1, 1, 1, 0, 0},
  {0, 1, 1, 1, 1, 1, 1, 0},
  {1, 1, 1, 1, 1, 1, 1, 1},
  {1, 1, 1, 1, 1, 1, 1, 1},
  {1, 1, 1, 1, 1, 1, 1, 1},
  {1, 1, 1, 1, 1, 1, 1, 1},
  {0, 1, 1, 1, 1, 1, 1, 0},
  {0, 0, 1, 1, 1, 1, 0, 0},
};

byte HeaterLevel4[8][8] = 
{
  {0, 1, 1, 1, 1, 1, 1, 0},
  {1, 1, 1, 1, 1, 1, 1, 1},
  {1, 1, 1, 1, 1, 1, 1, 1},
  {1, 1, 1, 1, 1, 1, 1, 1},
  {1, 1, 1, 1, 1, 1, 1, 1},
  {1, 1, 1, 1, 1, 1, 1, 1},
  {1, 1, 1, 1, 1, 1, 1, 1},
  {0, 1, 1, 1, 1, 1, 1, 0},
};

// LED initialize
void clear()
{
  for(int i = 0; i< 8; i++)
  {
    digitalWrite(rows[i], LOW);
    digitalWrite(cols[i],HIGH);
  }
}

void setup() 
{
  Serial.begin(9600);
  for(int i = 0; i <8; i++)
  {
    pinMode(rows[i], OUTPUT);
    pinMode(cols[i], OUTPUT);
  }
}


void loop()
{
  int recv_size = 0;
  char recv_buffer[35];

  if (Serial.available() > 0) 
  {
    memset(recv_buffer, 0, sizeof(recv_buffer));                // recv_buffer data reset
    recv_size = Serial.readBytesUntil('\n', recv_buffer, 35);
  }

  if (recv_size > 0) 
  {
    char cmd[3]; // 3 characters + null terminator
    memset(cmd, 0x00, sizeof(cmd));
    memcpy(cmd, recv_buffer, 3);

    if (strncmp(cmd, "SHT", 3) == 0) 
    {
      byte HeaterValue = recv_buffer[3]; // Directly assign the byte Heater_value

      if (HeaterValue == 0x00) // Compare with byte Heater_value 0x00 
      {
        memcpy(HeaterLevelLast, HeaterLevel0, sizeof(HeaterLevelLast));
      }
      else if (HeaterValue == 0x01) // Compare with byte Heater_value 0x00 
      {
        memcpy(HeaterLevelLast, HeaterLevel1, sizeof(HeaterLevelLast));
      }
      else if (HeaterValue == 0x02) // Compare with byte Heater_value 0x00 
      {
        memcpy(HeaterLevelLast, HeaterLevel2, sizeof(HeaterLevelLast));
      }
      else if (HeaterValue == 0x03) // Compare with byte Heater_value 0x00 
      {
        memcpy(HeaterLevelLast, HeaterLevel3, sizeof(HeaterLevelLast));
      }
      else if (HeaterValue == 0x04) // Compare with byte Heater_value 0x00 
      {
        memcpy(HeaterLevelLast, HeaterLevel4, sizeof(HeaterLevelLast));
      }

    
    }
  }

  for(int x = 0; x < 8; x++)
  {
    clear();
    digitalWrite(rows[x], HIGH);
    for(int y = 0; y < 8; y++)
    {
      if(HeaterLevelLast[x][y] == 1)
      {
        digitalWrite(cols[y], LOW);
      }
    }
    delay(2);
  }
}


