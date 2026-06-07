# bot.py - TOLIQ WEBHOOK VERSIYASI (KANAL XABARLARI BILAN)
import re
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiohttp import web

import config
import database as db
import keyboards as kb

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
db.init_db()

# Eski kodni o'chiring va o'rniga mana buni qo'ying:
WEBHOOK_HOST = os.environ.get("WEBHOOK_URL")
WEBHOOK_PATH = "/bot"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
# Webhook sozlamalari tagidan mana buni qo'shing:
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.environ.get("PORT", 8000))
class BotStates(StatesGroup):
    kutish_manga_nomi = State()
    kutish_manga_janr = State()
    kutish_manga_rasm = State()
    kutish_manga_holati = State()
    
    kutish_anime_nomi = State()
    kutish_anime_janr = State()
    kutish_anime_rasm = State()
    kutish_anime_holati = State()
    
    kutish_manhwa_nomi = State()
    kutish_manhwa_janr = State()
    kutish_manhwa_rasm = State()
    kutish_manhwa_holati = State()
    
    kutish_novel_nomi = State()
    kutish_novel_janr = State()
    kutish_novel_rasm = State()
    kutish_novel_holati = State()
    
    kutish_bob_turi = State()
    kutish_bob_content_id = State()
    kutish_bob_raqami = State()
    kutish_bob_fayl = State()
    
    kutish_admin_username = State()
    kutish_reklama = State()
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

async def kanalga_yangi_kontent_yuborish(content_type, nomi, janr, rasm, holati, content_id):
    """Kanalga batafsil yangi content xabar yuborish"""
    kanallar = db.kanallar_olish()
    if not kanallar: 
        return
    
    bot_info = await bot.get_me()
    
    if content_type == "manga":
        sarlavha = "✨ YANGI MANGA ✨"
        emoji = "📖"
        link_prefix = "manga_v"
    elif content_type == "anime":
        sarlavha = "✨ YANGI ANIME ✨"
        emoji = "🎬"
        link_prefix = "anime_v"
    elif content_type == "manhwa":
        sarlavha = "✨ YANGI MANXWA ✨"
        emoji = "📘"
        link_prefix = "manhwa_v"
    else:
        sarlavha = "✨ YANGI LIGHT NOVEL ✨"
        emoji = "📚"
        link_prefix = "novel_v"
    
    holati_display = "Ongoing" if holati.lower() == "ongoing" else "Completed"
    
    text = f"""
{sarlavha}

{emoji} <b>Nom:</b> {nomi}
📚 <b>Janri:</b> {janr}
📌 <b>Holati:</b> {holati_display}

━━━━━━━━━━━━━━━━━━
⏱️ <b>Yangi qism chiqdi!</b>

🚀 <b>Botda ko'rish:</b> @{bot_info.username}

#{content_type.lower()} #anime #manga
"""
    
    inline_btn = types.InlineKeyboardMarkup(row_width=1)
    inline_btn.add(
        types.InlineKeyboardButton(
            "📖 Mutolaa qilish / Ko'rish", 
            url=f"https://t.me/{bot_info.username}?start={link_prefix}_{content_id}"
        )
    )
    inline_btn.add(
        types.InlineKeyboardButton("Kanal", url=f"https://t.me/{kanallar[0].lstrip('@')}")
    )
    
    try:
        await bot.send_photo(
            chat_id=kanallar[0], 
            photo=rasm, 
            caption=text, 
            reply_markup=inline_btn, 
            parse_mode="HTML"
        )
        logger.info(f"✅ Kanalga {content_type} xabari: {nomi}")
    except Exception as e:
        logger.error(f"Kanal xabari yuborishda xato: {e}")

async def kanalga_yangi_qism_yuborish(content_type, content_id, content_nomi, qism_raqami, rasm):
    """Yangi bob/epizod qo'shilganda kanalga xabar"""
    kanallar = db.kanallar_olish()
    if not kanallar:
        return
    
    bot_info = await bot.get_me()
    
    if content_type == "manga":
        emoji = "📖"
        qism_type = "Bob"
        link_prefix = "manga_v"
    elif content_type == "anime":
        emoji = "🎬"
        qism_type = "Epizod"
        link_prefix = "anime_v"
    elif content_type == "manhwa":
        emoji = "📘"
        qism_type = "Bob"
        link_prefix = "manhwa_v"
    else:
        emoji = "📚"
        qism_type = "Bob"
        link_prefix = "novel_v"
    
    text = f"""
📣 <b>YANGI QISM YUKLANDI!</b>

{emoji} <b>{content_nomi}</b>
🆕 <b>{qism_raqami}-{qism_type}</b>

━━━━━━━━━━━━━━━━━━
⏱️ <b>Hoziroq ko'rishingiz mumkin!</b>

🚀 <b>Botda ko'rish:</b> @{bot_info.username}

#{content_type.lower()} #anime #manga
"""
    
    inline_btn = types.InlineKeyboardMarkup(row_width=1)
    inline_btn.add(
        types.InlineKeyboardButton(
            "📖 O'qish / Ko'rish",
            url=f"https://t.me/{bot_info.username}?start={link_prefix}_{content_id}"
        )
    )
    inline_btn.add(
        types.InlineKeyboardButton("Kanal", url=f"https://t.me/{kanallar[0].lstrip('@')}")
    )
    
    try:
        await bot.send_photo(
            chat_id=kanallar[0],
            photo=rasm,
            caption=text,
            reply_markup=inline_btn,
            parse_mode="HTML"
        )
        logger.info(f"✅ Kanalga {qism_type} xabari: {content_nomi} {qism_raqami}")
    except Exception as e:
        logger.error(f"Qism xabari yuborishda xato: {e}")

@dp.message_handler(commands=['start'], state='*')
async def start_cmd(message: types.Message, state: FSMContext):
    await state.finish()
    if await ban_tekshir(message.from_user.id, message): return
    db.user_qoshish(message.from_user.id, message.from_user.username, message.from_user.full_name)
    
    start_args = message.get_args()
    if start_args:
        parts = start_args.split("_")
        if len(parts) >= 3:
            c_type = parts[0]
            c_id = int(parts[2])
            if c_type == "manga":
                nomi, rasm, janr, h = db.manga_rasm_va_nomi(c_id)
                boblar = db.manga_boblar_royxati(c_id)
                if rasm and boblar:
                    await message.answer_photo(photo=rasm, caption=f"📖 **Manga:** {nomi}\n🎭 **Janr:** {janr}", reply_markup=kb.boblar_list_keyboard(boblar), parse_mode="Markdown")
                return

    is_admin = True if db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN) in ["bosh", "ishchi"] else False
    text = db.sozlama_olish("welcome_text", config.STANDART_XUSH_KELIBSIZ)
    await message.answer(text, reply_markup=kb.bosh_menu(is_admin=is_admin))

@dp.message_handler(lambda message: message.text == "👑 Admin Panel", state='*')
async def admin_panel(message: types.Message, state: FSMContext):
    await state.finish()
    r = db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN)
    if r == "bosh":
        await message.answer("👑 Bosh Admin Paneli", reply_markup=kb.bosh_admin_panel())
    elif r == "ishchi":
        await message.answer("🛠 Ishchi Admin Paneli", reply_markup=kb.ishchi_admin_panel())
    else:
        await message.answer("⚠️ Siz admin emassiz!")

@dp.message_handler(lambda message: message.text == "🚪 Panelda Chiqish", state='*')
async def chiqish(message: types.Message, state: FSMContext):
    await state.finish()
    is_admin = True if db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN) in ["bosh", "ishchi"] else False
    await message.answer("👋 Paneldan chiqdingiz!", reply_markup=kb.bosh_menu(is_admin=is_admin))

@dp.message_handler(lambda message: message.text == "❌ Bekor qilish", state='*')
async def bekor(message: types.Message, state: FSMContext):
    await state.finish()
    is_admin = True if db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN) in ["bosh", "ishchi"] else False
    await message.answer("❌ Bekor qilindi!", reply_markup=kb.bosh_menu(is_admin=is_admin))

# === MANGA QOSHISH ===
@dp.message_handler(lambda message: message.text == "➕ Yangi Manga Qo'shish", state='*')
async def yangi_manga(message: types.Message):
    if not db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN): return
    await message.answer("📖 Manga nomini kiriting:", reply_markup=kb.bekor_qilish_btn())
    await BotStates.kutish_manga_nomi.set()

@dp.message_handler(state=BotStates.kutish_manga_nomi)
async def manga_nomi(message: types.Message, state: FSMContext):
    await state.update_data(manga_nomi=message.text)
    await message.answer("📚 Janrini kiriting:")
    await BotStates.kutish_manga_janr.set()

@dp.message_handler(state=BotStates.kutish_manga_janr)
async def manga_janr(message: types.Message, state: FSMContext):
    await state.update_data(manga_janr=message.text)
    await message.answer("📸 Rasm yuboring:")
    await BotStates.kutish_manga_rasm.set()

@dp.message_handler(state=BotStates.kutish_manga_rasm, content_types=types.ContentType.PHOTO)
async def manga_rasm(message: types.Message, state: FSMContext):
    await state.update_data(manga_rasm=message.photo[-1].file_id)
    await message.answer("📌 Holati (ongoing/completed):")
    await BotStates.kutish_manga_holati.set()

@dp.message_handler(state=BotStates.kutish_manga_holati)
async def manga_holati(message: types.Message, state: FSMContext):
    holati = message.text.lower().strip()
    data = await state.get_data()
    manga_id = db.yangi_manga_baza_qoshish(data['manga_nomi'], data['manga_janr'], data['manga_rasm'], holati)
    await state.finish()
    await message.answer("✅ Manga qo'shildi!", reply_markup=kb.bosh_admin_panel())
    await kanalga_yangi_kontent_yuborish("manga", data['manga_nomi'], data['manga_janr'], data['manga_rasm'], holati, manga_id)

# === ANIME QOSHISH ===
@dp.message_handler(lambda message: message.text == "➕ Yangi Anime Qo'shish", state='*')
async def yangi_anime(message: types.Message):
    if not db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN): return
    await message.answer("🎬 Anime nomini kiriting:", reply_markup=kb.bekor_qilish_btn())
    await BotStates.kutish_anime_nomi.set()

@dp.message_handler(state=BotStates.kutish_anime_nomi)
async def anime_nomi(message: types.Message, state: FSMContext):
    await state.update_data(anime_nomi=message.text)
    await message.answer("📚 Janrini kiriting:")
    await BotStates.kutish_anime_janr.set()

@dp.message_handler(state=BotStates.kutish_anime_janr)
async def anime_janr(message: types.Message, state: FSMContext):
    await state.update_data(anime_janr=message.text)
    await message.answer("📸 Rasm yuboring:")
    await BotStates.kutish_anime_rasm.set()

@dp.message_handler(state=BotStates.kutish_anime_rasm, content_types=types.ContentType.PHOTO)
async def anime_rasm(message: types.Message, state: FSMContext):
    await state.update_data(anime_rasm=message.photo[-1].file_id)
    await message.answer("📌 Holati (ongoing/completed):")
    await BotStates.kutish_anime_holati.set()

@dp.message_handler(state=BotStates.kutish_anime_holati)
async def anime_holati(message: types.Message, state: FSMContext):
    holati = message.text.lower().strip()
    data = await state.get_data()
    anime_id = db.yangi_anime_baza_qoshish(data['anime_nomi'], data['anime_janr'], data['anime_rasm'], holati)
    await state.finish()
    await message.answer("✅ Anime qo'shildi!", reply_markup=kb.bosh_admin_panel())
    await kanalga_yangi_kontent_yuborish("anime", data['anime_nomi'], data['anime_janr'], data['anime_rasm'], holati, anime_id)

# === MANHWA QOSHISH ===
@dp.message_handler(lambda message: message.text == "➕ Yangi Manxwa Qo'shish", state='*')
async def yangi_manhwa(message: types.Message):
    if not db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN): return
    await message.answer("📘 Manxwa nomini kiriting:", reply_markup=kb.bekor_qilish_btn())
    await BotStates.kutish_manhwa_nomi.set()

@dp.message_handler(state=BotStates.kutish_manhwa_nomi)
async def manhwa_nomi(message: types.Message, state: FSMContext):
    await state.update_data(manhwa_nomi=message.text)
    await message.answer("📚 Janrini kiriting:")
    await BotStates.kutish_manhwa_janr.set()

@dp.message_handler(state=BotStates.kutish_manhwa_janr)
async def manhwa_janr(message: types.Message, state: FSMContext):
    await state.update_data(manhwa_janr=message.text)
    await message.answer("📸 Rasm yuboring:")
    await BotStates.kutish_manhwa_rasm.set()

@dp.message_handler(state=BotStates.kutish_manhwa_rasm, content_types=types.ContentType.PHOTO)
async def manhwa_rasm(message: types.Message, state: FSMContext):
    await state.update_data(manhwa_rasm=message.photo[-1].file_id)
    await message.answer("📌 Holati (ongoing/completed):")
    await BotStates.kutish_manhwa_holati.set()

@dp.message_handler(state=BotStates.kutish_manhwa_holati)
async def manhwa_holati(message: types.Message, state: FSMContext):
    holati = message.text.lower().strip()
    data = await state.get_data()
    manhwa_id = db.yangi_manhwa_baza_qoshish(data['manhwa_nomi'], data['manhwa_janr'], data['manhwa_rasm'], holati)
    await state.finish()
    await message.answer("✅ Manxwa qo'shildi!", reply_markup=kb.bosh_admin_panel())
    await kanalga_yangi_kontent_yuborish("manhwa", data['manhwa_nomi'], data['manhwa_janr'], data['manhwa_rasm'], holati, manhwa_id)

# === LIGHT NOVEL QOSHISH ===
@dp.message_handler(lambda message: message.text == "➕ Yangi Light Novel Qo'shish", state='*')
async def yangi_novel(message: types.Message):
    if not db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN): return
    await message.answer("📚 Light Novel nomini kiriting:", reply_markup=kb.bekor_qilish_btn())
    await BotStates.kutish_novel_nomi.set()

@dp.message_handler(state=BotStates.kutish_novel_nomi)
async def novel_nomi(message: types.Message, state: FSMContext):
    await state.update_data(novel_nomi=message.text)
    await message.answer("📚 Janrini kiriting:")
    await BotStates.kutish_novel_janr.set()

@dp.message_handler(state=BotStates.kutish_novel_janr)
async def novel_janr(message: types.Message, state: FSMContext):
    await state.update_data(novel_janr=message.text)
    await message.answer("📸 Rasm yuboring:")
    await BotStates.kutish_novel_rasm.set()

@dp.message_handler(state=BotStates.kutish_novel_rasm, content_types=types.ContentType.PHOTO)
async def novel_rasm(message: types.Message, state: FSMContext):
    await state.update_data(novel_rasm=message.photo[-1].file_id)
    await message.answer("📌 Holati (ongoing/completed):")
    await BotStates.kutish_novel_holati.set()

@dp.message_handler(state=BotStates.kutish_novel_holati)
async def novel_holati(message: types.Message, state: FSMContext):
    holati = message.text.lower().strip()
    data = await state.get_data()
    novel_id = db.yangi_novel_baza_qoshish(data['novel_nomi'], data['novel_janr'], data['novel_rasm'], holati)
    await state.finish()
    await message.answer("✅ Light Novel qo'shildi!", reply_markup=kb.bosh_admin_panel())
    await kanalga_yangi_kontent_yuborish("novel", data['novel_nomi'], data['novel_janr'], data['novel_rasm'], holati, novel_id)

# === BOB/EPIZOD QOSHISH ===
@dp.message_handler(lambda message: message.text == "➕ Yangi Bob Qo'shish", state='*')
async def bob_qoshish(message: types.Message):
    if not db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN): return
    btn = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn.add("Manga", "Anime", "Manxwa", "Light Novel")
    await message.answer("Qaysi turga qism qo'shmoqchisiz?", reply_markup=btn)
    await BotStates.kutish_bob_turi.set()

@dp.message_handler(state=BotStates.kutish_bob_turi)
async def bob_turi(message: types.Message, state: FSMContext):
    turi_map = {"Manga": "manga", "Anime": "anime", "Manxwa": "manhwa", "Light Novel": "novel"}
    if message.text not in turi_map:
        await message.answer("❌ Noto'g'ri tanlov!")
        return
    await state.update_data(b_turi=turi_map[message.text])
    await message.answer("Content ID raqamini kiriting:", reply_markup=kb.bekor_qilish_btn())
    await BotStates.kutish_bob_content_id.set()

@dp.message_handler(state=BotStates.kutish_bob_content_id)
async def bob_id(message: types.Message, state: FSMContext):
    try:
        await state.update_data(b_id=int(message.text))
        await message.answer("Bob/Epizod raqamini kiriting:")
        await BotStates.kutish_bob_raqami.set()
    except:
        await message.answer("❌ Raqam kiriting!")

@dp.message_handler(state=BotStates.kutish_bob_raqami)
async def bob_raqam(message: types.Message, state: FSMContext):
    try:
        await state.update_data(b_raqam=int(message.text))
        await message.answer("Faylni yuboring:")
        await BotStates.kutish_bob_fayl.set()
    except:
        await message.answer("❌ Raqam kiriting!")

@dp.message_handler(state=BotStates.kutish_bob_fayl, content_types=[types.ContentType.DOCUMENT, types.ContentType.PHOTO, types.ContentType.VIDEO])
async def bob_fayl(message: types.Message, state: FSMContext):
    data = await state.get_data()
    turi = data['b_turi']
    c_id = data['b_id']
    raqam = data['b_raqam']
    
    if message.document: file_id = message.document.file_id
    elif message.video: file_id = message.video.file_id
    else: file_id = message.photo[-1].file_id
    
    if turi == "manga":
        db.yangi_bob_baza_qoshish(c_id, raqam, file_id)
        nomi, rasm, _, _ = db.manga_rasm_va_nomi(c_id)
    elif turi == "anime":
        db.yangi_epizod_baza_qoshish(c_id, raqam, file_id)
        nomi, rasm, _, _ = db.anime_rasm_va_nomi(c_id)
    elif turi == "manhwa":
        db.yangi_manhwa_bob_baza_qoshish(c_id, raqam, file_id)
        nomi, rasm, _, _ = db.manhwa_rasm_va_nomi(c_id)
    elif turi == "novel":
        db.yangi_novel_bob_baza_qoshish(c_id, raqam, file_id)
        nomi, rasm, _, _ = db.novel_rasm_va_nomi(c_id)

    await state.finish()
    await message.answer(f"✅ {raqam}-qism yuklandi!", reply_markup=kb.bosh_admin_panel())
    
    # KANALGA YANGI QISM XABARI
    if nomi and rasm:
        await kanalga_yangi_qism_yuborish(turi, c_id, nomi, raqam, rasm)

# === BOSHQA ADMIN HANDLERS ===
@dp.message_handler(lambda message: message.text == "💼 Reklama matnini o'zgartirish", state='*')
async def reklama_matn_ozgartir(message: types.Message):
    if db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN) != "bosh": return
    await message.answer("📝 Yangi reklama matnini kiriting:", reply_markup=kb.bekor_qilish_btn())
    await BotStates.kutish_reklama.set()

@dp.message_handler(state=BotStates.kutish_reklama)
async def reklama_matn_saqlash(message: types.Message, state: FSMContext):
    db.sozlama_yangilash("reklama_matn", message.text)
    await state.finish()
    await message.answer("✅ Saqlandi!", reply_markup=kb.bosh_admin_panel())

@dp.message_handler(lambda message: message.text == "👤 Bog'lanish Userni O'zgartirish", state='*')
async def username_ozgartir(message: types.Message):
    if db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN) != "bosh": return
    hozirgi = db.sozlama_olish("bosh_admin_username", config.STANDART_ADMIN_USERNAME)
    await message.answer(f"Hozirgi: {hozirgi}\n\nYangi username kiriting (@bilan):", reply_markup=kb.bekor_qilish_btn())
    await BotStates.kutish_admin_username.set()

@dp.message_handler(state=BotStates.kutish_admin_username)
async def username_saqlash(message: types.Message, state: FSMContext):
    username = message.text.strip()
    if not username.startswith("@"):
        await message.answer("❌ @ bilan boshlang!")
        return
    db.sozlama_yangilash("bosh_admin_username", username)
    await state.finish()
    await message.answer(f"✅ O'zgartirildi: {username}", reply_markup=kb.bosh_admin_panel())

@dp.message_handler(lambda message: message.text == "🔗 Majburiy obuna sozlash", state='*')
async def obuna_boshqaruv(message: types.Message):
    if db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN) != "bosh": return
    await message.answer("🔗 Majburiy obuna boshqaruvi:", reply_markup=kb.majburiy_obuna_boshqaruv())

@dp.message_handler(lambda message: message.text == "➕ Kanal link qo'shish", state='*')
async def kanal_qoshish(message: types.Message):
    if db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN) != "bosh": return
    await message.answer("📢 Kanal linkini kiriting:", reply_markup=kb.bekor_qilish_btn())
    await BotStates.kutish_kanal_link.set()

@dp.message_handler(state=BotStates.kutish_kanal_link)
async def kanal_saqlash(message: types.Message, state: FSMContext):
    db.kanal_qoshish(message.text.strip())
    await state.finish()
    await message.answer("✅ Kanal qo'shildi!", reply_markup=kb.majburiy_obuna_boshqaruv())

@dp.message_handler(lambda message: message.text == "📊 Hozirgi kanallar", state='*')
async def kanallar_ko_rsat(message: types.Message):
    if db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN) != "bosh": return
    kanallar = db.kanallar_olish()
    if not kanallar:
        await message.answer("📭 Kanal yo'q", reply_markup=kb.majburiy_obuna_boshqaruv())
        return
    matn = "📊 Kanallar:\n\n"
    for i, k in enumerate(kanallar, 1):
        matn += f"{i}. {k}\n"
    await message.answer(matn, reply_markup=kb.majburiy_obuna_boshqaruv())

@dp.message_handler(lambda message: message.text == "📊 Statistika", state='*')
async def statistika(message: types.Message):
    if db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN) != "bosh": return
    stat = db.statistika_olish()
    matn = f"📊 **STATISTIKA**\n\n👥 Users: {stat['users']}\n📖 Manga Bobs: {stat['manga_bobs']}\n🎬 Anime Eps: {stat['anime_episodes']}"
    await message.answer(matn, reply_markup=kb.bosh_admin_panel(), parse_mode="Markdown")

@dp.message_handler(lambda message: message.text == "💼 Reklama xizmati", state='*')
async def reklama_xizmati(message: types.Message):
    if await ban_tekshir(message.from_user.id, message): return
    admin_username = db.sozlama_olish("bosh_admin_username", config.STANDART_ADMIN_USERNAME)
    reklama_matn = db.sozlama_olish("reklama_matn", config.STANDART_REKLAMA)
    markup = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton(f"👤 {admin_username} ga yozish", url=f"https://t.me/{admin_username.lstrip('@')}")
    )
    await message.answer(reklama_matn, reply_markup=markup, parse_mode="HTML")

# === WEBHOOK SERVER ===
async def handle_webhook(request: web.Request) -> web.Response:
    try:
        json_data = await request.json()
        update = types.Update(**json_data)
        await dp.feed_update(bot, update)
        return web.Response(text="ok")
    except Exception as e:
        logger.error(f"Webhook xatosi: {e}")
        return web.Response(text="error", status=400)

async def on_startup(app):
    logger.info(f"Webhook: {WEBHOOK_URL}")
    try:
        await bot.set_webhook(WEBHOOK_URL)
        logger.info("✅ Webhook o'rnatildi")
    except Exception as e:
        logger.error(f"Webhook xatosi: {e}")

async def on_shutdown(app):
    logger.info("Bot o'chmoqda...")
    await bot.delete_webhook()
    await bot.session.close()

async def health_check(request: web.Request) -> web.Response:
    return web.Response(text="OK", status=200)

def create_app() -> web.Application:
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle_webhook)
    app.router.add_get('/health', health_check)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app

if __name__ == '__main__':
    logger.info(f"Server {WEBAPP_PORT} portida ishga tushmoquyapti...")
    app = create_app()
    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)
