from datetime import datetime
import threading
import time
import winsound
import requests
import json


class Notifier:
    def __init__(self):
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

        # Check if this event is enabled
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

        # Desktop sound
        if self.sound_enabled:
            self.play_sound()

        # Discord notification
        if self.discord_enabled:
            self.send_discord_webhook(
                event_name,
                score,
                timestamp,
                server_name
            )

    def play_sound(self):
        try:
            winsound.PlaySound(
                "alert.wav",
                winsound.SND_FILENAME | winsound.SND_ASYNC
            )

        except Exception as e:
            print(f"Failed to play sound: {e}")

    def send_discord_webhook(
        self,
        event_name,
        score,
        timestamp,
        server_name=""
    ):
        if not self.webhook_url:
            print("Discord webhook URL is empty.")
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
                        "text": "C.R.E.N."
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
                print(
                    f"Discord webhook failed "
                    f"({response.status_code}): "
                    f"{response.text}"
                )
                return

            message = response.json()

            message_id = message.get("id")

            if not message_id:
                print(
                    "Discord webhook succeeded but no "
                    "message ID was returned."
                )
                return

            # Start the 5-minute despawn timer.
            threading.Thread(
                target=self.mark_despawned,
                args=(
                    message_id,
                    event_name,
                    score,
                    timestamp,
                    server_name
                ),
                daemon=True
            ).start()

        except requests.RequestException as e:
            print(f"Discord webhook request failed: {e}")

        except Exception as e:
            print(f"Discord webhook failed: {e}")

    def mark_despawned(
        self,
        message_id,
        event_name,
        score,
        timestamp,
        server_name
    ):
        # Wait 5 minutes before marking the event as despawned.
        # The application must remain running during this period.
        time.sleep(300)

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

        fields.extend(
            [
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
            ]
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

                    "color": 0xFF0000,

                    "fields": fields,

                    "footer": {
                        "text": "C.R.E.N."
                    }
                }
            ]
        }

        try:
            response = requests.patch(
                f"{self.webhook_url}/messages/{message_id}",
                json=payload,
                timeout=5
            )

            if response.status_code not in (200, 201, 204):
                print(
                    f"Failed to update Discord webhook "
                    f"({response.status_code}): "
                    f"{response.text}"
                )

        except requests.RequestException as e:
            print(f"Failed to update Discord webhook: {e}")

        except Exception as e:
            print(f"Failed to update webhook: {e}")