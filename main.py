import logging
import time
import json
import os
from functools import partial
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, CallbackQuery, Message
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, filters
import re

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = ''
SUPPORT_URL = 'https://t.me/raihanhost'
CHANNEL_URL = 'https://t.me/raihanhost'
CHANNEL_ID = '-1002211482813'  # Ваш полученный ID канала
REFERRAL_LINK_TEMPLATE = 'https://1wqsg.com/v3/landing-page/casino?p=qpjg&sub1={user_id}'
WEBAPP_URL_RU = 'https://lambent-praline-c1cc52.netlify.app'
WEBAPP_URL_EN = 'https://lambent-praline-c1cc52.netlify.app/index_en'

# Хранилище для отслеживания зарегистрированных пользователей
registered_users = set()
SESSION_FILE = 'sessions.json'

application = Application.builder().token(TOKEN).build()

def load_sessions():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r') as f:
            data = json.load(f)
            return data
    return {}

def save_sessions(sessions):
    with open(SESSION_FILE, 'w') as f:
        json.dump(sessions, f)

def load_registered_users():
    sessions = load_sessions()
    return set(sessions.get('registered_users', []))

def save_registered_users():
    sessions = {
        'registered_users': list(registered_users)
    }
    save_sessions(sessions)

registered_users = load_registered_users()

def escape_html(text):
    escape_chars = {'<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;'}
    return ''.join(escape_chars.get(char, char) for char in text)

def save_step(context, step, *args):
    if 'history' not in context.user_data:
        context.user_data['history'] = []
    if not context.user_data['history'] or context.user_data['history'][-1] != (step, args):
        context.user_data['history'].append((step, args))

def save_last_message(context, message):
    context.user_data['last_message'] = message

async def go_back(update: Update, context: CallbackContext) -> None:
    if 'history' in context.user_data and context.user_data['history']:
        context.user_data['history'].pop()  # Remove current step
        if context.user_data['history']:
            last_step, args = context.user_data['history'].pop()
            await last_step(update, context, *args)
            return
    await start(update, context)

async def start(update: Update, context: CallbackContext) -> None:
    save_step(context, start)
    keyboard = [
        [InlineKeyboardButton("Русский", callback_data='lang_ru'), InlineKeyboardButton("English", callback_data='lang_eng')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    caption = '<b>Выберите язык</b> / <b>Choose a language:</b>'
    message = await update.message.reply_photo(photo='lang.png', caption=caption, reply_markup=reply_markup, parse_mode='HTML') if update.message else await update.callback_query.message.reply_photo(photo='lang.png', caption=caption, reply_markup=reply_markup, parse_mode='HTML')
    save_last_message(context, message)

async def lang_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'lang_ru':
        context.user_data['lang'] = 'ru'
        await show_main_menu(query, context, 'ru')
    elif query.data == 'lang_eng':
        context.user_data['lang'] = 'eng'
        await show_main_menu(query, context, 'eng')

async def show_main_menu(query: CallbackQuery, context: CallbackContext, lang: str) -> None:
    save_step(context, partial(show_main_menu, lang=lang))
    try:
        await query.message.delete()
    except:
        pass

    if lang == 'ru':
        text = "<b>Главное меню:</b>"
        play_text = "🕹️Играть"
        support_text = "🆘 Поддержка"
        language_text = "🌐 Смена языка"
    else:
        text = "<b>Main Menu:</b>"
        play_text = "🕹️Play"
        support_text = "🆘 Support"
        language_text = "🌐 Change Language"

    keyboard = [
        [InlineKeyboardButton(play_text, callback_data='play')],
        [InlineKeyboardButton(language_text, callback_data='change_language'), InlineKeyboardButton(support_text, callback_data='support')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    last_message = context.user_data.get('last_message')
    if last_message:
        message = await last_message.reply_photo(photo='MainMenu.png' if lang == 'ru' else 'MainMenuEn.png', caption=text, reply_markup=reply_markup, parse_mode='HTML')
        save_last_message(context, message)

async def play_game(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    save_step(context, play_game)
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
        text = (f"👋 Здравствуйте! {user_name},\n\n"
                "Чтобы получить максимальную эффективность от использования данного бота, необходимо выполнить следующие шаги:\n\n"
                "1. Зарегистрируйте новый аккаунт - если у Вас уже есть аккаунт, пожалуйста, покиньте его и зарегистрируйте новый.\n"
                f"2. Используйте промокод <b>LIBTY</b> при регистрации нового аккаунта. Это важно, так как наш <b>ИИ</b> работает только с новыми аккаунтами.\n"
                "3. После регистрации нажмите на кнопку <b>“Проверить регистрацию”</b>.\n"
                "4. Если Вы не выполните эти шаги, наш бот не сможет добавить Ваш аккаунт в свою базу данных, и предоставляемые им сигналы могут не подойти.\n\n"
                "Спасибо за понимание!")
        keyboard = [
            [InlineKeyboardButton("📲 РЕГИСТРАЦИЯ", url=registration_url)],
            [InlineKeyboardButton("🔍 ПРОВЕРИТЬ РЕГИСТРАЦИЮ", callback_data='check_registration')],
            [InlineKeyboardButton("🏡 ГЛАВНОЕ МЕНЮ", callback_data='main_menu')]
        ]
    else:
        text = (f"👋 Hello! {user_name},\n\n"
                "To get the most out of using this bot, you need to follow these steps:\n\n"
                "1. Register a new account - if you already have an account, please leave it and register a new one.\n"
                f"2. Use the promo code <b>LIBTY</b> when registering a new account. This is important because our <b>AI</b> only works with new accounts.\n"
                "3. After registration, click the <b>“Check Registration”</b> button.\n"
                "4. If you do not follow these steps, our bot will not be able to add your account to its database, and the signals it provides may not be suitable.\n\n"
                "Thank you for your understanding!")
        keyboard = [
            [InlineKeyboardButton("📲 REGISTRATION", url=registration_url)],
            [InlineKeyboardButton("🔍 CHECK REGISTRATION", callback_data='check_registration')],
            [InlineKeyboardButton("🏡 MAIN MENU", callback_data='main_menu')]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    last_message = context.user_data.get('last_message')
    if last_message:
        message = await last_message.reply_photo(photo='play.png', caption=text, reply_markup=reply_markup, parse_mode='HTML')
        save_last_message(context, message)

async def check_registration(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    save_step(context, check_registration)
    user_id = query.from_user.id
    lang = context.user_data.get('lang', 'ru')
    try:
        await query.message.delete()
    except:
        pass
    await query.answer()

    logging.info(f"Checking registration for user_id: {user_id}")
    logging.info(f"Registered users: {registered_users}")

    if user_id in registered_users:
        text = "<b>Теперь вы можете получить сигнал!\nВаш аккаунт успешно зарегистрирован</b> ✅" if lang == 'ru' else "<b>Now you can receive a signal!\nYour account has been successfully registered</b> ✅"
        keyboard = [
            [InlineKeyboardButton("Начать игру 🕹", web_app=WebAppInfo(url=WEBAPP_URL_RU))] if lang == 'ru' else [InlineKeyboardButton("Start Game", web_app=WebAppInfo(url=WEBAPP_URL_EN))],
            [InlineKeyboardButton("Назад", callback_data='back')]
        ]
    else:
        text = "Регистрация не завершена. Пожалуйста, выполните все шаги и попробуйте снова." if lang == 'ru' else "Registration is not complete. Please complete all steps and try again."
        keyboard = [
            [InlineKeyboardButton("Назад", callback_data='back')]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = await query.message.reply_text(text=text, reply_markup=reply_markup, parse_mode='HTML')
    save_last_message(context, message)

async def show_support(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    save_step(context, show_support)
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
            [InlineKeyboardButton("Назад", callback_data='back')]
        ]
    else:
        text = "💬 Support\n\nIf you have any difficulties using the bot or would like to ask us a question, our manager will be happy to help you."
        keyboard = [
            [InlineKeyboardButton("Message", url=SUPPORT_URL)],
            [InlineKeyboardButton("Back", callback_data='back')]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    last_message = context.user_data.get('last_message')
    if last_message:
        message = await last_message.reply_photo(photo='SUPP.png' if lang == 'ru' else 'SUPPEN.png', caption=text, reply_markup=reply_markup, parse_mode='HTML')
        save_last_message(context, message)

async def change_language(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    save_step(context, change_language)
    try:
        await query.message.delete()
    except:
        pass
    await query.answer()
    await start(update, context)

async def main_menu(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    lang = context.user_data.get('lang', 'ru')
    await show_main_menu(query, context, lang)

class RegistrationSuccessFilter(filters.BaseFilter):
    def filter(self, message) -> bool:
        return str(message.chat_id) == CHANNEL_ID

async def log_all_channel_messages(update: Update, context: CallbackContext) -> None:
    if update.channel_post:
        message = update.channel_post.text
        logging.info(f"Received message: {message}")

        # Логируем все сообщения, чтобы понять, какие из них бот обрабатывает
        logging.info(f"Channel message: {message}")

        # Если сообщение содержит только цифры, обрабатываем его
        if message.isdigit():
            user_id = int(message)
            registered_users.add(user_id)
            logging.info(f'User {user_id} successfully registered.')
            logging.info(f"Registered users: {registered_users}")
            save_registered_users()

def main() -> None:
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(lang_selection, pattern='^lang_'))
    application.add_handler(CallbackQueryHandler(play_game, pattern='^play$'))
    application.add_handler(CallbackQueryHandler(check_registration, pattern='^check_registration$'))
    application.add_handler(CallbackQueryHandler(show_support, pattern='^support$'))
    application.add_handler(CallbackQueryHandler(change_language, pattern='^change_language$'))
    application.add_handler(CallbackQueryHandler(go_back, pattern='^back$'))
    application.add_handler(CallbackQueryHandler(main_menu, pattern='^main_menu$'))
    application.add_handler(MessageHandler(RegistrationSuccessFilter(), log_all_channel_messages))

    application.run_polling()

    # Сохранение состояния перед завершением работы
    save_registered_users()

if __name__ == '__main__':
    main()







