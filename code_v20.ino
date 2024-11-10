#include <Adafruit_NeoPixel.h> 
#include <U8glib.h>
#include <RotaryEncoder.h>
#include <OneButton.h>
#include <Volume.h>

#define encoderStep 1
#define encoderMin 0
#define encoderMax 24

// Wyświetlacz OLED
U8GLIB_SSD1306_128X64 display = U8GLIB_SSD1306_128X64(U8G_I2C_OPT_NONE);

// Matryca LED
Adafruit_NeoPixel matrix = Adafruit_NeoPixel(64, 6, NEO_GRB + NEO_KHZ800);

// Enkoder
RotaryEncoder encoder = RotaryEncoder(A2, A3);

// Przycisk do włączenia
OneButton startButton = OneButton(A0, false);

// Przycisk do zmiany częstotliwości
OneButton freqButton = OneButton(A1, false);

// Generowanie dźwięku
Volume testTone = Volume();

int result1[2][7]; 
int result2[2][7]; 
float averageResult[2][7]; 

int hz = 0;
int ear = 0;
int vol = 1;
int volNew;
int test;

float dbValue;
float db;

float dif;

char displayText[2][15] = {"Left Ear Test", "Right Ear Test"};
char dbText[25][8] = {"0 db", "5 db", "10 db", "15 db", "20 db", "25 db", "30 db", "35 db", "40 db", "45 db", "50 db", "55 db", "60 db", "65 db", "70 db", "75 db", "80 db", "85 db", "90 db", "95 db", "100 db", "105 db", "110 db", "115 db", "120 db"};
char freqText[7][8] = {"125 Hz", "250 Hz", "500 Hz", "1000 Hz", "2000 Hz", "4000 Hz", "8000 Hz"};

float defaultCalibration[7] = {33.5, 34.5, 34.5, 35.0, 33.0, 39.5, 43.5};
float ear3aCalibration[7] = {26, 14, 5.5, 0.0, 3.0, 5.5, 0.0};
float tdh39Calibration[7] = {45, 25.5, 11.5, 7.0, 9.0, 9.5, 13.0};

int freq[7] = {125, 250, 500, 1000, 2000, 4000, 8000};

bool startFlag = false;
bool switchFlag = false;
bool repeatFlag = false;
bool resultFlag = false;

void write(const char* text, int posx, int posy) {
  display.setColorIndex(1); 
  display.setFont(u8g_font_gdr11);
  display.drawStr(posx, posy, text);
}

void clearDisplay() {
  display.firstPage();
  do {
  } 
  while(display.nextPage());
}

void sendResultsToSerial() {
    Serial.println("\nAudiogram Results:");
    for (int i = 0; i < 2; i++) {
        Serial.print(i == 0 ? "Left Ear: " : "Right Ear: ");
        for (int j = 0; j < 7; j++) {
            float dbAverage = averageResult[i][j]; // Zakładając, że krok 5 dB odpowiada indeksom
            Serial.print(freq[j]);
            Serial.print(" Hz, ");
            Serial.print(dbAverage);
            Serial.print(" db");
            if (j < 6) Serial.print(" | ");
        }
        Serial.println();
    }
    Serial.println();
    delay(5000);
}

void calculateAverageResults() {
    for (int i = 0; i < 2; i++) { // dla każdego ucha
        for (int j = 0; j < 7; j++) { // dla każdej częstotliwości
            averageResult[i][j] = (result1[i][j] + result2[i][j]) / 2.0;
        }
    }
}

void initTest() {
  startFlag = true;
  Serial.println("Audiometry test initialized.");
}

void displayTestParams() {
  display.firstPage();
    do {
      write(displayText[ear], 15, 12);
      write("Freq: ", 0, 40);
      write("Vol: ", 0, 58);   
      write(freqText[hz], 60, 40);       
      write(dbText[volNew], 60, 58);
    } 
    while (display.nextPage());
}

void displayStartMessage() {
  startButton.tick();
  display.firstPage();
  do {
    write("Start", 42, 30);
    write("the test", 32, 48);
  } 
  while (display.nextPage());
}

void displaySwitchMessage() {
  display.firstPage();
  do {
    write("Switch", 40, 30);
    write("headphones", 20, 48);
  } 
  while (display.nextPage());
  delay(5000);
  switchFlag = true; 
}

void displayRepeatMessage() {
    display.firstPage();
    do {
    write("Repeat", 40, 30);
    write("the test", 38, 48);
    } 
    while (display.nextPage());
    delay(50000);
    repeatFlag = true;
}

void displayResultMessage() {
  hz = 0;
  ear = 2;
  delay(1000);
  display.firstPage();
  do {
    write("Audiogram", 22, 30);
    write("Executed", 30, 48);
  } 
  while (display.nextPage());
  delay(5000);
  resultFlag = true; 
}

void switchEar() {
  delay(5000);
  hz = 0;
  ear = 1;
}

void switchTest() {
  delay(5000);
  hz = -1;
  ear = 0;
  test = 2;
}

void nextFreqency() {
  if (test == 1) {
    result1[ear][hz] = dbValue;
    /*Serial.print("\nTest 1: ");
    Serial.print("Freq: ");
    Serial.print(freq[hz]);
    Serial.print(", Tsh: ");
    Serial.print(result1[ear][hz]);*/

    hz++;
    vol = 1;
    volNew = encoder.getPosition();
    encoder.setPosition(0);

    if (hz > 6 && ear == 0 && switchFlag == false) { 
      displaySwitchMessage();
      if (switchFlag) {
        switchEar();
        switchFlag = false;
      }
    } 
    else if (hz > 6 && ear == 1 && repeatFlag == false) {
      displayRepeatMessage();
      if (repeatFlag) {
        switchTest();
      }
    }
  }

  if (test == 2) {
    result2[ear][hz] = dbValue;
    /*Serial.print("\nTest 2: ");
    Serial.print("Freq: ");
    Serial.print(freq[hz]);
    Serial.print(", Tsh: ");
    Serial.print(result2[ear][hz]);*/

    hz++;
    vol = 1;
    volNew = encoder.getPosition();
    encoder.setPosition(0);

    if (hz > 6 && ear == 0 && switchFlag == false) { 
      displaySwitchMessage();
      if (switchFlag) {
        switchEar();
        switchFlag = false;
      }
    } 
    else if (hz > 6 && ear == 1 && resultFlag == false) {
      displayResultMessage();
      calculateAverageResults();
      if (resultFlag) {
        sendResultsToSerial();
      }
    }
  }
}

void calibration(float dbValue, float dif, float calibrationValues[]) {
  if (dbValue < calibrationValues[hz]) {
  db = 0;
  }
  if (abs(dbValue - calibrationValues[hz]) <= dif) {
    db = dbValue;
  }
  if (dbValue > calibrationValues[hz]) {
    db = dbValue;
  }
  testTone.tone(freq[hz], db);
}

void setup() {
  matrix.begin();
  matrix.show();
  
  display.begin(); 
  encoder.setPosition(encoderMin);
  
  startButton.attachLongPressStop(initTest);
  freqButton.attachLongPressStop(nextFreqency);
  
  testTone.begin(); 
  testTone.setMasterVolume(0.1);
  
  Serial.begin(9600); 
  Serial.println("Pure Tone Audiometry");
}

void loop() {  
  startButton.tick();
  freqButton.tick();
  encoder.tick();

  if (startFlag == false) {
    displayStartMessage();
    test = 1;
  }

  if (startFlag) {

    volNew = encoder.getPosition();
    if (volNew != vol) {
      if (volNew < encoderMin) {
        encoder.setPosition(encoderMin);
        volNew = encoderMin;
      } 
      else if (volNew > encoderMax) {
        encoder.setPosition(encoderMax);
        volNew = encoderMax;
      }

      if (ear < 2) {
        displayTestParams();
      }

      vol = volNew;
      dbValue = vol * 5;
      calibration(dbValue, 4.5, defaultCalibration);
    }
  } 
}
