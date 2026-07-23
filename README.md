# Clover Retribution Event Notifier

A desktop event notifier for **Roblox Clover Retribution** that monitors in-game chat using OCR and alerts you when supported world events appear.

Get notified through desktop sounds and optional Discord webhook notifications without having to constantly watch the in-game chat.

> This project is intended for convenience and monitoring only. It does not interact with the Roblox client or automate gameplay.

---

## ✨ Features

### 🔍 Event Detection

- Powered by **PaddleOCR**
- Automatically detects supported Clover Retribution world event announcements
- Select your own in-game chat capture region
- Enable or disable individual events
- Adjustable scan interval
- Built-in per-event cooldowns to prevent duplicate notifications

### 👁️ Live OCR

See exactly what the notifier is reading while it runs.

- Live preview of the selected chat region
- Live scrollable OCR text
- Preview and recognized text displayed side-by-side
- **Freeze OCR** to pause both the preview and text

### 🔔 Notifications

- Desktop sound notifications
- Optional Discord webhook notifications
- Enable sound and Discord notifications independently
- Optional server information in Discord notifications
- Built-in **Test Notification** button

### 📊 Session Monitoring

The dashboard keeps track of:

- Current monitoring status
- Session runtime
- Total detections
- Last detected event
- Detection confidence
- Detection time
- Optional server information

### 📄 Logs & Statistics

- Detection history
- Detection timestamps
- Confidence values
- Per-event statistics
- Clear detection history
- Export logs to TXT or CSV

### 🎨 Modern Interface

- Redesigned CustomTkinter interface
- Dashboard-focused main screen
- Dedicated **General**, **Discord**, and **Logs** pages
- Organized Event Detection, Notification, and Scanning settings
- Settings save automatically
- Modern card-based design

---

## 🎯 Supported Events

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

## 📥 Installation

The easiest way to install Clover Retribution Event Notifier is through the **GitHub Releases** page.

1. Open the latest release. (https://github.com/Rintomato/Clover-Retribution-Event-Notifier/releases)
2. Download the latest Windows build.
3. Extract the downloaded archive if necessary.
4. Run the Event Notifier application.

No separate Python or OCR installation is required when using the packaged release.

> Windows may display a security warning when running an unsigned application downloaded from the internet. Only download releases from this project's official GitHub repository.

---

## 🚀 Usage

1. Launch **Clover Retribution Event Notifier**.
2. Click **Select Chat Area**.
3. Select the area of your screen containing the Clover Retribution chat.
4. Open **General Settings** and choose the events you want to monitor.
5. Enable sound and/or Discord notifications.
6. If using Discord, enter your webhook URL under **Discord Settings**.
7. Optionally enter your server information.
8. Press **Start**.

Keep the selected chat region visible while monitoring.

When a supported event is detected, the notifier can:

- 🔔 Play a notification sound
- 📢 Send a Discord webhook notification
- 📄 Record the detection in the log
- 📊 Update your session statistics

Press **Stop** whenever you want to stop monitoring.

---

# 🆕 What's New in v2.0.0

**v2.0.0** is a major overhaul of Clover Retribution Event Notifier, featuring a new OCR engine, completely redesigned interface, improved live monitoring, and more reliable session controls.

### 🔍 PaddleOCR

- Replaced **EasyOCR** with **PaddleOCR**
- Updated the OCR processing system
- Improved the foundation for recognizing Clover Retribution chat text

### 👁️ Improved Live OCR

- Added a live preview of the selected capture region
- Added live scrollable OCR text
- Preview and recognized text are now displayed side-by-side
- Fixed **Freeze OCR** so both the preview and OCR text freeze together

### ⏯️ Better Session Controls

- **Stop** now stops monitoring immediately instead of waiting for the current scan interval
- Prevents multiple OCR monitoring threads from accidentally running at the same time
- Detection cooldowns reset when monitoring is stopped
- Starting a new session no longer risks suppressing an event detected near the end of the previous session

### 🎨 Complete GUI Redesign

- Completely redesigned the CustomTkinter interface
- New dashboard-focused home screen
- Dedicated **General**, **Discord**, and **Logs** pages
- Rounded card-based design
- Consistent buttons and hover states
- Improved spacing and typography
- Better organized settings sections:
  - Event Detection
  - Notifications
  - Scanning
- Restyled Event Statistics window
- Improved window sizing to prevent content from being cut off

### ⚙️ Settings Improvements

- Settings now save automatically
- Removed the unnecessary Discord webhook Save button
- Added optional server information
- Cleaner and more organized configuration pages

### 📄 Logs & Statistics

- Improved detection history presentation
- Added easier access to per-event statistics
- Detection logs can be exported to TXT or CSV

### 🛠️ Reliability Improvements

- Improved OCR thread handling
- Fixed Freeze OCR thread-safety behavior
- Improved Start/Stop behavior
- Prevented duplicate monitoring sessions
- Improved detection cooldown handling

---

## 📁 Repository Structure

```text
main.py          # Application entry point
gui.py           # CustomTkinter user interface
detector.py      # Event detection and matching logic
ocr.py           # PaddleOCR processing
selector.py      # Screen region selector
notifier.py      # Sound and Discord notifications
config.json      # Local user configuration
alert.WAV        # Notification sound (Can replace sound with another .WAV file with alert as the name)
```

---

## 📝 Notes

- Keep the selected chat region visible and unobstructed while monitoring.
- OCR accuracy can depend on the size, visibility, and quality of the captured chat text.
- Discord notifications require a valid Discord webhook URL.
- `config.json` may contain personal settings such as your Discord webhook URL and should not be shared publicly.

---

## ⚠️ Disclaimer

This project is an independent fan-made utility and is not affiliated with, endorsed by, or sponsored by Roblox or the developers of Clover Retribution.

Use at your own discretion and ensure your use complies with the game's rules and Roblox's Terms of Use.

---

## ❤️ Support

Clover Retribution Event Notifier is completely free to use.

If you find it helpful and would like to support its development, you can buy me a coffee on Ko-fi:

https://ko-fi.com/r1nkashime
