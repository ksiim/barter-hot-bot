import asyncio
from aiogram import F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery, FSInputFile
)
from aiogram.utils.media_group import MediaGroupBuilder

from bot import dp, bot

from models.dbs.orm import Orm
from models.dbs.models import *

from .callbacks import *
from .markups import *
from .states import *

@dp.message(Command('start'))
async def start_message_handler(message: Message, state: FSMContext):
    await state.clear()
    
    await Orm.create_user(message)
    await send_start_message(message)
    
async def send_start_message(message: Message):
    await bot.send_photo(
        chat_id=message.from_user.id,
        photo=start_photo_file_id,
        caption=await generate_start_text(message),
        reply_markup=start_markup,
    )
    
@dp.callback_query(F.data == "go")
async def go_callback_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    
    await callback.message.answer_document(
        caption="Продолжая общение со мной, ты согласаешься на обработку персональных данных",
        document=form_doc_file_id
    )
    
    await callback.message.answer(
        text="Для того, чтобы мы могли с вами связаться, отправьте мне свой номер телефона",
        reply_markup=phone_markup,
    )
    
    await state.set_state(AddEstateState.phone)
    
@dp.message(AddEstateState.phone)
async def phone_handler(message: Message, state: FSMContext):
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text
        
    await state.update_data(phone=phone)
    
    await message.answer(
        text="Теперь отправьте описание недвижимости. Предлагаем как можно подробнее ее описать. Город, район, дом, этаж, метраж и примерное состояние ремонта.",
    )
    
    await state.set_state(AddEstateState.description)
    
@dp.message(AddEstateState.description)
async def description_handler(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    
    await message.answer(
        text="Теперь отправьте до 10 фотографий недвижимости",
    )
    
    await state.update_data(photos=[], first_call=None, collecting=True)
    await state.set_state(AddEstateState.photos)


@dp.message(AddEstateState.photos, F.photo)
async def photos_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    current_photos = data.get("photos", [])
    first_call = data.get("first_call")
    collecting = data.get("collecting", False)
    
    if not collecting:
        return
    

    if first_call is None:
        await state.update_data(first_call=True)
        asyncio.create_task(wait_and_check(message, state))
    
    new_photo = message.photo[-1].file_id
    if len(current_photos) < 10:
        updated_photos = current_photos + [new_photo]
        await state.update_data(photos=updated_photos)
        
        if len(updated_photos) == 10:
            await check_and_proceed(message, state)

async def wait_and_check(message: Message, state: FSMContext):
    await asyncio.sleep(3)
    await check_and_proceed(message, state)

async def check_and_proceed(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    collecting = data.get("collecting", False)
    
    if not collecting:
        return
    
    if len(photos) < 1:
        await message.answer("Вы не отправили ни одной фотографии! Попробуйте снова.")
        await state.update_data(photos=[], first_call=None, collecting=True)
        return

    await state.update_data(collecting=False)
    
    await message.answer(
        text=f"Получено {len(photos)} фото. Переходим к следующему этапу!"
    )
    
    await barter(message, state)

async def barter(message: Message, state: FSMContext):
    await message.answer(
        text="Теперь отправьте, на что вы хотите обменять свою недвижимость. Здесь вы можете рассказать о своих пожеланиях по городу, району, типу дома, метражу и т.д."
    )
    
    await state.set_state(AddEstateState.barter_to)
    
@dp.message(AddEstateState.barter_to)
async def barter_to_handler(message: Message, state: FSMContext):
    await state.update_data(barter_to=message.text)
    
    data = await state.get_data()
    photos = data.get("photos", [])
    phone = data.get("phone")
    description = data.get("description")
    barter_to = message.text
    
    estate = Estate(
        user_id=message.from_user.id,
        phone=phone,
        description=description,
        trade_to=barter_to,
    )
    estate = await Orm.add_item(estate)
    
    for photo in photos:
        await Orm.add_item(Photo(file_id=photo, estate_id=estate.id))
    
    await message.answer(
        text="Спасибо за предоставленную информацию! Ваша недвижимость добавлена в нашу базу данных. Мы свяжемся с вами, если у нас будут подходящие варианты для обмена."
    )
    
    await send_to_admins(estate, photos)
    
async def send_to_admins(estate, photos):
    admins = await Orm.get_admins()
    
    caption = f"Добавлена новая недвижимость!\n\n{estate.description}\n\nОбмен на: {estate.trade_to}\n\nНомер телефона: {estate.phone}"
    media_group_builder = MediaGroupBuilder()
    for photo in photos:
        media_group_builder.add_photo(photo, caption=caption)
    media_group_builder.caption = caption
    for admin in admins:
        await bot.send_media_group(
            chat_id=admin.telegram_id,
            media=media_group_builder.build(),
        )
    
        
    
# @dp.message()
# async def message_handler(message: Message, state: FSMContext):
#     # await message.answer(
#     #     text=f"<code>{message.photo[-1].file_id}</code>",
#     # )
#     await message.answer(
#         text=f"<code>{message.document.file_id}</code>"
#     )
    