//The Tiny-zero is plugged into the RPI. This recieved messages over radio-broacast from the Tiny-zero plugged into the laptop (running on the Arduino IDE)
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
  while (!SerialMonitorInterface); // Wait for Serial connection

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

  SerialMonitorInterface.println("Receiver setup complete.");
}

void loop() {
  uint8_t buf[RH_RF22_MAX_MESSAGE_LEN];
  uint8_t len = sizeof(buf);

  if (nrf24.available()) {
    if (nrf24.recv(buf, &len)) {
      String receivedMsg = String((char*)buf).substring(0, len);
      SerialMonitorInterface.print("Received message: ");
      SerialMonitorInterface.println(receivedMsg);

      // If message is "W", print special acknowledgment to console
      if (receivedMsg == "W") {
        SerialMonitorInterface.println("Special command 'W' received!");
      }

      // Send reply back
      const char* reply = "I got your message";
      nrf24.send((uint8_t*)reply, strlen(reply));
      nrf24.waitPacketSent();

      SerialMonitorInterface.println("Sent reply to transmitter.");
    }
  }

  delay(100);
}
