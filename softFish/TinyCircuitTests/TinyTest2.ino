#include <SPI.h>
#include <RH_RF22.h>
#include <RH_NRF24.h>

#define use433 1  // 1 for 433MHz radio, 0 for NRF24L01
#define MAX_MESSAGE_LEN 64

#if(use433)
RH_RF22 radio(7, 3);  // (CS, INT)
#else
RH_NRF24 radio(9, 7); // (CE, CS)
#endif

#if defined(ARDUINO_ARCH_AVR)
  #define SerialMonitorInterface Serial
#elif defined(ARDUINO_ARCH_SAMD)
  #define SerialMonitorInterface SerialUSB
#else
  #define SerialMonitorInterface Serial
#endif

void setup() {
  SerialMonitorInterface.begin(115200);
  while (!SerialMonitorInterface);

  SerialMonitorInterface.println("Initializing Radio Transmitter...");

#if(use433)
  if (!radio.init()) {
    SerialMonitorInterface.println("433MHz radio init failed!");
    while (1);
  }

  radio.setTxPower(RH_RF22_TXPOW_20DBM);

  if (!radio.setModemConfig(RH_RF22::GFSK_Rb125Fd125)) {
    SerialMonitorInterface.println("setModemConfig failed!");
  }
#else
  if (!radio.init()) {
    SerialMonitorInterface.println("NRF24L01 radio init failed!");
    while (1);
  }

  if (!radio.setChannel(1)) {
    SerialMonitorInterface.println("setChannel failed");
  }

  if (!radio.setRF(RH_NRF24::DataRate250kbps, RH_NRF24::TransmitPower0dBm)) {
    SerialMonitorInterface.println("setRF failed");
  }
#endif

  SPI.setClockDivider(SPI_CLOCK_DIV4); // For AVR — safe for most boards
  SerialMonitorInterface.println("Ready to send IMU data via radio");
}

void loop() {
  if (SerialMonitorInterface.available() > 0) {
    String data = SerialMonitorInterface.readStringUntil('\n');
    SerialMonitorInterface.print("You sent me: ");
    SerialMonitorInterface.println(data);

    // Convert String to C-string
    char msg[MAX_MESSAGE_LEN];
    data.toCharArray(msg, MAX_MESSAGE_LEN);

    // Send over radio
    if (radio.send((uint8_t*)msg, strlen(msg))) {
      radio.waitPacketSent();
      SerialMonitorInterface.println("Sent over radio.");
    } else {
      SerialMonitorInterface.println("Radio send failed!");
    }

    // Wait for reply (optional)
    uint8_t buf[MAX_MESSAGE_LEN];
    uint8_t len = sizeof(buf);

    if (radio.waitAvailableTimeout(500)) {
      if (radio.recv(buf, &len)) {
        buf[len] = '\0';  // Null-terminate for safety
        SerialMonitorInterface.print("Received reply: ");
        SerialMonitorInterface.println((char*)buf);
      } else {
        SerialMonitorInterface.println("Failed to receive reply.");
      }
    } else {
      SerialMonitorInterface.println("No reply (timeout).");
    }
  }
}
