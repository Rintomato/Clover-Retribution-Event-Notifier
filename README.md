# C.R.E.N. — Clover Retribution Event Notifier

**C.R.E.N.** is a free desktop event notifier for **Roblox Clover Retribution** that monitors your in-game chat using OCR and alerts you when supported world events appear.

Get notified through desktop sounds and optional Discord webhook notifications without constantly watching the in-game chat.

> C.R.E.N. is a monitoring utility only. It does not interact with the Roblox client or automate gameplay.

---

## ✨ Features

### 🔍 Automatic Event Detection

C.R.E.N. continuously reads your selected in-game chat area and detects supported Clover Retribution event announcements.

- Powered by **RapidOCR + ONNX Runtime**
- Uses PP-OCR models for text recognition
- Select your own chat capture region
- Enable or disable individual events
- Adjustable scan interval
- Per-event cooldowns to prevent duplicate notifications

### 👁️ Live OCR

See exactly what C.R.E.N. is reading while it runs.

- Live preview of the selected chat region
- Live scrollable recognized text
- Preview and OCR text displayed side-by-side
- **Freeze OCR** pauses both the preview and recognized text

### 🔔 Notifications

Choose how you want to be notified when an event appears.

- Desktop sound alerts
- Optional Discord webhook notifications
- Sound and Discord notifications can be enabled independently
- Optional server information in Discord alerts
- Built-in **Test Notification** button
- Discord event notifications automatically update to **Despawned** after 5 minutes while C.R.E.N. remains running

### 📊 Session Monitoring

The dashboard gives you a quick overview of your current session:

- Monitoring status
- Session runtime
- Total detections
- Last detected event
- Detection confidence
- Detection time
- Optional server information

### 📄 Logs & Statistics

Keep track of events you've detected.

- Detection history
- Event timestamps
- Detection confidence
- Per-event statistics
- Clear detection history
- Export logs to TXT or CSV

### 🎨 Modern Interface

- CustomTkinter interface
- Dashboard-focused home screen
- Dedicated **General**, **Discord**, and **Logs** pages
- Organized settings and controls
- Automatic settings saving
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
- Blessed Sphere

---

## 📥 Download & Installation

The recommended way to install C.R.E.N. is through the **GitHub Releases** page:

https://github.com/Rintomato/Clover-Retribution-Event-Notifier/releases

1. Open the latest release.
2. Download the latest C.R.E.N. Windows build.
3. Extract the downloaded ZIP file.
4. Open the extracted **CREN** folder.
5. Run **CREN.exe**.

That's it — **Python and a separate OCR installation are not required** when using the packaged release.

> Windows may display a security warning because C.R.E.N. is not digitally signed. Only download builds from this project's official GitHub repository.

---

## 🚀 How to Use

1. Launch **C.R.E.N.**
2. Click **Select Chat Area**.
3. Select the part of your screen containing the Clover Retribution chat.
4. Open **General** and choose which events you want to monitor.
5. Enable sound and/or Discord notifications.
6. If using Discord, enter your webhook URL under **Discord**.
7. Optionally enter your server information.
8. Press **Start**.

Keep the selected chat area visible while C.R.E.N. is monitoring.

When a supported event is detected, C.R.E.N. can:

- 🔔 Play a notification sound
- 📢 Send a Discord notification
- 📄 Add the event to your detection history
- 📊 Update your session statistics

Press **Stop** whenever you want to stop monitoring.

---

## 🌐 Discord Notifications

To receive event alerts through Discord:

1. Create a webhook in the Discord channel where you want notifications.
2. Copy the webhook URL.
3. Open the **Discord** page in C.R.E.N.
4. Paste your webhook URL.
5. Enable Discord notifications.
6. Use **Test Notification** to make sure everything is working.

Your webhook URL is stored locally in your configuration file.

> Never share your `config.json` file publicly if it contains your Discord webhook URL.

---

# 🆕 What's New in v2.0.0

**C.R.E.N. v2.0.0** is a major overhaul focused on making the notifier feel like a complete desktop application.

### 🔍 New OCR System

- Replaced the previous EasyOCR engine
- Now uses **RapidOCR + ONNX Runtime**
- Uses lightweight PP-OCR models for Clover Retribution chat recognition
- Significantly reduced the packaged application's size compared with the earlier PaddleOCR-based v2 builds

### 👁️ Improved Live OCR

- Added live capture-region preview
- Added live scrollable OCR text
- Preview and recognized text are displayed side-by-side
- Fixed **Freeze OCR** so both panels freeze together

### ⏯️ Better Session Controls

- **Stop** now stops monitoring immediately
- Prevents duplicate OCR monitoring threads
- Detection cooldowns reset when monitoring stops
- Improved Start/Stop reliability between sessions

### 🎨 Complete Interface Redesign

- Completely redesigned CustomTkinter interface
- New dashboard
- Dedicated **General**, **Discord**, and **Logs** pages
- Redesigned settings sections and controls
- Improved spacing, typography, and window sizing
- Restyled event statistics
- Settings save automatically

### 📄 Improved Logs & Statistics

- Improved detection history
- Per-event statistics
- TXT and CSV log exporting
- Clear detection-history controls

### 🔔 Improved Notifications

- Desktop sound notifications
- Discord webhook alerts
- Optional server information
- Built-in notification testing
- Discord event messages update to **Despawned** after 5 minutes while the application remains running

### ⚡ Performance & Packaging

- Migrated from the heavyweight PaddlePaddle runtime to **RapidOCR + ONNX Runtime**
- Uses only the required English OCR models
- Removed unused OCR and machine-learning dependencies
- Reduced the packaged application footprint by roughly **75%** compared with the v1.0.1 build

---

## 📁 Repository Structure

```text
main.py          # Application entry point
gui.py           # CustomTkinter interface
detector.py      # Event detection and fuzzy matching
ocr.py           # RapidOCR / ONNX Runtime processing
selector.py      # Chat region selector
notifier.py      # Sound and Discord notifications
alert.WAV        # Default notification sound
main.spec        # PyInstaller build configuration
```

Runtime files such as `config.json`, detection history, and statistics are generated locally and are not included in the repository.

---

## 🔊 Custom Notification Sound

You can replace the default notification sound with your own `.WAV` file.

Replace:

```text
alert.WAV
```

with another WAV file using the **same filename**.

---

## 📝 Tips

For the best detection results:

- Keep the selected chat area visible and unobstructed.
- Make sure the entire event announcement can appear inside the selected region.
- Avoid selecting unnecessary parts of the screen.
- Use **Live OCR** to check what C.R.E.N. can currently read.
- If events aren't being recognized properly, try selecting the chat area again.

OCR accuracy can vary depending on text size, visibility, resolution, and other elements covering the chat.

---

## ⚠️ Disclaimer

C.R.E.N. is an independent fan-made utility and is not affiliated with, endorsed by, or sponsored by **Roblox** or the developers of **Clover Retribution**.

Use C.R.E.N. at your own discretion and ensure that your use complies with the game's rules and Roblox's Terms of Use.

---

## ❤️ Support

**C.R.E.N. is completely free to use.**

If you find the project useful and would like to support its development, you can buy me a coffee on Ko-fi:

https://ko-fi.com/r1nkashime
