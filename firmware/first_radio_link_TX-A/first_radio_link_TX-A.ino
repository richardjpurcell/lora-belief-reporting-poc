#include <SPI.h>
#include <LoRa.h>
#include "schedule_data_TXA.h"

// LilyGO LoRa32 / T3-style pin mapping
#define LORA_SCK   5
#define LORA_MISO 19
#define LORA_MOSI 27
#define LORA_SS   18
#define LORA_RST  14
#define LORA_DIO0 26

// North America / Canada ISM band
#define LORA_BAND 915E6

const char* RUN_ID = "R24";
const char* TX_ID = "TXA";
const char* NODE_ID = "N01";

const unsigned long SLOT_INTERVAL_MS = 1000;
uint16_t schedule_index = 0;
uint32_t packet_seq = 0;
unsigned long last_slot_ms = 0;

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
  Serial.println("Skipped-slot schedule replay.");
  Serial.print("Schedule rows: ");
  Serial.println(SCHEDULE_ROW_COUNT);
  Serial.print("SEND rows: ");
  Serial.println(SCHEDULE_SEND_COUNT);
  Serial.print("SKIP rows: ");
  Serial.println(SCHEDULE_SKIP_COUNT);
}

void sendSchedulePacket(const ScheduleRow& row) {
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

  packet_seq++;
}

void processScheduleSlot() {
  const ScheduleRow& row = SCHEDULE_ROWS[schedule_index % SCHEDULE_ROW_COUNT];

  Serial.print("slot ");
  Serial.print(schedule_index);
  Serial.print(" demand_index ");
  Serial.print(row.demand_index);

  if (row.send) {
    Serial.print(" SEND ");
    sendSchedulePacket(row);
  } else {
    Serial.println(" SKIP");
  }

  schedule_index++;
}

void loop() {
  unsigned long now = millis();

  if (now - last_slot_ms >= SLOT_INTERVAL_MS) {
    last_slot_ms = now;
    processScheduleSlot();
  }
}
