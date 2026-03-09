//Transmitter code for the Tiny-Zero. The Tiny-zero is plugged into the laptop and runs this script. The prompting is a little funky, but plugging and then uplugging works well. This transmits to the 
//other Tiny-zero on the RPI

#include <SPI.h>
#include <RH_RF22.h>
#include <RH_NRF24.h>

#define use433 1  // 1 for 433MHz RF22, 0 for NRF24L01

#if(use433)
RH_RF22 nrf24(7, 3);
#else
RH_NRF24 nrf24(9, 7);
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
  while (!SerialMonitorInterface); // Wait for Serial

#if(use433)
  if (!nrf24.init()) {
    SerialMonitorInterface.println("RF22 init failed");
  }
  nrf24.setTxPower(RH_RF22_TXPOW_20DBM);
  if (!nrf24.setModemConfig(RH_RF22::GFSK_Rb125Fd125)) {
    SerialMonitorInterface.println("setModemConfig failed");
  }
#else
  if (!nrf24.init()) {
    SerialMonitorInterface.println("NRF24 init failed");
  }
  if (!nrf24.setChannel(1)) {
    SerialMonitorInterface.println("Channel set failed");
  }
  if (!nrf24.setRF(RH_NRF24::DataRate250kbps, RH_NRF24::TransmitPower0dBm)) {
    SerialMonitorInterface.println("setRF failed");
  }
#endif

  SPI.setClockDivider(4);
  SerialMonitorInterface.println("Transmitter setup complete. Type 'W' to send a message.");
}

void loop() {
  if (SerialMonitorInterface.available()) {
    String input = SerialMonitorInterface.readStringUntil('\n');
    input.trim();

    SerialMonitorInterface.print("User input was: ");
    SerialMonitorInterface.println(input);

    if (input == "W") {
      SerialMonitorInterface.println("Sending 'W' to receiver...");

      uint8_t data[] = "W";
      nrf24.send(data, sizeof(data) - 1); // exclude null terminator
      nrf24.waitPacketSent();

      SerialMonitorInterface.println("Message sent. Waiting for reply...");

      // Wait for reply
      uint8_t buf[RH_RF22_MAX_MESSAGE_LEN];
      uint8_t len = sizeof(buf);

      if (nrf24.waitAvailableTimeout(2000)) { // wait up to 2 seconds
        if (nrf24.recv(buf, &len)) {
          String reply = String((char*)buf).substring(0, len);
          SerialMonitorInterface.print("Reply from receiver: ");
          SerialMonitorInterface.println(reply);
        } else {
          SerialMonitorInterface.println("Failed to receive reply.");
        }
      } else {
        SerialMonitorInterface.println("No reply from receiver.");
      }
    } else {
      SerialMonitorInterface.println("Unknown command. Please type 'W'.");
    }
  }
  delay(100);
}
