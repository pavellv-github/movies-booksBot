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
MAIN_MENU, EDITING, MARKING, ADDING_SINGLE, ADDING_MULTIPLE, MARKING_ITEM = range(6)

# Хранилище данных
user_data = {}

def get_main_keyboard():
    """Клавиатура главного меню"""
    keyboard = [
        [KeyboardButton("🎬 Фильмы"), KeyboardButton("📚 Книги")],
        [KeyboardButton("✅ Отметить прочитанное"), KeyboardButton("✏️ Редактировать списки")]
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

def get_marking_keyboard():
    """Клавиатура для отметки прочитанного/просмотренного"""
    keyboard = [
        [KeyboardButton("🎬 Отметить фильм"), KeyboardButton("📚 Отметить книгу")],
        [KeyboardButton("📊 Статистика"), KeyboardButton("🔙 Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: CallbackContext) -> int:
    """Обработчик команды /start"""
    user_id = update.message.from_user.id
    
    # Инициализация данных пользователя
    if user_id not in user_data:
        user_data[user_id] = {
            'movies': [],
            'books': [],
            'watched_movies': [],
            'read_books': []
        }
    
    stats = get_user_stats(user_id)
    
    await update.message.reply_text(
        f"🎉 Добро пожаловать!\n\n"
        f"📊 Ваша статистика:\n"
        f"🎬 Фильмов в очереди: {stats['movies_queued']}\n"
        f"🎬 Просмотрено: {stats['movies_watched']}\n"
        f"📚 Книг в очереди: {stats['books_queued']}\n"
        f"📚 Прочитано: {stats['books_read']}\n\n"
        "Доступные команды:\n"
        "🎬 Фильмы - получить случайный фильм\n"
        "📚 Книги - получить случайную книгу\n"
        "✅ Отметить прочитанное - перенести в завершенные\n"
        "✏️ Редактировать списки - добавить новые фильмы или книги",
        reply_markup=get_main_keyboard()
    )
    return MAIN_MENU

def get_user_stats(user_id):
    """Получить статистику пользователя"""
    if user_id not in user_data:
        return {'movies_queued': 0, 'movies_watched': 0, 'books_queued': 0, 'books_read': 0}
    
    return {
        'movies_queued': len(user_data[user_id]['movies']),
        'movies_watched': len(user_data[user_id]['watched_movies']),
        'books_queued': len(user_data[user_id]['books']),
        'books_read': len(user_data[user_id]['read_books'])
    }

async def show_random_movie(update: Update, context: CallbackContext) -> int:
    """Показать случайный фильм"""
    user_id = update.message.from_user.id
    movies = user_data[user_id]['movies']
    
    if not movies:
        stats = get_user_stats(user_id)
        await update.message.reply_text(
            f"📝 Список фильмов пуст. Добавьте фильмы через меню редактирования!\n\n"
            f"📊 Статистика:\n"
            f"🎬 Просмотрено: {stats['movies_watched']}",
            reply_markup=get_main_keyboard()
        )
        return MAIN_MENU
    
    random_movie = random.choice(movies)
    stats = get_user_stats(user_id)
    await update.message.reply_text(
        f"🎬 Рекомендую посмотреть:\n\n**{random_movie}**\n\n"
        f"📊 Статистика:\n"
        f"🎬 В очереди: {stats['movies_queued']}\n"
        f"🎬 Просмотрено: {stats['movies_watched']}",
        reply_markup=get_main_keyboard()
    )
    return MAIN_MENU

async def show_random_book(update: Update, context: CallbackContext) -> int:
    """Показать случайную книгу"""
    user_id = update.message.from_user.id
    books = user_data[user_id]['books']
    
    if not books:
        stats = get_user_stats(user_id)
        await update.message.reply_text(
            f"📝 Список книг пуст. Добавьте книги через меню редактирования!\n\n"
            f"📊 Статистика:\n"
            f"📚 Прочитано: {stats['books_read']}",
            reply_markup=get_main_keyboard()
        )
        return MAIN_MENU
    
    random_book = random.choice(books)
    stats = get_user_stats(user_id)
    await update.message.reply_text(
        f"📚 Рекомендую почитать:\n\n**{random_book}**\n\n"
        f"📊 Статистика:\n"
        f"📚 В очереди: {stats['books_queued']}\n"
        f"📚 Прочитано: {stats['books_read']}",
        reply_markup=get_main_keyboard()
    )
    return MAIN_MENU

async def start_marking(update: Update, context: CallbackContext) -> int:
    """Начать процесс отметки прочитанного/просмотренного"""
    user_id = update.message.from_user.id
    stats = get_user_stats(user_id)
    
    await update.message.reply_text(
        f"✅ Отметить прочитанное/просмотренное\n\n"
        f"📊 Текущая статистика:\n"
        f"🎬 Фильмов в очереди: {stats['movies_queued']}\n"
        f"🎬 Просмотрено: {stats['movies_watched']}\n"
        f"📚 Книг в очереди: {stats['books_queued']}\n"
        f"📚 Прочитано: {stats['books_read']}\n\n"
        "Выберите что хотите отметить:",
        reply_markup=get_marking_keyboard()
    )
    return MARKING

async def show_stats(update: Update, context: CallbackContext) -> int:
    """Показать статистику"""
    user_id = update.message.from_user.id
    stats = get_user_stats(user_id)
    
    await update.message.reply_text(
        f"📊 Ваша статистика:\n\n"
        f"🎬 Фильмы:\n"
        f"   В очереди: {stats['movies_queued']}\n"
        f"   Просмотрено: {stats['movies_watched']}\n\n"
        f"📚 Книги:\n"
        f"   В очереди: {stats['books_queued']}\n"
        f"   Прочитано: {stats['books_read']}\n\n"
        f"📈 Всего завершено: {stats['movies_watched'] + stats['books_read']}",
        reply_markup=get_marking_keyboard()
    )
    return MARKING

async def mark_movie(update: Update, context: CallbackContext) -> int:
    """Отметить фильм как просмотренный"""
    user_id = update.message.from_user.id
    movies = user_data[user_id]['movies']
    
    if not movies:
        await update.message.reply_text(
            "📝 Список фильмов пуст. Нечего отмечать!",
            reply_markup=get_marking_keyboard()
        )
        return MARKING
    
    # Показываем список фильмов для выбора (с разбивкой на части если нужно)
    movies_list = "\n".join([f"• {movie}" for movie in movies])
    
    # Проверяем длину сообщения
    if len(movies_list) > 4000:
        # Разбиваем на части
        await update.message.reply_text(
            "🎬 Список фильмов очень большой. Показываю первые 50 фильмов:"
        )
        short_list = "\n".join([f"• {movie}" for movie in movies[:50]])
        await update.message.reply_text(
            f"{short_list}\n\n... и еще {len(movies) - 50} фильмов\n\n"
            f"Введите название фильма:",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Отмена")]], resize_keyboard=True)
        )
    else:
        await update.message.reply_text(
            f"🎬 Выберите фильм для отметки:\n\n{movies_list}\n\n"
            f"Введите название фильма:",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Отмена")]], resize_keyboard=True)
        )
    
    context.user_data['marking_movie'] = True
    return MARKING_ITEM

async def mark_book(update: Update, context: CallbackContext) -> int:
    """Отметить книгу как прочитанную"""
    user_id = update.message.from_user.id
    books = user_data[user_id]['books']
    
    if not books:
        await update.message.reply_text(
            "📝 Список книг пуст. Нечего отмечать!",
            reply_markup=get_marking_keyboard()
        )
        return MARKING
    
    # Показываем список книг для выбора (с разбивкой на части если нужно)
    books_list = "\n".join([f"• {book}" for book in books])
    
    # Проверяем длину сообщения
    if len(books_list) > 4000:
        # Разбиваем на части
        await update.message.reply_text(
            "📚 Список книг очень большой. Показываю первые 50 книг:"
        )
        short_list = "\n".join([f"• {book}" for book in books[:50]])
        await update.message.reply_text(
            f"{short_list}\n\n... и еще {len(books) - 50} книг\n\n"
            f"Введите название книги:",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Отмена")]], resize_keyboard=True)
        )
    else:
        await update.message.reply_text(
            f"📚 Выберите книгу для отметки:\n\n{books_list}\n\n"
            f"Введите название книги:",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Отмена")]], resize_keyboard=True)
        )
    
    context.user_data['marking_book'] = True
    return MARKING_ITEM

async def process_marking(update: Update, context: CallbackContext) -> int:
    """Обработать отметку прочитанного/просмотренного"""
    user_id = update.message.from_user.id
    text = update.message.text.strip()
    
    if 'marking_movie' in context.user_data:
        # Отмечаем фильм
        if text in user_data[user_id]['movies']:
            user_data[user_id]['movies'].remove(text)
            user_data[user_id]['watched_movies'].append(text)
            stats = get_user_stats(user_id)
            await update.message.reply_text(
                f"✅ Фильм '{text}' отмечен как просмотренный!\n\n"
                f"📊 Обновленная статистика:\n"
                f"🎬 В очереди: {stats['movies_queued']}\n"
                f"🎬 Просмотрено: {stats['movies_watched']}",
                reply_markup=get_marking_keyboard()
            )
        else:
            await update.message.reply_text(
                f"❌ Фильм '{text}' не найден в списке. Проверьте написание.",
                reply_markup=get_marking_keyboard()
            )
        del context.user_data['marking_movie']
        return MARKING
        
    elif 'marking_book' in context.user_data:
        # Отмечаем книгу
        if text in user_data[user_id]['books']:
            user_data[user_id]['books'].remove(text)
            user_data[user_id]['read_books'].append(text)
            stats = get_user_stats(user_id)
            await update.message.reply_text(
                f"✅ Книга '{text}' отмечена как прочитанная!\n\n"
                f"📊 Обновленная статистика:\n"
                f"📚 В очереди: {stats['books_queued']}\n"
                f"📚 Прочитано: {stats['books_read']}",
                reply_markup=get_marking_keyboard()
            )
        else:
            await update.message.reply_text(
                f"❌ Книга '{text}' не найдена в списке. Проверьте написание.",
                reply_markup=get_marking_keyboard()
            )
        del context.user_data['marking_book']
        return MARKING
    
    return MARKING

async def start_editing(update: Update, context: CallbackContext) -> int:
    """Начать редактирование списков"""
    user_id = update.message.from_user.id
    stats = get_user_stats(user_id)
    
    await update.message.reply_text(
        f"✏️ Редактирование списков:\n\n"
        f"📊 Статистика:\n"
        f"🎬 Фильмов в очереди: {stats['movies_queued']}\n"
        f"🎬 Просмотрено: {stats['movies_watched']}\n"
        f"📚 Книг в очереди: {stats['books_queued']}\n"
        f"📚 Прочитано: {stats['books_read']}\n\n"
        "Выберите действие:",
        reply_markup=get_edit_keyboard()
    )
    return EDITING

async def add_single_movie(update: Update, context: CallbackContext) -> int:
    """Добавить один фильм"""
    context.user_data['adding_movie'] = True
    await update.message.reply_text(
        "🎬 Введите название фильма для добавления:",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Отмена")]], resize_keyboard=True)
    )
    return ADDING_SINGLE

async def add_single_book(update: Update, context: CallbackContext) -> int:
    """Добавить одну книгу"""
    context.user_data['adding_book'] = True
    await update.message.reply_text(
        "📚 Введите название книги для добавления:",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Отмена")]], resize_keyboard=True)
    )
    return ADDING_SINGLE

async def add_multiple_movies(update: Update, context: CallbackContext) -> int:
    """Добавить несколько фильмов"""
    context.user_data['adding_movies'] = True
    await update.message.reply_text(
        "🎬 Введите список фильмов (каждый с новой строки):",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Отмена")]], resize_keyboard=True)
    )
    return ADDING_MULTIPLE

async def add_multiple_books(update: Update, context: CallbackContext) -> int:
    """Добавить несколько книг"""
    context.user_data['adding_books'] = True
    await update.message.reply_text(
        "📚 Введите список книг (каждый с новой строки):",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Отмена")]], resize_keyboard=True)
    )
    return ADDING_MULTIPLE

async def process_single_addition(update: Update, context: CallbackContext) -> int:
    """Обработать добавление одного элемента"""
    user_id = update.message.from_user.id
    text = update.message.text.strip()
    
    if 'adding_movie' in context.user_data:
        user_data[user_id]['movies'].append(text)
        stats = get_user_stats(user_id)
        await update.message.reply_text(
            f"✅ Фильм '{text}' добавлен в список!\n\n"
            f"🎬 Фильмов в очереди: {stats['movies_queued']}",
            reply_markup=get_edit_keyboard()
        )
        del context.user_data['adding_movie']
        return EDITING
    elif 'adding_book' in context.user_data:
        user_data[user_id]['books'].append(text)
        stats = get_user_stats(user_id)
        await update.message.reply_text(
            f"✅ Книга '{text}' добавлена в список!\n\n"
            f"📚 Книг в очереди: {stats['books_queued']}",
            reply_markup=get_edit_keyboard()
        )
        del context.user_data['adding_book']
        return EDITING
    
    return EDITING

async def process_multiple_addition(update: Update, context: CallbackContext) -> int:
    """Обработать добавление нескольких элементов"""
    user_id = update.message.from_user.id
    text = update.message.text.strip()
    
    items = [item.strip() for item in text.split('\n') if item.strip()]
    
    if 'adding_movies' in context.user_data:
        user_data[user_id]['movies'].extend(items)
        stats = get_user_stats(user_id)
        await update.message.reply_text(
            f"✅ Добавлено {len(items)} фильмов в список!\n\n"
            f"🎬 Фильмов в очереди: {stats['movies_queued']}",
            reply_markup=get_edit_keyboard()
        )
        del context.user_data['adding_movies']
        return EDITING
    elif 'adding_books' in context.user_data:
        user_data[user_id]['books'].extend(items)
        stats = get_user_stats(user_id)
        await update.message.reply_text(
            f"✅ Добавлено {len(items)} книг в список!\n\n"
            f"📚 Книг в очереди: {stats['books_queued']}",
            reply_markup=get_edit_keyboard()
        )
        del context.user_data['adding_books']
        return EDITING
    
    return EDITING

async def cancel(update: Update, context: CallbackContext) -> int:
    """Отмена текущего действия"""
    # Очищаем все флаги
    for key in ['adding_movie', 'adding_book', 'adding_movies', 'adding_books', 'marking_movie', 'marking_book']:
        if key in context.user_data:
            del context.user_data[key]
    
    # Определяем откуда пришли
    if 'came_from_marking' in context.user_data:
        await update.message.reply_text("Действие отменено", reply_markup=get_marking_keyboard())
        del context.user_data['came_from_marking']
        return MARKING
    elif 'came_from_editing' in context.user_data:
        await update.message.reply_text("Действие отменено", reply_markup=get_edit_keyboard())
        del context.user_data['came_from_editing']
        return EDITING
    else:
        await update.message.reply_text("Действие отменено", reply_markup=get_main_keyboard())
        return MAIN_MENU

async def back_to_main(update: Update, context: CallbackContext) -> int:
    """Вернуться в главное меню"""
    # Очищаем все флаги
    for key in ['adding_movie', 'adding_book', 'adding_movies', 'adding_books', 'marking_movie', 'marking_book']:
        if key in context.user_data:
            del context.user_data[key]
    
    await update.message.reply_text("Главное меню:", reply_markup=get_main_keyboard())
    return MAIN_MENU

def main() -> None:
    """Запуск бота"""
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    if not TOKEN:
        raise ValueError("Не задан TELEGRAM_BOT_TOKEN в переменных окружения")
    
    application = Application.builder().token(TOKEN).build()
    
    # Основной ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [
                MessageHandler(filters.Text("🎬 Фильмы"), show_random_movie),
                MessageHandler(filters.Text("📚 Книги"), show_random_book),
                MessageHandler(filters.Text("✅ Отметить прочитанное"), start_marking),
                MessageHandler(filters.Text("✏️ Редактировать списки"), start_editing),
            ],
            EDITING: [
                MessageHandler(filters.Text("📝 Добавить один фильм"), add_single_movie),
                MessageHandler(filters.Text("📝 Добавить одну книгу"), add_single_book),
                MessageHandler(filters.Text("📋 Загрузить список фильмов"), add_multiple_movies),
                MessageHandler(filters.Text("📋 Загрузить список книг"), add_multiple_books),
                MessageHandler(filters.Text("🔙 Назад"), back_to_main),
            ],
            MARKING: [
                MessageHandler(filters.Text("🎬 Отметить фильм"), mark_movie),
                MessageHandler(filters.Text("📚 Отметить книгу"), mark_book),
                MessageHandler(filters.Text("📊 Статистика"), show_stats),
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
            MARKING_ITEM: [
                MessageHandler(filters.Text("🔙 Отмена"), cancel),
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_marking),
            ],
        },
        fallbacks=[MessageHandler(filters.Text("🔙 Назад"), back_to_main)],
    )
    
    application.add_handler(conv_handler)
    
    print("Бот запущен...")
    application.run_polling()

if __name__ == '__main__':
    main()