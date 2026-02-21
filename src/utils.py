import json

def load_quest():
    with open("data/quest_data.json", "r", encoding="utf-8") as f:
        return json.load(f)

items_names = {
    "marker": "Маркер",
    "kljuch": "Ключ",
}

quest_data = load_quest()