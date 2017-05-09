
#include "Arduino.h"
#include <Adafruit_NeoPixel.h>
#include <NeoPixelPainter.h>
#ifdef __AVR__
  #include <avr/power.h>
#endif
#include <Wire.h>
#define SLAVE_ADDRESS 0x04
int number = 0;
int state = 0;
#define NEOPIXEL_PIN 10
#define NUM_LEDS 60

#define MESSAGE_START 0
#define MESSAGE_LED 1
#define MESSAGE_R 2
#define MESSAGE_G 3
#define MESSAGE_B 4

Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUM_LEDS, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);
void setup() {
  pixels.begin(); // This initializes the NeoPixel library.
  Serial.begin( 19200 );
  Wire.begin(SLAVE_ADDRESS);
  Wire.onReceive(receiveData);
}
int id = 0;
int R = 0;
int G = 0;
int B = 0;
// callback for received data
void receiveData(int byteCount){

  while(Wire.available()) {
    number = Wire.read();
      Serial.print(number);
    if(number == 0xFF){
      if(state != MESSAGE_B){
        Serial.print("Message missed");
      }
      //Beginning of message
      state = MESSAGE_START;
      continue;
    }
    if(state == MESSAGE_START){
      id = (int)number;
      state = MESSAGE_LED;
      continue;
    }
    if(state == MESSAGE_LED){
      R =(int) number;
      state = MESSAGE_R;
      continue;
    }
    if(state == MESSAGE_R){
      G = (int)number;
      state = MESSAGE_G;
      continue;
    }
    if(state == MESSAGE_G){
      B = (int)number;
      state = MESSAGE_B;
      pixels.setPixelColor(id, pixels.Color(R,G,B)); // Moderately bright green color.
      pixels.show(); // This sends the updated pixel color to the hardware.
      continue;
    }  
  }
}
void loop() {
}

