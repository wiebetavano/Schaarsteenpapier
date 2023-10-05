// TODO refactor and abstract pin mapping
// https://stackoverflow.com/questions/15727814/arduino-hash-table-dictionary
// #define ? 
int pin1 = 4; // lowerFingers
int pin2 = 5; // upperFingers
int pin3 = 6; // turnwrist
int pin4 = 7; // movewrist

void setup() {
  Serial.begin(9600);
  pinMode(pin1, OUTPUT);
  pinMode(pin2, OUTPUT);
  pinMode(pin3, OUTPUT);
  pinMode(pin4, OUTPUT);
}

void loop() {
  // read the sensor:
  if (Serial.available() > 0) {
    char inByte = Serial.read();
    switch (inByte) {
      case 'Q': // query for a response
        Serial.write('R');
        break;
      case 'S': // play scissors
        digitalWrite(pin1, HIGH);
        digitalWrite(pin2, LOW);
        break;
      case 'R': // play rock
        digitalWrite(pin1, HIGH);
        digitalWrite(pin2, HIGH);
        break;
      case 'P': // play paper
        digitalWrite(pin1, LOW);
        digitalWrite(pin2, LOW);
        break;
      case 'H': // hand horizontal
        digitalWrite(pin3, HIGH);
        break;
      case 'V': // hand vertical
        digitalWrite(pin3, LOW);
        break;
      case 'U': // arm up
        digitalWrite(pin4, LOW);
        break;
      case 'D': // arm down
        digitalWrite(pin4, HIGH);
        break;
      default:
        break;
    }
  }
}