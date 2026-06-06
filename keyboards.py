# keyboards.py
from aiogram import types

def bosh_menu(is_admin=False):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("📖 Barcha Mangalar"),
        types.KeyboardButton("🎬 Barcha Animalar"),
        types.KeyboardButton("📘 Barcha Manxwalar"),
        types.KeyboardButton("💭 Barcha Light Novellar"),
        types.KeyboardButton("🔥 TOP (Hammasi)"),
        types.KeyboardButton("⏳ Ongoing (Hammasi)"),
        types.KeyboardButton("🔄 Davom ettirish"),
        types.KeyboardButton("🎲 Tasodifiy Content"),
        types.KeyboardButton("📢 Yangiliklar"),
        types.KeyboardButton("📩 Feedback / Aloqa"),
        types.KeyboardButton("💼 Reklama xizmati")
    )
    if is_admin:
        markup.add(types.KeyboardButton("👑 Admin Panel"))
    return markup

def bosh_admin_panel():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("➕ Yangi Manga Qo'shish"),
        types.KeyboardButton("➕ Yangi Bob Qo'shish"),
        types.KeyboardButton("➕ Yangi Anime Qo'shish"),
        types.KeyboardButton("➕ Yangi Epizod Qo'shish"),
        types.KeyboardButton("➕ Yangi Manxwa Qo'shish"),
        types.KeyboardButton("➕ Yangi Manxwa Bob Qo'shish"),
        types.KeyboardButton("➕ Yangi Light Novel Qo'shish"),
        types.KeyboardButton("➕ Yangi Novel Bob Qo'shish"),
        types.KeyboardButton("🗑 Content O'chirish"),
        types.KeyboardButton("🚫 Foydalanuvchini Bloklash"),
        types.KeyboardButton("🔗 Majburiy obuna sozlash"),
        types.KeyboardButton("💼 Reklama matnini o'zgartirish"),
        types.KeyboardButton("👤 Bog'lanish Userni O'zgartirish"),
        types.KeyboardButton("✉️ Xabar Yuborish"),
        types.KeyboardButton("📊 Statistika"),
        types.KeyboardButton("👥 Foydalanuvchilar ro'yxati"),
        types.KeyboardButton("➕ Ishchi Admin Qo'shish"),
        types.KeyboardButton("📝 Yangilik Qo'shish"),
        types.KeyboardButton("🚪 Panelda Chiqish")
    )
    return markup

def ishchi_admin_panel():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("➕ Yangi Manga Qo'shish"),
        types.KeyboardButton("➕ Yangi Bob Qo'shish"),
        types.KeyboardButton("➕ Yangi Anime Qo'shish"),
        types.KeyboardButton("➕ Yangi Epizod Qo'shish"),
        types.KeyboardButton("📝 Yangilik Qo'shish"),
        types.KeyboardButton("🚪 Panelda Chiqish")
    )
    return markup

def bekor_qilish_btn():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(types.KeyboardButton("❌ Bekor qilish"))
    return markup

def majburiy_obuna_markup(kanallar):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for i, kanal in enumerate(kanallar, 1):
        markup.add(types.InlineKeyboardButton(f"📢 {i}-kanalga a'zo bo'lish", url=kanal))
    markup.add(types.InlineKeyboardButton("✅ Tekshirish", callback_data="tekshirish_obuna"))
    return markup

def majburiy_obuna_boshqaruv():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("➕ Kanal link qo'shish"),
        types.KeyboardButton("🗑 Kanal link o'chirish"),
        types.KeyboardButton("📊 Hozirgi kanallar"),
        types.KeyboardButton("🚪 Orqaga")
    )
    return markup

# Content Kayitlari
def content_list_keyboard(contentlar):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for c_id, c_nomi in contentlar:
        markup.add(types.InlineKeyboardButton(f"📖 {c_nomi}", callback_data=f"content_v_{c_id}"))
    return markup

def boblar_list_keyboard(boblar):
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = []
    for b_id, b_raqam in boblar:
        buttons.append(types.InlineKeyboardButton(f"🔢 {b_raqam}", callback_data=f"bob_open_{b_id}"))
    markup.add(*buttons)
    return markup

def epizodlar_list_keyboard(epizodlar):
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = []
    for e_id, e_raqam in epizodlar:
        buttons.append(types.InlineKeyboardButton(f"📺 {e_raqam}", callback_data=f"ep_open_{e_id}"))
    markup.add(*buttons)
    return markup

def bob_boshqaruv_keyboard(bob_id, likes, oldingi_id, keyingi_id, is_admin=False):
    markup = types.InlineKeyboardMarkup(row_width=2)
    navigation_buttons = []
    if oldingi_id:
        navigation_buttons.append(types.InlineKeyboardButton("⬅️ Oldingi bob", callback_data=f"bob_open_{oldingi_id}"))
    if keyingi_id:
        navigation_buttons.append(types.InlineKeyboardButton("Keyingi bob ➡️", callback_data=f"bob_open_{keyingi_id}"))
    if navigation_buttons:
        markup.row(*navigation_buttons)
        
    markup.add(
        types.InlineKeyboardButton(f"❤️ {likes}", callback_data=f"like_{bob_id}"),
        types.InlineKeyboardButton("✍️ Sharh yozish", callback_data=f"comm_{bob_id}")
    )
    markup.add(types.InlineKeyboardButton("💬 Sharhlarni ko'rish", callback_data=f"viewcomm_{bob_id}"))
    
    if is_admin:
        markup.add(types.InlineKeyboardButton("🗑 Bobni o'chirish", callback_data=f"delbob_{bob_id}"))
    return markup

def davom_tugmasini_generatsiya_qil(tarix):
    """Foydalanuvchining tarix ma'lumotlari asosida davom tugmalarini yaratadi"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = []
    
    if tarix["manga"][0]:
        nomi, bob = tarix["manga"]
        buttons.append(types.InlineKeyboardButton(f"📖 {nomi} - {bob}-Bob", callback_data=f"davom_manga_{nomi}_{bob}"))
    
    if tarix["anime"][0]:
        nomi, ep = tarix["anime"]
        buttons.append(types.InlineKeyboardButton(f"🎬 {nomi} - {ep}-Epizod", callback_data=f"davom_anime_{nomi}_{ep}"))
    
    if tarix["manhwa"][0]:
        nomi, bob = tarix["manhwa"]
        buttons.append(types.InlineKeyboardButton(f"📘 {nomi} - {bob}-Bob", callback_data=f"davom_manhwa_{nomi}_{bob}"))
    
    if tarix["novel"][0]:
        nomi, bob = tarix["novel"]
        buttons.append(types.InlineKeyboardButton(f"💭 {nomi} - {bob}-Bob", callback_data=f"davom_novel_{nomi}_{bob}"))
    
    if buttons:
        markup.add(*buttons)
        return markup
    return None

def content_tanlash_inline(contentlar, prefix):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for c_id, c_nomi in contentlar:
        markup.add(types.InlineKeyboardButton(f"📁 {c_nomi}", callback_data=f"{prefix}_{c_id}"))
    return markup

def content_ochirish_inline(contentlar, prefix):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for c_id, c_nomi in contentlar:
        markup.add(types.InlineKeyboardButton(f"🗑 {c_nomi}", callback_data=f"{prefix}_{c_id}"))
    return markup

def ban_vaqti_inline():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("⏱ 1 soat", callback_data="ban_time_3600"),
        types.InlineKeyboardButton("⏱ 1 kun", callback_data="ban_time_86400"),
        types.InlineKeyboardButton("⏱ 3 kun", callback_data="ban_time_259200"),
        types.InlineKeyboardButton("⏱ 1 hafta", callback_data="ban_time_604800"),
        types.InlineKeyboardButton("🚫 Umrbod", callback_data="ban_time_perm")
    )
    return markup

def users_pagination_keyboard(current_offset, current_limit, total_users):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    
    if current_offset > 0:
        old_offset = max(0, current_offset - current_limit)
        buttons.append(types.InlineKeyboardButton("⬅️ Oldingi", callback_data=f"users_page_{old_offset}"))
        
    if current_offset + current_limit < total_users:
        next_offset = current_offset + current_limit
        buttons.append(types.InlineKeyboardButton("Keyingi ➡️", callback_data=f"users_page_{next_offset}"))
        
    if buttons:
        markup.row(*buttons)
    return markup

def kanallar_tanlash_inline(kanallar):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for i, kanal in enumerate(kanallar, 1):
        markup.add(types.InlineKeyboardButton(f"🗑 {i}. {kanal}", callback_data=f"del_kanal_{kanal}"))
    return markup
