# Noise Level Monitor

A real-time decibel (dB) meter built with Python. This application provides a visual and terminal-based interface to monitor noise levels via your microphone, featuring a custom gauge, configurable alerts, and an industrial-inspired UI.

*(Replace with your actual image path if available)*

## 🚀 Features

* **Dual Interface**: Choose between a modern Kivy-based GUI and a lightweight, SSH-friendly terminal version.
* **Custom Gradient Gauge**: A high-fidelity visual meter inspired by industrial sound level charts (Green to Red segments).
* **Configurable Alerts**: Set a custom dB threshold. When noise exceeds this limit, the app triggers:
* A visual red alarm state on the gauge.
* An optional audio alert sound.


* **Persistent Settings**: Thresholds and alert preferences are saved automatically in a configuration file.
* **Iconic Design**: Uses Google Material Symbols for a modern, clean settings interface.

## 🛠️ Installation

### 1. Prerequisites

Ensure you have Python 3.8+ installed. You will need a functioning microphone.

### 2. Dependencies

Install the required libraries:

```bash
# Core requirements
pip install kivy pyaudio numpy

# For audio alert playback (recommended provider)
pip install ffpyplayer

```

### 3. Assets

To ensure the GUI renders correctly, place the following files in the project root:

* `material_symbols.ttf`: The Google Material Symbols font file.
* `alert.wav`: The audio file for the loud noise notification.

## 📖 Usage

### GUI Version

Launch the graphical interface with:

```bash
python main.py

```

* **Settings**: Click the gear icon ($\u2699$) to adjust the alert threshold (default is 85 dB) or toggle sound alerts.
* **Gauge**: The needle turns red and the display flashes when the threshold is reached.

### Terminal Version

For a fast, command-line only monitor:

```bash
python terminal_noise.py

```

This version uses ANSI colors and an ASCII bar to represent noise levels directly in your console.

## ⚙️ How it Works

The application captures raw audio chunks using `PyAudio`. It calculates the **Root Mean Square (RMS)** of the signal and converts it to a logarithmic scale using the decibel formula:

$$dB = 20 \cdot \log_{10}(RMS)$$

*Note: Microphones vary in sensitivity. Use the settings (or code constants) to apply a calibration offset for higher accuracy.*

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

## 🤝 Contributing

Contributions are welcome!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request