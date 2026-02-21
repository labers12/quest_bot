import os
import re
import json

SOURCE_DIR = "Scenes_eng"  # Папка с переименованными файлами
OUTPUT_FILE = "quest_data.json"

def parse_md_to_dict():
    quest_data = {}
    
    # Регулярки для захвата данных
    re_description = re.compile(r"Описание:\s*(.*?)(?=\n\n|\nСобытие:|\nДействия:|$)", re.DOTALL)
    re_events = re.compile(r"Событие:\s*(.*?)(?=\n\n|\nДействия:|$)", re.DOTALL)
    re_actions = re.compile(r"\[\[(.*?)\|(.*?)\]\]|\[\[(.*?)\]\]")

    for filename in os.listdir(SOURCE_DIR):
        if not filename.endswith(".md"):
            continue
            
        file_id = os.path.splitext(filename)[0]
        with open(os.path.join(SOURCE_DIR, filename), 'r', encoding='utf-8') as f:
            content = f.read()

        # Извлекаем описание
        desc_match = re_description.search(content)
        description = desc_match.group(1).strip() if desc_match else ""

        # Извлекаем события (например, получение предмета)
        event_match = re_events.search(content)
        event_text = event_match.group(1).strip() if event_match else None
        
        # Парсим предмет, если он есть в событии
        item_match = re.search(r"\[\[(.*?)\]\]", event_text) if event_text else None
        item_received = item_match.group(1) if item_match else None

        # Извлекаем кнопки
        actions = []
        for match in re_actions.finditer(content):
            # match.group(1) и (2) — если есть |, group(3) — если просто [[ID]]
            target = match.group(1) or match.group(3)
            text = match.group(2) or target # Если текста нет, текст кнопки = ID
            actions.append({
                "target": target.strip(),
                "text": text.strip()
            })

        quest_data[file_id] = {
            "description": description,
            "item_to_add": item_received,
            "actions": actions
        }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(quest_data, f, ensure_ascii=False, indent=4)
    
    print(f"✅ Готово! Создан файл {OUTPUT_FILE}")

if __name__ == "__main__":
    parse_md_to_dict()