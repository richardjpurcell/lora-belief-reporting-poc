int counter = 0;

void setup() {
  Serial.begin(115200);
  delay(1500);

  Serial.println();
  Serial.println("=== LilyGO LoRa32 serial test ===");
  Serial.println("Role: TX-B");
}

void loop() {
  Serial.print("TX-B heartbeat ");
  Serial.println(counter++);
  delay(1000);
}