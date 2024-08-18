import os
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from datetime import datetime, timedelta

import database.requests as requests
import app.keyboards as keyboard

router: Router = Router()
bot: Bot = Bot(token=os.getenv("TOKEN"))

ADMIN_IDs = [1858903376]


class AddUser(StatesGroup):
    name = State()
    phone_number = State()


class Booking(StatesGroup):
    day = State()
    start_time = State()
    end_time = State()
    table = State()


@router.message(CommandStart())
async def start_command(message: Message, state: FSMContext):
    if message.chat.type == "private":
        user = await requests.get_user_by_id(message.from_user.id)
        if not user:
            await state.set_state(AddUser.name)
            await message.answer(
                "Xush kelibsiz!\n\nIltimos, kelgusida siz haqingizda ma'lumot olishimiz uchun shaxsiy ma'lumotlaringiz kerak bo'ladi. \n(Bularning barchasi siz bilan bog'lanish uchun ishlatilinadi)\n\nKerakli ma'lumotlar:\n1. Ismingiz\n2.Telefon raqamingiz\n\nIltimos ismingizni kiriting 👇🏻"
            )
        else:
            await state.set_state(Booking.day)
            await message.answer_photo(
                "AgACAgEAAxkBAANaZsC8HA_fq5suL-MMcRFqhulvdNAAAoOrMRvoDghGoCYpE9z8qloBAAMCAAN4AAM1BA",
                caption=f"Xush kelibsiz, {user.name}!\n\nUshbu rasmda siz bizning restoranimiz stollar joylashuvi haqida to'liqroq ma'lumot olasiz.\n\nQuyidagi tugmalar orqali o'zingizga kerakli kunni tanlang 👇🏻\nAgar siz izlagan kun mavjud bo'lmasa biz bilan bog'lanib buyurtma berishingiz mumkin.\n\n☎️ Murojaat uchun raqam: +998712000665",
                reply_markup=await keyboard.choose_day(),
                parse_mode="HTML",
            )


@router.message(AddUser.name, F.text)
async def get_name(message: Message, state: FSMContext):
    if message.chat.type == "private":
        if len(message.text) <= 75:
            await state.update_data(name=message.text)
            await state.set_state(AddUser.phone_number)
            await message.answer(
                f"✅ Yaxshi, {message.text}\n\nEndi esa telefon raqamingizni pastdagi 'telefon raqam yuborish' tugmasi orqali yuboring 👇🏻\n\nEslatma: Faqat uzbek raqamlari qabul qilinadi!",
                reply_markup=keyboard.phone_number,
            )
        else:
            await message.answer(
                "‼️ Ism juda uzun kiritildi, ismingiz 75ta belgidan oshiq bo'lmasligi kerak!"
            )


@router.message(AddUser.name)
async def get_name_error(message: Message):
    if message.chat.type == "private":
        await message.answer(
            "‼️ Noto'gri urinish, iltimos ismingizni bizga yozma tarzda yuboring!"
        )


@router.message(AddUser.phone_number, F.contact)
async def create_user(message: Message, state: FSMContext):
    if message.chat.type == "private":
        phone = message.contact.phone_number
        if phone.startswith("998") or phone.startswith("+998"):
            name = (await state.get_data())["name"]
            await requests.create_user(
                message.from_user.id,
                name,
                phone if phone.startswith("+") else f"+{phone}",
            )
            await message.answer(
                "Hammasi joyida!\n\nEndi siz bemalol bizning botimiz orqali stol buyurtma qilsangiz bo'ladi ✅\n\nBotni qayta ishga tushirish uchun /start buyrug'ini bering",
                reply_markup=keyboard.remove,
            )
        else:
            await message.reply(
                "‼️ Restoranimiz xavfsizligiga ko'ra faqatgina o'zbek raqam orqali ochilgan telegram hisob orqali botimizdan foydalanish mumkin!",
                reply_markup=keyboard.remove,
            )
            print(message.contact.phone_number)
        await state.clear()


@router.message(AddUser.phone_number)
async def get_phone_error(message: Message):
    await message.answer(
        "Iltimos telefon raqamingizni pastdagi tugma orqali yuboring 👇🏻"
    )


@router.message(Booking.start_time, F.text)
async def get_start_time(message: Message, state: FSMContext):
    try:
        [hour, minute] = message.text.split(":")
        hour = hour[:2]
        minute = minute[:2]
        date = await state.get_data()
        if date["day"] == "current" and datetime.now() > datetime.now().replace(
            hour=int(hour), minute=int(minute), second=0, microsecond=0
        ):
            raise ValueError("Vaqt xato berildi")
        await state.update_data(start_time=[int(hour), int(minute)])
        await state.set_state(Booking.end_time)
        await message.answer(
            "Vaqt tanlandi ✅\n\nEndi esa tahminiy qachongacha davom etishini ham xuddi shu formatda yuboring"
        )
    except:
        await message.answer(
            "❗️ Vaqtni noto'g'ri formatda yubordingiz, iltimos tekshirib qayta urinib ko'ring"
        )


@router.message(Booking.end_time, F.text)
async def get_end_time(message: Message, state: FSMContext):
    try:
        [hour, minute] = message.text.split(":")
        hour = hour[:2]
        minute = minute[:2]
        await state.update_data(end_time=[int(hour), int(minute)])
        data = await state.get_data()
        now = datetime.now()
        start_time = now.replace(
            hour=data["start_time"][0],
            minute=data["start_time"][1],
            second=0,
            microsecond=0,
        )
        end_time = now.replace(
            hour=data["end_time"][0],
            minute=data["end_time"][1],
            second=0,
            microsecond=0,
        )

        if data["day"] == "tomorrow":
            start_time += timedelta(days=1)
            end_time += timedelta(days=1)
        await state.update_data(
            start_time=start_time,
            end_time=end_time,
        )
        free_tables = list(await requests.get_free_tables(start_time, end_time))
        await state.set_state(Booking.table)
        await message.answer_photo(
            "AgACAgEAAxkBAANaZsC8HA_fq5suL-MMcRFqhulvdNAAAoOrMRvoDghGoCYpE9z8qloBAAMCAAN4AAM1BA",
            caption="Vaqt tanlandi ✅\n\nEndi esa quyidagi bo'sh stollardan birini tanlang 👇🏻\n\n(Stollar qatorlar asosida raqamlangan)",
            reply_markup=await keyboard.tables(free_tables),
        )
    except:
        await message.answer(
            "❗️ Vaqtni noto'g'ri formatda yubordingiz, iltimos tekshirib qayta urinib ko'ring"
        )


@router.callback_query(Booking.day, F.data.startswith("day"))
async def get_day(callback: CallbackQuery, state: FSMContext):
    day = callback.data.split("_")[1]
    await state.update_data(day=day)
    await state.set_state(Booking.start_time)
    await callback.answer()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=f"Kun tanlandi: *{'Bugun' if day == 'current' else 'Ertaga'}*\nEndi esa o'zingizga qulay vaqtni tanlang. \n\nQuyidagi misollar orqali qulay vaqtni xabar ko'rinishida yuboring 👇🏻\n\n*14:00\n09:30*",
        parse_mode="markdown",
    )


@router.callback_query(Booking.table, F.data.startswith("table"))
async def booking_table(callback: CallbackQuery, state: FSMContext):
    table_id = callback.data.split("_")[1]
    user = await requests.get_user_by_id(callback.from_user.id)
    data = await state.get_data()
    try:
        booking = await requests.booking_table(
            table_id, user.id, data["start_time"], data["end_time"]
        )
        table = await requests.get_table(booking.table_id)
        user = await requests.get_user(booking.user_id)
        await bot.edit_message_caption(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            caption=f"*Buyurtma muvaffaqiyatli yaratildi* ✅\n\nTez orada operatorlarimiz siz bilan bog'lanishadi.\nAloqa uchun telefon raqamingiz: {user.phone_number}",
            parse_mode="markdown",
        )
        for admin_id in ADMIN_IDs:
            await bot.send_message(
                chat_id=admin_id,
                text=f"*Yangi buyurtma* ✅\n\n🆔 Buyurtma id'si: {booking.id}\n📝 Buyurtma stoli: {table.name}\n👤 Buyurtmachi: {user.name}\n☎️ Telefon raqam: {user.phone_number}\n\n⏰ Buyurtma boshlanish vaqti: {booking.start_time}\n⏰ Buyurtma tugash vaqti: {booking.end_time}",
                parse_mode="markdown",
            )
    except Exception as e:
        await bot.edit_message_caption(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            caption="❗️ *Buyurtma qilishda xatolik ro'y berdi.*\nIltimos barcha ma'lumotlaringizni tekshirib, qayta urinib ko'ring yoki biz bilan bog'laning\n\n☎️ Murojaat uchun raqam: +998712000665",
            parse_mode="markdown",
        )
        print(e)
    await state.clear()
