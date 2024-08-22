void setup() {
  // Initialize serial communication at 9600 bits per second:
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    char recv_buffer[5] = {0}; // Initialize serial buffer
    int recv_size = Serial.readBytesUntil('\n', recv_buffer, 4);

    if (recv_size == 4) {
      char cmd[4] = {0};  // Add null-terminator and initialize
      memcpy(cmd, recv_buffer, 3);
      byte value = recv_buffer[3]; // The fourth byte is the command value (0 or 1)

      if (strncmp(cmd, "GLI", 3) == 0) {
        int sensorValue = analogRead(A0);  // Read the light sensor value from A0
        byte scaledValue = map(sensorValue, 0, 1023, 0, 255);  // Scale to 0-255
        Serial.print("GLI");
        Serial.println(scaledValue);  // Send the scaled value as a byte
      }
    }
  }
}
