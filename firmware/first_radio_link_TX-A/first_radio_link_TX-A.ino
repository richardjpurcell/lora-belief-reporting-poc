#include <SPI.h>
#include <LoRa.h>

// LilyGO LoRa32 / T3-style pin mapping
#define LORA_SCK   5
#define LORA_MISO 19
#define LORA_MOSI 27
#define LORA_SS   18
#define LORA_RST  14
#define LORA_DIO0 26

// North America / Canada ISM band
#define LORA_BAND 915E6

int seq = 0;

void setup() {
  Serial.begin(115200);
  delay(1500);

  Serial.println();
  Serial.println("=== TX-A: LilyGO LoRa32 sender ===");

  SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_SS);
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);

  if (!LoRa.begin(LORA_BAND)) {
    Serial.println("LoRa init failed. Check pins, antenna, and board type.");
    while (true) {
      delay(1000);
    }
  }

  LoRa.enableCrc();
  // Keep transmit power modest for indoor bench testing.
  LoRa.setTxPower(10);

  Serial.println("LoRa init OK.");
  Serial.println("Sending packets...");
}

void loop() {
  float priority;
  float usefulness;

  // TX-A is the lower-value baseline stream.
  // Deterministic mild variation keeps the run reproducible.
  int phase = seq % 4;

  if (phase == 0) {
    priority = 0.25;
    usefulness = 0.20;
  } else if (phase == 1) {
    priority = 0.30;
    usefulness = 0.25;
  } else if (phase == 2) {
    priority = 0.35;
    usefulness = 0.30;
  } else {
    priority = 0.40;
    usefulness = 0.35;
  }

  String payload =
    "R12,TXA,N01," +
    String(seq) + "," +
    String(millis()) +
    ",A,1," +
    String(priority, 2) + "," +
    String(usefulness, 2) +
    ",30,R";

  Serial.print("sending: ");
  Serial.println(payload);

  LoRa.beginPacket();
  LoRa.print(payload);
  LoRa.endPacket();

  seq++;
  delay(1000);
}
