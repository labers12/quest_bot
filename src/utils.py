import json

def load_quest():
    """Загружает данные квеста из JSON"""
    with open("data/quest_data.json", "r", encoding="utf-8") as f:
        return json.load(f)

quest_data = load_quest()
