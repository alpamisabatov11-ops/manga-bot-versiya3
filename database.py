# database.py — PostgreSQL va 4 Content Turi
import os
import time
import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.environ.get("DATABASE_URL", "")

def get_conn():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    conn = get_conn()
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            name TEXT,
            ban_status TEXT DEFAULT 'active',
            ban_gacha BIGINT DEFAULT 0,
            
            oxirgi_manga TEXT,
            oxirgi_manga_bob INTEGER,
            
            oxirgi_anime TEXT,
            oxirgi_anime_episode INTEGER,
            
            oxirgi_manhwa TEXT,
            oxirgi_manhwa_bob INTEGER,
            
            oxirgi_novel TEXT,
            oxirgi_novel_bob INTEGER
        )
    """)

    # MANGALAR TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mangalar (
            id SERIAL PRIMARY KEY,
            nomi TEXT UNIQUE,
            janr TEXT,
            rasm_id TEXT,
            holati TEXT DEFAULT 'ongoing',
            likes INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # BOBLAR (Manga chapters)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS boblar (
            id SERIAL PRIMARY KEY,
            manga_id INTEGER REFERENCES mangalar(id) ON DELETE CASCADE,
            bob_raqami INTEGER,
            file_id TEXT
        )
    """)

    # ANIMALAR TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS animalar (
            id SERIAL PRIMARY KEY,
            nomi TEXT UNIQUE,
            janr TEXT,
            rasm_id TEXT,
            holati TEXT DEFAULT 'ongoing',
            likes INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # EPIZODLAR (Anime episodes)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS epizodlar (
            id SERIAL PRIMARY KEY,
            anime_id INTEGER REFERENCES animalar(id) ON DELETE CASCADE,
            episode_raqami INTEGER,
            file_id TEXT
        )
    """)

    # MANXWALAR TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS manxwalar (
            id SERIAL PRIMARY KEY,
            nomi TEXT UNIQUE,
            janr TEXT,
            rasm_id TEXT,
            holati TEXT DEFAULT 'ongoing',
            likes INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # MANXWA BOBLAR
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS manxwa_boblar (
            id SERIAL PRIMARY KEY,
            manhwa_id INTEGER REFERENCES manxwalar(id) ON DELETE CASCADE,
            bob_raqami INTEGER,
            file_id TEXT
        )
    """)

    # LIGHT NOVELLAR TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS light_novellar (
            id SERIAL PRIMARY KEY,
            nomi TEXT UNIQUE,
            janr TEXT,
            rasm_id TEXT,
            holati TEXT DEFAULT 'ongoing',
            likes INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # LIGHT NOVEL BOBLAR
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS novel_boblar (
            id SERIAL PRIMARY KEY,
            novel_id INTEGER REFERENCES light_novellar(id) ON DELETE CASCADE,
            bob_raqami INTEGER,
            file_id TEXT
        )
    """)

    # KOMMENTLAR
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kommentlar (
            id SERIAL PRIMARY KEY,
            content_type TEXT,
            content_id INTEGER,
            chapter_id INTEGER,
            user_id BIGINT,
            user_name TEXT,
            matn TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ADMINLAR
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS adminlar (
            user_id BIGINT PRIMARY KEY,
            turi TEXT
        )
    """)

    # KANALLAR
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kanallar (
            link TEXT PRIMARY KEY
        )
    """)

    # YANGILIKLAR
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS yangiliklar (
            id SERIAL PRIMARY KEY,
            matn TEXT,
            sana TEXT
        )
    """)

    # SOZLAMALAR (Admin tomonidan o'zgartiriladigan sozlamalar)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sozlamalar (
            kalit TEXT PRIMARY KEY,
            qiymat TEXT
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()

# === SOZLAMALAR ===
def sozlama_yangilash(kalit, qiymat):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sozlamalar (kalit, qiymat) VALUES (%s, %s)
        ON CONFLICT (kalit) DO UPDATE SET qiymat = EXCLUDED.qiymat
    """, (kalit, qiymat))
    conn.commit()
    cursor.close()
    conn.close()

def sozlama_olish(kalit, standart_qiymat=""):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT qiymat FROM sozlamalar WHERE kalit = %s", (kalit,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else standart_qiymat

# === USER OPERATSIYALARI ===
def user_qoshish(user_id, username=None, name=None):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (user_id, username, name) VALUES (%s, %s, %s)
        ON CONFLICT (user_id) DO UPDATE SET username = EXCLUDED.username, name = EXCLUDED.name
    """, (user_id, username, name))
    conn.commit()
    cursor.close()
    conn.close()

def barcha_user_idlar():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [r[0] for r in rows if r[0] is not None]

def foydalanuvchilar_royxati(offset=0, limit=50):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, name FROM users LIMIT %s OFFSET %s", (limit, offset))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

# === BAN TIZIMI ===
def user_ban_qilish(user_id, status_kod):
    conn = get_conn()
    cursor = conn.cursor()
    if status_kod == 1:
        cursor.execute("UPDATE users SET ban_status = 'permanent', ban_gacha = 0 WHERE user_id = %s", (user_id,))
    else:
        cursor.execute("UPDATE users SET ban_status = 'active', ban_gacha = 0 WHERE user_id = %s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()

def user_vaqtinchalik_ban_qilish(user_id, soniya):
    conn = get_conn()
    cursor = conn.cursor()
    tugash_vaqti = int(time.time()) + soniya
    cursor.execute("UPDATE users SET ban_status = 'temporary', ban_gacha = %s WHERE user_id = %s", (tugash_vaqti, user_id))
    conn.commit()
    cursor.close()
    conn.close()

def user_ban_tekshirish_kengaytirilgan(user_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT ban_status, ban_gacha FROM users WHERE user_id = %s", (user_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row: return "active"
    status, gacha = row
    if status == "permanent": return "permanent"
    if status == "temporary":
        qolgan_vaqt = gacha - int(time.time())
        if qolgan_vaqt > 0: return qolgan_vaqt
        else:
            user_ban_qilish(user_id, 0)
            return "active"
    return "active"

# === ADMIN TEKSHIRISH ===
def admin_tekshirish(user_id, bosh_admin_id):
    if user_id == bosh_admin_id: return "bosh"
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT turi FROM adminlar WHERE user_id = %s", (user_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else None

def ishchi_admin_qoshish(user_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO adminlar (user_id, turi) VALUES (%s, 'ishchi') ON CONFLICT (user_id) DO NOTHING", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()

# === MANGA OPERATSIYALARI ===
def yangi_manga_baza_qoshish(nomi, janr, rasm_id, holati="ongoing"):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO mangalar (nomi, janr, rasm_id, holati) VALUES (%s, %s, %s, %s) RETURNING id", 
                      (nomi, janr, rasm_id, holati))
        manga_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return manga_id
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return None

def hamma_mangalar_id_bilan():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nomi FROM mangalar")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def mangalar_royxati(filtr=None):
    conn = get_conn()
    cursor = conn.cursor()
    if filtr == "top":
        cursor.execute("SELECT id, nomi FROM mangalar ORDER BY likes DESC LIMIT 10")
    elif filtr == "ongoing":
        cursor.execute("SELECT id, nomi FROM mangalar WHERE holati = 'ongoing'")
    else:
        cursor.execute("SELECT id, nomi FROM mangalar")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def tasodifiy_manga_olish():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nomi FROM mangalar ORDER BY RANDOM() LIMIT 1")
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

def manga_rasm_va_nomi(manga_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT nomi, rasm_id, janr, holati FROM mangalar WHERE id = %s", (manga_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row if row else (None, None, None, None)

def manga_ochirish_baza(manga_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM mangalar WHERE id = %s", (manga_id,))
    conn.commit()
    cursor.close()
    conn.close()

# === BOB OPERATSIYALARI ===
def yangi_bob_baza_qoshish(manga_id, bob_raqami, file_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO boblar (manga_id, bob_raqami, file_id) VALUES (%s, %s, %s) RETURNING id", 
                  (manga_id, bob_raqami, file_id))
    bob_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return bob_id

def manga_boblar_royxati(manga_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, bob_raqami FROM boblar WHERE manga_id = %s ORDER BY bob_raqami ASC", (manga_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def bob_malumot(bob_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.nomi, b.bob_raqami, b.file_id, m.likes, b.manga_id, m.janr, m.holati
        FROM boblar b JOIN mangalar m ON b.manga_id = m.id
        WHERE b.id = %s
    """, (bob_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

def bob_ochirish_baza(bob_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM boblar WHERE id = %s", (bob_id,))
    conn.commit()
    cursor.close()
    conn.close()

def keyingi_oldingi_bob_id(manga_id, joriy_raqam):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM boblar WHERE manga_id = %s AND bob_raqami = %s", (manga_id, joriy_raqam - 1))
    old = cursor.fetchone()
    cursor.execute("SELECT id FROM boblar WHERE manga_id = %s AND bob_raqami = %s", (manga_id, joriy_raqam + 1))
    keyingi = cursor.fetchone()
    cursor.close()
    conn.close()
    return (old[0] if old else None, keyingi[0] if keyingi else None)

# === ANIME OPERATSIYALARI ===
def yangi_anime_baza_qoshish(nomi, janr, rasm_id, holati="ongoing"):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO animalar (nomi, janr, rasm_id, holati) VALUES (%s, %s, %s, %s) RETURNING id", 
                      (nomi, janr, rasm_id, holati))
        anime_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return anime_id
    except Exception:
        conn.rollback()
        cursor.close()
        conn.close()
        return None

def hamma_animalar_id_bilan():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nomi FROM animalar")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def animalar_royxati(filtr=None):
    conn = get_conn()
    cursor = conn.cursor()
    if filtr == "top":
        cursor.execute("SELECT id, nomi FROM animalar ORDER BY likes DESC LIMIT 10")
    elif filtr == "ongoing":
        cursor.execute("SELECT id, nomi FROM animalar WHERE holati = 'ongoing'")
    else:
        cursor.execute("SELECT id, nomi FROM animalar")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def tasodifiy_anime_olish():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nomi FROM animalar ORDER BY RANDOM() LIMIT 1")
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

def anime_rasm_va_nomi(anime_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT nomi, rasm_id, janr, holati FROM animalar WHERE id = %s", (anime_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row if row else (None, None, None, None)

def anime_ochirish_baza(anime_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM animalar WHERE id = %s", (anime_id,))
    conn.commit()
    cursor.close()
    conn.close()

# === EPIZOD OPERATSIYALARI ===
def yangi_epizod_baza_qoshish(anime_id, episode_raqami, file_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO epizodlar (anime_id, episode_raqami, file_id) VALUES (%s, %s, %s) RETURNING id", 
                  (anime_id, episode_raqami, file_id))
    ep_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return ep_id

def anime_epizodlar_royxati(anime_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, episode_raqami FROM epizodlar WHERE anime_id = %s ORDER BY episode_raqami ASC", (anime_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def epizod_malumot(epizod_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.nomi, e.episode_raqami, e.file_id, a.likes, e.anime_id, a.janr, a.holati
        FROM epizodlar e JOIN animalar a ON e.anime_id = a.id
        WHERE e.id = %s
    """, (epizod_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

def epizod_ochirish_baza(epizod_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM epizodlar WHERE id = %s", (epizod_id,))
    conn.commit()
    cursor.close()
    conn.close()

# === MANHWA OPERATSIYALARI ===
def yangi_manhwa_baza_qoshish(nomi, janr, rasm_id, holati="ongoing"):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO manxwalar (nomi, janr, rasm_id, holati) VALUES (%s, %s, %s, %s) RETURNING id", 
                      (nomi, janr, rasm_id, holati))
        manhwa_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return manhwa_id
    except Exception:
        conn.rollback()
        cursor.close()
        conn.close()
        return None

def hamma_manxwalar_id_bilan():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nomi FROM manxwalar")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def manxwalar_royxati(filtr=None):
    conn = get_conn()
    cursor = conn.cursor()
    if filtr == "top":
        cursor.execute("SELECT id, nomi FROM manxwalar ORDER BY likes DESC LIMIT 10")
    elif filtr == "ongoing":
        cursor.execute("SELECT id, nomi FROM manxwalar WHERE holati = 'ongoing'")
    else:
        cursor.execute("SELECT id, nomi FROM manxwalar")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def manhwa_rasm_va_nomi(manhwa_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT nomi, rasm_id, janr, holati FROM manxwalar WHERE id = %s", (manhwa_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row if row else (None, None, None, None)

def manhwa_ochirish_baza(manhwa_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM manxwalar WHERE id = %s", (manhwa_id,))
    conn.commit()
    cursor.close()
    conn.close()

def yangi_manhwa_bob_baza_qoshish(manhwa_id, bob_raqami, file_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO manxwa_boblar (manhwa_id, bob_raqami, file_id) VALUES (%s, %s, %s) RETURNING id", 
                  (manhwa_id, bob_raqami, file_id))
    bob_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return bob_id

def manhwa_boblar_royxati(manhwa_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, bob_raqami FROM manxwa_boblar WHERE manhwa_id = %s ORDER BY bob_raqami ASC", (manhwa_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

# === LIGHT NOVEL OPERATSIYALARI ===
def yangi_novel_baza_qoshish(nomi, janr, rasm_id, holati="ongoing"):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO light_novellar (nomi, janr, rasm_id, holati) VALUES (%s, %s, %s, %s) RETURNING id", 
                      (nomi, janr, rasm_id, holati))
        novel_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return novel_id
    except Exception:
        conn.rollback()
        cursor.close()
        conn.close()
        return None

def hamma_novellar_id_bilan():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nomi FROM light_novellar")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def novellar_royxati(filtr=None):
    conn = get_conn()
    cursor = conn.cursor()
    if filtr == "top":
        cursor.execute("SELECT id, nomi FROM light_novellar ORDER BY likes DESC LIMIT 10")
    elif filtr == "ongoing":
        cursor.execute("SELECT id, nomi FROM light_novellar WHERE holati = 'ongoing'")
    else:
        cursor.execute("SELECT id, nomi FROM light_novellar")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def novel_rasm_va_nomi(novel_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT nomi, rasm_id, janr, holati FROM light_novellar WHERE id = %s", (novel_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row if row else (None, None, None, None)

def novel_ochirish_baza(novel_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM light_novellar WHERE id = %s", (novel_id,))
    conn.commit()
    cursor.close()
    conn.close()

def yangi_novel_bob_baza_qoshish(novel_id, bob_raqami, file_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO novel_boblar (novel_id, bob_raqami, file_id) VALUES (%s, %s, %s) RETURNING id", 
                  (novel_id, bob_raqami, file_id))
    bob_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return bob_id

def novel_boblar_royxati(novel_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, bob_raqami FROM novel_boblar WHERE novel_id = %s ORDER BY bob_raqami ASC", (novel_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

# === TARIX OPERATSIYALARI ===
def user_tarix_yangilash(user_id, content_type, content_nomi, raqam):
    """content_type: manga, anime, manhwa, novel"""
    conn = get_conn()
    cursor = conn.cursor()
    if content_type == "manga":
        cursor.execute("UPDATE users SET oxirgi_manga = %s, oxirgi_manga_bob = %s WHERE user_id = %s", 
                      (content_nomi, raqam, user_id))
    elif content_type == "anime":
        cursor.execute("UPDATE users SET oxirgi_anime = %s, oxirgi_anime_episode = %s WHERE user_id = %s", 
                      (content_nomi, raqam, user_id))
    elif content_type == "manhwa":
        cursor.execute("UPDATE users SET oxirgi_manhwa = %s, oxirgi_manhwa_bob = %s WHERE user_id = %s", 
                      (content_nomi, raqam, user_id))
    elif content_type == "novel":
        cursor.execute("UPDATE users SET oxirgi_novel = %s, oxirgi_novel_bob = %s WHERE user_id = %s", 
                      (content_nomi, raqam, user_id))
    conn.commit()
    cursor.close()
    conn.close()

def user_tarix_olish_hammasi(user_id):
    """Barcha 4 ta content turi uchun tarix qaytaradi"""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT oxirgi_manga, oxirgi_manga_bob, 
               oxirgi_anime, oxirgi_anime_episode,
               oxirgi_manhwa, oxirgi_manhwa_bob,
               oxirgi_novel, oxirgi_novel_bob
        FROM users WHERE user_id = %s
    """, (user_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        return {
            "manga": (None, None),
            "anime": (None, None),
            "manhwa": (None, None),
            "novel": (None, None)
        }
    return {
        "manga": (row[0], row[1]),
        "anime": (row[2], row[3]),
        "manhwa": (row[4], row[5]),
        "novel": (row[6], row[7])
    }

# === LIKE OPERATSIYALARI ===
def like_qoshish(content_type, content_id):
    """content_type: manga, anime, manhwa, novel"""
    conn = get_conn()
    cursor = conn.cursor()
    if content_type == "manga":
        cursor.execute("UPDATE mangalar SET likes = likes + 1 WHERE id = %s", (content_id,))
    elif content_type == "anime":
        cursor.execute("UPDATE animalar SET likes = likes + 1 WHERE id = %s", (content_id,))
    elif content_type == "manhwa":
        cursor.execute("UPDATE manxwalar SET likes = likes + 1 WHERE id = %s", (content_id,))
    elif content_type == "novel":
        cursor.execute("UPDATE light_novellar SET likes = likes + 1 WHERE id = %s", (content_id,))
    conn.commit()
    cursor.close()
    conn.close()

# === KOMMENT OPERATSIYALARI ===
def komment_qoshish(content_type, content_id, chapter_id, user_id, user_name, matn):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO kommentlar (content_type, content_id, chapter_id, user_id, user_name, matn) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (content_type, content_id, chapter_id, user_id, user_name, matn))
    conn.commit()
    cursor.close()
    conn.close()

def kommentlar_olish(content_type, chapter_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_name, matn FROM kommentlar 
        WHERE content_type = %s AND chapter_id = %s 
        ORDER BY id DESC
    """, (content_type, chapter_id))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

# === KANAL OPERATSIYALARI ===
def kanal_qoshish(link):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO kanallar (link) VALUES (%s) ON CONFLICT DO NOTHING", (link,))
    conn.commit()
    cursor.close()
    conn.close()

def kanallar_olish():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT link FROM kanallar")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [r[0] for r in rows]

def kanallarni_tozalash():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM kanallar")
    conn.commit()
    cursor.close()
    conn.close()

def kanal_ochirish(link):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM kanallar WHERE link = %s", (link,))
    conn.commit()
    cursor.close()
    conn.close()

# === YANGILIK OPERATSIYALARI ===
def yangilik_qoshish(matn):
    sana = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO yangiliklar (matn, sana) VALUES (%s, %s)", (matn, sana))
    conn.commit()
    cursor.close()
    conn.close()

def yangiliklar_olish():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT matn, sana FROM yangiliklar ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

# === STATISTIKA ===
def statistika_olish():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM boblar")
    manga_bobs = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM epizodlar")
    anime_eps = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return {
        "users": users,
        "manga_bobs": manga_bobs,
        "anime_episodes": anime_eps,
        "total": users + manga_bobs + anime_eps
    }
