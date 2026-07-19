from rapidfuzz import fuzz
import time


class EventDetector:
    def __init__(self):
        self.events = {
            "Bandit Lord": [
                "Whispers rise; One of the Bandit Lords emerges from the shadows."
            ],

            "Warlord": [
                "The Warlord of the Grasslands steps forward, challenge in his eyes."
            ],

            "Khamsin": [
                "The sands shift; Khamsin, the Sand Sage, emerges from the dunes."
            ],

            "Desert Village Rumor": [
                "Somebody has seen something they might not survive to tell, word has it they're in the Desert Village",
                "Somebody has seen something they might not survive to tell, word has it they’re in the Desert Village"
            ],

            "Craftsman": [
                "A seasoned Wolf Hunter Craftsman has arrived in the forest, his tools at the ready to forge exceptional gear for worthy adventurers."
            ],

            "Corrupt Night": [
                "The air grows heavy, and darkness takes hold as every creature is consumed by corruption."
            ],

            "Mana Wisp": [
                "Mana fluttering can be heard across the grasslands",
                "mana fluttering"
            ],

            "Radiant Wisp": ["Radiant Wisp"],
            "Blood Wisp": ["Blood Wisp"],
            "Wind Wisp": ["Wind Wisp"],

            "Shadowhand Rift": [
                "A rift shrouded in sinister mana tears open",
                "the Shadowhand stands watch, guarding what lies beyond."
            ],

            "Devil Rift": [
                "Something feels off"
            ],

            "Spirit Rift": [
                "A strange energy is felt throughout the kingdom"
            ],

            "Giant Demon Assault": [
                "The seal shattered",
                "a giant demon now walks the land"
            ],

            "Ayato": [
                "The veil shimmers and a lone figure emerges."
            ],

            "Dragon Balls": [
                "A single star shines",
                "Two stars align",
                "Three stars blaze",
                "Four stars glow",
                "Five stars radiate",
                "Six stars shimmer",
                "As seven stars converge"
            ]
        }

        # Similarity required (0-100)
        self.threshold = 88

        # Cooldown per event (seconds)
        self.cooldown = 8 * 60

        # Stores last detection time for each event
        self.last_detected = {}

    def check(self, text):
        text = text.lower()

        best_event = None
        best_score = 0

        for event, phrases in self.events.items():
            for phrase in phrases:
                score = fuzz.partial_ratio(phrase.lower(), text)

                if score > best_score:
                    best_score = score
                    best_event = event

        if best_score >= self.threshold:
            now = time.time()
            last = self.last_detected.get(best_event, 0)

            if now - last >= self.cooldown:
                self.last_detected[best_event] = now
                return best_event, best_score

        return None

    def reset_cooldowns(self):
        """Clear all event cooldowns."""
        self.last_detected.clear()