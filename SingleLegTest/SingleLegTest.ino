#include <Servo.h>

Servo coxaServo;
Servo femurServo;
Servo tibiaServo;

bool hasAttached = false;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);

}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    char charBuf[50];
    input.toCharArray(charBuf, 50);

    // Split the string by commas
    char *token1 = strtok(charBuf, ",");
    char *token2 = strtok(NULL, ",");
    char *token3 = strtok(NULL, ",");

    // Check if all three tokens exist
    if (token1 != NULL && token2 != NULL && token3 != NULL) {
      int coxaPulse = atoi(token1);   // Convert first token to int
      int femurPulse = atof(token2);  // Convert second token to float
      int tibiaPulse = atoi(token3);   // Convert third token to int

      coxaServo.writeMicroseconds(coxaPulse);
      femurServo.writeMicroseconds(femurPulse);
      tibiaServo.writeMicroseconds(tibiaPulse);

      if (hasAttached == false) {
        coxaServo.attach(9, 500, 2500);
        femurServo.attach(8, 500, 2500);
        tibiaServo.attach(7, 500, 2500);
        hasAttached = true;
      }
      Serial.println("Done");
    } else {
    Serial.println("ERR");
    }
  }
}
