from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from .utils import quest_data
from .database import (
    reset_player,
    get_player_state,
    update_player_scene,
    add_item_to_inventory,
    has_items
)

router = Router()

def get_keyboard(scene_id: str, user_id: int):
    """Создает клавиатуру с кнопками действий для сцены"""
    builder = InlineKeyboardBuilder()
    scene = quest_data.get(scene_id)

    if not scene or not scene.get("actions"):
        return None

    for action in scene["actions"]:
        # Проверяем, есть ли у игрока нужные предметы
        required = action.get("required_items", [])
        if required and not has_items(user_id, required):
            continue  # Скрываем кнопку, если нет предметов

        builder.row(types.InlineKeyboardButton(
            text=action['text'],
            callback_data=f'scene:{action["target"]}'
        ))

    return builder.as_markup()

@router.message(Command("start"))
async def start_command(message: types.Message):
    """Начало игры - сброс прогресса и переход на стартовую сцену"""
    user_id = message.from_user.id
    reset_player(user_id)

    scene = quest_data.get("start")
    if not scene:
        await message.answer("Ошибка: стартовая сцена не найдена")
        return

    await message.answer(
        text=scene["description"],
        reply_markup=get_keyboard("start", user_id)
    )

@router.message(Command("inventory"))
async def inventory_command(message: types.Message):
    """Показывает инвентарь игрока"""
    user_id = message.from_user.id
    state = get_player_state(user_id)
    inventory = state["inventory"]

    if not inventory:
        await message.answer("🎒 Ваш инвентарь пуст")
        return

    # Получаем названия предметов из quest_data
    item_names = []
    for item_id in inventory:
        # Ищем предмет во всех сценах
        found_name = None
        for scene in quest_data.values():
            for item in scene.get("items_to_add", []):
                if item["id"] == item_id:
                    found_name = item["name"]
                    break
            if found_name:
                break
        item_names.append(found_name or item_id)

    inventory_text = "🎒 Ваш инвентарь:\n" + "\n".join(f"• {name}" for name in item_names)
    await message.answer(inventory_text)

@router.callback_query(F.data.startswith("scene:"))
async def handle_scene_transition(callback: types.CallbackQuery):
    """Обработка перехода на новую сцену"""
    user_id = callback.from_user.id
    target_id = callback.data.split(':')[1]

    # Получаем новую сцену
    new_scene = quest_data.get(target_id)
    if not new_scene:
        await callback.answer("Сцена не найдена", show_alert=True)
        return

    # Проверяем проигрыш
    if new_scene.get("is_loss"):
        await callback.message.edit_text(
            text=f"{new_scene['description']}\n\n💀 Вы проиграли. Игра начинается заново.",
            reply_markup=None
        )
        reset_player(user_id)
        await callback.answer()
        return

    # Проверяем победу
    if new_scene.get("is_win"):
        await callback.message.edit_text(
            text=f"{new_scene['description']}\n\n🎉 Поздравляем! Вы прошли игру!",
            reply_markup=None
        )
        reset_player(user_id)
        await callback.answer()
        return

    # Добавляем предметы в инвентарь
    items_to_add = new_scene.get("items_to_add", [])
    for item in items_to_add:
        item_id = item["id"]
        item_name = item["name"]

        state = get_player_state(user_id)
        if item_id not in state["inventory"]:
            add_item_to_inventory(user_id, item_id)
            await callback.message.answer(f"📦 Получен предмет: {item_name}")

    # Обновляем текущую сцену
    update_player_scene(user_id, target_id)

    # Показываем новую сцену
    await callback.message.edit_text(
        text=new_scene["description"],
        reply_markup=get_keyboard(target_id, user_id)
    )
    await callback.answer()
