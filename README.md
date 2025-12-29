# BLE Heart Rate Monitor (ESP BLE Proxy)

This custom Home Assistant integration connects to a **Bluetooth Low Energy (BLE) Heart Rate Monitor (HRM)** using Home Assistant’s **ESP BLE Proxy** and exposes the **heart rate (bpm)** as a sensor.

The integration uses the **standard Heart Rate Service (UUID 0x180D)** and subscribes to **Heart Rate Measurement notifications (UUID 0x2A37)**.

---

## ✨ Features

- ❤️ Reads heart rate in **beats per minute (bpm)**
- 📡 Uses **ESPHome ESP32 BLE Proxy**
- 🔔 Uses **BLE notifications** (no polling)
- 🧩 **UI-based setup** (MAC address entered in Home Assistant UI)
- 🧠 Correct parsing of 8-bit and 16-bit HR values
- ⚡ Low latency, real-time updates
<img width="712" height="176" alt="grafik" src="https://github.com/user-attachments/assets/39ce8476-03f8-4b05-a3de-3da26e43c601" />
---



## 📦 Requirements

- Home Assistant **2023.9 or newer**
- At least one **ESP32 running ESPHome** with BLE Proxy enabled
- A BLE Heart Rate Monitor that supports:
  - Heart Rate Service `0x180D`
  - Heart Rate Measurement Characteristic `0x2A37`

---

## 🔧 ESPHome BLE Proxy Configuration

Your ESP32 must include this in its ESPHome YAML:

```yaml
esp32_ble_tracker:

bluetooth_proxy:
  active: true


