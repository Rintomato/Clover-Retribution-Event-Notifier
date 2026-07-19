# Clover Retribution Event Notifier

An OCR-based desktop notifier for **Roblox Clover Retribution** that detects world event announcements from your game chat and instantly alerts you with desktop sounds and optional Discord webhook notifications.

> This project is intended for convenience and monitoring only. It does not interact with the Roblox client or automate gameplay.

---

## Features

- 🔍 OCR-based event detection
- 🔔 Instant sound notifications
- 📢 Discord webhook notifications
- ✅ Enable or disable individual events
- 🖥️ Simple CustomTkinter interface
- 🎯 Select your own OCR capture region
- ⏱️ Built-in cooldown to prevent duplicate notifications

---

## Supported Events

- Bandit Lord
- Warlord
- Khamsin
- Desert Village Rumor
- Craftsman
- Corrupt Night
- Mana Wisp
- Elemental Wisp
- Shadowhand Rift
- Devil Rift
- Spirit Rift
- Giant Demon Assault
- Ayato
- Dragon Balls

---

## Requirements

- Windows
- Python 3.12+
- Tesseract OCR

Python packages used include:

- customtkinter
- pytesseract
- pillow
- mss
- rapidfuzz
- requests
- pywin32

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Rintomato/Clover-Retribution-Event-Notifier.git
cd Clover-Retribution-Event-Notifier
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python main.py
```

---

## Usage

1. Launch the application.
2. Select the chat capture region.
3. (Optional) Enter a Discord webhook URL.
4. Choose which world events to monitor.
5. Press **Start**.
6. Keep the Roblox chat visible while playing.

When a supported event is detected, the notifier will:
- Play a notification sound.
- Send a Discord webhook message (if configured).

---

## Repository Structure

```
main.py          # Application entry point
gui.py           # User interface
detector.py      # Event detection logic
ocr.py           # OCR processing
selector.py      # Region selector
notifier.py      # Discord webhook notifications
config.json      # User configuration (generated locally)
alert.WAV        # Notification sound
```

---

## Notes

- `config.json` is intentionally excluded from the repository because it contains personal settings such as webhook URLs.
- Build files, cache files, and other generated files are excluded through `.gitignore`.

---

## Disclaimer

This project is an independent fan-made utility and is not affiliated with, endorsed by, or sponsored by Roblox or the developers of Clover Retribution.

Use at your own discretion and ensure your use complies with the game's rules and Roblox's Terms of Use.

## Support

This project is completely free to use. If you find it helpful and would like to support its development, you can buy me a coffee on Ko-fi!

https://ko-fi.com/r1nkashime
