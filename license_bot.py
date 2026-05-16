# ============================================================
# Shuvo Khan License Bot — সম্পূর্ণ কোড
# ============================================================
# CMD-এ চালাও:
# pip install pyTelegramBotAPI requests
# python license_bot.py
# ============================================================

import telebot
import requests
import random
import string
from datetime import datetime, timedelta

# ============================================================
# কনফিগারেশন
# ============================================================
BOT_TOKEN    = "8867355240:AAGc6fVh7YSZq28pat2tBLfUWSLeJffXC5c"
ADMIN_ID     = 7865823978
API_URL      = "http://shuvokhan.atwebpages.com/admin_api.php"
ADMIN_SECRET = "SHUVO_VIP_ADMIN_2026"
# ============================================================

bot = telebot.TeleBot(BOT_TOKEN)

# Pending রিকোয়েস্ট সংরক্ষণ
pending = {}  # {device_id: chat_id}


# ──────────────────────────────────────────────
# Helper: API Call
# ──────────────────────────────────────────────
def call_api(action, data=None):
    if data is None:
        data = {}
    data['action'] = action
    data['admin_secret'] = ADMIN_SECRET
    try:
        r = requests.post(API_URL, data=data, timeout=20)
        return r.json()
    except Exception as e:
        return {"status": "error", "msg": str(e)}


def gen_key():
    chars = string.ascii_uppercase + string.digits
    return f"SHUVO-{''.join(random.choices(chars, k=5))}-{''.join(random.choices(chars, k=5))}"


# ──────────────────────────────────────────────
# /start
# ──────────────────────────────────────────────
@bot.message_handler(commands=['start'])
def cmd_start(msg):
    name = msg.from_user.first_name or "বন্ধু"
    bot.send_message(msg.chat.id,
        f"👋 স্বাগতম, *{name}*!\n\n"
        f"আমি *Shuvo Khan License Bot* 🤖\n\n"
        f"লাইসেন্স পেতে তোমার *Device ID* পাঠাও।\n"
        f"Device ID সফটওয়্যারের License পেজে পাবে।\n\n"
        f"📌 উদাহরণ:\n`SHUVO-KHAN-LOGIN-XXXXXXXXXXXXXXX`",
        parse_mode='Markdown'
    )


# ──────────────────────────────────────────────
# /help
# ──────────────────────────────────────────────
@bot.message_handler(commands=['help'])
def cmd_help(msg):
    bot.send_message(msg.chat.id,
        "📖 *সাহায্য মেনু*\n\n"
        "👤 *ইউজারদের জন্য:*\n"
        "• সফটওয়্যার চালু করো\n"
        "• License পেজ থেকে Device ID কপি করো\n"
        "• এই বটে Device ID পাঠাও\n"
        "• Admin অ্যাপ্রুভ করলে Key পাবে\n\n"
        "✅ Device ID Format:\n`SHUVO-KHAN-LOGIN-XXXXXXXXXXXXXXX`",
        parse_mode='Markdown'
    )


# ──────────────────────────────────────────────
# /pending — সব pending রিকোয়েস্ট দেখো
# ──────────────────────────────────────────────
@bot.message_handler(commands=['pending'])
def cmd_pending(msg):
    if msg.chat.id != ADMIN_ID:
        bot.send_message(msg.chat.id, "❌ তুমি Admin না!")
        return
    if not pending:
        bot.send_message(ADMIN_ID, "📭 কোনো pending রিকোয়েস্ট নেই।")
        return
    text = "📋 *Pending রিকোয়েস্ট:*\n\n"
    for did, cid in pending.items():
        text += f"🔸 `{did}`\n   Chat ID: `{cid}`\n\n"
    text += "✅ অ্যাপ্রুভ করতে:\n`/approve <device_id> <days>`\n"
    text += "❌ রিজেক্ট করতে:\n`/reject <device_id>`"
    bot.send_message(ADMIN_ID, text, parse_mode='Markdown')


# ──────────────────────────────────────────────
# /approve <device_id> <days> — অ্যাপ্রুভ করো
# ──────────────────────────────────────────────
@bot.message_handler(commands=['approve'])
def cmd_approve(msg):
    if msg.chat.id != ADMIN_ID:
        bot.send_message(msg.chat.id, "❌ তুমি Admin না!")
        return

    parts = msg.text.strip().split()
    if len(parts) < 3:
        bot.send_message(ADMIN_ID,
            "⚠️ সঠিক ফরম্যাট:\n`/approve <device_id> <days>`\n\n"
            "উদাহরণ:\n`/approve SHUVO-KHAN-LOGIN-ABC123 30`",
            parse_mode='Markdown')
        return

    device_id = parts[1].strip()
    days_str  = parts[2].strip()

    if not days_str.isdigit():
        bot.send_message(ADMIN_ID, "❌ Days অবশ্যই সংখ্যা হতে হবে।")
        return

    days   = int(days_str)
    key    = gen_key()
    expiry = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')

    result = call_api('add', {'key': key, 'device': device_id, 'expiry': expiry})

    if result.get('status') == 'success':
        user_chat_id = pending.get(device_id)
        if user_chat_id:
            bot.send_message(user_chat_id,
                f"🎉 *তোমার লাইসেন্স অ্যাপ্রুভ হয়েছে!*\n\n"
                f"🔑 *License Key:*\n`{key}`\n\n"
                f"💻 *Device ID:*\n`{device_id}`\n\n"
                f"📅 *মেয়াদ:* {days} দিন\n"
                f"⏰ *Expiry:* {expiry}\n\n"
                f"✅ Key কপি করে সফটওয়্যারে বসাও!",
                parse_mode='Markdown'
            )
            del pending[device_id]

        bot.send_message(ADMIN_ID,
            f"✅ *অ্যাপ্রুভ সফল!*\n\n"
            f"🔑 Key: `{key}`\n"
            f"💻 Device: `{device_id}`\n"
            f"📅 {days} দিন | Expiry: {expiry}",
            parse_mode='Markdown'
        )
    else:
        bot.send_message(ADMIN_ID,
            f"❌ *API Error:*\n{result.get('msg', 'Unknown Error')}",
            parse_mode='Markdown'
        )


# ──────────────────────────────────────────────
# /reject <device_id> — রিজেক্ট করো
# ──────────────────────────────────────────────
@bot.message_handler(commands=['reject'])
def cmd_reject(msg):
    if msg.chat.id != ADMIN_ID:
        bot.send_message(msg.chat.id, "❌ তুমি Admin না!")
        return

    parts = msg.text.strip().split()
    if len(parts) < 2:
        bot.send_message(ADMIN_ID,
            "⚠️ সঠিক ফরম্যাট:\n`/reject <device_id>`",
            parse_mode='Markdown')
        return

    device_id = parts[1].strip()
    user_chat_id = pending.get(device_id)

    if user_chat_id:
        bot.send_message(user_chat_id,
            "❌ *তোমার রিকোয়েস্ট রিজেক্ট হয়েছে।*\n\n"
            "বিস্তারিত জানতে Admin-এর সাথে যোগাযোগ করো।",
            parse_mode='Markdown'
        )
        del pending[device_id]
        bot.send_message(ADMIN_ID,
            f"✅ `{device_id}` রিজেক্ট করা হয়েছে।",
            parse_mode='Markdown')
    else:
        bot.send_message(ADMIN_ID,
            f"⚠️ `{device_id}` pending তালিকায় নেই।",
            parse_mode='Markdown')


# ──────────────────────────────────────────────
# /broadcast <message> — সবাইকে মেসেজ দাও
# ──────────────────────────────────────────────
@bot.message_handler(commands=['broadcast'])
def cmd_broadcast(msg):
    if msg.chat.id != ADMIN_ID:
        bot.send_message(msg.chat.id, "❌ তুমি Admin না!")
        return
    text = msg.text.replace('/broadcast', '').strip()
    if not text:
        bot.send_message(ADMIN_ID,
            "⚠️ মেসেজ লেখো:\n`/broadcast <message>`",
            parse_mode='Markdown')
        return
    sent = 0
    for cid in set(pending.values()):
        try:
            bot.send_message(cid,
                f"📢 *Admin Message:*\n\n{text}",
                parse_mode='Markdown')
            sent += 1
        except: pass
    bot.send_message(ADMIN_ID, f"✅ {sent} জনকে মেসেজ পাঠানো হয়েছে।")


# ──────────────────────────────────────────────
# Device ID রিসিভ করো
# ──────────────────────────────────────────────
@bot.message_handler(func=lambda m: True)
def handle_message(msg):
    text = msg.text.strip() if msg.text else ''
    chat_id = msg.chat.id
    name = msg.from_user.first_name or "ইউজার"

    if text.upper().startswith('SHUVO-KHAN-LOGIN-'):
        device_id = text.upper()

        if device_id in pending:
            bot.send_message(chat_id,
                "⏳ তোমার রিকোয়েস্ট ইতোমধ্যে পাঠানো হয়েছে।\n"
                "Admin অ্যাপ্রুভ করলে Key পাবে।"
            )
            return

        pending[device_id] = chat_id

        bot.send_message(chat_id,
            f"✅ *রিকোয়েস্ট পাঠানো হয়েছে!*\n\n"
            f"💻 Device ID:\n`{device_id}`\n\n"
            f"⏳ Admin অ্যাপ্রুভ করলে তোমার License Key পাবে।\n"
            f"একটু অপেক্ষা করো! 🙏",
            parse_mode='Markdown'
        )

        bot.send_message(ADMIN_ID,
            f"🔔 *নতুন লাইসেন্স রিকোয়েস্ট!*\n\n"
            f"👤 নাম: *{name}*\n"
            f"🆔 Chat ID: `{chat_id}`\n"
            f"💻 Device ID:\n`{device_id}`\n\n"
            f"✅ অ্যাপ্রুভ করতে:\n"
            f"`/approve {device_id} 30`\n\n"
            f"❌ রিজেক্ট করতে:\n"
            f"`/reject {device_id}`",
            parse_mode='Markdown'
        )

    else:
        bot.send_message(chat_id,
            "❓ তোমার *Device ID* পাঠাও।\n\n"
            "📌 Format:\n`SHUVO-KHAN-LOGIN-XXXXXXXXXXXXXXX`\n\n"
            "Device ID সফটওয়্যারের License পেজে পাবে।",
            parse_mode='Markdown'
        )


# ──────────────────────────────────────────────
# Bot চালু
# ──────────────────────────────────────────────
print("=" * 40)
print("🤖 Shuvo Khan License Bot চালু হচ্ছে...")
print("✅ Bot running! Ctrl+C দিয়ে বন্ধ করো।")
print("=" * 40)
bot.infinity_polling()
