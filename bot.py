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
    
    kutish_bob_content_id = State()
    kutish_bob_raqami = State()
    kutish_bob_fayl = State()
    
    kutish_admin_id = State()
    kutish_welcome = State()
    kutish_reklama = State()
    kutish_admin_username = State()
    kutish_kanal_link = State()
    kutish_yangilik = State()
    kutish_feedback = State()
    kutish_komment = State()
    kutish_rassilka = State()
    kutish_ban_id = State()
    kutish_del_kanal = State()

async def ban_tekshir(user_id, message: types.Message) -> bool:
    ban_status = db.user_ban_tekshirish_kengaytirilgan(user_id)
    if ban_status == "permanent":
        await message.answer("🚫 Siz botdan butunlay bloklangansiz!")
        return True
    elif isinstance(ban_status, int):
        soat = ban_status // 3600
        minut = (ban_status % 3600) // 60
        if soat > 0:
            await message.answer(f"⏳ Siz qoidabuzarlik tufayli vaqtinchalik cheklangansiz.\n⏱ Qolgan vaqt: {soat} soat, {minut} daqiqa.")
        else:
            await message.answer(f"⏳ Siz vaqtinchalik cheklangansiz.\n⏱ Qolgan vaqt: {minut} daqiqa.")
        return True
    return False

@dp.message_handler(commands=['start'], state='*')
async def start_cmd(message: types.Message, state: FSMContext):
    await state.finish()
    if await ban_tekshir(message.from_user.id, message): return
        
    db.user_qoshish(
        user_id=message.from_user.id,
        username=message.from_user.username,
        name=message.from_user.full_name
    )
    r = db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN)
    is_admin = True if r in ["bosh", "ishchi"] else False
    
    kanallar = db.kanallar_olish()
    if kanallar:
        await message.answer("🚨 Botdan to'liq foydalanish uchun hamkor kanallarimizga a'zo bo'ling:", reply_markup=kb.majburiy_obuna_markup(kanallar))
        return
        
    text = db.sozlama_olish("welcome_text", config.STANDART_XUSH_KELIBSIZ)
    await message.answer(text, reply_markup=kb.bosh_menu(is_admin=is_admin))

@dp.callback_query_handler(text="tekshirish_obuna", state='*')
async def tekshirish_obuna_callback(call: types.CallbackQuery):
    ban_status = db.user_ban_tekshirish_kengaytirilgan(call.from_user.id)
    if ban_status == "permanent" or isinstance(ban_status, int):
        return await call.answer("🚫 Sizda cheklov mavjud!", show_alert=True)
        
    db.user_qoshish(call.from_user.id, call.from_user.username, call.from_user.full_name)
    r = db.admin_tekshirish(call.from_user.id, config.BOSH_ADMIN)
    is_admin = True if r in ["bosh", "ishchi"] else False
    text = db.sozlama_olish("welcome_text", config.STANDART_XUSH_KELIBSIZ)
    await call.message.answer(text, reply_markup=kb.bosh_menu(is_admin=is_admin))
    await call.answer()

@dp.message_handler(commands=['admin'], state='*')
@dp.message_handler(lambda message: message.text == "👑 Admin Panel", state='*')
async def admin_cmd(message: types.Message, state: FSMContext):
    await state.finish()
    if await ban_tekshir(message.from_user.id, message): return
    r = db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN)
    if r == "bosh":
        await message.answer("👑 Bosh Admin paneli!", reply_markup=kb.bosh_admin_panel())
    elif r == "ishchi":
        await message.answer("🛠 Ishchi Admin paneli!", reply_markup=kb.ishchi_admin_panel())
    else:
        await message.answer("⚠️ Siz admin emassiz!")

@dp.message_handler(lambda message: message.text == "❌ Bekor qilish", state='*')
async def cancel_action(message: types.Message, state: FSMContext):
    await state.finish()
    r = db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN)
    is_admin = True if r in ["bosh", "ishchi"] else False
    await message.answer("Bekor qilindi", reply_markup=kb.bosh_menu(is_admin=is_admin))

# === REKLAMA XIZMATI ===
@dp.message_handler(lambda message: message.text == "💼 Reklama xizmati", state='*')
async def reklama_xizmati(message: types.Message):
    if await ban_tekshir(message.from_user.id, message): return
    
    admin_username = db.sozlama_olish("bosh_admin_username", config.STANDART_ADMIN_USERNAME)
    reklama_matn = db.sozlama_olish("reklama_matn", config.STANDART_REKLAMA)
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(
            f"👤 {admin_username} ga yozish",
            url=f"https://t.me/{admin_username.lstrip('@')}"
        )
    )
    
    await message.answer(reklama_matn, reply_markup=markup, parse_mode="HTML")

# === DAVOM ETTIRISH ===
@dp.message_handler(lambda message: message.text == "🔄 Davom ettirish", state='*')
async def davom_ettirish_handler(message: types.Message):
    if await ban_tekshir(message.from_user.id, message): return
    
    tarix = db.user_tarix_olish_hammasi(message.from_user.id)
    markup = kb.davom_tugmasini_generatsiya_qil(tarix)
    
    if not markup or not markup.keyboard or len(markup.keyboard) == 0:
        r = db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN)
        is_admin = True if r in ["bosh", "ishchi"] else False
        await message.answer("📭 Hali hech narsa o'qimagansizsiz!", reply_markup=kb.bosh_menu(is_admin=is_admin))
        return
    
    await message.answer("🔄 To'xtab qolgan joydan davom etish:", reply_markup=markup)

@dp.callback_query_handler(lambda call: call.data.startswith("davom_"))
async def davom_callback(call: types.CallbackQuery):
    if await ban_tekshir(call.from_user.id, call.message): return
    
    parts = call.data.replace("davom_", "").split("_", 2)
    content_type = parts[0]
    nomi = parts[1] if len(parts) > 1 else ""
    raqam = int(parts[2]) if len(parts) > 2 else 0
    
    if not nomi or not raqam:
        await call.answer("❌ Xato!", show_alert=True)
        return
    
    # Content ID ni nomi bilan topish
    if content_type == "manga":
        all_content = db.hamma_mangalar_id_bilan()
    elif content_type == "anime":
        all_content = db.hamma_animalar_id_bilan()
    elif content_type == "manhwa":
        all_content = db.hamma_manxwalar_id_bilan()
    else:
        all_content = db.hamma_novellar_id_bilan()
    
    content_id = None
    for c_id, c_nomi in all_content:
        if c_nomi == nomi:
            content_id = c_id
            break
    
    if not content_id:
        await call.answer("Content topilmadi!", show_alert=True)
        return
    
    # Content malumotini oladi
    if content_type == "manga":
        boblar = db.manga_boblar_royxati(content_id)
        for bob_id, bob_raq in boblar:
            if bob_raq == raqam:
                info = db.bob_malumot(bob_id)
                if info:
                    nomi, bob_raqami, file_id, likes, manga_id, janr, holati = info
                    await call.message.answer_photo(
                        photo=file_id,
                        caption=f"📖 <b>{nomi}</b>\n{bob_raqami}-Bob\n📋 {janr}\n📌 {holati}",
                        parse_mode="HTML"
                    )
                    db.user_tarix_yangilash(call.from_user.id, "manga", nomi, bob_raqami)
                break
    # Anime, Manhwa, Novel uchun ham shunga o'xshash...
    
    await call.answer()

# === BOG'LANISH USERNAME O'ZGARTIRISH ===
@dp.message_handler(lambda message: message.text == "👤 Bog'lanish Userni O'zgartirish", state='*')
async def bog_lanish_username_ozgartir(message: types.Message):
    if db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN) != "bosh": 
        return await message.answer("⚠️ Faqat Bosh Admin ruxsati bor!")
    
    hozirgi = db.sozlama_olish("bosh_admin_username", config.STANDART_ADMIN_USERNAME)
    await message.answer(
        f"👤 Hozirgi: <b>{hozirgi}</b>\n\nYangi username kiriting (@bilan):",
        reply_markup=kb.bekor_qilish_btn(),
        parse_mode="HTML"
    )
    await BotStates.kutish_admin_username.set()

@dp.message_handler(state=BotStates.kutish_admin_username)
async def bog_lanish_username_saqlash(message: types.Message, state: FSMContext):
    username = message.text.strip()
    if not username.startswith("@") or len(username) < 2:
        await message.answer("❌ Noto'g'ri format! @username ko'rinishida yozing.")
        return
    
    db.sozlama_yangilash("bosh_admin_username", username)
    await state.finish()
    await message.answer(f"✅ O'zgartirildi: <b>{username}</b>", reply_markup=kb.bosh_admin_panel(), parse_mode="HTML")

# === REKLAMA MATNINI O'ZGARTIRISH ===
@dp.message_handler(lambda message: message.text == "💼 Reklama matnini o'zgartirish")
async def reklama_matn_ozgartir(message: types.Message):
    if db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN) != "bosh": return
    await message.answer("📝 Yangi reklama matnini kiriting:", reply_markup=kb.bekor_qilish_btn())
    await BotStates.kutish_reklama.set()

@dp.message_handler(state=BotStates.kutish_reklama)
async def reklama_matn_saqlash(message: types.Message, state: FSMContext):
    db.sozlama_yangilash("reklama_matn", message.text)
    await state.finish()
    await message.answer("✅ Saqlandi!", reply_markup=kb.bosh_admin_panel())

# === MAJBURIY OBUNA ===
@dp.message_handler(lambda message: message.text == "🔗 Majburiy obuna sozlash", state='*')
async def majburiy_obuna_boshqaruv(message: types.Message):
    if db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN) != "bosh": return
    await message.answer("🔗 Majburiy obuna boshqaruvi:", reply_markup=kb.majburiy_obuna_boshqaruv())

@dp.message_handler(lambda message: message.text == "➕ Kanal link qo'shish", state='*')
async def kanal_link_qoshish(message: types.Message):
    if db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN) != "bosh": return
    await message.answer("📢 Kanal linkini kiriting (masalan: @manga_channel):", reply_markup=kb.bekor_qilish_btn())
    await BotStates.kutish_kanal_link.set()

@dp.message_handler(state=BotStates.kutish_kanal_link)
async def kanal_link_saqlash(message: types.Message, state: FSMContext):
    link = message.text.strip()
    db.kanal_qoshish(link)
    await state.finish()
    await message.answer(f"✅ Kanal qo'shildi: <b>{link}</b>", reply_markup=kb.majburiy_obuna_boshqaruv(), parse_mode="HTML")

@dp.message_handler(lambda message: message.text == "📊 Hozirgi kanallar", state='*')
async def hozirgi_kanallar_ko_rsat(message: types.Message):
    if db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN) != "bosh": return
    kanallar = db.kanallar_olish()
    if not kanallar:
        await message.answer("📭 Hali kanal yo'q", reply_markup=kb.majburiy_obuna_boshqaruv())
        return
    
    matn = "📊 Hozirgi kanallar:\n\n"
    for i, k in enumerate(kanallar, 1):
        matn += f"{i}. {k}\n"
    
    await message.answer(matn, reply_markup=kb.majburiy_obuna_boshqaruv())

@dp.message_handler(lambda message: message.text == "🗑 Kanal link o'chirish", state='*')
async def kanal_link_ochir(message: types.Message):
    if db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN) != "bosh": return
    kanallar = db.kanallar_olish()
    if not kanallar:
        await message.answer("📭 Hali kanal yo'q", reply_markup=kb.majburiy_obuna_boshqaruv())
        return
    
    markup = kb.kanallar_tanlash_inline(kanallar)
    await message.answer("🗑 Qaysi kanalni o'chirish?", reply_markup=markup)

@dp.callback_query_handler(lambda call: call.data.startswith("del_kanal_"))
async def del_kanal_callback(call: types.CallbackQuery):
    kanal = call.data.replace("del_kanal_", "")
    db.kanal_ochirish(kanal)
    await call.answer(f"✅ {kanal} o'chirildi!")
    await call.message.edit_text("🗑 O'chirildi!")

# === MANGA QOSHISH ===
@dp.message_handler(lambda message: message.text == "➕ Yangi Manga Qo'shish")
async def yangi_manga_boshlash(message: types.Message):
    r = db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN)
    if not r: return await message.answer("❌ Ruxsat berilmagan!")
    await message.answer("📖 Manga nomini kiriting:", reply_markup=kb.bekor_qilish_btn())
    await BotStates.kutish_manga_nomi.set()

@dp.message_handler(state=BotStates.kutish_manga_nomi)
async def manga_nomi_olish(message: types.Message, state: FSMContext):
    await state.update_data(manga_nomi=message.text)
    await message.answer("📚 Janrni kiriting (masalan: Ekshon, Fantasy):")
    await BotStates.kutish_manga_janr.set()

@dp.message_handler(state=BotStates.kutish_manga_janr)
async def manga_janr_olish(message: types.Message, state: FSMContext):
    await state.update_data(manga_janr=message.text)
    await message.answer("📸 Rasm yuboring:")
    await BotStates.kutish_manga_rasm.set()

@dp.message_handler(state=BotStates.kutish_manga_rasm, content_types=types.ContentType.PHOTO)
async def manga_rasm_olish(message: types.Message, state: FSMContext):
    rasm_id = message.photo[-1].file_id
    await state.update_data(manga_rasm=rasm_id)
    await message.answer("📌 Holati (ongoing/completed):")
    await BotStates.kutish_manga_holati.set()

@dp.message_handler(state=BotStates.kutish_manga_holati)
async def manga_holati_olish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    nomi = data.get("manga_nomi")
    janr = data.get("manga_janr")
    rasm = data.get("manga_rasm")
    holati = message.text.lower()
    
    if holati not in ["ongoing", "completed"]:
        await message.answer("❌ ongoing yoki completed yozing!")
        return
    
    manga_id = db.yangi_manga_baza_qoshish(nomi, janr, rasm, holati)
    
    if manga_id:
        await state.finish()
        await message.answer(
            f"✅ Manga qo'shildi!\n\n📖 {nomi}\n📚 {janr}\n📌 {holati}",
            reply_markup=kb.bosh_admin_panel()
        )
        
        # Kanal xabari
        kanallar = db.kanallar_olish()
        if kanallar:
            kanal = kanallar[0]
            await bot.send_photo(
                kanal,
                photo=rasm,
                caption=f"🎉 <b>YANGI MANGA!</b>\n\n📖 <b>{nomi}</b>\n📚 Janr: {janr}\n📌 Holati: {holati}",
                parse_mode="HTML"
            )
    else:
        await message.answer("❌ Xato! Manga nomi takrorlanadi bo'lishi mumkin.")

# === ANIME QOSHISH (Shunga o'xshash) ===
# ... Anime, Manhwa, Light Novel uchun ham shunga o'xshash handlers ...

# === BOB/EPIZOD QOSHISH ===
@dp.message_handler(lambda message: message.text == "➕ Yangi Bob Qo'shish")
async def yangi_bob_boshlash(message: types.Message):
    r = db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN)
    if not r: return
    mangalar = db.hamma_mangalar_id_bilan()
    if not mangalar: return await message.answer("📭 Manga yo'q!")
    await message.answer("📖 Manga tanlang:", reply_markup=kb.content_tanlash_inline(mangalar, "addbob_manga"))

@dp.callback_query_handler(lambda call: call.data.startswith("addbob_manga_"))
async def manga_bob_tanlash(call: types.CallbackQuery, state: FSMContext):
    manga_id = int(call.data.replace("addbob_manga_", ""))
    await state.update_data(bob_manga_id=manga_id)
    await call.message.answer("📌 Bob raqamini kiriting:")
    await BotStates.kutish_bob_raqami.set()

@dp.message_handler(state=BotStates.kutish_bob_raqami)
async def bob_raqam_olish(message: types.Message, state: FSMContext):
    try:
        raqam = int(message.text)
        await state.update_data(bob_raqami=raqam)
        await message.answer("📄 Bob faylini yuboring (PDF yoki rasm):")
        await BotStates.kutish_bob_fayl.set()
    except:
        await message.answer("❌ Raqam kiriting!")

@dp.message_handler(state=BotStates.kutish_bob_fayl, content_types=[types.ContentType.DOCUMENT, types.ContentType.PHOTO])
async def bob_fayl_olish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    manga_id = data.get("bob_manga_id")
    raqam = data.get("bob_raqami")
    
    if message.document:
        file_id = message.document.file_id
    else:
        file_id = message.photo[-1].file_id
    
    db.yangi_bob_baza_qoshish(manga_id, raqam, file_id)
    await state.finish()
    
    manga_nomi, _ , _, _ = db.manga_rasm_va_nomi(manga_id)
    await message.answer(
        f"✅ Bob qo'shildi!\n\n📖 {manga_nomi}\n📌 {raqam}-Bob",
        reply_markup=kb.bosh_admin_panel()
    )

# === STATISTIKA ===
@dp.message_handler(lambda message: message.text == "📊 Statistika")
async def statistika_show(message: types.Message):
    if db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN) != "bosh": return
    stat = db.statistika_olish()
    matn = f"""
📊 <b>STATISTIKA</b>

👥 Foydalanuvchilar: {stat['users']}
📖 Manga Boblari: {stat['manga_bobs']}
🎬 Anime Epizodlari: {stat['anime_episodes']}

📈 Jami: {stat['total']}
    """
    await message.answer(matn.strip(), parse_mode="HTML", reply_markup=kb.bosh_admin_panel())

# === FOYDALANUVCHILAR RO'YXATI ===
@dp.message_handler(lambda message: message.text == "👥 Foydalanuvchilar ro'yxati")
async def users_list_show(message: types.Message):
    if db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN) != "bosh": return
    users = db.foydalanuvchilar_royxati(offset=0, limit=50)
    total = len(db.barcha_user_idlar())
    
    matn = f"👤 Foydalanuvchilar (Jami: {total}):\n\n"
    for i, (u_id, username, name) in enumerate(users, 1):
        user_link = f"@{username}" if username else "Username yo'q"
        name_safe = name if name else "Ism yo'q"
        matn += f"{i}. <b>{name_safe}</b> - {user_link}\n"
    
    await message.answer(matn, parse_mode="HTML", reply_markup=kb.users_pagination_keyboard(0, 50, total))

# === BAN TIZIMI ===
@dp.message_handler(lambda message: message.text == "🚫 Foydalanuvchini Bloklash")
async def ban_start(message: types.Message):
    if db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN) != "bosh": return
    await message.answer("🚫 Foydalanuvchi ID raqamini kiriting:", reply_markup=kb.bekor_qilish_btn())
    await BotStates.kutish_ban_id.set()

@dp.message_handler(state=BotStates.kutish_ban_id)
async def ban_id_qabul(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Faqat raqam kiriting!")
        return
    
    target_id = int(message.text)
    ban_status = db.user_ban_tekshirish_kengaytirilgan(target_id)
    
    if ban_status != "active":
        db.user_ban_qilish(target_id, 0)
        await state.finish()
        await message.answer(f"✅ {target_id} blokdan chiqarildi!", reply_markup=kb.bosh_admin_panel())
        return
    
    await state.update_data(ban_id=target_id)
    await message.answer(f"⏳ {target_id} uchun ban muddatini tanlang:", reply_markup=kb.ban_vaqti_inline())

@dp.callback_query_handler(lambda call: call.data.startswith("ban_time_"), state=BotStates.kutish_ban_id)
async def ban_time_callback(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    target_id = data.get("ban_id")
    vaqt = call.data.replace("ban_time_", "")
    
    if vaqt == "perm":
        db.user_ban_qilish(target_id, 1)
        msg = f"🚫 {target_id} umrbod bloklandi."
    else:
        db.user_vaqtinchalik_ban_qilish(target_id, int(vaqt))
        msg = f"⏳ {target_id} vaqtinchalik bloklandi."
    
    await state.finish()
    await call.message.answer(msg, reply_markup=kb.bosh_admin_panel())
    await call.answer()

# === MAIN MENU CALLBACK HANDLERS ===
@dp.callback_query_handler(lambda call: call.data.startswith("content_v_"))
async def content_boblar_korsat(call: types.CallbackQuery):
    if await ban_tekshir(call.from_user.id, call.message): return
    # Content type ni bilmaymiz, shuning uchun barcha tablada izlaymiz
    content_id = int(call.data.replace("content_v_", ""))
    
    # Manga ichida qidirish
    mangalar = db.hamma_mangalar_id_bilan()
    for m_id, m_nomi in mangalar:
        if m_id == content_id:
            boblar = db.manga_boblar_royxati(content_id)
            caption_text = f"📖 <b>{m_nomi}</b> boblari:"
            nomi, rasm, _, _ = db.manga_rasm_va_nomi(content_id)
            if rasm and boblar:
                await call.message.answer_photo(photo=rasm, caption=caption_text, 
                                               reply_markup=kb.boblar_list_keyboard(boblar), parse_mode="HTML")
            elif boblar:
                await call.message.answer(caption_text, reply_markup=kb.boblar_list_keyboard(boblar), parse_mode="HTML")
            await call.answer()
            return

@dp.callback_query_handler(lambda call: call.data.startswith("bob_open_"))
async def bob_ko_rsat(call: types.CallbackQuery):
    if await ban_tekshir(call.from_user.id, call.message): return
    bob_id = int(call.data.replace("bob_open_", ""))
    info = db.bob_malumot(bob_id)
    
    if not info:
        await call.answer("❌ Bob topilmadi!", show_alert=True)
        return
    
    nomi, bob_raqami, file_id, likes, manga_id, janr, holati = info
    oldingi_id, keyingi_id = db.keyingi_oldingi_bob_id(manga_id, bob_raqami)
    
    r = db.admin_tekshirish(call.from_user.id, config.BOSH_ADMIN)
    is_admin = r in ["bosh", "ishchi"]
    
    caption = f"📖 <b>{nomi}</b>\n{bob_raqami}-Bob\n📚 {janr}\n📌 {holati}"
    
    await call.message.answer_photo(
        photo=file_id,
        caption=caption,
        reply_markup=kb.bob_boshqaruv_keyboard(bob_id, likes, oldingi_id, keyingi_id, is_admin),
        parse_mode="HTML"
    )
    
    # Tarix yangilash
    db.user_tarix_yangilash(call.from_user.id, "manga", nomi, bob_raqami)
    await call.answer()

@dp.callback_query_handler(lambda call: call.data.startswith("like_"))
async def like_qoshish_callback(call: types.CallbackQuery):
    bob_id = int(call.data.replace("like_", ""))
    db.like_qoshish("manga", bob_id)
    await call.answer("❤️ Yoqdi!", show_alert=False)

@dp.callback_query_handler(lambda call: call.data.startswith("comm_"))
async def komment_yozish(call: types.CallbackQuery, state: FSMContext):
    bob_id = int(call.data.replace("comm_", ""))
    await state.update_data(current_bob_id=bob_id)
    await call.message.answer("✍️ Sharhingizni yozing:")
    await BotStates.kutish_komment.set()

@dp.message_handler(state=BotStates.kutish_komment)
async def komment_saqlash(message: types.Message, state: FSMContext):
    data = await state.get_data()
    bob_id = data.get("current_bob_id")
    db.komment_qoshish("manga", 0, bob_id, message.from_user.id, message.from_user.full_name, message.text)
    await state.finish()
    r = db.admin_tekshirish(message.from_user.id, config.BOSH_ADMIN)
    is_admin = True if r in ["bosh", "ishchi"] else False
    await message.answer("✅ Sharh saqlandi!", reply_markup=kb.bosh_menu(is_admin=is_admin))

@dp.callback_query_handler(lambda call: call.data.startswith("viewcomm_"))
async def sharhlarni_ko_rsat(call: types.CallbackQuery):
    bob_id = int(call.data.replace("viewcomm_", ""))
    sharhlar = db.kommentlar_olish("manga", bob_id)
    
    if not sharhlar:
        await call.answer("💬 Sharh yo'q!", show_alert=True)
        return
    
    matn = "💬 <b>Sharhlar:</b>\n\n"
    for user_name, komment in sharhlar:
        matn += f"👤 <b>{user_name}</b>:\n{komment}\n\n"
    
    await call.message.answer(matn, parse_mode="HTML")
    await call.answer()

# Main Menu Handlers
@dp.message_handler(lambda message: message.text == "📖 Barcha Mangalar", state='*')
async def barcha_mangalar(message: types.Message):
    if await ban_tekshir(message.from_user.id, message): return
    mangalar = db.mangalar_royxati()
    if not mangalar:
        await message.answer("📭 Manga yo'q!", reply_markup=kb.bosh_menu())
        return
    await message.answer("📖 Mangalar:", reply_markup=kb.content_list_keyboard(mangalar))

@dp.message_handler(lambda message: message.text == "🔥 TOP (Hammasi)", state='*')
async def top_content(message: types.Message):
    if await ban_tekshir(message.from_user.id, message): return
    top = db.mangalar_royxati("top")
    if not top:
        await message.answer("📭 Content yo'q!")
        return
    matn = "🔥 TOP 10:\n\n"
    for i, (c_id, c_nomi) in enumerate(top, 1):
        matn += f"{i}. {c_nomi}\n"
    await message.answer(matn)

@dp.message_handler(lambda message: message.text == "⏳ Ongoing (Hammasi)", state='*')
async def ongoing_content(message: types.Message):
    if await ban_tekshir(message.from_user.id, message): return
    ongoing = db.mangalar_royxati("ongoing")
    if not ongoing:
        await message.answer("📭 Content yo'q!")
        return
    await message.answer("⏳ Ongoing:", reply_markup=kb.content_list_keyboard(ongoing))

@dp.message_handler(lambda message: message.text == "🎲 Tasodifiy Content", state='*')
async def tasodifiy_content(message: types.Message):
    if await ban_tekshir(message.from_user.id, message): return
    # Tasodifiy manga, anime, yoki boshqa
    content = db.tasodifiy_manga_olish()
    if content:
        c_id, c_nomi = content
        await message.answer(f"🎲 Tasodifiy: <b>{c_nomi}</b>", parse_mode="HTML")
        # Boblarini ko'rsata
        boblar = db.manga_boblar_royxati(c_id)
        if boblar:
            await message.answer("Boblari:", reply_markup=kb.boblar_list_keyboard(boblar))

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
