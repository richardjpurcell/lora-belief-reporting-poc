#include <SPI.h>
#include <LoRa.h>

// RXB: LilyGO T-Beam pin mapping; verify against board revision during upload/test
#define LORA_SCK   5
#define LORA_MISO 19
#define LORA_MOSI 27
#define LORA_SS   18
#define LORA_RST  23
#define LORA_DIO0 26

// North America / Canada ISM band
#define LORA_BAND 915E6

const char* RX_ID = "RXC_TBEAM";
const char* RX_BOARD = "LilyGO T-Beam receiver";

void setup() {
  Serial.begin(115200);
  delay(1500);

  Serial.println();
  Serial.print("=== ");
  Serial.print(RX_ID);
  Serial.print(": ");
  Serial.print(RX_BOARD);
  Serial.println(" ===");

  SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_SS);
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);

  if (!LoRa.begin(LORA_BAND)) {
    Serial.println("LoRa init failed. Check pins, antenna, and board type.");
    while (true) {
      delay(1000);
    }
  }



  Serial.println("LoRa init OK.");
  Serial.println("Waiting for packets...");
}

void loop() {
  int packetSize = LoRa.parsePacket();

  if (packetSize) {
    String payload = "";

    while (LoRa.available()) {
      payload += (char)LoRa.read();
    }

    Serial.print("RX,");
    Serial.print(millis());
    Serial.print(",");
    Serial.print(payload);
    Serial.print(",");
    Serial.print(LoRa.packetRssi());
    Serial.print(",");
    Serial.println(LoRa.packetSnr());
  }
}
