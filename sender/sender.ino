#include <SPI.h>
#include <RF24.h>

#define CE_PIN 7
#define CSN_PIN 8

// NRF24L01 setup
RF24 radio(CE_PIN, CSN_PIN);

// Address for communication
const byte address[6] = "00001";

void setup() {
  Serial.begin(9600);
  Serial.println("Starting Transmitter...");

  // Initialize NRF24L01
  if (!radio.begin()) {
    Serial.println("NRF24L01 not connected!");
    while (1);  // Stop if module not connected
  }

  radio.openWritingPipe(address);
  radio.setPALevel(RF24_PA_LOW);
  radio.stopListening();  // Set as transmitter
  Serial.println("Transmitter ready!");
}

void loop() {
  // Check if command is available from Serial Monitor
  if (Serial.available() > 0) {
    char command = Serial.read();
    
    // Only allow valid commands
    if (command == 'F' || command == 'B' || command == 'L' || command == 'R' || command == 'S') {
      Serial.print("Sending command: ");
      Serial.println(command);

      // Flush the buffer to remove extra characters
      while (Serial.available() > 0) {
        Serial.read();
      }

      // Send the command via NRF
      if (radio.write(&command, sizeof(command))) {
        Serial.println("Command sent successfully!");
      } else {
        Serial.println("Failed to send command!");
      }
    } else {
      Serial.println("Invalid command! Use F, B, L, R, or S.");
    }
  }
  delay(10);
}
