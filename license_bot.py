# ============================================================
# Shuvo Khan License Bot — সম্পূর্ণ ও সংশোধিত কোড (Render-এর জন্য)
# ============================================================
# হোস্টিংয়ের জন্য requirements.txt ফাইলে নিচের ৩টি লাইব্রেরি লিখবেন:
# pyTelegramBotAPI
# requests
# flask
# ============================================================

import telebot
import requests
import random
import string
import threading
from flask import Flask
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ============================================================
# কনফিগারেশন (সঠিক টোকেন ও ক্যাপিটাল Q সহ)
# ============================================================
BOT_TOKEN    = "8867355240:AAGc6fVh7YSZQ28pat2tBLfUWSLeJffXC5c"
ADMIN_ID     = 7865823978
API_URL      = "http://shuvokhan.atwebpages.com/admin_api.php"
ADMIN_SECRET = "SHUVO_VIP_ADMIN_2026"
# ============================================================

bot = telebot.TeleBot(BOT_TOKEN)

# Render হোস্টিং সচল রাখার জন্য Flask Web Server সেটআপ
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and running 24/7!"

def run_web_server():
    # Render সাধারণত 10000 পোর্টে রান করে
    app.run(host='0.0.0.0', port=10000)

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
# /start — স্টার্ট বাটন সহ মেনু
# ──────────────────────────────────────────────
@bot.message_handler(commands=['start'])
def cmd_start(msg):
    name = msg.from_user.first_name or "বন্ধু"
    
    # ইনলাইন কিবোর্ড বাটন তৈরি
    markup = InlineKeyboardMarkup()
    btn_submit = InlineKeyboardButton("📥 Submit Device ID", callback_data="submit_id")
    btn_help = InlineKeyboardButton("📖 Help Menu", callback_data="show_help")
    markup.add(btn_submit, btn_help)
    
    bot.send_message(msg.chat.id,
        f"👋 স্বাগতম, *{name}*!\n\n"
        f"আমি *Shuvo Khan License Bot* 🤖\n\n"
        f"নিচের বাটনগুলো ব্যবহার করে খুব সহজেই লাইসেন্স কী এর জন্য রিকোয়েস্ট পাঠাতে পারো।",
        parse_mode='Markdown',
        reply_markup=markup
    )


# ──────────────────────────────────────────────
# Buttons (Callback Query) Handling
# ──────────────────────────────────────────────
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "submit_id":
        bot.send_message(call.message.chat.id,
            "📝 তোমার *Device ID* টি লিখে বা কপি করে এখানে মেসেজ আকারে পাঠাও।\n\n"
            "📌 উদাহরণ:\n`SHUVO-KHAN-LOGIN-XXXXXXXXXXXXXXX`",
            parse_mode='Markdown'
        )
    elif call.data == "show_help":
        send_help_text(call.message.chat.id)
    
    # বাটন ক্লিকের লোডিং অ্যানিমেশন বন্ধ করার জন্য
    bot.answer_callback_query(call.id)


# ──────────────────────────────────────────────
# /help মেনু ফাংশন
# ──────────────────────────────────────────────
def send_help_text(chat_id):
    bot.send_message(chat_id,
        "📖 *সাহায্য মেনু*\n\n"
        "👤 *ইউজারদের জন্য:*\n"
        "• সফটওয়্যার চালু করো\n"
        "• License পেজ থেকে Device ID কপি করো\n"
        "• এই বটে Device ID পাঠাও\n"
        "• Admin অ্যাপ্রুভ করলে Key পাবে\n\n"
        "✅ Device ID Format:\n`SHUVO-KHAN-LOGIN-XXXXXXXXXXXXXXX`",
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['help'])
def cmd_help(msg):
    send_help_text(msg.chat.id)


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
            try:
                del pending[device_id]
            except KeyError:
                pass

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
        try:
            del pending[device_id]
        except KeyError:
            pass
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
            f"একতু অপেক্ষা করো! 🙏",
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
# সার্ভার ও বট একসাথে চালুকরণ
# ──────────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 40)
    print("🤖 Shuvo Khan License Bot চালু হচ্ছে...")
    print("= " * 40)
    
    # ব্যাকগ্রাউন্ডে Flask সার্ভার চালু করার জন্য থ্রেডিং
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
    
    # টেলিগ্রাম বট স্টার্ট করা
    bot.infinity_polling()
# ──────────────────────────────────────────────
def send_help_text(chat_id):
    bot.send_message(chat_id,
        "📖 *সাহায্য মেনু*\n\n"
        "👤 *ইউজারদের জন্য:*\n"
        "• সফটওয়্যার চালু করো\n"
        "• License পেজ থেকে Device ID কপি করো\n"
        "• এই বটে Device ID পাঠাও\n"
        "• Admin অ্যাপ্রুভ করলে Key পাবে\n\n"
        "✅ Device ID Format:\n`SHUVO-KHAN-LOGIN-XXXXXXXXXXXXXXX`",
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['help'])
def cmd_help(msg):
    send_help_text(msg.chat.id)


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
            try:
                del pending[device_id]
            except KeyError:
                pass

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
        try:
            del pending[device_id]
        except KeyError:
            pass
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
            f"একতু অপেক্ষা করো! 🙏",
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
# সার্ভার ও বট একসাথে চালুকরণ
# ──────────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 40)
    print("🤖 Shuvo Khan License Bot চালু হচ্ছে...")
    print("= " * 40)
    
    # ব্যাকগ্রাউন্ডে Flask সার্ভার চালু করার জন্য থ্রেডিং
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
    
    # টেলিগ্রাম বট স্টার্ট করা
    bot.infinity_polling()
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
