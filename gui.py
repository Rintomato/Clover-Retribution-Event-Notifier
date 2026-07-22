"""
Event Notifier — GUI
=====================
CustomTkinter front-end for the Clover Retribution Event Notifier.

Wires up your existing backend modules:
    ocr.py       -> OCRReader     (PaddleOCR + mss screen capture)
    detector.py  -> EventDetector (fuzzy phrase matching + per-event cooldowns)
    notifier.py  -> Notifier      (sound + Discord webhook, incl. despawn edit)
    selector.py  -> AreaSelector  (modal drag-to-select capture region)

This file does NOT reimplement OCR/detection/notification logic — it just
calls into those modules and reflects what they do on screen.

config.json layout (created/maintained automatically by this file):
    {
      "left": int, "top": int, "width": int, "height": int,  # capture region
      "webhook_url": str,
      "server_name": str,
      "events": {<14 event group names>: bool},               # enable toggles
      "sound_enabled": bool,
      "discord_enabled": bool,
      "scan_interval": "1 second"
    }

NOTE ON selector.py: when you finish dragging a selection, AreaSelector saves
ONLY the region keys to config.json (this is how it already worked). To avoid
wiping out your webhook/events settings when that happens, this file re-merges
its full in-memory config and re-saves it immediately after every selection.

Event toggle names match exactly what notifier.py checks against (it groups
the individual Dragon Ball stages under "Dragon Balls" and the three colored
wisps under "Elemental Wisp") — so these are the 14 fixed groups from your
README, not a free-form/add-your-own list.
"""

import os
import json
import time
import queue
import threading
from datetime import datetime

import customtkinter as ctk
from tkinter import messagebox

from PIL import Image
from mss import mss

from ocr import OCRReader
from detector import EventDetector
from notifier import Notifier
from selector import AreaSelector


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# ---------------------------------------------------------------------------
# v2.0 shared style constants — used across every page for a consistent,
# modern look (rounded cards, consistent spacing/typography, hover states).
# Purely cosmetic; nothing here touches config/detection data or backend calls.
# ---------------------------------------------------------------------------
RADIUS_CARD = 14
RADIUS_BOX = 10
RADIUS_BTN = 8
BTN_HEIGHT = 36
CARD_FG = ("gray90", "gray15")
BOX_FG = ("gray85", "gray17")
MUTED = ("gray35", "gray65")
ACCENT_HOVER = ("gray75", "gray28")
PAGE_PAD = 22


def make_card(parent, **kwargs):
    """A rounded 'card' frame used to visually group related widgets."""
    kwargs.setdefault("corner_radius", RADIUS_CARD)
    kwargs.setdefault("fg_color", CARD_FG)
    return ctk.CTkFrame(parent, **kwargs)


def make_button(parent, **kwargs):
    """CTkButton with the shared rounded/hover styling, unless overridden."""
    kwargs.setdefault("corner_radius", RADIUS_BTN)
    kwargs.setdefault("height", BTN_HEIGHT)
    kwargs.setdefault("cursor", "hand2")
    kwargs.setdefault("hover_color", ACCENT_HOVER)
    return ctk.CTkButton(parent, **kwargs)


def make_back_button(parent, command):
    return make_button(
        parent, text="← Back", width=90, command=command,
        fg_color="transparent", border_width=1, border_color=MUTED,
        text_color=MUTED, hover_color=ACCENT_HOVER,
    )

APP_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(APP_DIR, "config.json")
DETECTIONS_PATH = os.path.join(APP_DIR, "detections.json")
EVENT_STATS_PATH = os.path.join(APP_DIR, "event_stats.csv")

# These 14 names match notifier.py's internal grouping exactly (dragon-ball
# stages roll up into "Dragon Balls", the 3 wisp colors roll up into
# "Elemental Wisp"). Toggling one of these here toggles the whole group.
EVENT_GROUPS = [
    "Bandit Lord",
    "Warlord",
    "Khamsin",
    "Desert Village Rumor",
    "Craftsman",
    "Corrupt Night",
    "Mana Wisp",
    "Elemental Wisp",
    "Shadowhand Rift",
    "Devil Rift",
    "Spirit Rift",
    "Giant Demon Assault",
    "Ayato",
    "Dragon Balls",
]

SCAN_INTERVAL_OPTIONS = ["0.5 second", "1 second", "2 seconds", "5 seconds"]

DEFAULT_CONFIG = {
    "left": None,
    "top": None,
    "width": None,
    "height": None,
    "webhook_url": "",
    "server_name": "",
    "events": {name: True for name in EVENT_GROUPS},
    "sound_enabled": True,
    "discord_enabled": True,
    "scan_interval": "1 second",
}


# --------------------------------------------------------------------------
# Config / helper functions
# --------------------------------------------------------------------------

def load_config():
    config = dict(DEFAULT_CONFIG)
    config["events"] = dict(DEFAULT_CONFIG["events"])
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            config.update(loaded)
            events = dict(DEFAULT_CONFIG["events"])
            events.update(loaded.get("events", {}))
            config["events"] = events
        except (json.JSONDecodeError, OSError):
            pass
    return config


def save_config(config):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except OSError as e:
        print(f"[config] failed to save: {e}")


def load_detections():
    if os.path.exists(DETECTIONS_PATH):
        try:
            with open(DETECTIONS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []
    return []


def save_detections(entries):
    try:
        with open(DETECTIONS_PATH, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2)
    except OSError as e:
        print(f"[detections] failed to save: {e}")


def has_region(config):
    return all(config.get(k) is not None for k in ("left", "top", "width", "height"))


def scan_interval_to_seconds(label):
    try:
        return float(label.split()[0])
    except (ValueError, IndexError):
        return 1.0


def format_timestamp():
    return datetime.now().strftime("%I:%M %p").lstrip("0")


# --------------------------------------------------------------------------
# Main application
# --------------------------------------------------------------------------

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🚨 Event Notifier")
        self.geometry("960x800")
        self.minsize(860, 720)

        self.config_data = load_config()
        self.detections = load_detections()

        # backend objects (cheap to construct except OCRReader, which lazy-loads)
        self.detector = EventDetector()
        self.notifier = Notifier()
        self.ocr_reader = None

        # runtime/session state
        self.is_running = False
        self.session_state = "Stopped" if has_region(self.config_data) else "Waiting for chat area..."
        self.session_detection_count = 0
        self.start_time = None
        self.last_runtime = 0

        self.stop_event = threading.Event()
        self.ocr_thread = None
        self.detection_queue = queue.Queue()

        self.freeze_var = ctk.BooleanVar(value=False)
        self.is_frozen = False
        self.freeze_var.trace_add("write", self._on_freeze_changed)
        self.live_ctk_image = None

        # ---- container that holds every page ----
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for PageClass in (DashboardPage, GeneralPage, DiscordPage, LogsPage):
            page = PageClass(parent=container, controller=self)
            self.frames[PageClass.__name__] = page
            page.grid(row=0, column=0, sticky="nsew")

        self.show_frame("DashboardPage")

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.after(500, self.update_live_preview)
        self.after(200, self.process_detection_queue)
        self.after(1000, self.tick_runtime)

    # ---------------------------------------------------------- navigation
    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show()

    def on_close(self):
        self.stop_ocr()
        self.destroy()

    def _on_freeze_changed(self, *_args):
        self.is_frozen = self.freeze_var.get()

    # ---------------------------------------------------------- OCR region
    def select_area(self):
        selector = AreaSelector(parent=self)
        result = selector.run()
        if not result:
            return
        # selector.py just wrote {left, top, width, height} to config.json,
        # overwriting everything else. Re-merge and re-save the full config
        # so webhook/events/etc. survive.
        self.config_data.update(result)
        save_config(self.config_data)

        if self.session_state == "Waiting for chat area...":
            self.session_state = "Stopped"
        self.frames["DashboardPage"].on_region_selected()

    # ---------------------------------------------------------- OCR control
    def start_ocr(self):
        if not has_region(self.config_data):
            messagebox.showwarning("No region selected", "Please select a chat area first.")
            return
        if self.is_running or (self.ocr_thread and self.ocr_thread.is_alive()):
            return

        self.is_running = True
        self.stop_event.clear()
        self.session_detection_count = 0
        self.start_time = time.time()
        self.session_state = "Loading OCR engine..." if self.ocr_reader is None else "Monitoring"
        self.frames["DashboardPage"].refresh_session()

        self.ocr_thread = threading.Thread(target=self._ocr_loop, daemon=True)
        self.ocr_thread.start()

    def stop_ocr(self):
        if not self.is_running:
            return
        self.stop_event.set()
        self.is_running = False
        if self.start_time:
            self.last_runtime = int(time.time() - self.start_time)
        self.start_time = None
        self.session_state = "Stopped"
        self.detector.reset_cooldowns()
        self.frames["DashboardPage"].refresh_session()

        if self.ocr_thread and self.ocr_thread.is_alive():
            self.ocr_thread.join(timeout=2)

    def _ocr_loop(self):
        """Background thread: load PaddleOCR (once), then loop read -> detect -> notify."""
        if self.ocr_reader is None:
            try:
                self.ocr_reader = OCRReader()
            except Exception as e:
                self.detection_queue.put({"_error": f"Failed to load OCR engine:\n{e}"})
                self.is_running = False
                return
            self.session_state = "Monitoring"
            self.detection_queue.put({"_session_state": "Monitoring"})

        while not self.stop_event.is_set():
            interval = scan_interval_to_seconds(self.config_data.get("scan_interval", "1 second"))
            try:
                text, _debug_lines = self.ocr_reader.read_chat()
            except Exception as e:
                print(f"[ocr] read_chat failed: {e}")
                if self.stop_event.wait(interval):
                    break
                continue

            if not self.is_frozen:
                self.detection_queue.put({"_live_text": text})

            result = self.detector.check(text)
            if result:
                event_name, score = result
                server_name = self.config_data.get("server_name", "")

                try:
                    self.notifier.notify(event_name, score, server_name)
                except Exception as e:
                    print(f"[notifier] notify failed: {e}")

                self.detection_queue.put({
                    "event": event_name,
                    "confidence": score,
                    "timestamp": format_timestamp(),
                    "server": server_name,
                })

            if self.stop_event.wait(interval):
                break

    # ---------------------------------------------------------- detections
    def process_detection_queue(self):
        try:
            while True:
                item = self.detection_queue.get_nowait()
                if "_error" in item:
                    self.is_running = False
                    self.session_state = "Stopped"
                    self.frames["DashboardPage"].refresh_session()
                    messagebox.showerror("OCR engine error", item["_error"])
                elif "_session_state" in item:
                    self.session_state = item["_session_state"]
                    self.frames["DashboardPage"].refresh_session()
                elif "_live_text" in item:
                    self.frames["DashboardPage"].set_live_text(item["_live_text"])
                else:
                    self._handle_detection(item)
        except queue.Empty:
            pass
        self.after(200, self.process_detection_queue)

    def _handle_detection(self, detection):
        """Update the UI/log for a detection. Notifying (sound/Discord) already
        happened in the OCR loop via notifier.notify() — this just reflects it."""
        self.session_detection_count += 1
        self.detections.append(detection)
        save_detections(self.detections)

        self.frames["DashboardPage"].show_last_detection(detection)
        self.frames["DashboardPage"].refresh_session()
        self.frames["LogsPage"].append_log_line(detection)

    def test_notification(self):
        server_name = self.config_data.get("server_name", "")
        detection = {
            "event": "Test Event",
            "confidence": 100.0,
            "timestamp": format_timestamp(),
            "server": server_name,
        }

        def _fire():
            try:
                self.notifier.notify("Test Event", 100.0, server_name)
            except Exception as e:
                print(f"[notifier] test notify failed: {e}")

        threading.Thread(target=_fire, daemon=True).start()
        self._handle_detection(detection)

    # ---------------------------------------------------------- live preview
    def update_live_preview(self):
        dashboard = self.frames["DashboardPage"]
        cfg = self.config_data

        if has_region(cfg) and not self.is_frozen:
            try:
                region = {"left": cfg["left"], "top": cfg["top"], "width": cfg["width"], "height": cfg["height"]}
                with mss() as sct:
                    shot = sct.grab(region)
                image = Image.frombytes("RGB", shot.size, shot.rgb)
                box_w, box_h = dashboard.live_box_size()
                display_image = image.copy()
                display_image.thumbnail((box_w, box_h))
                self.live_ctk_image = ctk.CTkImage(
                    light_image=display_image, dark_image=display_image,
                    size=display_image.size,
                )
                dashboard.set_live_image(self.live_ctk_image)
            except Exception:
                pass
        elif not has_region(cfg):
            dashboard.set_live_placeholder("No region selected")

        self.after(500, self.update_live_preview)

    def tick_runtime(self):
        if self.is_running and self.start_time:
            self.frames["DashboardPage"].refresh_session()
        self.after(1000, self.tick_runtime)

    # ---------------------------------------------------------- settings helpers
    def update_config(self, key, value):
        self.config_data[key] = value
        save_config(self.config_data)

    def set_event_enabled(self, name, enabled):
        self.config_data["events"][name] = enabled
        save_config(self.config_data)

    # ---------------------------------------------------------- logs helpers
    def clear_logs(self):
        if not messagebox.askyesno("Clear logs", "Delete all detection history? This cannot be undone."):
            return
        self.detections = []
        save_detections(self.detections)
        self.session_detection_count = 0
        self.frames["LogsPage"].refresh_log_view()
        self.frames["DashboardPage"].refresh_session()

    def export_txt(self):
        if not self.detections:
            messagebox.showinfo("Export TXT", "No detections to export yet.")
            return
        path = os.path.join(APP_DIR, f"detections_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(path, "w", encoding="utf-8") as f:
            for d in self.detections:
                f.write(LogsPage.format_line(d) + "\n")
        messagebox.showinfo("Export TXT", f"Saved to:\n{path}")

    def export_csv(self):
        if not self.detections:
            messagebox.showinfo("Export CSV", "No detections to export yet.")
            return
        import csv
        path = os.path.join(APP_DIR, f"detections_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Event", "Confidence", "Server"])
            for d in self.detections:
                writer.writerow([d["timestamp"], d["event"], f"{d['confidence']:.1f}", d.get("server", "")])
        messagebox.showinfo("Export CSV", f"Saved to:\n{path}")

    def show_event_stats(self):
        if not self.detections:
            messagebox.showinfo("Event Stats", "No detections yet.")
            return
        counts = {}
        for d in self.detections:
            counts[d["event"]] = counts.get(d["event"], 0) + 1
        ordered = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)

        # keep event_stats.csv (Event,Count) up to date, matching your existing file format
        import csv
        with open(EVENT_STATS_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Event", "Count"])
            for name, count in ordered:
                writer.writerow([name, count])

        win = ctk.CTkToplevel(self)
        win.title("Event Stats")
        win.geometry("320x420")
        win.minsize(280, 300)
        ctk.CTkLabel(win, text="Detections by Event", font=ctk.CTkFont(size=15, weight="bold")).pack(pady=14)
        listframe = ctk.CTkScrollableFrame(win, corner_radius=RADIUS_CARD, fg_color=CARD_FG)
        listframe.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        for name, count in ordered:
            row = ctk.CTkFrame(listframe, fg_color="transparent")
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=name).pack(side="left")
            ctk.CTkLabel(row, text=str(count), font=ctk.CTkFont(weight="bold")).pack(side="right")


# --------------------------------------------------------------------------
# Dashboard (Home) page
# --------------------------------------------------------------------------

class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        pad = {"padx": PAGE_PAD}

        ctk.CTkLabel(self, text="🚨 Event Notifier", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(20, 14))

        # ---- Session / Last Detection panel ----
        panel = ctk.CTkFrame(self, fg_color="transparent")
        panel.pack(fill="x", **pad, pady=(0, 16))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_columnconfigure(1, weight=1)

        session_box = make_card(panel)
        session_box.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ctk.CTkLabel(session_box, text="Session", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=16, pady=(14, 6))
        self.session_state_label = ctk.CTkLabel(session_box, text="Waiting for chat area...")
        self.session_state_label.pack(anchor="w", padx=16)
        self.detections_label = ctk.CTkLabel(session_box, text="Detections: 0", text_color=MUTED)
        self.detections_label.pack(anchor="w", padx=16, pady=(8, 0))
        self.runtime_label = ctk.CTkLabel(session_box, text="Runtime: 0s", text_color=MUTED)
        self.runtime_label.pack(anchor="w", padx=16, pady=(0, 14))

        detection_box = make_card(panel)
        detection_box.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        ctk.CTkLabel(detection_box, text="Last Detection", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=16, pady=(14, 6))
        self.last_detection_label = ctk.CTkLabel(detection_box, text="None yet")
        self.last_detection_label.pack(anchor="w", padx=16)
        self.last_confidence_label = ctk.CTkLabel(detection_box, text="", text_color=MUTED)
        self.last_confidence_label.pack(anchor="w", padx=16)
        self.last_time_label = ctk.CTkLabel(detection_box, text="", text_color=MUTED)
        self.last_time_label.pack(anchor="w", padx=16)
        self.last_server_label = ctk.CTkLabel(detection_box, text="", text_color=MUTED)
        self.last_server_label.pack(anchor="w", padx=16, pady=(0, 14))

        # ---- OCR Region ----
        ctk.CTkLabel(self, text="OCR Region", font=ctk.CTkFont(weight="bold")).pack(anchor="w", **pad)
        region_row = ctk.CTkFrame(self, fg_color="transparent")
        region_row.pack(fill="x", **pad, pady=(6, 16))
        make_button(region_row, text="🖱 Select Chat Area", command=controller.select_area, width=170).pack(side="left")
        self.region_status_label = ctk.CTkLabel(region_row, text="", text_color=MUTED)
        self.region_status_label.pack(side="left", padx=12)

        # ---- Controls ----
        ctk.CTkLabel(self, text="Controls", font=ctk.CTkFont(weight="bold")).pack(anchor="w", **pad)
        controls_row = ctk.CTkFrame(self, fg_color="transparent")
        controls_row.pack(fill="x", **pad, pady=(6, 16))
        make_button(controls_row, text="▶ Start", command=controller.start_ocr, width=110).pack(side="left")
        make_button(controls_row, text="■ Stop", command=controller.stop_ocr, width=110,
                    fg_color="#8a2020", hover_color="#a52a2a").pack(side="left", padx=8)
        make_button(controls_row, text="🔔 Test Notification", command=controller.test_notification, width=180).pack(side="left")

        # ---- Live OCR ----
        live_header = ctk.CTkFrame(self, fg_color="transparent")
        live_header.pack(fill="x", **pad)
        ctk.CTkLabel(live_header, text="Live OCR", font=ctk.CTkFont(weight="bold")).pack(side="left")
        ctk.CTkCheckBox(live_header, text="Freeze OCR", variable=controller.freeze_var,
                        cursor="hand2").pack(side="left", padx=12)

        live_panel = ctk.CTkFrame(self, fg_color="transparent")
        live_panel.pack(fill="both", expand=True, **pad, pady=(6, 16))
        live_panel.grid_columnconfigure(0, weight=1)
        live_panel.grid_columnconfigure(1, weight=1)
        live_panel.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(live_panel, text="OCR PREVIEW", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=MUTED).grid(row=0, column=0, sticky="w", padx=(0, 8), pady=(0, 6))
        ctk.CTkLabel(live_panel, text="OCR TEXT", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=MUTED).grid(row=0, column=1, sticky="w", padx=(8, 0), pady=(0, 6))

        self.live_box = ctk.CTkLabel(live_panel, text="No region selected",
                                      fg_color=BOX_FG, corner_radius=RADIUS_BOX)
        self.live_box.grid(row=1, column=0, sticky="nsew", padx=(0, 8))

        self.live_text_box = ctk.CTkTextbox(live_panel, wrap="word", state="disabled",
                                             fg_color=BOX_FG, corner_radius=RADIUS_BOX)
        self.live_text_box.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
        self._set_live_text_content("No region selected")

        # ---- Settings nav ----
        sep = ctk.CTkFrame(self, height=1, fg_color=("gray70", "gray30"))
        sep.pack(fill="x", **pad, pady=(0, 10))
        ctk.CTkLabel(self, text="Settings", font=ctk.CTkFont(weight="bold")).pack(anchor="w", **pad)
        nav_row = ctk.CTkFrame(self, fg_color="transparent")
        nav_row.pack(fill="x", **pad, pady=(6, 20))
        make_button(nav_row, text="⚙ General", command=lambda: controller.show_frame("GeneralPage"), width=115).pack(side="left")
        make_button(nav_row, text="🌐 Discord", command=lambda: controller.show_frame("DiscordPage"), width=115).pack(side="left", padx=8)
        make_button(nav_row, text="📄 Logs", command=lambda: controller.show_frame("LogsPage"), width=115).pack(side="left")

        if controller.detections:
            self.show_last_detection(controller.detections[-1])

    def on_show(self):
        self.on_region_selected()

    def on_region_selected(self):
        cfg = self.controller.config_data
        if has_region(cfg):
            self.region_status_label.configure(
                text=f"Region: {cfg['left']},{cfg['top']} ({cfg['width']}x{cfg['height']})"
            )
            if not self.controller.is_running:
                self._set_live_text_content("Press Start to begin scanning...")
        else:
            self.region_status_label.configure(text="")
        self.refresh_session()

    def refresh_session(self):
        self.session_state_label.configure(text=self.controller.session_state)
        self.detections_label.configure(text=f"Detections: {self.controller.session_detection_count}")
        if self.controller.is_running and self.controller.start_time:
            runtime = int(time.time() - self.controller.start_time)
        else:
            runtime = self.controller.last_runtime
        self.runtime_label.configure(text=f"Runtime: {runtime}s")

    def show_last_detection(self, detection):
        self.last_detection_label.configure(text=detection["event"])
        self.last_confidence_label.configure(text=f"{detection['confidence']:.1f}% Confidence")
        self.last_time_label.configure(text=detection["timestamp"])
        if detection.get("server"):
            self.last_server_label.configure(text=f"Server: {detection['server']}")
        else:
            self.last_server_label.configure(text="")

    def live_box_size(self):
        w = max(self.live_box.winfo_width(), 400)
        h = max(self.live_box.winfo_height(), 150)
        return w, h

    def set_live_image(self, ctk_image):
        self.live_box.configure(image=ctk_image, text="")

    def set_live_placeholder(self, text):
        self.live_box.configure(image=None, text=text)
        self._set_live_text_content(text)

    def set_live_text(self, text):
        self._set_live_text_content(text if text.strip() else "(no text detected)")

    def _set_live_text_content(self, text):
        self.live_text_box.configure(state="normal")
        self.live_text_box.delete("1.0", "end")
        self.live_text_box.insert("1.0", text)
        self.live_text_box.configure(state="disabled")


# --------------------------------------------------------------------------
# General settings page
# --------------------------------------------------------------------------

class GeneralPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.event_vars = {}
        pad = {"padx": PAGE_PAD}

        back_row = ctk.CTkFrame(self, fg_color="transparent")
        back_row.pack(fill="x", **pad, pady=(18, 0))
        make_back_button(back_row, command=lambda: controller.show_frame("DashboardPage")).pack(side="left")

        ctk.CTkLabel(self, text="⚙ General Settings", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", **pad, pady=(12, 16))

        ctk.CTkLabel(self, text="EVENT DETECTION", font=ctk.CTkFont(size=11, weight="bold"), text_color=MUTED).pack(anchor="w", **pad)
        self.event_scroll = ctk.CTkScrollableFrame(self, height=190, label_text="", corner_radius=RADIUS_CARD, fg_color=CARD_FG)
        self.event_scroll.pack(fill="x", **pad, pady=(6, 18))

        for name in EVENT_GROUPS:
            var = ctk.BooleanVar(value=True)
            self.event_vars[name] = var
            ctk.CTkCheckBox(
                self.event_scroll, text=name, variable=var, cursor="hand2",
                command=lambda n=name, v=var: controller.set_event_enabled(n, v.get()),
            ).pack(anchor="w", pady=4, padx=10)

        ctk.CTkLabel(self, text="NOTIFICATIONS", font=ctk.CTkFont(size=11, weight="bold"), text_color=MUTED).pack(anchor="w", **pad)
        notif_frame = make_card(self)
        notif_frame.pack(fill="x", **pad, pady=(6, 18))
        self.discord_var = ctk.BooleanVar()
        self.sound_var = ctk.BooleanVar()
        ctk.CTkSwitch(
            notif_frame, text="Discord Notifications", variable=self.discord_var, cursor="hand2",
            command=lambda: controller.update_config("discord_enabled", self.discord_var.get()),
        ).pack(anchor="w", pady=(14, 6), padx=16)
        ctk.CTkSwitch(
            notif_frame, text="Sound Notifications", variable=self.sound_var, cursor="hand2",
            command=lambda: controller.update_config("sound_enabled", self.sound_var.get()),
        ).pack(anchor="w", pady=(0, 14), padx=16)

        ctk.CTkLabel(self, text="SCANNING", font=ctk.CTkFont(size=11, weight="bold"), text_color=MUTED).pack(anchor="w", **pad)
        interval_row = make_card(self)
        interval_row.pack(fill="x", **pad, pady=(6, 18))
        ctk.CTkLabel(interval_row, text="Scan Interval").pack(side="left", padx=(16, 8), pady=14)
        self.interval_var = ctk.StringVar()
        self.interval_combo = ctk.CTkComboBox(
            interval_row, variable=self.interval_var, values=SCAN_INTERVAL_OPTIONS, width=150,
            corner_radius=RADIUS_BTN, button_hover_color=ACCENT_HOVER,
            command=lambda choice: controller.update_config("scan_interval", choice),
        )
        self.interval_combo.pack(side="left", pady=14)

    def on_show(self):
        cfg = self.controller.config_data
        self.discord_var.set(cfg.get("discord_enabled", True))
        self.sound_var.set(cfg.get("sound_enabled", True))
        self.interval_var.set(cfg.get("scan_interval", "1 second"))
        for name, var in self.event_vars.items():
            var.set(cfg.get("events", {}).get(name, True))


# --------------------------------------------------------------------------
# Discord settings page
# --------------------------------------------------------------------------

class DiscordPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self._save_job = None
        pad = {"padx": PAGE_PAD}

        back_row = ctk.CTkFrame(self, fg_color="transparent")
        back_row.pack(fill="x", **pad, pady=(18, 0))
        make_back_button(back_row, command=lambda: controller.show_frame("DashboardPage")).pack(side="left")

        ctk.CTkLabel(self, text="🌐 Discord Settings", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", **pad, pady=(12, 18))

        card = make_card(self)
        card.pack(fill="x", **pad)

        ctk.CTkLabel(card, text="Webhook URL").pack(anchor="w", padx=16, pady=(16, 4))
        self.webhook_entry = ctk.CTkEntry(card, corner_radius=RADIUS_BTN)
        self.webhook_entry.pack(fill="x", padx=16, pady=(0, 14))
        self.webhook_entry.bind("<KeyRelease>", self.schedule_save)

        ctk.CTkLabel(card, text="Server Name (Optional)").pack(anchor="w", padx=16, pady=(0, 4))
        self.server_entry = ctk.CTkEntry(card, corner_radius=RADIUS_BTN)
        self.server_entry.pack(fill="x", padx=16, pady=(0, 14))
        self.server_entry.bind("<KeyRelease>", self.schedule_save)

        ctk.CTkLabel(card, text="✓ Changes save automatically", text_color="#4caf50").pack(anchor="w", padx=16, pady=(0, 16))

    def on_show(self):
        cfg = self.controller.config_data
        self.webhook_entry.delete(0, "end")
        self.webhook_entry.insert(0, cfg.get("webhook_url", ""))
        self.server_entry.delete(0, "end")
        self.server_entry.insert(0, cfg.get("server_name", ""))

    def schedule_save(self, event=None):
        if self._save_job:
            self.after_cancel(self._save_job)
        self._save_job = self.after(400, self.save_now)

    def save_now(self):
        self.controller.update_config("webhook_url", self.webhook_entry.get().strip())
        self.controller.update_config("server_name", self.server_entry.get().strip())


# --------------------------------------------------------------------------
# Logs page
# --------------------------------------------------------------------------

class LogsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        pad = {"padx": PAGE_PAD}

        back_row = ctk.CTkFrame(self, fg_color="transparent")
        back_row.pack(fill="x", **pad, pady=(18, 0))
        make_back_button(back_row, command=lambda: controller.show_frame("DashboardPage")).pack(side="left")

        ctk.CTkLabel(self, text="📄 Detection Logs", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", **pad, pady=(12, 16))

        self.log_text = ctk.CTkTextbox(self, wrap="word", state="disabled",
                                        fg_color=BOX_FG, corner_radius=RADIUS_BOX)
        self.log_text.pack(fill="both", expand=True, **pad, pady=(0, 12))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", **pad, pady=(0, 18))
        make_button(btn_row, text="Clear", width=90, command=controller.clear_logs,
                    fg_color="#8a2020", hover_color="#a52a2a").pack(side="left")
        make_button(btn_row, text="Export TXT", width=100, command=controller.export_txt).pack(side="left", padx=8)
        make_button(btn_row, text="Export CSV", width=100, command=controller.export_csv).pack(side="left")
        make_button(btn_row, text="Event Stats", width=100, command=controller.show_event_stats).pack(side="left", padx=8)

    def on_show(self):
        self.refresh_log_view()

    def refresh_log_view(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        for d in self.controller.detections:
            self.log_text.insert("end", self.format_line(d) + "\n")
        self.log_text.configure(state="disabled")
        self.log_text.see("end")

    def append_log_line(self, detection):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", self.format_line(detection) + "\n")
        self.log_text.configure(state="disabled")
        self.log_text.see("end")

    @staticmethod
    def format_line(d):
        line = f"{d['timestamp']} - {d['event']} ({d['confidence']:.1f}%)"
        if d.get("server"):
            line += f" [Server: {d['server']}]"
        return line


# --------------------------------------------------------------------------
# Standalone entry point (main.py is the normal way to run this)
# --------------------------------------------------------------------------

if __name__ == "__main__":
    app = App()
    app.mainloop()
