from datetime import datetime
import threading
import time
import winsound
import json
import urllib.request
import urllib.error


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
                self.sound_enabled = config.get("sound_enabled", True)
                self.discord_enabled = config.get("discord_enabled", True)
        except Exception as e:
            print(f"Failed to load config.json: {e}")
            self.webhook_url = ""
            self.events = {}
            self.sound_enabled = True
            self.discord_enabled = True

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
            "Blessed Sphere",
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

        if self.sound_enabled:
            self.play_sound()
        if self.discord_enabled:
            self.send_discord_webhook(event_name, score, timestamp, server_name)

    @staticmethod
    def _request_json(url, payload, method="POST", timeout=5):
        """Send a JSON body via urllib and return (status_code, parsed_body_or_None)."""
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                status = resp.getcode()
                body = resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            status = e.code
            body = e.read().decode("utf-8") if e.fp else ""
        parsed = None
        if body:
            try:
                parsed = json.loads(body)
            except json.JSONDecodeError:
                parsed = None
        return status, parsed

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
            status, message = self._request_json(
                self.webhook_url + "?wait=true", payload, method="POST", timeout=5
            )

            if status not in (200, 201):
                print(f"Discord webhook failed ({status}): {message}")
                return

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
            self._request_json(
                f"{self.webhook_url}/messages/{message_id}", payload, method="PATCH", timeout=5
            )

        except Exception as e:
            print(f"Failed to update webhook: {e}")