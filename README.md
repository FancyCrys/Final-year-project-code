#  Smart AI Traffic Control System

A low-cost, Raspberry Pi–based intelligent traffic light controller using real-time computer vision and adaptive logic to optimize vehicle flow at intersections.

Built with Python, OpenCV, and RPi.GPIO — this project is a proof-of-concept for smarter, scalable urban mobility systems using embedded hardware.



---

##  Features

-  Detects vehicles in 3 separate lanes using a PiCamera
-  Dynamically adjusts green light duration based on real-time traffic density
-  Simulates traffic signals using LEDs connected to GPIO pins
-  Lightweight image processing using OpenCV (no ML model required)
-  Runs fully offline – ideal for remote, low-resource environments

---

## Demo

https://youtube.com/shorts/67UjEdX1ZpA

---

##  Tech Stack

- **Raspberry Pi 4 Model B**
- **PiCamera v2** (using `picamera2`)
- **Python 3.10+**
- **OpenCV**
- **RPi.GPIO**
- **Breadboard + LEDs** for signal simulation

---

## Getting Started

###  Hardware Requirements

- Raspberry Pi 4 (or 3B+)
- PiCamera module
- Breadboard with 9 LEDs (3 per lane: red, yellow, green)
- Jumper wires & 220Ω resistors
- MicroSD card with Raspberry Pi OS


