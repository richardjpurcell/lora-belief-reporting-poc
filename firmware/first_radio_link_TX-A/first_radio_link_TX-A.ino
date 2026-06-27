#include <SPI.h>
#include <LoRa.h>
#include "trace_data_TXA.h"

// LilyGO LoRa32 / T3-style pin mapping
#define LORA_SCK   5
#define LORA_MISO 19
#define LORA_MOSI 27
#define LORA_SS   18
#define LORA_RST  14
#define LORA_DIO0 26

// North America / Canada ISM band
#define LORA_BAND 915E6

const char* RUN_ID = "R23";
const char* TX_ID = "TXA";
const char* NODE_ID = "N01";

const unsigned long SEND_INTERVAL_MS = 1000;
uint16_t trace_index = 0;
uint32_t packet_seq = 0;
unsigned long last_send_ms = 0;

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

void sendTracePacket() {
  const TraceRow& row = TRACE_ROWS[trace_index % TRACE_ROW_COUNT];

  char payload[160];

  snprintf(
    payload,
    sizeof(payload),
    "%s,%s,%s,%lu,%lu,%c,%u,%.2f,%.2f,%u,%c",
    RUN_ID,
    TX_ID,
    NODE_ID,
    (unsigned long)packet_seq,
    millis(),
    row.region,
    row.event,
    row.priority,
    row.usefulness,
    row.stale_after,
    row.policy
  );

  Serial.print("sending: ");
  Serial.println(payload);

  LoRa.beginPacket();
  LoRa.print(payload);
  LoRa.endPacket();

  trace_index++;
  packet_seq++;
}

void loop() {
  unsigned long now = millis();

  if (now - last_send_ms >= SEND_INTERVAL_MS) {
    last_send_ms = now;
    sendTracePacket();
  }
}
