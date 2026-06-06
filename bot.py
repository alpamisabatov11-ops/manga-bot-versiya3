# bot.py
import re
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import config
import database as db
import keyboards as kb

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
db.init_db()

class BotStates(StatesGroup):
    id_kutish = State()
    
    # Manga States
    kutish_manga_nomi = State()
    kutish_manga_janr = State()
    kutish_manga_rasm = State()
    kutish_manga_holati = State()
    
    # Anime States
    kutish_anime_nomi = State()
    kutish_anime_janr = State()
    kutish_anime_rasm = State()
    kutish_anime_holati = State()
    
    # Manhwa States
    kutish_manhwa_nomi = State()
    kutish_manhwa_janr = State()
    kutish_manhwa_rasm = State()
    kutish_manhwa_holati = State()
    
    # Light Novel States
    kutish_novel_nomi = State()
    kutish_novel_janr = State()
    kutish_novel_rasm = State()
    kutish_novel_holati = State()
    
    # Boblar / Epizodlar yuklash States
    kutish_bob_turi = State() # manga, anime, manhwa, novel
    kutish_bob_content_id = State()
    kutish_bob_raqami = State()
    kutish_bob_fayl = State()
    
    # Admin sozlamalari
    kutish_admin_id = State()
    kutish_welcome = State()
    kutish_reklama = State()
    kutish_admin_username = State()
    kutish_kanal_link = State()
    kutish_ban_id = State()

async def ban_tekshir(user_id, message: types.Message) -> bool:
    ban_status = db.user_ban_tekshirish_kengaytirilgan(user_id)
    if ban_status == "permanent":
        await message.answer("🚫 Siz botdan butunlay bloklangansiz!")
        return True
    elif isinstance(ban_status, int):
        soat = ban_status // 3600
        minut = (ban_status % 3600) // 60
        await message.answer(f"⏳ Siz vaqtinchalik cheklangansiz.\n⏱ Qolgan vaqt: {soat} soat, {minut} daqiqa.")
        return True
    return False

# === KANALGA YANGI KONTENT POSTINI YUBORISH ===
async def kanalga_yangi_kontent_yuborish(content_type, nomi, janr, rasm, holati, content_id):
    kanallar = db.kanallar_olish()
    if not kanallar: return
    
    bot_info = await bot.get_me()
    turlar = {
        "manga": ("📖 YANGI MANGA!", "manga_v"),
        "anime": ("🎬 YANGI ANIME!", "anime_v"),
        "manhwa": ("🔥 YANGI MANHWA!", "manhwa_v"),
        "novel": ("📚 YANGI LIGHT NOVEL!", "novel_v")
    }
    sarlavha, prefiks = turlar.get(content_type, ("📣 YANGI KONTENT!", "content_v"))
    
    inline_btn = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("🚀 Botda ko'rish", url=f"https://t.me/{bot_info.username}?start={prefiks}_{content_id}")
    )
    
    text = (
        f"{sarlavha}\n\n"
        f"📌 **Nomi:** {nomi}\n"
        f"🎭 **Janri:** {janr}\n"
        f"⚡ **Holati:** {str(holati).upper()}\n\n"
        f"🤖 Mutolaa qilish yoki tomosha qilish uchun pastdagi tugmani bosing 👇"
    )
    try:
        await bot.send_photo(chat_id=kanallar[0], photo=rasm, caption=text, reply_markup=inline_btn, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Kanalga post yuborishda xatolik: {e}")

@dp.message_handler(commands=['start'], state='*')
async def start_cmd(message: types.Message, state: FSMContext):
    await state.finish()
    if await ban_tekshir(message.from_user.id, message): return
        
    db.user_qoshish(message.from_user.id, message.from_user.username, message.from_user.full_name)
    
    # Deep Linking orqali kanal tugmasidan kelganda tekshirish
    start_args = message.get_args()
    if start_args:
        # Masalan: manga_v_12, anime_v_5 ko'rinishida keladi
        parts = start_args.split("_")
        if len(parts) >= 3:
            c_type = parts[0]
            c_id = int(parts[2])
            
            if c_type == "manga":
                nomi, rasm, janr, h = db.manga_rasm_va_nomi(c_id)
                boblar = db.manga_boblar_royxati(c_id)
                await message.answer_photo(photo=rasm, caption=f"📖 **Manga:** {nomi}\n🎭 **Janr:** {janr}", reply_markup=kb.boblar_list_keyboard(boblar))
                return
            elif c_type == "anime":
                nomi, rasm, janr, h = db.anime_rasm_va_nomi(c_id)
                epizodlar = db.anime_epizodlar_royxati(c_id)
                await message.answer_photo(photo=rasm, caption=f"🎬 **Anime:** {nomi}\n🎭 **Janr:** {janr}", reply_markup=kb.epizodlar_list_keyboard(epizodlar))
                return
            elif c_type == "manhwa":
                nomi, rasm, janr, h = db.manhwa_rasm_va_nomi(c_id)
                boblar = db.manhwa_boblar_royxati(c_id)
                await message.answer_photo(photo=rasm, caption=f"🔥 **Manhwa:** {nomi}\n🎭 **Janr:** {janr}", reply_markup=kb.boblar_list_keyboard(boblar))
                return
            elif c_type == "novel":
                nomi, rasm, janr, h = db.novel_rasm_va_nomi(c_id)
                boblar = db.novel_boblar_royxati(c_id)
                await message.answer_photo(photo=rasm, caption=f"📚 **Light Novel:** {nomi}\n🎭 **Janr:** {janr}", reply_markup=kb.boblar_list_keyboard(boblar))
                return

    is_admin = True if db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN) in ["bosh", "ishchi"] else False
    text = db.sozlama_olish("welcome_text", config.STANDART_XUSH_KELIBSIZ)
    await message.answer(text, reply_markup=kb.bosh_menu(is_admin=is_admin))

# ================= ADMIN: MANGA QOSHISH =================
@dp.message_handler(lambda message: message.text == "➕ Yangi Manga Qo'shish", state="*")
async def yangi_manga_boshlash(message: types.Message):
    if not db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN): return
    await message.answer("📖 Manga nomini kiriting:", reply_markup=kb.bekor_qilish_btn())
    await BotStates.kutish_manga_nomi.set()

@dp.message_handler(state=BotStates.kutish_manga_nomi)
async def manga_nomi_olish(message: types.Message, state: FSMContext):
    await state.update_data(manga_nomi=message.text)
    await message.answer("📚 Janrini kiriting:")
    await BotStates.kutish_manga_janr.set()

@dp.message_handler(state=BotStates.kutish_manga_janr)
async def manga_janr_olish(message: types.Message, state: FSMContext):
    await state.update_data(manga_janr=message.text)
    await message.answer("📸 Muqova rasmini yuboring:")
    await BotStates.kutish_manga_rasm.set()

@dp.message_handler(state=BotStates.kutish_manga_rasm, content_types=types.ContentType.PHOTO)
async def manga_rasm_olish(message: types.Message, state: FSMContext):
    await state.update_data(manga_rasm=message.photo[-1].file_id)
    await message.answer("📌 Holati (ongoing/completed):")
    await BotStates.kutish_manga_holati.set()

@dp.message_handler(state=BotStates.kutish_manga_holati)
async def manga_holati_olish(message: types.Message, state: FSMContext):
    holati = message.text.lower().strip()
    data = await state.get_data()
    manga_id = db.yangi_manga_baza_qoshish(data['manga_nomi'], data['manga_janr'], data['manga_rasm'], holati)
    await state.finish()
    await message.answer("✅ Manga qo'shildi va kanalga xabar yuborildi!", reply_markup=kb.bosh_admin_panel())
    await kanalga_yangi_kontent_yuborish("manga", data['manga_nomi'], data['manga_janr'], data['manga_rasm'], holati, manga_id)

# ================= ADMIN: ANIME QOSHISH =================
@dp.message_handler(lambda message: message.text == "➕ Yangi Anime Qo'shish", state="*")
async def yangi_anime_boshlash(message: types.Message):
    if not db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN): return
    await message.answer("🎬 Anime nomini kiriting:", reply_markup=kb.bekor_qilish_btn())
    await BotStates.kutish_anime_nomi.set()

@dp.message_handler(state=BotStates.kutish_anime_nomi)
async def anime_nomi_olish(message: types.Message, state: FSMContext):
    await state.update_data(anime_nomi=message.text)
    await message.answer("📚 Janrini kiriting:")
    await BotStates.kutish_anime_janr.set()

@dp.message_handler(state=BotStates.kutish_anime_janr)
async def anime_janr_olish(message: types.Message, state: FSMContext):
    await state.update_data(anime_janr=message.text)
    await message.answer("📸 Muqova rasmini yuboring:")
    await BotStates.kutish_anime_rasm.set()

@dp.message_handler(state=BotStates.kutish_anime_rasm, content_types=types.ContentType.PHOTO)
async def anime_rasm_olish(message: types.Message, state: FSMContext):
    await state.update_data(anime_rasm=message.photo[-1].file_id)
    await message.answer("📌 Holati (ongoing/completed):")
    await BotStates.kutish_anime_holati.set()

@dp.message_handler(state=BotStates.kutish_anime_holati)
async def anime_holati_olish(message: types.Message, state: FSMContext):
    holati = message.text.lower().strip()
    data = await state.get_data()
    anime_id = db.yangi_anime_baza_qoshish(data['anime_nomi'], data['anime_janr'], data['anime_rasm'], holati)
    await state.finish()
    await message.answer("✅ Anime qo'shildi va kanalga xabar yuborildi!", reply_markup=kb.bosh_admin_panel())
    await kanalga_yangi_kontent_yuborish("anime", data['anime_nomi'], data['anime_janr'], data['anime_rasm'], holati, anime_id)

# ================= ADMIN: MANHWA QOSHISH =================
@dp.message_handler(lambda message: message.text == "➕ Yangi Manhwa Qo'shish", state="*")
async def yangi_manhwa_boshlash(message: types.Message):
    if not db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN): return
    await message.answer("🔥 Manhwa nomini kiriting:", reply_markup=kb.bekor_qilish_btn())
    await BotStates.kutish_manhwa_nomi.set()

@dp.message_handler(state=BotStates.kutish_manhwa_nomi)
async def manhwa_nomi_olish(message: types.Message, state: FSMContext):
    await state.update_data(manhwa_nomi=message.text)
    await message.answer("📚 Janrini kiriting:")
    await BotStates.kutish_manhwa_janr.set()

@dp.message_handler(state=BotStates.kutish_manhwa_janr)
async def manhwa_janr_olish(message: types.Message, state: FSMContext):
    await state.update_data(manhwa_janr=message.text)
    await message.answer("📸 Muqova rasmini yuboring:")
    await BotStates.kutish_manhwa_rasm.set()

@dp.message_handler(state=BotStates.kutish_manhwa_rasm, content_types=types.ContentType.PHOTO)
async def manhwa_rasm_olish(message: types.Message, state: FSMContext):
    await state.update_data(manhwa_rasm=message.photo[-1].file_id)
    await message.answer("📌 Holati (ongoing/completed):")
    await BotStates.kutish_manhwa_holati.set()

@dp.message_handler(state=BotStates.kutish_manhwa_holati)
async def manhwa_holati_olish(message: types.Message, state: FSMContext):
    holati = message.text.lower().strip()
    data = await state.get_data()
    manhwa_id = db.yangi_manhwa_baza_qoshish(data['manhwa_nomi'], data['manhwa_janr'], data['manhwa_rasm'], holati)
    await state.finish()
    await message.answer("✅ Manhwa qo'shildi va kanalga xabar yuborildi!", reply_markup=kb.bosh_admin_panel())
    await kanalga_yangi_kontent_yuborish("manhwa", data['manhwa_nomi'], data['manhwa_janr'], data['manhwa_rasm'], holati, manhwa_id)

# ================= ADMIN: LIGHT NOVEL QOSHISH =================
@dp.message_handler(lambda message: message.text == "➕ Yangi Light Novel Qo'shish", state="*")
async def yangi_novel_boshlash(message: types.Message):
    if not db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN): return
    await message.answer("📚 Light Novel nomini kiriting:", reply_markup=kb.bekor_qilish_btn())
    await BotStates.kutish_novel_nomi.set()

@dp.message_handler(state=BotStates.kutish_novel_nomi)
async def novel_nomi_olish(message: types.Message, state: FSMContext):
    await state.update_data(novel_nomi=message.text)
    await message.answer("📚 Janrini kiriting:")
    await BotStates.kutish_novel_janr.set()

@dp.message_handler(state=BotStates.kutish_novel_janr)
async def novel_janr_olish(message: types.Message, state: FSMContext):
    await state.update_data(novel_janr=message.text)
    await message.answer("📸 Muqova rasmini yuboring:")
    await BotStates.kutish_novel_rasm.set()

@dp.message_handler(state=BotStates.kutish_novel_rasm, content_types=types.ContentType.PHOTO)
async def novel_rasm_olish(message: types.Message, state: FSMContext):
    await state.update_data(novel_rasm=message.photo[-1].file_id)
    await message.answer("📌 Holati (ongoing/completed):")
    await BotStates.kutish_novel_holati.set()

@dp.message_handler(state=BotStates.kutish_novel_holati)
async def novel_holati_olish(message: types.Message, state: FSMContext):
    holati = message.text.lower().strip()
    data = await state.get_data()
    novel_id = db.yangi_novel_baza_qoshish(data['novel_nomi'], data['novel_janr'], data['novel_rasm'], holati)
    await state.finish()
    await message.answer("✅ Light Novel qo'shildi va kanalga xabar yuborildi!", reply_markup=kb.bosh_admin_panel())
    await kanalga_yangi_kontent_yuborish("novel", data['novel_nomi'], data['novel_janr'], data['novel_rasm'], holati, novel_id)


# ================= BOBLAR / EPIZODLAR YUKLASH VA KANALGA AVTO-XABAR =================
@dp.message_handler(lambda message: message.text == "➕ Yangi Bob/Epizod Qo'shish", state="*")
async def bob_qoshish_boshlash(message: types.Message):
    if not db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN): return
    # Tanlash uchun keyboard: Manga, Anime, Manhwa, Light Novel
    btn = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn.add("Manga Bob", "Anime Epizod", "Manhwa Bob", "Light Novel Bob")
    await message.answer("Qaysi kontent turiga qism qo'shmoqchisiz?", reply_markup=btn)
    await BotStates.kutish_bob_turi.set()

@dp.message_handler(state=BotStates.kutish_bob_turi)
async def bob_turi_olish(message: types.Message, state: FSMContext):
    turi = message.text
    if turi == "Manga Bob": await state.update_data(b_turi="manga")
    elif turi == "Anime Epizod": await state.update_data(b_turi="anime")
    elif turi == "Manhwa Bob": await state.update_data(b_turi="manhwa")
    elif turi == "Light Novel Bob": await state.update_data(b_turi="novel")
    else:
        await message.answer("Noto'g'ri tanlov!")
        await state.finish()
        return
    
    await message.answer("Kontent ID raqamini kiriting (Bazadagi ID):", reply_markup=kb.bekor_qilish_btn())
    await BotStates.kutish_bob_content_id.set()

@dp.message_handler(state=BotStates.kutish_bob_content_id)
async def bob_id_olish(message: types.Message, state: FSMContext):
    await state.update_data(b_id=int(message.text))
    await message.answer("Qism/Bob raqamini kiriting (Faqat raqam, masalan: 5):")
    await BotStates.kutish_bob_raqami.set()

@dp.message_handler(state=BotStates.kutish_bob_raqami)
async def bob_raqam_olish(message: types.Message, state: FSMContext):
    await state.update_data(b_raqam=int(message.text))
    await message.answer("Faylni yuboring (Rasm, Video yoki Dokument ko'rinishida):")
    await BotStates.kutish_bob_fayl.set()

@dp.message_handler(state=BotStates.kutish_bob_fayl, content_types=[types.ContentType.DOCUMENT, types.ContentType.VIDEO, types.ContentType.PHOTO])
async def bob_fayl_yakunlash(message: types.Message, state: FSMContext):
    data = await state.get_data()
    turi = data['b_turi']
    c_id = data['b_id']
    raqam = data['b_raqam']
    
    # File ID aniqlash
    if message.document: file_id = message.document.file_id
    elif message.video: file_id = message.video.file_id
    else: file_id = message.photo[-1].file_id
    
    kanallar = db.kanallar_olish()
    bot_info = await bot.get_me()
    
    if turi == "manga":
        db.yangi_bob_baza_qoshish(c_id, raqam, file_id)
        nomi, rasm, _, _ = db.manga_rasm_va_nomi(c_id)
        prefiks = "manga_v"
    elif turi == "anime":
        db.yangi_epizod_baza_qoshish(c_id, raqam, file_id)
        nomi, rasm, _, _ = db.anime_rasm_va_nomi(c_id)
        prefiks = "anime_v"
    elif turi == "manhwa":
        db.yangi_manhwa_bob_baza_qoshish(c_id, raqam, file_id)
        nomi, rasm, _, _ = db.manhwa_rasm_va_nomi(c_id)
        prefiks = "manhwa_v"
    elif turi == "novel":
        db.yangi_novel_bob_baza_qoshish(c_id, raqam, file_id)
        nomi, rasm, _, _ = db.novel_rasm_va_nomi(c_id)
        prefiks = "novel_v"

    await state.finish()
    await message.answer(f"✅ {raqam}-qism muvaffaqiyatli yuklandi!", reply_markup=kb.bosh_admin_panel())
    
    # Kanalga yangi yuklangan qism haqida avtomatik xabar yuborish
    if kanallar and nomi:
        inline_btn = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("📖 Mutolaa qilish / Ko'rish", url=f"https://t.me/{bot_info.username}?start={prefiks}_{c_id}")
        )
        text = (
            f"📣 **YANGI QISM YUKLANDI!**\n\n"
            f"📌 **Nomi:** {nomi}\n"
            f"🆕 **Yangi qism:** {raqam}-bob/epizod\n\n"
            f"⚡ Hoziroq botga kirib ko'rishingiz mumkin!"
        )
        try:
            await bot.send_photo(chat_id=kanallar[0], photo=rasm, caption=text, reply_markup=inline_btn, parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Kanalga qism xabari yuborishda xato: {e}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
