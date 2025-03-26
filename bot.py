import os
import logging
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telegram import (
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    Update, 
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    CallbackQueryHandler, 
    MessageHandler, 
    filters, 
    ContextTypes,
    ConversationHandler
)

from helpers import fetch_cities, fetch_countries, fetch_tours, format_tour_details
from nlp_processor import process_message

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SAMO_TOKEN = os.getenv("SAMO_OAUTH_TOKEN")

# Constants for ConversationHandler
SELECTING_ACTION, SELECTING_CITY, SELECTING_COUNTRY, SELECTING_DATES, BOOKING_TOUR, COLLECT_NAME, COLLECT_PHONE, CONFIRM_BOOKING = range(8)

# User session storage
user_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user what they want to do."""
    user_id = update.effective_user.id
    user_sessions[user_id] = {}
    
    keyboard = [
        [InlineKeyboardButton("🔍 Поиск туров", callback_data="search_tours")],
        [InlineKeyboardButton("❓ Помощь", callback_data="help")]
    ]
    
    await update.message.reply_text(
        "Добро пожаловать в Crystal Bay Travel! 🏖️\n\n"
        "Я помогу вам найти идеальный тур для вашего отпуска. "
        "Чем я могу вам помочь сегодня?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return SELECTING_ACTION

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = (
        "🌴 *Crystal Bay Travel Bot* 🌴\n\n"
        "*Доступные команды:*\n"
        "/start - Начать общение с ботом\n"
        "/help - Показать это сообщение\n"
        "/search - Начать поиск туров\n"
        "/cancel - Отменить текущее действие\n\n"
        "*Как использовать:*\n"
        "1. Выберите город вылета\n"
        "2. Выберите страну назначения\n"
        "3. Выберите даты поездки\n"
        "4. Просмотрите доступные туры\n"
        "5. Забронируйте понравившийся тур\n\n"
        "Вы также можете задать мне вопрос о турах или услугах Crystal Bay Travel, и я постараюсь помочь!"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel and end the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    
    await update.message.reply_text(
        'Поиск отменен. Когда захотите продолжить, нажмите /start.',
        reply_markup=ReplyKeyboardRemove()
    )
    
    return ConversationHandler.END

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the inline keyboard button press."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data == "search_tours":
        return await select_departure_city(update, context)
    elif data == "help":
        await query.message.reply_text(
            "🌴 *Crystal Bay Travel Bot* 🌴\n\n"
            "Этот бот поможет вам найти и забронировать идеальный тур.\n\n"
            "*Как использовать:*\n"
            "1. Выберите город вылета\n"
            "2. Выберите страну назначения\n"
            "3. Выберите даты поездки\n"
            "4. Просмотрите доступные туры\n"
            "5. Забронируйте понравившийся тур\n\n"
            "Для начала нажмите /start.",
            parse_mode='Markdown'
        )
        return SELECTING_ACTION
    elif data.startswith("city_"):
        city_id = data.split("_")[1]
        if user_id not in user_sessions:
            user_sessions[user_id] = {}
        user_sessions[user_id]["departure_city"] = city_id
        return await select_country(update, context)
    elif data.startswith("country_"):
        country_id = data.split("_")[1]
        user_sessions[user_id]["country"] = country_id
        return await select_dates(update, context)
    elif data.startswith("date_"):
        date_selected = data.split("_")[1]
        user_sessions[user_id]["checkin"] = date_selected
        return await search_tours(update, context)
    elif data.startswith("book_"):
        tour_id = data.split("_")[1]
        user_sessions[user_id]["tour_id"] = tour_id
        return await initiate_booking(update, context)
    elif data == "confirm_booking":
        return await finalize_booking(update, context)
    elif data == "cancel_booking":
        await query.message.reply_text("Бронирование отменено. Для начала нового поиска нажмите /start.")
        return ConversationHandler.END
    
    # Default fallback
    await query.message.reply_text("Непонятная команда. Для начала нажмите /start.")
    return SELECTING_ACTION

async def select_departure_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show available departure cities."""
    query = update.callback_query if update.callback_query else None
    message = query.message if query else update.message
    
    try:
        cities = await fetch_cities(SAMO_TOKEN)
        
        if not cities:
            await message.reply_text(
                "😔 Не удалось получить список городов вылета. Пожалуйста, попробуйте позже."
            )
            return SELECTING_ACTION
        
        # Create a keyboard with cities
        keyboard = []
        row = []
        for i, city in enumerate(cities):
            row.append(InlineKeyboardButton(city["nameAlt"], callback_data=f"city_{city['id']}"))
            
            # 2 buttons per row
            if (i + 1) % 2 == 0 or i == len(cities) - 1:
                keyboard.append(row)
                row = []
        
        await message.reply_text(
            "Выберите город вылета:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        return SELECTING_CITY
        
    except Exception as e:
        logger.error(f"Error in select_departure_city: {e}")
        await message.reply_text(
            "😔 Произошла ошибка при получении списка городов. Пожалуйста, попробуйте позже."
        )
        return SELECTING_ACTION

async def select_country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show available countries based on selected departure city."""
    query = update.callback_query
    user_id = query.from_user.id
    
    try:
        city_id = user_sessions[user_id]["departure_city"]
        countries = await fetch_countries(SAMO_TOKEN, city_id)
        
        if not countries:
            await query.message.reply_text(
                "😔 Не удалось получить список стран. Пожалуйста, попробуйте позже."
            )
            return SELECTING_CITY
        
        # Create a keyboard with countries
        keyboard = []
        row = []
        for i, country in enumerate(countries):
            row.append(InlineKeyboardButton(country["nameAlt"], callback_data=f"country_{country['id']}"))
            
            # 2 buttons per row
            if (i + 1) % 2 == 0 or i == len(countries) - 1:
                keyboard.append(row)
                row = []
        
        await query.message.reply_text(
            "Выберите страну назначения:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        return SELECTING_COUNTRY
        
    except Exception as e:
        logger.error(f"Error in select_country: {e}")
        await query.message.reply_text(
            "😔 Произошла ошибка при получении списка стран. Пожалуйста, попробуйте позже."
        )
        return SELECTING_CITY

async def select_dates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show available travel dates."""
    query = update.callback_query
    
    # Generate dates for the next 30 days
    dates = [(datetime.now() + timedelta(days=i)) for i in range(1, 31)]
    
    # Create a keyboard with dates (3 dates per row)
    keyboard = []
    row = []
    for i, date in enumerate(dates[:21]):  # Limit to 21 days to keep interface cleaner
        formatted_date = date.strftime("%d.%m")
        raw_date = date.strftime("%Y%m%d")
        row.append(InlineKeyboardButton(formatted_date, callback_data=f"date_{raw_date}"))
        
        # 3 buttons per row
        if (i + 1) % 3 == 0 or i == len(dates) - 1:
            keyboard.append(row)
            row = []
    
    await query.message.reply_text(
        "Выберите дату заезда:\n(Даты показаны в формате ДД.ММ)",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return SELECTING_DATES

async def search_tours(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Search for tours based on user selections."""
    query = update.callback_query
    user_id = query.from_user.id
    session = user_sessions[user_id]
    
    await query.message.reply_text("🔎 Ищем туры, пожалуйста подождите...")
    
    try:
        tours = await fetch_tours(
            SAMO_TOKEN,
            session["departure_city"],
            session["country"],
            session["checkin"]
        )
        
        if not tours:
            await query.message.reply_text(
                "😞 Туры по вашим параметрам не найдены.\n"
                "Попробуйте изменить даты или направление."
            )
            
            # Provide option to start over
            keyboard = [[InlineKeyboardButton("🔍 Новый поиск", callback_data="search_tours")]]
            await query.message.reply_text(
                "Хотите начать поиск заново?",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return SELECTING_ACTION
        
        user_sessions[user_id]["tours"] = tours
        
        # Display found tours (limit to 5 to avoid message limit)
        await query.message.reply_text(f"🏝️ Найдено {len(tours)} туров:")
        
        for tour in tours[:5]:  # Limit to 5 tours to avoid spam
            tour_info = format_tour_details(tour)
            
            keyboard = [[InlineKeyboardButton("📅 Забронировать", callback_data=f"book_{tour['id']}")]]
            await query.message.reply_text(
                tour_info,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        
        # Add option for new search
        keyboard = [[InlineKeyboardButton("🔍 Новый поиск", callback_data="search_tours")]]
        await query.message.reply_text(
            "Хотите начать поиск заново?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        return BOOKING_TOUR
        
    except Exception as e:
        logger.error(f"Error in search_tours: {e}")
        await query.message.reply_text(
            "😔 Произошла ошибка при поиске туров. Пожалуйста, попробуйте позже."
        )
        
        # Provide option to start over
        keyboard = [[InlineKeyboardButton("🔍 Новый поиск", callback_data="search_tours")]]
        await query.message.reply_text(
            "Хотите начать поиск заново?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return SELECTING_ACTION

async def initiate_booking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Begin the booking process by collecting user information."""
    query = update.callback_query
    user_id = query.from_user.id
    tour_id = query.data.split("_")[1]
    
    # Store the selected tour
    user_sessions[user_id]["tour_id"] = tour_id
    
    # Find the selected tour details
    selected_tour = None
    for tour in user_sessions[user_id].get("tours", []):
        if tour["id"] == tour_id:
            selected_tour = tour
            break
    
    if selected_tour:
        tour_info = format_tour_details(selected_tour)
        user_sessions[user_id]["selected_tour_info"] = tour_info
        
        await query.message.reply_text(
            f"Вы выбрали:\n\n{tour_info}\n\n"
            "Для оформления бронирования, пожалуйста, укажите ваше полное имя:",
            parse_mode='Markdown'
        )
        
        return COLLECT_NAME
    else:
        await query.message.reply_text(
            "😔 Информация о выбранном туре не найдена. Пожалуйста, начните поиск заново."
        )
        return SELECTING_ACTION

async def collect_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Collect the user's name for booking."""
    user_id = update.effective_user.id
    user_sessions[user_id]["name"] = update.message.text
    
    await update.message.reply_text(
        "Спасибо! Теперь укажите ваш номер телефона для связи:"
    )
    
    return COLLECT_PHONE

async def collect_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Collect the user's phone number for booking."""
    user_id = update.effective_user.id
    user_sessions[user_id]["phone"] = update.message.text
    
    # Summarize booking details for confirmation
    tour_info = user_sessions[user_id]["selected_tour_info"]
    name = user_sessions[user_id]["name"]
    phone = user_sessions[user_id]["phone"]
    
    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_booking")],
        [InlineKeyboardButton("❌ Отменить", callback_data="cancel_booking")]
    ]
    
    await update.message.reply_text(
        f"Пожалуйста, проверьте детали бронирования:\n\n"
        f"{tour_info}\n\n"
        f"*Имя*: {name}\n"
        f"*Телефон*: {phone}\n\n"
        f"Все верно?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    return CONFIRM_BOOKING

async def finalize_booking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Complete the booking process."""
    query = update.callback_query
    user_id = query.from_user.id
    
    # In a real implementation, this would send the booking to the API
    # For now, we'll just confirm to the user
    
    await query.message.reply_text(
        "✅ Ваша бронь успешно оформлена!\n\n"
        "Наш менеджер свяжется с вами в ближайшее время для подтверждения деталей и оплаты.\n\n"
        "Спасибо за выбор Crystal Bay Travel! 🏝️"
    )
    
    # Clean up session data
    if user_id in user_sessions:
        del user_sessions[user_id]
    
    # Provide option to start a new search
    keyboard = [[InlineKeyboardButton("🔍 Новый поиск", callback_data="search_tours")]]
    await query.message.reply_text(
        "Хотите найти еще один тур?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return SELECTING_ACTION

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle free text messages from user using NLP."""
    message_text = update.message.text
    user_id = update.effective_user.id
    
    # Process the message using OpenAI
    response = await process_message(message_text, user_sessions.get(user_id, {}))
    
    # Send the response
    await update.message.reply_text(response)
    
    # Add a keyboard with common actions
    keyboard = [
        [InlineKeyboardButton("🔍 Поиск туров", callback_data="search_tours")],
        [InlineKeyboardButton("❓ Помощь", callback_data="help")]
    ]
    
    await update.message.reply_text(
        "Чем еще я могу помочь?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return SELECTING_ACTION

def main():
    """Start the bot."""
    # Create the Application
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # Setup conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECTING_ACTION: [
                CallbackQueryHandler(callback_handler),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
            ],
            SELECTING_CITY: [CallbackQueryHandler(callback_handler)],
            SELECTING_COUNTRY: [CallbackQueryHandler(callback_handler)],
            SELECTING_DATES: [CallbackQueryHandler(callback_handler)],
            BOOKING_TOUR: [CallbackQueryHandler(callback_handler)],
            COLLECT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_name)],
            COLLECT_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_phone)],
            CONFIRM_BOOKING: [CallbackQueryHandler(callback_handler)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    application.add_handler(conv_handler)
    
    # Add standalone command handlers
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("search", select_departure_city))
    
    # Start the Bot
    logger.info("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
