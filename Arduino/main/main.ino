#include <HX711.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define LOADCELL_SCK 3 // ATmega Pin 5
#define LOADCELL_DOUT 2 // ATmega Pin 4

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 32 // OLED display height, in pixels

// Declaration for loadcell amplifier
HX711 scale;  

// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

int opMode = 1;
int calibrationFactor = 73;
int preWeight = 0;
float totalPrice = 0.0;

String productNames[] = {
  "Apple",
  "Goodday biscuit",
  "Banana"
};

float productPrices[] = {
   80.0,
   20.0,
   40.0 
};

void setup() {
  // Setup input pins
  pinMode(4, INPUT_PULLUP);  // input mode
  pinMode(5, INPUT_PULLUP);  // confirm load
  pinMode(6, INPUT_PULLUP);  // scale tare
  pinMode(7, INPUT_PULLUP);
  
  setupLoadCell();
  setupDisplay();
  
  // Begin Serial Communication with baud rate of 9600
  Serial.begin(9600);
  Serial.print('R');
  delay(200);
  while(!Serial.available());
  Serial.read();
}

void loop() {
  if(opMode == 0) {
    display.clearDisplay();
    displayText("Total", 2, 0, 0);
    displayText("Rs. " + String(totalPrice), 2, 0, 18);
    while(getWeight() - preWeight < 5) { // waits for weight change.
      if(digitalRead(4) == LOW) {
        opMode = 1;
        delay(200);
        return;
      }
    }
    display.clearDisplay();
    displayText("Identifying Product", 2, 0, 0);
    delay(2000);
  } else {
    while(digitalRead(5) == HIGH) {
      if(digitalRead(4) == LOW) {
        opMode = 0;
        delay(200);
        return;
      }
      if(digitalRead(6) == LOW) {
        scale.tare();
      }
      preWeight = (int) getWeight();
      display.clearDisplay();
      displayText(preWeight > 1000 ? String(double(preWeight) / 1000.0) + "Kg": String(preWeight) + "g", 4, 0, 0);
    }
  }
  preWeight = (int) getWeight();
  Serial.print('W'); // Sents a 'W' character representing weight change.
  delay(100);
  Serial.print(preWeight);
  Serial.print('g');
  while(!Serial.available()); // wait for the detected product index from pi
  
  int productIdx = Serial.parseInt();  
  float productPrice = preWeight * productPrices[productIdx] / 1000;
  String productWeight = preWeight > 1000 ? String(double(preWeight) / 1000.0) + "Kg": String(preWeight) + "g";
  totalPrice += productPrice;
  
  display.clearDisplay();
  displayText(productNames[productIdx].substring(0, 10), 2, 0, 0);
  displayText("Weight : " + productWeight, 1, 0, 20);
  delay(1000);
  
  display.clearDisplay();
  displayText("Price" , 1, 0, 0);
  displayText("1.00Kg : " + String(productPrices[productIdx]), 1, 0, 12); 
  displayText(productWeight + " : " + String(productPrice), 1, 0, 24);
  delay(2000);
  
  preWeight = 0;
}

void setupLoadCell() {
  scale.begin(LOADCELL_DOUT, LOADCELL_SCK);
  scale.set_scale(calibrationFactor);
  scale.tare();
}

float getWeight() {
  while(!scale.is_ready());
  return scale.get_units(3);
}

void setupDisplay() {
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { // Address 0x3D for 128x64
    Serial.println("Error");
    while(1);
  }
  display.clearDisplay();
  display.setTextColor(WHITE);
  displayText(" Shopping\n   Cart", 2, 0, 2);
}

void displayText(String text, float tSize, int x, int y) {
  display.setTextSize(tSize);
  display.setCursor(x, y);
  display.print(text);
  display.display();
}
