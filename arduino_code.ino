#include <Wire.h>
#include <LiquidCrystal_I2C.h>
LiquidCrystal_I2C lcd(0x27, 16, 2);

float smoothValue = 0;
bool firstRun = true;

void setup() {
  Serial.begin(9600);
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0,0);
  lcd.print("RF SHIELD AI");
  lcd.setCursor(0,1);
  lcd.print("System Ready");
  delay(2000);
  lcd.clear();
}

void loop() {
  long sum = 0;
  for(int i=0; i<15; i++){
    sum += analogRead(A0);
    delay(20);
  }
  int currentReading = sum / 15;

  if(firstRun){
    smoothValue = currentReading;
    firstRun = false;
  } else {
    smoothValue = (smoothValue * 0.75) + (currentReading * 0.25);
  }

  int drift = random(-3, 4);
  int displayValue = (int)smoothValue + drift;
  if(displayValue < 0) displayValue = 0;

  lcd.setCursor(0,0);
  lcd.print("RF: ");
  lcd.print(displayValue);
  lcd.print("   ");

  lcd.setCursor(0,1);
  if(displayValue <= 60){
    lcd.print("Sky Safe      ");
  }
  else if(displayValue <= 120){
    lcd.print("Suspicious   ");
  }
  else if(displayValue < 150){
    lcd.print("Warning: Drone");
  }
  else {
    lcd.print("DRONE DETECTED!");
  }

  Serial.println(displayValue);
  delay(1000);
}
