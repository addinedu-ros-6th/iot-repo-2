#define BLUE 8
#define GREEN 9
#define RED 10

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:

  if (Serial.available() > 0) 
  {
    char recv_buffer[5] = {0};
    int recv_size = Serial.readBytesUntil('\n', recv_buffer, 4);

    if (recv_size ==4)
    {
      char cmd[4] = {0};
      strncpy(cmd, recv_buffer, 3);
      byte value = recv_buffer[3];

      if (strncmp(cmd, "SAC", 3) == 0 && (value == 0 || value == 1))
      {
        if (value == 0)
        {
          Serial.println("AC OFF");
          analogWrite(RED,0);
          analogWrite(GREEN,0);
          analogWrite(BLUE,0);
        }
        if (value == 1)
        {
          Serial.println("AC POWER");
          analogWrite(RED,255);
          analogWrite(GREEN,255);
          analogWrite(BLUE,255);
        }
        if (value == 2)
        {
          Serial.println("AC HIGH");
          analogWrite(RED,0);
          analogWrite(GREEN,0);
          analogWrite(BLUE,255);
        }
        if (value ==3)
        {
          Serial.println("AC Middle");
          analogWrite(RED,0);
          analogWrite(GREEN,255);
          analogWrite(BLUE,0);
        }
        if (value ==4)
        Serial.println("AC LOW");
          analogWrite(RED,255);
          analogWrite(GREEN,0);
          analogWrite(BLUE,0);
      } 
    }
  } 
}
