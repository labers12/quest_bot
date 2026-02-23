import sqlite3
import json
from pathlib import Path

DB_PATH = Path("data/players.db")

def init_db():
    """Создает таблицу для игроков, если её нет"""
    DB_PATH.parent.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            user_id INTEGER PRIMARY KEY,
            current_scene TEXT DEFAULT 'start',
            inventory TEXT DEFAULT '[]',
            game_active BOOLEAN DEFAULT 1
        )
    """)

    conn.commit()
    conn.close()

def reset_player(user_id: int):
    """Сбрасывает игрока на начало"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO players (user_id, current_scene, inventory, game_active)
        VALUES (?, 'start', '[]', 1)
    """, (user_id,))

    conn.commit()
    conn.close()

def get_player_state(user_id: int) -> dict:
    """Получает состояние игрока"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT current_scene, inventory, game_active
        FROM players
        WHERE user_id = ?
    """, (user_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        reset_player(user_id)
        return {
            "current_scene": "start",
            "inventory": [],
            "game_active": True
        }

    return {
        "current_scene": row[0],
        "inventory": json.loads(row[1]),
        "game_active": bool(row[2])
    }

def update_player_scene(user_id: int, scene_id: str):
    """Обновляет текущую сцену игрока"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE players
        SET current_scene = ?
        WHERE user_id = ?
    """, (scene_id, user_id))

    conn.commit()
    conn.close()

def add_item_to_inventory(user_id: int, item_id: str):
    """Добавляет предмет в инвентарь"""
    state = get_player_state(user_id)
    inventory = state["inventory"]

    if item_id not in inventory:
        inventory.append(item_id)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE players
        SET inventory = ?
        WHERE user_id = ?
    """, (json.dumps(inventory, ensure_ascii=False), user_id))

    conn.commit()
    conn.close()

def has_items(user_id: int, required_items: list) -> bool:
    """Проверяет, есть ли у игрока все нужные предметы"""
    state = get_player_state(user_id)
    inventory = state["inventory"]

    return all(item in inventory for item in required_items)
