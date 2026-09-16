# RF-SHIELD AI v4.0 - Intelligent Sky Safety & RF Threat Detection System

### 🚀 Project Expo 2026

## 📌 Abstract
In modern aviation, RF interference from illegal jammers and unauthorized transmitters poses a serious threat to pilot-ATC communication, especially during landing. 
RF-SHIELD AI v4.0 is an intelligent, AI-powered protection system that continuously monitors the RF spectrum, identifies harmful interference in real-time, and provides instant visual and audio alerts to ensure aircraft safety.

## 🎯 Objective
- To detect illegal RF jammers near sensitive zones
- To protect aircraft communication from interference
- To give real-time SKY SAFE status indication
- To alert control room instantly with buzzer and LED system

## ✨ Key Features
- 📡 Wide Range RF Scanning (800MHz - 2.4GHz)
- 🤖 AI Based Threat Classification - Safe / Warning / Critical
- 🟢 SKY SAFE Indicator System
- 📊 Live RF Graph Visualization in PC
- 🚨 Instant Buzzer & Tri-Color LED Alert
- 💾 Automatic Data Logging (CSV Format)
- 🖥️ Professional Python GUI for Monitoring

## 🛠️ Hardware Components
- Arduino Uno R3
- RF Receiver Module (433MHz)
- 16x2 LCD Display with I2C
- Active Buzzer - 5V
- LEDs - Red, Yellow, Green with Resistors
- Breadboard & Jumper Wires

## 💻 Software & Technology
- Embedded C (Arduino IDE)
- Python 3.11
- Tkinter for GUI Design
- Matplotlib for Real-Time Graph
- PySerial for Arduino-PC Communication
- AI Logic for Signal Classification

## ⚙️ Working Principle
1.  RF Receiver continuously captures surrounding RF signals.
2.  Arduino processes the signal strength (RSSI) and frequency.
3.  Inbuilt AI logic compares signal with threshold levels.
4.  Based on threat level, system decides: SAFE, WARNING, or DANGER.
5.  LCD displays status, LEDs glow accordingly, Buzzer alerts if critical.
6.  Python GUI receives data via Serial and shows live graph and logs.

## 🔌 Circuit Diagram
- RF Module VCC -> 5V, GND -> GND, DATA -> A0
- LCD RS->12, EN->11, D4->5, D5->4, D6->3, D7->2
- Buzzer Positive -> D8, Negative -> GND
- Green LED -> D9, Yellow LED -> D10, Red LED -> D13

## 🚀 How To Run
Step 1: Upload `arduino_code.ino` to Arduino Uno
Step 2: Connect RF module and other components as per circuit
Step 3: Install Python libraries: pip install pyserial matplotlib
Step 4: Run `python rf_shield_gui.py`
Step 5: Select COM Port and click CONNECT to start monitoring

## 📈 Advantages
- Low Cost and Portable
- High Accuracy Detection (<1 Sec Response)
- Can be installed near airports, military bases
- Expandable for Drone Detection in future

## 👩‍💻 Developed By
**Dhanushya S. L, A. P. Akshaya, Akshaya S**

Project Expo 2026
