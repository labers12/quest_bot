import os
import re
import json

SOURCE_DIR = "Scenes_eng"
OUTPUT_FILE = "data/quest_data.json"

# Маппинг ID предметов на русские названия (для обратной совместимости)
ITEM_NAMES = {
    "marker": "Маркер",
    "kljuch": "Ключ",
    "digit_1": "Цифра 1",
    "digit_4": "Цифра 4",
    "digit_7": "Цифра 7"
}

def parse_scenes():
    """
    Парсит markdown файлы сцен в JSON

    Поддерживаемый формат:

    Описание: Текст сцены

    Событие: Получен предмет "Название" (item_id)

    Результат: победа|проигрыш

    Действия:
    1. [[target_id|Текст кнопки]] требует: item1, item2
    2. [[target_id]]
    """
    quest_data = {}

    for filename in os.listdir(SOURCE_DIR):
        if not filename.endswith(".md"):
            continue

        scene_id = os.path.splitext(filename)[0]
        filepath = os.path.join(SOURCE_DIR, filename)

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        scene = parse_scene_content(content)
        quest_data[scene_id] = scene

    # Сохраняем результат
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(quest_data, f, ensure_ascii=False, indent=2)

    print(f"Обработано {len(quest_data)} сцен")
    print(f"Создан файл {OUTPUT_FILE}")

def parse_scene_content(content: str) -> dict:
    """Парсит содержимое одной сцены"""
    scene = {
        "description": "",
        "items_to_add": [],
        "actions": [],
        "is_win": False,
        "is_loss": False
    }

    # Парсим описание
    desc_match = re.search(r"Описание:\s*(.*?)(?=\n\n|\nСобытие:|\nРезультат:|\nДействия:|$)", content, re.DOTALL)
    if desc_match:
        scene["description"] = desc_match.group(1).strip()

    # Парсим события (предметы)
    event_match = re.search(r"Событие:\s*(.*?)(?=\n\n|\nРезультат:|\nДействия:|$)", content, re.DOTALL)
    if event_match:
        event_text = event_match.group(1)
        # Ищем формат: Получен предмет "Название" (item_id)
        item_matches = re.finditer(r'предмет\s+"([^"]+)"\s+\((\w+)\)', event_text)
        for match in item_matches:
            scene["items_to_add"].append({
                "id": match.group(2),
                "name": match.group(1)
            })

        # Поддержка старого формата: [[item_id]]
        if not scene["items_to_add"]:
            old_format = re.search(r'\[\[(\w+)\]\]', event_text)
            if old_format:
                item_id = old_format.group(1)
                scene["items_to_add"].append({
                    "id": item_id,
                    "name": ITEM_NAMES.get(item_id, item_id)  # Используем маппинг или ID
                })

    # Парсим результат (победа/проигрыш)
    result_match = re.search(r"Результат:\s*(победа|проигрыш)", content, re.IGNORECASE)
    if result_match:
        result_type = result_match.group(1).lower()
        if result_type == "победа":
            scene["is_win"] = True
        elif result_type == "проигрыш":
            scene["is_loss"] = True

    # Парсим действия
    actions_match = re.search(r"Действия:\s*(.*?)$", content, re.DOTALL)
    if actions_match:
        actions_text = actions_match.group(1)

        # Ищем все ссылки формата [[target]] или [[target|text]]
        for line in actions_text.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Убираем нумерацию (1. 2. и т.д.)
            line = re.sub(r'^\d+\.\s*', '', line)

            # Парсим ссылку
            link_match = re.search(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]', line)
            if not link_match:
                continue

            target = link_match.group(1).strip()
            text = link_match.group(2).strip() if link_match.group(2) else target

            # Парсим требования (если есть)
            required_items = []
            requires_match = re.search(r'требует:\s*([\w,\s]+)', line)
            if requires_match:
                items_str = requires_match.group(1)
                required_items = [item.strip() for item in items_str.split(',')]

            scene["actions"].append({
                "target": target,
                "text": text,
                "required_items": required_items
            })

    return scene

if __name__ == "__main__":
    parse_scenes()
