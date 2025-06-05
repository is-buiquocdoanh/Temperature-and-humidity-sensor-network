# TEAMPERATURE AND HUMIDITY SENSOR NETWORK (STM32F103 + RA-02)

This project enables wireless data collection of temperature and humidity from distributed sensing nodes using STM32F103 + AHT10 sensor + LCD + LoRa RA-02. Data is transmitted to a PC gateway and displayed/stored via a GUI application.

---

## 📦 Sensor Module Design for Temperature and Humidity Measurement
| **No.** | **Description**                                                                                                                                                                                                              |
| ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1**   | - **Measuring range**: -10°C to 70°C, 0–100% RH <br> - **Accuracy**: ±1°C, ±3% RH <br> - **Display resolution**: 0.1°C, 1% RH                                                                                                |
| **2**   | **Power source** and device operation time is **1 month** (advanced: 24 months). <br> Battery can be **single-use** or **rechargeable**. <br> Battery can be **charged directly on the device** or **removed for charging**. |
| **3**   | - **Estimated size**: 50 mm × 80 mm *(compact cylindrical shape for easy integration into smart agriculture systems)* <br> - **Estimated weight**: <150g <br> - **Protection level**: IPx7 or IPx8                           |
| **4**   | - **Sample time per measurement**: <120s *(advanced: <20s)*                                                                                                                                                                  |
| **5**   | **PC connection**: RF communication with a transmission range >100m from the measurement system to the RF receiving station (which is connected to power and network)                                                        |
| **6**   | - **Minimum management** of 100 sensing devices *(advanced: expandable number of devices with up to 5000m communication range)* <br> - **Data latency**: <10s *(advanced: <2s)*                                              |
| **7**   | **PC software**: collects measurement data from sensor nodes, manages data, exports reports in Excel format, provides a consistent and unified interface                                                                     |
| **8**   | **LED indicators**: 3 LEDs for temperature threshold indication and humidity levels <br> Threshold values and sampling intervals **can be updated from the PC**                                                              |
| **9**   | **Firmware update via OTA (Over The Air)** *(advanced feature)*                                                                                                                                                              |


---

## 🔧 Hardware Used

- STM32F103C8T6 (or C6T8)
- LoRa RA-02 (SX1278)
- AHT10 (I2C)
- I2C LCD 1602
- RGB LEDs (Red, Yellow, Green)
- 3.7V Li-ion battery or external 5V source

---

## 🔌 Wiring (minimum)

| Component | STM32 Pins |
|----------|------------|
| AHT10 SDA/SCL | I2C2 (PB10, PB11) |
| LCD I2C | I2C1 (PB6, PB7) |
| LoRa RA-02 | SPI1 (PA5, PA6, PA7), NSS: PA4, DIO0: PA0, RST: PB1 |
| LEDs | PB12, PB13, PB14 |
| UART debug/config | USART1 (PA9: TX, PA10: RX) |
| Power | 3.7V via Li-ion + TP4056 + boost circuit (if needed) |

---

## 💻 PC Software (Python GUI)

- Script: `LoRaMonitor.py`
- Features:
  - COM port selection
  - Realtime data table
  - Send `SET:` command to nodes
  - Export to Excel
  - Clear data

### 🧪 Configuration Command Format

```text
SET:TMAX=35:TMIN=25:HMAX=75:HMIN=40:INTERVAL=15
