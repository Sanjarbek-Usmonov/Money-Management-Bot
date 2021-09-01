from django.http import HttpResponse
import telebot
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import TgUser
from core.models import Profile, Wallet, Category
from .markups import *
from django.db.models import F

bot = telebot.TeleBot(settings.BOT_TOKEN)
@csrf_exempt
def web_hook_view(request):
    if request.method == 'POST':
        bot.process_new_updates([telebot.types.Update.de_json(request.body.decode('utf-8'))])
    return HttpResponse('ok')


@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        user = TgUser.objects.get(user_id=message.from_user.id)
    except TgUser.DoesNotExist:
        user = TgUser.objects.create(user_id=message.from_user.id)
        profile = Profile.objects.create(tg_user=user)
        Wallet.objects.create(profile=profile)
        Category.objects.create(user=profile)
    wallet = Wallet.objects.get(profile__tg_user__user_id=message.from_user.id)
    text = f'Assalomu alaykum {message.from_user.first_name}! \n\n' \
           f'Ushbu botda siz daromadingizni kiritib qilayotgan sarf va xarajatlaringizni yozib borgan holda ' \
           f'daromadingizni boshqarishingiz mumkin! ' \
           f'Qisqacha ro\'yxatdan o\'tib olish uchun iltimos Ism-Familiyangizni quyidagidek yuboring:\n\n' \
           f'"Ism Familiya"'

    msg = bot.send_message(message.from_user.id, text)
    bot.register_next_step_handler(msg, set_names)

def set_names(message):
    names = message.text
    name = names.split()
    if len(name) == 2:
        text = 'Rahmat siz ro\'yxatdan o\'tdingiz\n\n' \
               f'Bosh Menyu\n\n' \
               f'Ma\'lumot tugmasini bosib bazi narsalarni bilib oling\n' \
               f'😉😉😉😉😉😉😉😉'
        user = TgUser.objects.get(user_id=message.from_user.id)
        profile = Profile.objects.get(tg_user=user)
        profile.first_name = name[0]
        profile.last_name = name[1]
        profile.save()
        bot.send_message(message.from_user.id, text, reply_markup=home_markup())
    else:
        text = "Iltimos 2 dona so'zdan iborat to'g'ri ism familiya kiriting!\n" \
               "😩😩😩😩"
        msg = bot.send_message(message.from_user.id, text)
        bot.register_next_step_handler(msg, set_names)

@bot.message_handler(func=lambda m: True)
def echo_message(message):
    wallet = Wallet.objects.get(profile__tg_user__user_id=message.from_user.id)
    if (wallet.balance) <= 300000:
        text = f"😨😨😨😨😨😨😨😨\n\n" \
               f"💰 Sizning Balansingiz miqdori: {wallet.balance} so'm qoldi.\n\n" \
               f"📉 Balans kam qoldi! \n\n" \
               f"💸 Iltimos balansingizga daromad qo'shing yoki xarajatlarni kamaytiring!\n" \
               f"🛍⌛️🍱➕🏋🏽‍♂️🚖"
        bot.send_message(message.from_user.id, text)

    if message.text == '⚙ Sozlamalar':
        name = Profile.objects.get(tg_user__user_id=message.from_user.id)
        time = TgUser.objects.get(user_id=message.from_user.id)
        wallet = Wallet.objects.get(profile__tg_user__user_id=message.from_user.id)
        category = Category.objects.get(user__tg_user__user_id=message.from_user.id)
        outcomes = category.other + category.food + category.taxes + category.extra_payments + category.clothes + category.transport
        text = f"🧍🏿 Ism: {name.first_name}\n\n" \
               f"🧍🏿 Familiya: {name.last_name}\n\n" \
               f"💰 Hamyonga qo'yilgan mablag': {wallet.balance + outcomes}\n\n" \
               f"💸 Barcha xarajatlar miqdori: {outcomes}\n\n" \
               f"🤑 Sizda qolgan mablag': {wallet.balance}\n\n" \
               f"⏰ Profil hosil qilingan vaqt: {time.created_at}\n\n\n" \
               f"👇🏽 Quyidagilardan birini tanlang 👇🏽"
        bot.send_message(message.from_user.id, text, reply_markup=settings_markup())

    if message.text == '🔀 Ism-Familiyani o\'zgartirish':
        text = "Quyidagi shaklda boshqa ism-familiyangizni yuboring:\n\n" \
               "Ism Familiya"
        msg = bot.send_message(message.from_user.id, text, reply_markup=info_markup())
        bot.register_next_step_handler(msg, update_info)

    if message.text == '👜 Hamyonni 0️⃣ so\'m qilish':
        wallet = Wallet.objects.get(profile__tg_user__user_id=message.from_user.id)
        wallet.balance = 0
        wallet.save()
        text = f"Sizning hamyoningizda hech qanday mablag' qolmadi!\n\n" \
               f"🙅🏽🙅🏽🙅🏽🙅🏽🙅🏽🙅🏽🙅🏽\n\n" \
               f"💰 Hamyoningizdagi mablag': {wallet.balance} so'm\n\n" \
               f"ℹ️ Bosh Menyuga o'tib Balans tugmasi orqali hisobingizni to'ldiring!\n" \
               f"😅😁😄😀😉😋😋😋😋"
        bot.send_message(message.from_user.id, text, reply_markup=settings_markup())

    if message.text == '💳 Xarajatlarni 0️⃣ so\'m qilish':
        category = Category.objects.get(user__tg_user__user_id=message.from_user.id)
        category.extra_payments = 0
        category.clothes = 0
        category.food = 0
        category.taxes = 0
        category.other = 0
        category.transport = 0
        category.save()
        outcomes = category.other + category.food + category.taxes + category.extra_payments + category.clothes + category.transport
        text = f"Sizning xarajatlaringiz {outcomes} so'm!\n\n" \
               f"Xarajatlaringiz 0 ga tenglashtirildi, endi siz boshidan hisoblab borishingiz mumkin! 😄😄"
        bot.send_message(message.from_user.id, text, reply_markup=settings_markup())

    if message.text == '📈 Statistika':
        name = Profile.objects.get(tg_user__user_id=message.from_user.id)
        times = TgUser.objects.get(user_id=message.from_user.id)
        wallet = Wallet.objects.get(profile__tg_user__user_id=message.from_user.id)
        category = Category.objects.get(user__tg_user__user_id=message.from_user.id)
        outcomes = category.other + category.food + category.taxes + category.extra_payments + category.clothes + category.transport
        text = f"📈📈📈📈📈📈📈📈📈📈\n" \
               f"Assalomu alaykum {message.from_user.first_name}\n\n" \
               f"S T A T I S T I K A\n\n" \
               f"🧍🏿 Ism: {name.first_name}\n\n" \
               f"🧍🏿 Familiya: {name.last_name}\n\n" \
               f"💰 Hamyonga qo'yilgan mablag': {wallet.balance + outcomes} so'm\n\n" \
               f"💸 Barcha xarajatlar miqdori: {outcomes} so'm\n\n" \
               f"🤑 Sizda qolgan mablag': {wallet.balance} so'm\n\n" \
               f"🍱 Oziq-ovqat uchun sarflangan mablag': {category.food} so'm\n" \
               f"🚖 Transportga sarflangan mablag': {category.transport} so'm\n" \
               f"👕 Kiyim-kechaklarga sarflangan mablag': {category.clothes} so'm\n" \
               f"💵 Soliqlarga sarflangan mablag': {category.taxes} so'm\n" \
               f"🏋️‍♂️ Sport va dam olishga sarflangan mablag': {category.extra_payments} so'm\n" \
               f"➕ Boshqa xarajatlarga sarflangan mablag': {category.other} so'm\n\n" \
               f"⏰ Profil hosil qilingan vaqt: {times.created_at.ctime()}\n\n\n" \
               f"👇🏽 Quyidagilardan birini tanlang 👇🏽"
        bot.send_message(message.from_user.id, text)

    if message.text == 'ℹ Ma\'lumot':
        wallet = Wallet.objects.get(profile__tg_user__user_id=message.from_user.id)
        info_text = f"👋 Assalomu alaykum {message.from_user.first_name}!\n\n" \
                    f"Bizning bot qanday vazifa bajarishi haqida menimcha bilib oldingiz.😅 " \
                    f"Bot sizga yaxshigina ko'mak beradi deb umid qilamiz! 😅" \
                    f"Avval siz xarajatlarni kiritishdan oldin 💰 Balans tugmasini bosing va " \
                    f"maoshingiz miqdorini kiritib qo'ying 🤑, keyin esa biz xarajatlaringizga qarab " \
                    f"maoshingizni hisoblab boramiz va maoshingizning 3️⃣0️⃣0️⃣0️⃣0️⃣0️⃣ so'm qolganida sizga maoshingiz" \
                    f" kam qolganligi haqida xabar beramiz!⏰💵💵\n\n" \
                    f"ℹ️ Hurmatli mijoz! Botdan foydalanayotganda chalkashliklar yuzaga kelmasligi uchun iltimos " \
                    f"hisobingiz va xarajatlaringiz miqdorini nazorat qilib turing!" \
                    f" Shunda xarajatlaringiz haqida bilib borasiz 😅😅😅. Biz esa sizga buning uchun ko'maklashamiz 😉😉😉.\n\n" \
                    f"💲 Sizning joriy hisobingizdagi mablag': {wallet.balance} so'm\n\n" \
                    f"❓ 🧠 Qo'shimcha savol va takliflaringiz bo'lsa murojaat uchun quyidagi profilga yozing:\n" \
                    f"👨🏿 @sanjarbekusmonov13"
        bot.send_message(message.from_user.id, info_text, reply_markup=info_markup())

    if message.text == '🔙 Orqaga':
        text = "Bosh Menyu"
        bot.send_message(message.from_user.id, text, reply_markup=home_markup())

    if message.text == '🥘 Oziq-ovqat':
        category = Category.objects.get(user__tg_user__user_id=message.from_user.id)
        text = "Oziq-ovqatlar uchun qilgan xarajatlaringizni qo'shing: " \
               f"Siz hozirgi kungacha {category.food} so'm xarajat qilgansiz!"
        msg = bot.send_message(message.from_user.id, text, reply_markup=categories_markup())
        bot.register_next_step_handler(msg, update_food)

    if message.text == '🚖 Transport':
        category = Category.objects.get(user__tg_user__user_id=message.from_user.id)
        text = "Transport uchun qilgan xarajatlaringizni qo'shing: \n\n" \
               f"Siz hozirgi kungacha {category.transport} so'm xarajat qilgansiz!"
        msg = bot.send_message(message.from_user.id, text, reply_markup=categories_markup())
        bot.register_next_step_handler(msg, update_transport)

    if message.text == '🛍 Kiyim-kechak':
        category = Category.objects.get(user__tg_user__user_id=message.from_user.id)
        text = "Kiyim-boshlar uchun qilgan xarajatlaringizni qo'shing: \n\n" \
               f"Siz hozirgi kungacha {category.clothes} so'm xarajat qilgansiz!"
        msg = bot.send_message(message.from_user.id, text, reply_markup=categories_markup())
        bot.register_next_step_handler(msg, update_clothes)

    if message.text == '⌛ Soliqlar':
        category = Category.objects.get(user__tg_user__user_id=message.from_user.id)
        text = "Soliqlar uchun qilgan xarajatlaringizni qo'shing: \n\n" \
               f"Siz hozirgi kungacha {category.taxes} so'm xarajat qilgansiz!"
        msg = bot.send_message(message.from_user.id, text, reply_markup=categories_markup())
        bot.register_next_step_handler(msg, update_taxes)

    if message.text == '🏋️‍♂ Sport va Dam olish':
        category = Category.objects.get(user__tg_user__user_id=message.from_user.id)
        text = "Sport va dam olish uchun qilgan xarajatlaringizni qo'shing: \n\n" \
               f"Siz hozirgi kungacha {category.extra_payments} so'm xarajat qilgansiz!"
        msg = bot.send_message(message.from_user.id, text, reply_markup=categories_markup())
        bot.register_next_step_handler(msg, update_extra)

    if message.text == '➕ Boshqa xarajatlar':
        category = Category.objects.get(user__tg_user__user_id=message.from_user.id)
        text = "Boshqa xarajatlaringizni qo'shing: \n\n" \
               f"Siz hozirgi kungacha {category.other} so'm xarajat qilgansiz!"
        msg = bot.send_message(message.from_user.id, text, reply_markup=categories_markup())
        bot.register_next_step_handler(msg, update_other)

    if message.text == '💰 Balans':
        text = "👇🏽 Quyidagilardan birini tanlang: "
        bot.send_message(message.from_user.id, text, reply_markup=balance_markups())

    if message.text == '➕ Balansga mablag\' qo\'shish':
        text = "Oylik maoshingiz yoki daromadingizni kiriting:\n" \
               "😋😋😋😋"
        msg = bot.send_message(message.from_user.id, text, reply_markup=balance_markup())
        bot.register_next_step_handler(msg, update_balance)

    if message.text == '💰 Joriy qolgan mablag\' miqdori':
        text = f"📈 Sizning barcha xarajatlardan tashqari qolgan mablag'ingiz miqdori: \n" \
               f"💵 {wallet.balance} so'm"
        bot.send_message(message.from_user.id, text, reply_markup=balance_markups())

def update_balance(message):
    msg = message.text
    if msg == '🔙 Orqaga':
        text = "📱 Bosh Menyu"
        bot.send_message(message.from_user.id, text, reply_markup=home_markup())
    wallet = Wallet.objects.get(profile__tg_user__user_id=message.from_user.id)
    wallet.balance = wallet.balance + int(msg)
    wallet.save()
    # Wallet.objects.update(profile__tg_user__user_id=message.from_user.id, balance=sum)
    full_wallet = Wallet.objects.get(profile__tg_user__user_id=message.from_user.id)
    text = f"Tabriklaymiz! 👏🏿👏🏿👏🏿👏🏿👏🏿\n\n" \
           f"💰 Sizning joriy hisobingiz: {full_wallet.balance} so'm"
    bot.send_message(message.from_user.id, text, reply_markup=info_markup())

def update_food(message):
    data = message.text
    if data == '🔙 Orqaga':
        text = "📱 Bosh Menyu"
        bot.send_message(message.from_user.id, text, reply_markup=home_markup())
    wallet = Wallet.objects.get(profile__tg_user__user_id=message.from_user.id)
    if int(data) >= wallet.balance:
        text = f"😵😵😵😵😵😵😵😵😵😵😵😵😵\n\n" \
               f"🥶 Hurmatli {message.from_user.first_name}\n" \
               f"👝 Sizning hisobingizda qolgan mablag' {wallet.balance} so'm 💵\n\n" \
               f"💰 Siz {data} so'm 💵 mablag' sarflay olmaysiz!"
        bot.send_message(message.from_user.id, text, reply_markup=home_markup())
    else:
        wallet.balance = wallet.balance - int(data)
        wallet.save()
        category = Category.objects.get(user__tg_user__user_id=message.from_user.id)
        category.food = int(data) + category.food
        category.save()
        text = f"🍱 Sizning oziq ovqatlarga qilgan jami xarajatlaringiz: \n" \
               f"💰 {category.food} so'm"
        bot.send_message(message.from_user.id, text, reply_markup=info_markup())

def update_transport(message):
    data = message.text
    if data == '🔙 Orqaga':
        text = "📱 Bosh Menyu"
        bot.send_message(message.from_user.id, text, reply_markup=home_markup())
    wallet = Wallet.objects.get(profile__tg_user__user_id=message.from_user.id)
    if int(data) >= wallet.balance:
        text = f"😵😵😵😵😵😵😵😵😵😵😵😵😵\n\n" \
               f"🥶 Hurmatli {message.from_user.first_name}\n" \
               f"👝 Sizning hisobingizda qolgan mablag' {wallet.balance} so'm 💵\n\n" \
               f"💰 Siz {data} so'm 💵 mablag' sarflay olmaysiz!"
        bot.send_message(message.from_user.id, text, reply_markup=home_markup())
    else:
        wallet.balance = wallet.balance - int(data)
        wallet.save()
        category = Category.objects.get(user__tg_user__user_id=message.from_user.id)
        category.transport = int(data) + category.transport
        category.save()
        text = f"🚖 Sizning transportga qilgan jami xarajatlaringiz: \n" \
               f"💰 {category.transport} so'm"
        bot.send_message(message.from_user.id, text, reply_markup=info_markup())

def update_clothes(message):
    data = message.text
    if data == '🔙 Orqaga':
        text = "📱 Bosh Menyu"
        bot.send_message(message.from_user.id, text, reply_markup=home_markup())

    wallet = Wallet.objects.get(profile__tg_user__user_id=message.from_user.id)
    if int(data) >= wallet.balance:
        text = f"😵😵😵😵😵😵😵😵😵😵😵😵😵\n\n" \
               f"🥶 Hurmatli {message.from_user.first_name}\n" \
               f"👝 Sizning hisobingizda qolgan mablag' {wallet.balance} so'm 💵\n\n" \
               f"💰 Siz {data} so'm 💵 mablag' sarflay olmaysiz!"
        bot.send_message(message.from_user.id, text, reply_markup=home_markup())
    else:
        wallet.balance = wallet.balance - int(data)
        wallet.save()
        category = Category.objects.get(user__tg_user__user_id=message.from_user.id)
        category.clothes = int(data) + category.clothes
        category.save()
        text = f"👕 Sizning kiyim-boshlarga qilgan jami xarajatlaringiz: \n" \
               f"💰 {category.clothes} so'm"
        bot.send_message(message.from_user.id, text, reply_markup=info_markup())

def update_taxes(message):
    data = message.text
    if data == '🔙 Orqaga':
        text = "📱 Bosh Menyu"
        bot.send_message(message.from_user.id, text, reply_markup=home_markup())
    wallet = Wallet.objects.get(profile__tg_user__user_id=message.from_user.id)
    if int(data) >= wallet.balance:
        text = f"😵😵😵😵😵😵😵😵😵😵😵😵😵\n\n" \
               f"🥶 Hurmatli {message.from_user.first_name}\n" \
               f"👝 Sizning hisobingizda qolgan mablag' {wallet.balance} so'm 💵\n\n" \
               f"💰 Siz {data} so'm 💵 mablag' sarflay olmaysiz!"
        bot.send_message(message.from_user.id, text, reply_markup=home_markup())
    else:
        wallet.balance = wallet.balance - int(data)
        wallet.save()
        category = Category.objects.get(user__tg_user__user_id=message.from_user.id)
        category.taxes = int(data) + category.taxes
        category.save()
        text = f"💸 Sizning soliqlarga qilgan jami xarajatlaringiz: \n" \
               f"💰 {category.taxes} so'm"
        bot.send_message(message.from_user.id, text, reply_markup=info_markup())

def update_extra(message):
    data = message.text
    if data == '🔙 Orqaga':
        text = "📱 Bosh Menyu"
        bot.send_message(message.from_user.id, text, reply_markup=home_markup())
    wallet = Wallet.objects.get(profile__tg_user__user_id=message.from_user.id)
    if int(data) >= wallet.balance:
        text = f"😵😵😵😵😵😵😵😵😵😵😵😵😵\n\n" \
               f"🥶 Hurmatli {message.from_user.first_name}\n" \
               f"👝 Sizning hisobingizda qolgan mablag' {wallet.balance} so'm 💵\n\n" \
               f"💰 Siz {data} so'm 💵 mablag' sarflay olmaysiz!"
        bot.send_message(message.from_user.id, text, reply_markup=home_markup())
    else:
        wallet.balance = wallet.balance - int(data)
        wallet.save()
        category = Category.objects.get(user__tg_user__user_id=message.from_user.id)
        category.extra_payments = int(data) + category.extra_payments
        category.save()
        text = f"🏋🏽‍♂️ Sizning sport va dam olishga qilgan jami xarajatlaringiz: \n" \
               f"💰 {category.extra_payments} so'm"
        bot.send_message(message.from_user.id, text, reply_markup=info_markup())

def update_other(message):
    data = message.text
    if data == '🔙 Orqaga':
        text = "📱 Bosh Menyu"
        bot.send_message(message.from_user.id, text, reply_markup=home_markup())
    wallet = Wallet.objects.get(profile__tg_user__user_id=message.from_user.id)
    if int(data) >= wallet.balance:
        text = f"😵😵😵😵😵😵😵😵😵😵😵😵😵\n\n" \
               f"🥶 Hurmatli {message.from_user.first_name}\n" \
               f"👝 Sizning hisobingizda qolgan mablag' {wallet.balance} so'm 💵\n\n" \
               f"💰 Siz {data} so'm 💵 mablag' sarflay olmaysiz!"
        bot.send_message(message.from_user.id, text, reply_markup=home_markup())
    else:
        wallet.balance = wallet.balance - int(data)
        wallet.save()
        category = Category.objects.get(user__tg_user__user_id=message.from_user.id)
        category.other = int(data) + category.other
        category.save()
        text = f"➕ Sizning boshqa qilgan jami xarajatlaringiz: \n" \
               f"💰 {category.other} so'm"
        bot.send_message(message.from_user.id, text, reply_markup=info_markup())

def update_info(message):
    msg = message.text
    if msg == '🔙 Orqaga':
        text = "📱 Bosh Menyu"
        bot.send_message(message.from_user.id, text, reply_markup=home_markup())
    else:
        name = msg.split()
        profile = Profile.objects.get(tg_user__user_id=message.from_user.id)
        profile.first_name = name[0]
        profile.last_name = name[1]
        profile.save()
        text = f"Sizning ism-familiyangiz muvaffaqiyatli\n" \
               f"<<< {profile.first_name + ' ' + profile.last_name} >>> ga o'zgartirildi!\n\n" \
               f"📱 Bosh Menyu"
        bot.send_message(message.from_user.id, text, reply_markup=home_markup())
