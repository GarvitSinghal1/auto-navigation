// Arduino code for auto navigation robot
// Receives commands from Python and controls motors

// Motor pins
// Motor A (Left)
const int ENA = 3;  // PWM pin for speed control
const int IN1 = 2;  // Direction control
const int IN2 = 4;  // Direction control

// Motor B (Right)
const int ENB = 6;  // PWM pin for speed control
const int IN3 = 5;  // Direction control
const int IN4 = 7;  // Direction control

// Speed settings
const int SPEED = 150;  // 0-255 for PWM

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Set all motor pins as outputs
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  
  // Initially stop motors
  stopMotors();
  
  Serial.println("Arduino ready for commands");
}

void loop() {
  // Check if data is available from Python
  if (Serial.available() > 0) {
    char command = Serial.read();
    executeCommand(command);
  }
}

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
      // Invalid command, do nothing
      break;
  }
}

void moveForward() {
  // Left motor forward
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  analogWrite(ENA, SPEED);
  
  // Right motor forward
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  analogWrite(ENB, SPEED);
}

void moveBackward() {
  // Left motor backward
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  analogWrite(ENA, SPEED);
  
  // Right motor backward
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  analogWrite(ENB, SPEED);
}

void turnLeft() {
  // Left motor stop or reverse
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  analogWrite(ENA, SPEED);
  
  // Right motor forward
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  analogWrite(ENB, SPEED);
}

void turnRight() {
  // Left motor forward
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  analogWrite(ENA, SPEED);
  
  // Right motor stop or reverse
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  analogWrite(ENB, SPEED);
}

void stopMotors() {
  // Stop both motors
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  analogWrite(ENA, 0);
  
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  analogWrite(ENB, 0);
} 