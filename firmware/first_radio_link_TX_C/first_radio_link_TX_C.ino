#include <SPI.h>
#include <LoRa.h>
#include <SD.h>

// LilyGO LoRa32 / T3-style LoRa pin mapping
#define LORA_SCK   5
#define LORA_MISO 19
#define LORA_MOSI 27
#define LORA_SS   18
#define LORA_RST  14
#define LORA_DIO0 26

// microSD pin mapping.
// These are intentionally kept explicit because LilyGO/TTGO LoRa board
// revisions differ. If SD init fails, confirm these against the exact board.
#define SD_SCK    14
#define SD_MISO    2
#define SD_MOSI   15
#define SD_CS     13

// North America / Canada ISM band
#define LORA_BAND 915E6

const char* RUN_ID = "R31";
const char* TX_ID = "TXC";
const char* NODE_ID = "N31";

const char* SCHEDULE_FILE = "/schedule.csv";

const unsigned long SLOT_INTERVAL_MS = 1000;
const unsigned long STARTUP_OFFSET_MS = 1000;

const uint16_t MAX_SCHEDULE_ROWS = 256;

struct ScheduleRow {
  uint16_t demand_index;
  char region;
  uint8_t event;
  float priority;
  float usefulness;
  uint16_t stale_after;
  char policy;
  uint8_t send;
};

ScheduleRow schedule_rows[MAX_SCHEDULE_ROWS];
uint16_t schedule_row_count = 0;
uint16_t schedule_send_count = 0;
uint16_t schedule_skip_count = 0;

uint16_t schedule_index = 0;
uint32_t packet_seq = 0;
unsigned long last_slot_ms = 0;

SPIClass sdSPI(HSPI);

void fatalError(const char* message) {
  Serial.print("ERROR: ");
  Serial.println(message);
  Serial.println("Replay halted.");
  while (true) {
    delay(1000);
  }
}

String csvField(const String& line, int target_index) {
  int start = 0;
  int field_index = 0;

  while (true) {
    int comma = line.indexOf(',', start);
    int end = (comma == -1) ? line.length() : comma;

    if (field_index == target_index) {
      String value = line.substring(start, end);
      value.trim();
      return value;
    }

    if (comma == -1) {
      return "";
    }

    start = comma + 1;
    field_index++;
  }
}

bool parseScheduleLine(const String& line, ScheduleRow& row) {
  String seq = csvField(line, 0);
  String region = csvField(line, 1);
  String event = csvField(line, 2);
  String priority = csvField(line, 3);
  String usefulness = csvField(line, 4);
  String stale_after = csvField(line, 5);
  String policy = csvField(line, 6);
  String send = csvField(line, 7);

  if (
    seq.length() == 0 ||
    region.length() == 0 ||
    event.length() == 0 ||
    priority.length() == 0 ||
    usefulness.length() == 0 ||
    stale_after.length() == 0 ||
    policy.length() == 0 ||
    send.length() == 0
  ) {
    return false;
  }

  if (!(send == "0" || send == "1")) {
    return false;
  }

  row.demand_index = (uint16_t)seq.toInt();
  row.region = region.charAt(0);
  row.event = (uint8_t)event.toInt();
  row.priority = priority.toFloat();
  row.usefulness = usefulness.toFloat();
  row.stale_after = (uint16_t)stale_after.toInt();
  row.policy = policy.charAt(0);
  row.send = (uint8_t)send.toInt();

  return true;
}

void loadScheduleFromSD() {
  Serial.println("Initializing microSD replay schedule...");

  sdSPI.begin(SD_SCK, SD_MISO, SD_MOSI, SD_CS);

  if (!SD.begin(SD_CS, sdSPI)) {
    fatalError("SD init failed. Check card, format, and board-specific SD pins.");
  }

  File file = SD.open(SCHEDULE_FILE, FILE_READ);
  if (!file) {
    fatalError("Could not open /schedule.csv.");
  }

  String header = file.readStringUntil('\n');
  header.trim();

  const String expected_header = "seq,region,event,priority,usefulness,stale_after,policy,send";
  if (header != expected_header) {
    Serial.print("Observed header: ");
    Serial.println(header);
    fatalError("Unexpected schedule CSV header.");
  }

  uint16_t line_number = 1;

  while (file.available()) {
    String line = file.readStringUntil('\n');
    line.trim();
    line_number++;

    if (line.length() == 0) {
      continue;
    }

    if (schedule_row_count >= MAX_SCHEDULE_ROWS) {
      fatalError("Schedule exceeds MAX_SCHEDULE_ROWS.");
    }

    ScheduleRow row;
    if (!parseScheduleLine(line, row)) {
      Serial.print("Malformed schedule row at line ");
      Serial.println(line_number);
      fatalError("Could not parse schedule row.");
    }

    schedule_rows[schedule_row_count] = row;
    schedule_row_count++;

    if (row.send) {
      schedule_send_count++;
    } else {
      schedule_skip_count++;
    }
  }

  file.close();

  if (schedule_row_count == 0) {
    fatalError("Schedule contains zero rows.");
  }

  Serial.println("SD replay mode.");
  Serial.print("schedule_file=");
  Serial.println(SCHEDULE_FILE);
  Serial.print("tx_id=");
  Serial.println(TX_ID);
  Serial.print("node_id=");
  Serial.println(NODE_ID);
  Serial.print("rows_loaded=");
  Serial.println(schedule_row_count);
  Serial.print("send_rows=");
  Serial.println(schedule_send_count);
  Serial.print("skip_rows=");
  Serial.println(schedule_skip_count);
  Serial.print("replay_period_rows=");
  Serial.println(schedule_row_count);
  Serial.println("packet_format=existing");
}

void setup() {
  Serial.begin(115200);
  delay(1500);

  Serial.println();
  Serial.println("=== TX-C: LilyGO LoRa32 sender ===");

  SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_SS);
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);

  if (!LoRa.begin(LORA_BAND)) {
    fatalError("LoRa init failed. Check pins, antenna, and board type.");
  }

  LoRa.enableCrc();

  // Keep transmit power modest for indoor bench testing.
  LoRa.setTxPower(10);

  Serial.println("LoRa init OK.");

  Serial.print("Startup offset ms: ");
  Serial.println(STARTUP_OFFSET_MS);
  delay(STARTUP_OFFSET_MS);

  loadScheduleFromSD();
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
  const ScheduleRow& row = schedule_rows[schedule_index % schedule_row_count];

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
