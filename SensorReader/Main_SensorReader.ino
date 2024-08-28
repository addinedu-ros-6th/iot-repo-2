#include <DFRobot_DHT11.h>
DFRobot_DHT11 DHT;
#define DHT11_PIN A2

#include <SPI.h>
#include <MFRC522.h>


//RFID
const int RST_PIN = 9;
const int SS_PIN = 10;
MFRC522 rc522(SS_PIN, RST_PIN);

const int UID_INDEX = 60;
int index = 60;
MFRC522::StatusCode status;
MFRC522::MIFARE_Key key;

//Door Detect Sensor
int doorSensor = 3;    // Door 센서의 신호핀 연결
int cardSensor = 2;    // Card 센서의 신호핀 연결
int lightSensor = A1;
int doorSensorValue = 0; 
int cardSensorValue = 0; 
int lightSensorValue = 0;
int scaledValue = 0;     


void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600); 

  for (int i = 0; i < 6; i++)
  {
    key.keyByte[i] = 0xFF;
  }
}

MFRC522::StatusCode checkAuth(int index)
{
  MFRC522::StatusCode status = rc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, index, &key, &(rc522.uid));
  return status;
}

MFRC522::StatusCode readData(int index, byte* data)
{
  MFRC522::StatusCode status = checkAuth(index);
  if (status != MFRC522::STATUS_OK)
  {
    return status;
  }

  byte buffer[18];
  byte length = 18;
  status = rc522.MIFARE_Read(index, buffer, &length);
  if (status == MFRC522::STATUS_OK)
  {
    memcpy(data, buffer, 12);
  }
  return status;
}

MFRC522::StatusCode writeData(int index, byte* data, int length)
{
  MFRC522::StatusCode status = checkAuth(index);
  if (status != MFRC522::STATUS_OK)
  {
    return status;
  }
  byte buffer[16];
  memset(buffer, 0x00, sizeof(buffer));
  memcpy(buffer, data, length);

  status = rc522.MIFARE_Write(index, buffer, 16);
  return status; 

  //Door Detect Sensor
  pinMode(doorSensor, INPUT);  
  pinMode(cardSensor, INPUT);  
  pinMode(lightSensor, INPUT); 
  pinMode(4,OUTPUT);
 }

void loop() {

  SPI.begin();
  rc522.PCD_Init();

  int recv_size = 0;
  char recv_buffer[16];

  if(Serial.available() > 0)
  {
    recv_size = Serial.readBytesUntil('\n', recv_buffer, 16);
  }

  bool newCard = rc522.PICC_IsNewCardPresent();
  bool readCard = rc522.PICC_ReadCardSerial();

  if (recv_size > 0)
  {
    char cmd[3];
    memset(cmd, 0x00, sizeof(cmd));
    memcpy(cmd, recv_buffer, 3);

    char uid[8];
    memset(uid, 0x00, sizeof(uid));
    memcpy(uid, recv_buffer+3, 8);

    char send_buffer[16];
    memset(send_buffer, 0x00, sizeof(send_buffer));
    memcpy(send_buffer, cmd, 3);
     
    MFRC522::StatusCode status = MFRC522::STATUS_ERROR;
    if (newCard == true && readCard == true)
    {
      if(strncmp(cmd, "GST", 3) == 0)
      {     
        digitalWrite(4, HIGH);
        byte read_uid[16];
        status = readData(UID_INDEX, read_uid);  // UID 읽기
        send_buffer[3] = (status == MFRC522::STATUS_OK) ? 0x00 : 0xFF;
        if (status == MFRC522::STATUS_OK)
        {
          memcpy(send_buffer + 4, read_uid, 8);  // UID를 send_buffer에 복사
        }
         Serial.write(send_buffer, 12);  
         Serial.println();       
      }
      else if(strncmp(cmd, "SID", 3) == 0)
      {
        status = writeData(UID_INDEX, (byte*)uid, 8);  // 수정된 writeData 호출
        send_buffer[3] = (status == MFRC522::STATUS_OK) ? 0x00 : 0xFF;
        Serial.write(send_buffer, 12);
        Serial.println();
      }
    }
    else
    {
      if(strncmp(cmd, "GST", 3) == 0)
      {     
        send_buffer[3] = 1;
        Serial.write(send_buffer, 12);
        Serial.println();
      }
    }
 
    //Door Detect Sensor
    if(strncmp(cmd, "GDS", 3) == 0)
    {
      doorSensorValue = digitalRead(doorSensor);  // Door value 읽기
      send_buffer[3] = doorSensorValue;
      Serial.write(send_buffer, 12);
      Serial.println();
    }
    if(strncmp(cmd, "GCS", 3) == 0)
    {
      cardSensorValue = digitalRead(cardSensor);  // Card value 읽기
      send_buffer[3] = cardSensorValue;
      Serial.write(send_buffer, 12);
      Serial.println();
    }
    if(strncmp(cmd, "GLI", 3) == 0)
    {
      lightSensorValue = analogRead(lightSensor);  // Light value 읽기
      scaledValue = map(lightSensorValue, 0, 1023, 0, 255);
      send_buffer[3] = scaledValue;
      Serial.write(send_buffer, 12);
      Serial.println();
    }
    if(strncmp(cmd, "GTH", 3) == 0)
    {
      DHT.read(DHT11_PIN);
      send_buffer[3] = DHT.temperature;
      send_buffer[4] =  DHT.humidity;
      Serial.write(send_buffer, 12);
      Serial.println();
    }
  }
}
