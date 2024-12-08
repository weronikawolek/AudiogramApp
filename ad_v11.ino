// Słuchawki JBL Tune 110
// Impedancja (Z) - 16 Ohm
// Czułość (S) - 96 db SPL/mW 

#include <Adafruit_NeoPixel.h>
#include <U8glib.h>
#include <RotaryEncoder.h>
#include <OneButton.h>
#include <AD9850.h>
#include <X9C103S.h>

#define encoderMin 0
#define encoderMax 24
#define maxPot 60

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

// Potencjometr cyfrowy
X9C103S pot = X9C103S(11, 10, 12); 

int result1[2][7]; 
int result2[2][7]; 
float averageResult[2][7]; 

int hz = 0;
int ear = 0;
int vol = 1;
int volNew;
int test;
int calibrationMode;  // Zmienna przechowująca tryb kalibracji

const float sensitivity = 96.0; 
const float impedance = 16.0;
const float maxVoltage = 4.5;

float voltage;
float res;
float spl;
float db;
float dif;    

char displayText[2][15] = {"Left Ear Test", "Right Ear Test"};
char dbText[25][8] = {"0 db", "5 db", "10 db", "15 db", "20 db", "25 db", "30 db", "35 db", "40 db", "45 db", "50 db", "55 db", "60 db", "65 db", "70 db", "75 db", "80 db", "85 db", "90 db", "95 db", "100 db", "105 db", "110 db", "115 db", "120 db"};
char freqText[7][8] = {"125 Hz", "250 Hz", "500 Hz", "1000 Hz", "2000 Hz", "4000 Hz", "8000 Hz"};

float defaultCalibration[7] = {33.5, 34.5, 34.5, 35.0, 33.0, 39.5, 43.5};
float ear3aCalibration[7] = {26, 14, 5.5, 0.0, 3.0, 5.5, 0.0};
float tdh39Calibration[7] = {45, 25.5, 11.5, 7.0, 9.0, 9.5, 13.0};
float bioCalibration[7] = {10, 10, 10, 10, 10, 10, 10};

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

void calculateAverageResults() {
    for (int i = 0; i < 2; i++) { 
        for (int j = 0; j < 7; j++) { 
            averageResult[i][j] = (result1[i][j] + result2[i][j]) / 2.0;
        }
    }
}

void sendResultsToSerial() {
    Serial.println("\nAudiogram Results:");
    for (int i = 0; i < 2; i++) {
        Serial.print(i == 0 ? "Left ear: " : "Right ear: ");
        for (int j = 0; j < 7; j++) {
            float dbAverage = averageResult[i][j]; 
            Serial.print(freq[j]);
            Serial.print(" Hz, ");
            Serial.print(dbAverage);
            Serial.print(" db");
            if (j < 6) Serial.print(" | ");
        }
        Serial.println();
    }
    Serial.println();
    delay(1000);
}

void initTest() {
  freqButton.attachLongPressStop(nextFreqency);
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
    write("Initialize", 30, 30);
    write("the test", 34, 48);
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
  delay(1000);
  switchFlag = true; 
}

void displayRepeatMessage() {
    display.firstPage();
    do {
    write("Repeat", 40, 30);
    write("the test", 38, 48);
    } 
    while (display.nextPage());
    delay(1000);
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
  resultFlag = true; 
}

void switchEar() {
  hz = 0;
  ear = 1;
}

void switchTest() {
  hz = -1;
  ear = 0;
  test = 2;
}

void nextFreqency() {
  if (test == 1) {

    result1[ear][hz] = spl;
    Serial.print("\nTest 1: ");
    Serial.print("Freq: ");
    Serial.print(freq[hz]);
    Serial.print(", Tsh: ");
    Serial.print(result1[ear][hz]);

    hz++;
    vol = 1;
    volNew = encoder.getPosition();
    encoder.setPosition(encoderMin);

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
    result2[ear][hz] = spl;

    Serial.print("\nTest 2: ");
    Serial.print("Freq: ");
    Serial.print(freq[hz]);
    Serial.print(", Tsh: ");
    Serial.print(result2[ear][hz]);

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

float calculateResistanceDefault(float spl) {
  voltage = sqrt(96 * pow(10, (spl - 16) / 10.0));
  res = voltage/10.24;
  //float maxVoltaeg = 5;
  //res = impedance * ((maxVoltage / voltage) - 1);
  pot.setResistance(res); 
}

float calculateResistanceEar3a (float spl) {
  voltage = sqrt(102.5 * pow(10, (spl - 10) / 10.0));
  res = voltage/10.24;
  pot.setResistance(res); 
}

float calculateResistanceTdh39 (float spl) {
  voltage = sqrt(108 * pow(10, (spl - 10) / 10.0));
  res = voltage/10.24;
  pot.setResistance(res); 
}

void calibration(float db, float dif, float calibrationValues[], int nr) {
  if (db < calibrationValues[hz]) {
    spl = 0;
    DDS.down();
  }
  if (abs(db - calibrationValues[hz]) <= dif) {
    spl = db;
    DDS.setfreq(freq[hz], 0);
  }
  if (db > calibrationValues[hz]) {
    spl = db;
    DDS.setfreq(freq[hz], 0);
  }

  if (nr == 1) {
    calculateResistanceDefault(spl);
  }
  else if (nr == 2) {
    calculateResistanceEar3a(spl);
  }
  else if (nr == 3) {
    calculateResistanceTdh39(spl);
  }
}


void setup() {
  DDS.begin(6, 7, 8, 9);           
  DDS.calibrate(125000000);        

  pot.initializePot();
  pot.decreaseResistance(100);
  
  encoder.setPosition(encoderMin);
  
  display.begin(); 
  
  startButton.attachLongPressStop(initTest);

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
        pot.decreaseResistance(100);
      } 
      else if (volNew > encoderMax) {
        encoder.setPosition(encoderMax);
        volNew = encoderMax;
        pot.setResistance(maxPot);
      }

      if (ear < 2) {
        displayTestParams();
      }

      vol = volNew;
      db = vol * 5;

      if (Serial.available()) {
        calibrationMode = Serial.read();
        Serial.println("Calibration mode: ");
        Serial.print(calibrationMode);
      }

      if (calibrationMode == 49) {
        calibration(db, 4.5, defaultCalibration, 1);
      } 
      if (calibrationMode == 50) {
        calibration(db, 4.5, ear3aCalibration, 2);
      } 
      if (calibrationMode == 51) {
        calibration(db, 4.5, tdh39Calibration, 3);
      }
      if (calibrationMode == 52) {
        calibration(db, 4.5, bioCalibration, 1);
      }
    }
  } 
}