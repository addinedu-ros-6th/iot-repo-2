#include <DHT.h>

#define DHTPIN A0     // DHT11 센서가 연결된 디지털 핀
#define DHTTYPE DHT11 // DHT 11 센서 사용

DHT dht(DHTPIN, DHTTYPE);

float simulatedTemperature;

void setup() {
  Serial.begin(9600);
  dht.begin();

  // 초기 온도 설정
  simulatedTemperature = dht.readTemperature();
}

void loop() {
  unsigned long currentMillis = millis();
  int recv_size = 0;
  char recv_buffer[5];
  if (Serial.available() > 0) 
  {
    char recv_buffer[5] = {0};
    int recv_size = Serial.readBytesUntil('\n', recv_buffer, 4);
  
    if (recv_size == 3)
    {
      if (strncmp(recv_buffer, "GTH", 3) == 0)
      {
        float humidity = dht.readHumidity();
        // 실제 온도 대신 시뮬레이션된 온도 사용
        
        Serial.print("GTH");
        Serial.print(humidity);
        Serial.print(",");
        Serial.println(simulatedTemperature);
      }
    }
  }
}