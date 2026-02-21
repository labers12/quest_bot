import os
import re
from pathlib import Path
from transliterate import slugify

# Настройки
SOURCE_DIR = "Scenes"  # Папка с твоими текущими .md файлами
OUTPUT_DIR = "Scenes_eng"  # Куда сохранить результат

def get_slug(name):
    """Превращает 'Привет Мир' в 'privet_mir'"""
    # Удаляем расширение для обработки имени
    name_without_ext = os.path.splitext(name)[0]
    slug = slugify(name_without_ext, language_code='ru')
    return slug.replace('-', '_') if slug else name_without_ext.lower()

def migrate_quest():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 1. Собираем карту соответствий {Старое имя: Новое имя}
    rename_map = {}
    files = [f for f in os.listdir(SOURCE_DIR) if f.endswith('.md')]
    
    for filename in files:
        new_name = get_slug(filename) + ".md"
        rename_map[os.path.splitext(filename)[0]] = os.path.splitext(new_name)[0]

    # 2. Читаем, заменяем ссылки и сохраняем
    for filename in files:
        old_path = os.path.join(SOURCE_DIR, filename)
        new_filename = rename_map[os.path.splitext(filename)[0]] + ".md"
        new_path = os.path.join(OUTPUT_DIR, new_filename)

        with open(old_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Регулярка ищет [[Имя Файла]] или [[Имя Файла|Текст]]
        # Группа 1 — это само имя, которое мы заменим
        def replace_link(match):
            old_link = match.group(1)
            # Если в ссылке есть разделитель |, берем только левую часть для поиска ID
            parts = old_link.split('|')
            file_id = parts[0].strip()
            
            if file_id in rename_map:
                new_id = rename_map[file_id]
                # Собираем ссылку обратно (с текстом кнопки, если он был)
                if len(parts) > 1:
                    return f"[[{new_id}|{parts[1]}]]"
                return f"[[{new_id}]]"
            return match.group(0) # Если не нашли в карте, оставляем как есть

        new_content = re.sub(r'\[\[(.*?)\]\]', replace_link, content)

        with open(new_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Обработан: {filename} -> {new_filename}")

if __name__ == "__main__":
    migrate_quest()
