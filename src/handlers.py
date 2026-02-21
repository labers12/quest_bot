from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from .utils import quest_data, items_names

router = Router()

def get_keyboard(scene_id: str):
    builder = InlineKeyboardBuilder()
    scene = quest_data.get(scene_id)

    if not scene:
        return None
    
    for action in scene["actions"]:
        builder.row(types.InlineKeyboardButton(
            text = action['text'],
            callback_data = f'scene:{action["target"]}'
        ))
    return builder.as_markup()

@router.message(Command("start"))
async def start_command(message: types.Message):
    initial_scene = "start"
    scene = quest_data.get(initial_scene)

    await message.answer(
        text = scene["description"],
        reply_markup= get_keyboard(initial_scene)
    )

@router.callback_query(F.data.startswith("scene:"))
async def handle_step(callback: types.CallbackQuery):
    target_id = callback.data.split(':')[1]
    scene = quest_data.get(target_id)

    if not scene:
        await callback.answer("Сцена пуста или не найдена")
        return
    if scene.get("item_to_add"):
        item_id = scene["item_to_add"]
        name = items_names.get(item_id,item_id)
        await callback.message.answer(f'Вы получили {name}')
    await callback.message.edit_text(
        text = scene["description"],
        reply_markup=get_keyboard(target_id)
    )
    await callback.answer()
    
