# config.py
import os

# Environment variables - Render'dan o'qiladi
TOKEN = os.environ.get("BOT_TOKEN", "")
BOSH_ADMIN = int(os.environ.get("BOSH_ADMIN_ID", "0"))
KANAL_ID = os.environ.get("KANAL_ID", "")
DATABASE_URL = os.environ.get("DATABASE_URL", "")

# DEFAULT SOZLAMALAR (Database'ga qo'shiladi)
STANDART_ADMIN_USERNAME = "@admin"
STANDART_REKLAMA = "📢 Reklama va hamkorlik uchun bosh admin bilan bog'laning"
STANDART_XUSH_KELIBSIZ = "👋 Assalomu alaykum! Bizning Manga Botimizga xush kelibsiz!\n\nBu yerda siz eng sara mangalarni o'zbek tilida o'qishingiz mumkin. Quyidagi tugmalardan birini tanlang 👇"
