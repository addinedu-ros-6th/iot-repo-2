#include <LiquidCrystal_I2C.h>
#include <Wire.h>
#include <SPI.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);  // set the LCD address to 0x27 for a 16 chars and 2 line display

void setup() {
  Serial.begin(9600);
  lcd.init();                      // initialize the lcd 
  lcd.begin(16, 2);  // initialize the lcd for 16 chars 2 lines, turn on backlight
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("LCD Loading");
}

void loop() {
  int recv_size = 0;
  char recv_buffer[35];

  if (Serial.available() > 0) {
    memset(recv_buffer, 0, sizeof(recv_buffer));                // recv_buffer data reset
    recv_size = Serial.readBytesUntil('\n', recv_buffer, 35);
  }

  if (recv_size > 0) {
    char cmd[3]; // 3 characters + null terminator
    memset(cmd, 0x00, sizeof(cmd));
    memcpy(cmd, recv_buffer, 3);



    if (strncmp(cmd, "SLC", 3) == 0) 
    {
      byte Ledvalue = recv_buffer[3]; // Directly assign the byte value
      lcd.clear();

      if (Ledvalue == 0x00) { // Compare with byte value 0x00
        lcd.setCursor(0, 0); // First line, 16 characters are available
        lcd.print("Welcome"); // Filled with Space
        // Serial.println(Ledvalue, HEX); // Print value in hexadecimal
      } 
      else if (Ledvalue == 0x01) { // Compare with byte value 0x01
        lcd.setCursor(0, 0); // First line, 16 characters are available
        lcd.print("Opened Door"); // Filled with Space
        // Serial.println(Ledvalue, HEX); // Print value in hexadecimal
      }
      else if (Ledvalue == 0x02) { // Compare with byte value 0x02
        lcd.setCursor(0, 0); // First line, 16 characters are available
        lcd.print("Closed Door"); // Filled with Space
        // Serial.println(Ledvalue, HEX); // Print value in hexadecimal
      }
      else if (Ledvalue == 0x03) { // Compare with byte value 0x03
        lcd.setCursor(0, 0); // First line, 16 characters are available
        lcd.print("ArduMension"); // Filled with Space
        // Serial.println(Ledvalue, HEX); // Print value in hexadecimal
      }
    }
  }
}