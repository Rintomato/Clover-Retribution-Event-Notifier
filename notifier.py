from datetime import datetime
import threading
import time
import winsound
import requests
import json


class Notifier:
    def __init__(self):
        # Paste your Discord webhook URL here
        self.webhook_url = ""

        self.reload_config()

    def reload_config(self):
        try:
            with open("config.json", "r", encoding="utf-8") as file:
                config = json.load(file)
                self.webhook_url = config.get("webhook_url", "")
                self.events = config.get("events", {})
        except Exception as e:
            print(f"Failed to load config.json: {e}")
            self.webhook_url = ""
            self.events = {}

    def notify(self, event_name, score, server_name=""):
        self.reload_config()

        dragon_events = {
            "One Star Dragon Ball",
            "Two Star Dragon Ball",
            "Three Star Dragon Ball",
            "Four Star Dragon Ball",
            "Five Star Dragon Ball",
            "Six Star Dragon Ball",
            "Seven Star Dragon Ball",
        }

        elemental_wisps = {
            "Blood Wisp",
            "Radiant Wisp",
            "Wind Wisp",
        }

        if event_name in dragon_events:
            config_name = "Dragon Balls"
        elif event_name in elemental_wisps:
            config_name = "Elemental Wisp"
        else:   
            config_name = event_name


        if not self.events.get(config_name, True):
            return

        timestamp = datetime.now().strftime("%H:%M:%S")

        print()
        print("=" * 60)
        print(f"[{timestamp}] EVENT DETECTED!")
        print(f"Event      : {event_name}")
        print(f"Similarity : {score:.1f}%")

        if server_name.strip():
            print(f"Server     : {server_name}")

        print("=" * 60)
        print()

        self.play_sound()
        self.send_discord_webhook(event_name, score, timestamp, server_name)

    def play_sound(self):
        try:
            winsound.PlaySound(
                "alert.wav",
                winsound.SND_FILENAME | winsound.SND_ASYNC
            )
        except Exception as e:
            print(f"Failed to play sound: {e}")

    def send_discord_webhook(self, event_name, score, timestamp, server_name=""):
        if not self.webhook_url:
            return

        fields = [
            {
                "name": "Similarity",
                "value": f"{score:.1f}%",
                "inline": True
            }
        ]

        if server_name.strip():
            fields.append(
                {
                    "name": "Server",
                    "value": server_name,
                    "inline": True
                }
            )

        fields.append(
            {
                "name": "Time",
                "value": timestamp,
                "inline": True
            }
        )

        payload = {
            "content": "@everyone",
            "allowed_mentions": {
                "parse": ["everyone"]
            },
            "embeds": [
                {
                    "title": "🚨 Event Detected!",
                    "description": f"**{event_name}**",
                    "color": 0x00FF00,
                    "fields": fields,
                    "footer": {
                        "text": "Event Notifier"
                    }
                }
            ]
        }

        try:
            response = requests.post(
                self.webhook_url + "?wait=true",
                json=payload,
                timeout=5
            )

            if response.status_code not in (200, 201):
                print(f"Discord webhook failed ({response.status_code}): {response.text}")
                return

            message = response.json()

            threading.Thread(
                target=self.mark_despawned,
                args=(message["id"], event_name, score, timestamp, server_name),
                daemon=True
            ).start()

        except Exception as e:
            print(f"Discord webhook failed: {e}")

    def mark_despawned(self, message_id, event_name, score, timestamp, server_name):
        time.sleep(300)  # 5 minutes

        fields = [
            {
                "name": "Similarity",
                "value": f"{score:.1f}%",
                "inline": True
            }
        ]

        if server_name.strip():
            fields.append(
                {
                    "name": "Server",
                    "value": server_name,
                    "inline": True
                }
            )

        fields.extend([
            {
                "name": "Time",
                "value": timestamp,
                "inline": True
            },
            {
                "name": "Status",
                "value": "❌ Despawned",
                "inline": False
            }
        ])

        payload = {
            "content": "@everyone",
            "embeds": [
                {
                    "title": "🚨 Event Detected!",
                    "description": f"**{event_name}**",
                    "color": 0xFF0000,
                    "fields": fields,
                    "footer": {
                        "text": "Event Notifier"
                    }
                }
            ]
        }

        try:
            requests.patch(
                f"{self.webhook_url}/messages/{message_id}",
                json=payload,
                timeout=5
            )

        except Exception as e:
            print(f"Failed to update webhook: {e}")