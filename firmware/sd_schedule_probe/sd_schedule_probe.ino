#include <SPI.h>
#include <SD.h>

// Candidate LilyGO/TTGO LoRa32 onboard microSD pins.
// Confirm against actual board behavior.
#define SD_SCK    14
#define SD_MISO    2
#define SD_MOSI   15
#define SD_CS     13

const char* SCHEDULE_FILE = "/schedule.csv";

SPIClass sdSPI(HSPI);

void fatalError(const char* message) {
  Serial.print("ERROR: ");
  Serial.println(message);
  while (true) {
    delay(1000);
  }
}

void setup() {
  Serial.begin(115200);
  delay(1500);

  Serial.println();
  Serial.println("=== SD schedule probe ===");

  Serial.println("Initializing SD...");
  sdSPI.begin(SD_SCK, SD_MISO, SD_MOSI, SD_CS);

  if (!SD.begin(SD_CS, sdSPI)) {
    fatalError("SD init failed.");
  }

  Serial.println("SD init OK.");

  File file = SD.open(SCHEDULE_FILE, FILE_READ);
  if (!file) {
    fatalError("Could not open /schedule.csv.");
  }

  Serial.println("Opened /schedule.csv");
  Serial.println("First lines:");

  int line_count = 0;
  while (file.available() && line_count < 20) {
    String line = file.readStringUntil('\n');
    line.trim();
    Serial.println(line);
    line_count++;
  }

  file.close();
  Serial.println("Probe complete.");
}

void loop() {
  delay(1000);
}