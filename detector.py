from rapidfuzz import fuzz
import time


class EventDetector:
    def __init__(self):
        self.events = {
            "Bandit Lord": [
                "Whispers rise; One of the Bandit Lords emerges from the shadows.", "Whispers rise", "One of the Bandit Lords emerges from the shadows."
            ],

            "Warlord": [
                "The Warlord of the Grasslands steps forward", "challenge in his eyes.", "The Warlord of the Grasslands"
            ],

            "Khamsin": [
                "The sands shift; Khamsin", "the Sand Sage", "emerges from the dunes."
            ],

            "Desert Village Rumor": [
                "Somebody has seen something they might not survive to tell, word has it they're in the Desert Village",
                "Somebody has seen something they might not survive to tell", "word has it they're in the Desert Village"
            ],

            "Craftsman": [
                "A seasoned Wolf Hunter Craftsman has arrived in the forest, his tools at the ready to forge exceptional gear for worthy adventurers."
                "worthy adventurers",
            ],

            "Corrupt Night": [
                "The air grows heavy, and darkness takes hold as every creature is consumed by corruption.", 
                "The air grows heavy", "and darkness takes hold as every creature", "is consumed by corruption."
            ],

            "Mana Wisp": [
                "Mana fluttering can be heard across the grasslands",
                "mana fluttering"
            ],

            "Radiant Wisp": ["Radiant Wisp", "A radiant wisp has appeared in the grasslands"],
            "Blood Wisp": ["Blood Wisp", "A blood wisp has appeared in the grasslands"],
            "Wind Wisp": ["Wind Wisp", "A wind wisp has appeared in the grasslands"],

            "Shadowhand Rift": [
                "A rift shrouded in sinister mana tears open",
                "the Shadowhand stands watch, guarding what lies beyond."
            ],

            "Devil Rift": [
                "Something feels off", "Something feels off..."
            ],

            "Spirit Rift": [
                "A strange energy is felt throughout the kingdom", "A strange energy", "is felt throughout the kingdom"
            ],

            "Giant Demon Assault": [
                "The seal shattered",
                "a giant demon now walks the land"
            ],

            "Ayato": [
                "The veil shimmers and a lone figure emerges."
            ],

            "One Star Dragon Ball": [
                "A single star shines",
                "igniting the spark of an epic saga",
                "where strength and courage begin their dance",
                "courage begin their dance",
            ],

            "Two Star Dragon Ball": [
                "Two stars align",
                "forging alliances in the face of looming shadows",
                "a bond stronger than fate",
            ],

            "Three Star Dragon Ball": [
                "Three stars blaze",
                "a beacon of trials overcome",
                "where friends gather and powers awaken",
                "awaken",
            ],

            "Four Star Dragon Ball": [
                "Four stars glow",
                "making the corners of a journey fraught with adversaries",
                "yet bound by the light of hope",
            ],

            "Five Star Dragon Ball": [
                "Five stars radiate",
                "a testament to battles fought",
                "wisdom gained, and spirits unbroken",
            ],

            "Six Star Dragon Ball": [
                "Six stars shimmer",
                "near completion",
                "a prelude to the ultimate challenge",
                "echoing the heartbeats of heroes.",
            ],

            "Seven Star Dragon Ball": [
                "As seven stars converge",
                "the heavens themselves pause to mourn and honor a legacy",
                "in this moment, the universe whispers thanks to its visionary",
                "and a final wish awaits",
                "a tribute to the master of dreams",
            ],

            "Blessed Sphere": [
                "A blessed sphere",
                "A Blessed Sphere has materialized somewhere in the grasslands...",
                "has materialized somewhere in the grasslands",
                "A Blessed Sphere has materialized",
                "somewhere in the grasslands",
            ],
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