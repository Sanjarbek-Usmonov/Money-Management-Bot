from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def home_markup():
    reply_markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    reply_markup.add(*[
        '🥘 Oziq-ovqat',
        '🚖 Transport',
        '🛍 Kiyim-kechak',
        '⌛ Soliqlar',
        '🏋️‍♂ Sport va Dam olish',
        '➕ Boshqa xarajatlar',
        'ℹ Ma\'lumot',
        '💰 Balans'
    ])
    reply_markup.row(KeyboardButton('📈 Statistika'))
    reply_markup.row(KeyboardButton('⚙ Sozlamalar'))
    return reply_markup

def info_markup():
    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    reply_markup.add('🔙 Orqaga')
    return reply_markup

def balance_markup():
    reply_markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    reply_markup.add(*[
        '500000', '1000000',
        '1500000', '2000000',
        '2500000', '3000000',
        '4000000', '5000000'
    ])
    reply_markup.row('🔙 Orqaga')
    return reply_markup

def settings_markup():
    reply_markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    reply_markup.add(*[
        '🔀 Ism-Familiyani o\'zgartirish',
        '👜 Hamyonni 0️⃣ so\'m qilish',
        '💳 Xarajatlarni 0️⃣ so\'m qilish'
    ])
    reply_markup.add('🔙 Orqaga')
    return reply_markup

def categories_markup():
    reply_markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    reply_markup.add(*[
        '10000', '20000',
        '30000', '40000',
        '50000', '60000',
        '80000', '100000'
    ])
    reply_markup.row('🔙 Orqaga')
    return reply_markup

def balance_markups():
    reply_markups = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    reply_markups.add(*[
        '➕ Balansga mablag\' qo\'shish',
        '💰 Joriy qolgan mablag\' miqdori'
    ])
    reply_markups.row('🔙 Orqaga')
    return reply_markups
