#include <SPI.h>
#include <RF24.h>

// Motor pins
// Motor A (Left)
const int ENA = 3;
const int IN1 = 2;
const int IN2 = 4;

// Motor B (Right)
const int ENB = 6;
const int IN3 = 5;
const int IN4 = 7;

// NRF24L01 setup
RF24 radio(7, 8);  // CE = 7, CSN = 8

// Address for communication
const byte address[6] = "00001";

// Speed settings
const int SPEED = 150;  // 0-255 for PWM

void setup() {
  Serial.begin(9600);
  Serial.println("Starting Receiver...");

  // Initialize NRF24L01
  if (!radio.begin()) {
    Serial.println("NRF24L01 not connected!");
    while (1);  // Stop if module not connected
  }

  radio.openReadingPipe(0, address);
  radio.setPALevel(RF24_PA_LOW);
  radio.startListening();  // Set as receiver
  Serial.println("Receiver ready!");

  // Set motor pins as outputs
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  // Stop motors initially
  stopMotors();
}

// Main loop - Check for incoming commands
void loop() {
  if (radio.available()) {
    char command = 0;
    radio.read(&command, sizeof(command));
    Serial.print("Received command: ");
    Serial.println(command);

    // Execute the command
    executeCommand(command);
  }
  delay(10);
}

// Command execution logic
void executeCommand(char command) {
  switch (command) {
    case 'F':  // Move forward
      moveForward();
      break;
    case 'B':  // Move backward
      moveBackward();
      break;
    case 'L':  // Turn left
      turnLeft();
      break;
    case 'R':  // Turn right
      turnRight();
      break;
    case 'S':  // Stop
      stopMotors();
      break;
    default:
      Serial.println("Unknown command!");
      break;
  }
}

// Motor control functions
void moveForward() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  analogWrite(ENA, SPEED);

  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  analogWrite(ENB, SPEED);
}

void moveBackward() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  analogWrite(ENA, SPEED);

  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  analogWrite(ENB, SPEED);
}

void turnLeft() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  analogWrite(ENA, SPEED);

  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  analogWrite(ENB, SPEED);
}

void turnRight() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  analogWrite(ENA, SPEED);

  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  analogWrite(ENB, SPEED);
}

void stopMotors() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  analogWrite(ENA, 0);

  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  analogWrite(ENB, 0);
}
