import json
from pathlib import Path
import customtkinter as ctk
from selector import AreaSelector
from ocr import OCRReader
from detector import EventDetector
from notifier import Notifier


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")

        self.title("Event Notifier")
        self.geometry("760x650")
        self.resizable(False, False)

        self.ocr = None
        self.detector = EventDetector()
        self.notifier = Notifier()
        self.ocr_running = False

        self.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(self, text="🚨 Event Notifier", font=("Arial", 26, "bold"))
        title.grid(row=0, column=0, pady=(15, 10))

        self.status_label = ctk.CTkLabel(self, text="🔴 Waiting for chat area...", anchor="w",
                                         font=("Arial", 15, "bold"))
        self.status_label.grid(row=1, column=0, sticky="ew", padx=20)

        server_frame = ctk.CTkFrame(self)
        server_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(15,5))
        server_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(server_frame, text="Server",
                     font=("Arial",15,"bold")).grid(row=0,column=0,sticky="w",padx=10,pady=(10,5))
        self.server_entry = ctk.CTkEntry(server_frame, placeholder_text="Code")
        self.server_entry.grid(row=1,column=0,sticky="ew",padx=10,pady=(0,10))

        region_frame = ctk.CTkFrame(self)
        region_frame.grid(row=3,column=0,sticky="ew",padx=20,pady=5)
        ctk.CTkLabel(region_frame,text="OCR Region",
                     font=("Arial",15,"bold")).pack(anchor="w",padx=10,pady=(10,5))
        self.select_button = ctk.CTkButton(region_frame,text="Select Chat Area",
                                           command=self.select_area,
                                           fg_color="#2563eb")
        self.select_button.pack(anchor="w",padx=10,pady=(0,10))

        controls = ctk.CTkFrame(self)
        controls.grid(row=4,column=0,sticky="ew",padx=20,pady=5)
        ctk.CTkLabel(controls,text="Controls",
                     font=("Arial",15,"bold")).pack(anchor="w",padx=10,pady=(10,5))

        btns=ctk.CTkFrame(controls,fg_color="transparent")
        btns.pack(padx=10,pady=(0,10),fill="x")

        self.start_button=ctk.CTkButton(btns,text="▶ Start",
                                        command=self.start_ocr,
                                        state="disabled",
                                        fg_color="#16a34a")
        self.start_button.pack(side="left",padx=(0,10))

        self.stop_button=ctk.CTkButton(btns,text="■ Stop",
                                       command=self.stop_ocr,
                                       state="disabled",
                                       fg_color="#dc2626")
        self.stop_button.pack(side="left",padx=(0,10))

        self.test_button=ctk.CTkButton(
            btns,
            text="🔔 Test Notification",
            command=lambda: self.notifier.notify(
                "Test Event",
                100,
                self.server_entry.get().strip()
                ),                        
                                       fg_color="#7c3aed")
        self.test_button.pack(side="left")


        self.events_frame=ctk.CTkFrame(self)
        self.events_frame.grid(row=5,column=0,sticky="ew",padx=20,pady=5)

        self.events_expanded=False

        self.toggle_btn=ctk.CTkButton(
            self.events_frame,
            text="▶ World Events",
            command=self.toggle_events,
            fg_color="transparent",
            anchor="w"
        )
        self.toggle_btn.pack(fill="x",padx=10,pady=(10,5))

        self.scroll=ctk.CTkScrollableFrame(self.events_frame,height=180)

        self.event_vars={}
        for ev in [
            "Bandit Lord","Warlord","Khamsin","Desert Village Rumor","Craftsman",
            "Corrupt Night","Mana Wisp","Elemental Wisp","Shadowhand Rift",
            "Devil Rift","Spirit Rift","Giant Demon Assault","Ayato","Dragon Balls"
        ]:
            v=ctk.BooleanVar(value=True)
            self.event_vars[ev]=v
            ctk.CTkCheckBox(self.scroll, text=ev, variable=v, command=self.save_config).pack(anchor="w")

        webhook_frame = ctk.CTkFrame(self)
        webhook_frame.grid(row=6,column=0,sticky="ew",padx=20,pady=5)
        webhook_frame.grid_columnconfigure(0,weight=1)

        ctk.CTkLabel(webhook_frame,text="Discord Webhook",
                     font=("Arial",15,"bold")).grid(row=0,column=0,sticky="w",padx=10,pady=(10,5))
        self.webhook_entry=ctk.CTkEntry(webhook_frame,placeholder_text="Discord Webhook URL")
        self.webhook_entry.grid(row=1,column=0,sticky="ew",padx=10,pady=(0,10))
        self.save_button=ctk.CTkButton(webhook_frame,text="Save",
                                       command=self.save_config)
        self.save_button.grid(row=1,column=1,padx=10,pady=(0,10))
        self.load_config()



    def toggle_events(self):
        if self.events_expanded:
            self.scroll.pack_forget()
            self.toggle_btn.configure(text="▶ World Events")
        else:
            self.scroll.pack(fill="both", expand=True, padx=10, pady=(0,10))
            self.toggle_btn.configure(text="▼ World Events")

        self.events_expanded = not self.events_expanded

    def select_area(self):
        try:
            selector=AreaSelector(self)
            area=selector.run()
            if area:
                self.status_label.configure(text=f"🟡 Region Selected ({area['width']} x {area['height']})")
                self.start_button.configure(state="normal")
            else:
                self.status_label.configure(text="🔴 Selection cancelled.")
        except Exception as e:
            self.status_label.configure(text=f"❌ Error: {e}")

    def start_ocr(self):
        if self.ocr is None:
            self.status_label.configure(text="🟡 Loading OCR...")
            self.update()
            self.ocr=OCRReader()

        self.ocr_running=True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status_label.configure(text="🟢 Monitoring")
        self.update_ocr()

    def stop_ocr(self):
        self.ocr_running=False
        
        # Reset event cooldowns
        self.detector.reset_cooldowns()
        
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.status_label.configure(text="🔴 Stopped")

    def update_ocr(self):
        if not self.ocr_running:
            return

        try:
            text = self.ocr.read_chat()
            result = self.detector.check(text)

            if result:
                event_name, score = result
                self.notifier.notify(
                    event_name,
                    score,
                    self.server_entry.get().strip()
                )

        except Exception as e:
            print(e)

        self.after(1000, self.update_ocr)

    def load_config(self):
        config_path = Path("config.json")
        if not config_path.exists():
            return

        try:
            data = json.loads(config_path.read_text())

            self.webhook_entry.delete(0, "end")
            self.webhook_entry.insert(0, data.get("webhook_url", ""))

            events = data.get("events", {})
            for name, var in self.event_vars.items():
                var.set(events.get(name, True))

        except Exception:
            pass

    def save_config(self):
        config_path = Path("config.json")

        data = {}
        if config_path.exists():
            try:
                data = json.loads(config_path.read_text())
            except Exception:
                data = {}

        data["webhook_url"] = self.webhook_entry.get().strip()
        data["events"] = {
            name: var.get()
            for name, var in self.event_vars.items()
        }

        config_path.write_text(json.dumps(data, indent=4))
        self.status_label.configure(text="✅ Settings saved.")
