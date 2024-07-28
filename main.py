import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, CallbackQuery
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext
import requests

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = '7261209338:AAF-KKdojVZ96tcGaOCXsfbY0ilWSSL_aQs'
SUPPORT_URL = 'https://t.me/raihanhost'
CHANNEL_URL = 'https://t.me/karxpuz'
REFERRAL_LINK_TEMPLATE = 'https://1wbknx.com/v3/aggressive-casino?p=lht9&sub1={user_id}'
CHECK_REGISTRATION_URL = 'http://31.207.47.223:5000/check_registration'
WEBAPP_URL_RU = 'https://lambent-praline-c1cc52.netlify.app'
WEBAPP_URL_EN = 'https://lambent-praline-c1cc52.netlify.app/index_en'

def escape_markdown(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Рус", callback_data='lang_ru'), InlineKeyboardButton("Eng", callback_data='lang_eng')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    caption = '*Выберите язык* / *Choose a language:*'
    if update.message:
        await update.message.reply_photo(photo='lang.png', caption=caption, reply_markup=reply_markup, parse_mode='MarkdownV2')
    elif update.callback_query:
        query = update.callback_query
        await query.message.reply_photo(photo='lang.png', caption=caption, reply_markup=reply_markup, parse_mode='MarkdownV2')

async def lang_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'lang_ru':
        context.user_data['lang'] = 'ru'
        await show_main_menu(query, 'ru')
    elif query.data == 'lang_eng':
        context.user_data['lang'] = 'eng'
        await show_main_menu(query, 'eng')

async def show_main_menu(query: CallbackQuery, lang: str) -> None:
    try:
        await query.message.delete()
    except:
        pass

    if lang == 'ru':
        text = "*Главное меню*"
        play_text = "🕹️Играть"
        support_text = "🆘 Поддержка"
        language_text = "🌐 Смена языка"
    else:
        text = "*Main Menu*"
        play_text = "🕹️Play"
        support_text = "🆘 Support"
        language_text = "🌐 Change Language"

    keyboard = [
        [InlineKeyboardButton(play_text, callback_data='play')],
        [InlineKeyboardButton(language_text, callback_data='change_language'), InlineKeyboardButton(support_text, callback_data='support')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_photo(photo='MainMenu.png' if lang == 'ru' else 'MainMenuEn.png', caption=escape_markdown(text), reply_markup=reply_markup, parse_mode='MarkdownV2')

async def play_game(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    try:
        await query.message.delete()
    except:
        pass
    await query.answer()

    user_name = query.from_user.first_name
    user_id = query.from_user.id
    registration_url = REFERRAL_LINK_TEMPLATE.format(user_id=user_id)
    lang = context.user_data.get('lang', 'ru')

    if lang == 'ru':
        text = (f"👋 Здравствуйте! {escape_markdown(user_name)},\n\n"
                "Чтобы получить максимальную эффективность от использования данного бота, необходимо выполнить следующие шаги:\n\n"
                "1. Зарегистрируйте новый аккаунт - если у Вас уже есть аккаунт, пожалуйста, покиньте его и зарегистрируйте новый.\n"
                f"2. Используйте промокод *LIBTY* при регистрации нового аккаунта. Это важно, так как наш *ИИ* работает только с новыми аккаунтами.\n"
                "3. После регистрации нажмите на кнопку *“Проверить регистрацию”*.\n"
                "4. Если Вы не выполните эти шаги, наш бот не сможет добавить Ваш аккаунт в свою базу данных, и предоставляемые им сигналы могут не подойти.\n\n"
                "Спасибо за понимание!")
        keyboard = [
            [InlineKeyboardButton("📲 РЕГИСТРАЦИЯ", url=registration_url)],
            [InlineKeyboardButton("🔍 ПРОВЕРИТЬ РЕГИСТРАЦИЮ", callback_data='check_registration')],
            [InlineKeyboardButton("🏡 ГЛАВНОЕ МЕНЮ", callback_data='main_menu')]
        ]
    else:
        text = (f"👋 Hello! {escape_markdown(user_name)},\n\n"
                "To get the most out of using this bot, you need to follow these steps:\n\n"
                "1. Register a new account - if you already have an account, please leave it and register a new one.\n"
                f"2. Use the promo code *LIBTY* when registering a new account. This is important because our *AI* only works with new accounts.\n"
                "3. After registration, click the *“Check Registration”* button.\n"
                "4. If you do not follow these steps, our bot will not be able to add your account to its database, and the signals it provides may not be suitable.\n\n"
                "Thank you for your understanding!")
        keyboard = [
            [InlineKeyboardButton("Register", url=registration_url)],
            [InlineKeyboardButton("Check Registration", callback_data='check_registration')],
            [InlineKeyboardButton("Back", callback_data='main_menu')]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_photo(photo='play.png', caption=escape_markdown(text), reply_markup=reply_markup, parse_mode='MarkdownV2')

async def check_registration(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    lang = context.user_data.get('lang', 'ru')
    try:
        await query.message.delete()
    except:
        pass
    await query.answer()

    logging.info(f"Checking registration for user_id: {user_id}")
    response = requests.get(CHECK_REGISTRATION_URL, params={'user_id': user_id})
    logging.info(f"Response from server: {response.json()}")

    if response.status_code == 200 and response.json().get('registered'):
        text = "Ваш аккаунт успешно зарегистрирован! Теперь вы можете начать игру." if lang == 'ru' else "Your account has been successfully registered! Now you can start the game."
        keyboard = [
            [InlineKeyboardButton("Начать игру", web_app=WebAppInfo(url=WEBAPP_URL_RU))] if lang == 'ru' else [InlineKeyboardButton("Start Game", web_app=WebAppInfo(url=WEBAPP_URL_EN))],
            [InlineKeyboardButton("Назад", callback_data='main_menu')] if lang == 'ru' else [InlineKeyboardButton("Back", callback_data='main_menu')]
        ]
    else:
        text = "Регистрация не завершена. Пожалуйста, выполните все шаги и попробуйте снова." if lang == 'ru' else "Registration is not complete. Please complete all steps and try again."
        keyboard = [
            [InlineKeyboardButton("Назад", callback_data='main_menu')] if lang == 'ru' else [InlineKeyboardButton("Back", callback_data='main_menu')]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(text=escape_markdown(text), reply_markup=reply_markup, parse_mode='MarkdownV2')

async def show_support(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    lang = context.user_data.get('lang', 'ru')
    try:
        await query.message.delete()
    except:
        pass
    await query.answer()

    if lang == 'ru':
        text = "💬 Поддержка\n\nЕсли у Вас возникли какие-либо сложности при работе с ботом, либо Вы хотели бы задать нам вопрос – наш менеджер с радостью поможет Вам разобраться."
        keyboard = [
            [InlineKeyboardButton("Написать", url=SUPPORT_URL)],
            [InlineKeyboardButton("Назад", callback_data='main_menu')]
        ]
    else:
        text = "💬 Support\n\nIf you have any difficulties using the bot or would like to ask us a question, our manager will be happy to help you."
        keyboard = [
            [InlineKeyboardButton("Message", url=SUPPORT_URL)],
            [InlineKeyboardButton("Back", callback_data='main_menu')]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_photo(photo='SUPP.png' if lang == 'ru' else 'SUPPEN.png', caption=escape_markdown(text), reply_markup=reply_markup, parse_mode='MarkdownV2')

async def main_menu(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    lang = context.user_data.get('lang', 'ru')
    try:
        await query.message.delete()
    except:
        pass
    await query.answer()
    await show_main_menu(query, lang)

async def change_language(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    try:
        await query.message.delete()
    except:
        pass
    await query.answer()
    await start(update, context)

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(lang_selection, pattern='^lang_'))
    application.add_handler(CallbackQueryHandler(play_game, pattern='^play$'))
    application.add_handler(CallbackQueryHandler(check_registration, pattern='^check_registration$'))
    application.add_handler(CallbackQueryHandler(show_support, pattern='^support$'))
    application.add_handler(CallbackQueryHandler(main_menu, pattern='^main_menu$'))
    application.add_handler(CallbackQueryHandler(change_language, pattern='^change_language$'))

    application.run_polling()

if __name__ == '__main__':
    main()

















