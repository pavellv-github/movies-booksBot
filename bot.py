import os
import random
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, ConversationHandler, filters

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
CHOOSING, EDITING, ADDING_SINGLE, ADDING_MULTIPLE = range(4)

# Хранилище данных (в реальном приложении лучше использовать базу данных)
user_data = {}

def get_main_keyboard():
    """Клавиатура главного меню"""
    keyboard = [
        [KeyboardButton("🎬 Фильмы"), KeyboardButton("📚 Книги")],
        [KeyboardButton("✏️ Редактировать списки")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_edit_keyboard():
    """Клавиатура для редактирования списков"""
    keyboard = [
        [KeyboardButton("📝 Добавить один фильм"), KeyboardButton("📝 Добавить одну книгу")],
        [KeyboardButton("📋 Загрузить список фильмов"), KeyboardButton("📋 Загрузить список книг")],
        [KeyboardButton("🔙 Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /start"""
    user_id = update.message.from_user.id
    
    # Инициализация данных пользователя
    if user_id not in user_data:
        user_data[user_id] = {
            'movies': [],
            'books': []
        }
    
    await update.message.reply_text(
        "🎉 Добро пожаловать!\n\n"
        "Я помогу вам выбрать случайный фильм или книгу из ваших списков.\n\n"
        "Доступные команды:\n"
        "🎬 Фильмы - получить случайный фильм\n"
        "📚 Книги - получить случайную книгу\n"
        "✏️ Редактировать списки - добавить новые фильмы или книги",
        reply_markup=get_main_keyboard()
    )

async def show_random_movie(update: Update, context: CallbackContext) -> None:
    """Показать случайный фильм"""
    user_id = update.message.from_user.id
    movies = user_data[user_id]['movies']
    
    if not movies:
        await update.message.reply_text(
            "📝 Список фильмов пуст. Добавьте фильмы через меню редактирования!",
            reply_markup=get_main_keyboard()
        )
        return
    
    random_movie = random.choice(movies)
    await update.message.reply_text(
        f"🎬 Рекомендую посмотреть:\n\n**{random_movie}**\n\n"
        f"Всего в списке: {len(movies)} фильмов",
        reply_markup=get_main_keyboard()
    )

async def show_random_book(update: Update, context: CallbackContext) -> None:
    """Показать случайную книгу"""
    user_id = update.message.from_user.id
    books = user_data[user_id]['books']
    
    if not books:
        await update.message.reply_text(
            "📝 Список книг пуст. Добавьте книги через меню редактирования!",
            reply_markup=get_main_keyboard()
        )
        return
    
    random_book = random.choice(books)
    await update.message.reply_text(
        f"📚 Рекомендую почитать:\n\n**{random_book}**\n\n"
        f"Всего в списке: {len(books)} книг",
        reply_markup=get_main_keyboard()
    )

async def start_editing(update: Update, context: CallbackContext) -> int:
    """Начать редактирование списков"""
    user_id = update.message.from_user.id
    movies_count = len(user_data[user_id]['movies'])
    books_count = len(user_data[user_id]['books'])
    
    await update.message.reply_text(
        f"✏️ Редактирование списков:\n\n"
        f"🎬 Фильмов в списке: {movies_count}\n"
        f"📚 Книг в списке: {books_count}\n\n"
        "Выберите действие:",
        reply_markup=get_edit_keyboard()
    )
    return CHOOSING

async def add_single_movie(update: Update, context: CallbackContext) -> int:
    """Добавить один фильм"""
    context.user_data['adding_movie'] = True  # ДОБАВЛЕНО
    await update.message.reply_text(
        "🎬 Введите название фильма для добавления:",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Отмена")]], resize_keyboard=True)
    )
    return ADDING_SINGLE

async def add_single_book(update: Update, context: CallbackContext) -> int:
    """Добавить одну книгу"""
    context.user_data['adding_book'] = True  # ДОБАВЛЕНО
    await update.message.reply_text(
        "📚 Введите название книги для добавления:",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Отмена")]], resize_keyboard=True)
    )
    return ADDING_SINGLE

async def add_multiple_movies(update: Update, context: CallbackContext) -> int:
    """Добавить несколько фильмов"""
    context.user_data['adding_movies'] = True  # ДОБАВЛЕНО
    await update.message.reply_text(
        "🎬 Введите список фильмов (каждый с новой строки):",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Отмена")]], resize_keyboard=True)
    )
    return ADDING_MULTIPLE

async def add_multiple_books(update: Update, context: CallbackContext) -> int:
    """Добавить несколько книг"""
    context.user_data['adding_books'] = True  # ДОБАВЛЕНО
    await update.message.reply_text(
        "📚 Введите список книг (каждый с новой строки):",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Отмена")]], resize_keyboard=True)
    )
    return ADDING_MULTIPLE

async def process_single_addition(update: Update, context: CallbackContext) -> int:
    """Обработать добавление одного элемента"""
    user_id = update.message.from_user.id
    text = update.message.text.strip()
    
    # Определяем, что добавляем (из контекста или храним в user_data)
    if 'adding_movie' in context.user_data:
        user_data[user_id]['movies'].append(text)
        await update.message.reply_text(
            f"✅ Фильм '{text}' добавлен в список!",
            reply_markup=get_edit_keyboard()
        )
        del context.user_data['adding_movie']
    elif 'adding_book' in context.user_data:
        user_data[user_id]['books'].append(text)
        await update.message.reply_text(
            f"✅ Книга '{text}' добавлена в список!",
            reply_markup=get_edit_keyboard()
        )
        del context.user_data['adding_book']
    
    return CHOOSING

async def process_multiple_addition(update: Update, context: CallbackContext) -> int:
    """Обработать добавление нескольких элементов"""
    user_id = update.message.from_user.id
    text = update.message.text.strip()
    
    items = [item.strip() for item in text.split('\n') if item.strip()]
    
    if 'adding_movies' in context.user_data:
        user_data[user_id]['movies'].extend(items)
        await update.message.reply_text(
            f"✅ Добавлено {len(items)} фильмов в список!",
            reply_markup=get_edit_keyboard()
        )
        del context.user_data['adding_movies']
    elif 'adding_books' in context.user_data:
        user_data[user_id]['books'].extend(items)
        await update.message.reply_text(
            f"✅ Добавлено {len(items)} книг в список!",
            reply_markup=get_edit_keyboard()
        )
        del context.user_data['adding_books']
    
    return CHOOSING

async def cancel(update: Update, context: CallbackContext) -> int:
    """Отмена текущего действия"""
    # Очищаем флаги добавления
    for key in ['adding_movie', 'adding_book', 'adding_movies', 'adding_books']:
        if key in context.user_data:
            del context.user_data[key]
    
    await update.message.reply_text(
        "Действие отменено",
        reply_markup=get_edit_keyboard()
    )
    return CHOOSING

async def back_to_main(update: Update, context: CallbackContext) -> int:
    """Вернуться в главное меню"""
    # Очищаем флаги добавления
    for key in ['adding_movie', 'adding_book', 'adding_movies', 'adding_books']:
        if key in context.user_data:
            del context.user_data[key]
    
    await update.message.reply_text(
        "Главное меню:",
        reply_markup=get_main_keyboard()
    )
    return ConversationHandler.END

def main() -> None:
    """Запуск бота"""
    # Получаем токен из переменной окружения
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    if not TOKEN:
        raise ValueError("Не задан TELEGRAM_BOT_TOKEN в переменных окружения")
    
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()
    
    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    
    # Обработчики кнопок главного меню
    application.add_handler(MessageHandler(filters.Text("🎬 Фильмы"), show_random_movie))
    application.add_handler(MessageHandler(filters.Text("📚 Книги"), show_random_book))
    
    # ConversationHandler для редактирования списков
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Text("✏️ Редактировать списки"), start_editing)],
        states={
            CHOOSING: [
                MessageHandler(filters.Text("📝 Добавить один фильм"), add_single_movie),
                MessageHandler(filters.Text("📝 Добавить одну книгу"), add_single_book),
                MessageHandler(filters.Text("📋 Загрузить список фильмов"), add_multiple_movies),
                MessageHandler(filters.Text("📋 Загрузить список книг"), add_multiple_books),
                MessageHandler(filters.Text("🔙 Назад"), back_to_main),
            ],
            ADDING_SINGLE: [
                MessageHandler(filters.Text("🔙 Отмена"), cancel),
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_single_addition),
            ],
            ADDING_MULTIPLE: [
                MessageHandler(filters.Text("🔙 Отмена"), cancel),
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_multiple_addition),
            ],
        },
        fallbacks=[MessageHandler(filters.Text("🔙 Назад"), back_to_main)],
    )
    
    application.add_handler(conv_handler)
    
    # Запуск бота
    print("Бот запущен...")
    application.run_polling()

if __name__ == '__main__':
    main()