import os
import logging
import requests
import openai
from dotenv import load_dotenv
from datetime import datetime, timedelta
# Import directly from telegram module
import telegram
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext

# Alias the necessary classes
InlineKeyboardButton = telegram.InlineKeyboardButton
InlineKeyboardMarkup = telegram.InlineKeyboardMarkup
Update = telegram.Update

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# API configuration
API_URL = "https://booking.crystalbay.com/export/default.php"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SAMO_TOKEN = os.getenv("SAMO_OAUTH_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

# User sessions storage
user_sessions = {}

def start(update: Update, context: CallbackContext):
    """Start command handler - displays welcome message and initial options"""
    keyboard = [[InlineKeyboardButton("🔍 Поиск туров", callback_data="search_tours")]]
    # Use send_message for version 13
    context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="Добро пожаловать в Crystal Bay Travel! 🏖️", 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def callback_handler(update: Update, context: CallbackContext):
    """Handle callback queries from inline keyboards"""
    query = update.callback_query
    query.answer()  # Answer the callback query to stop the loading animation
    
    data = query.data
    user_id = query.from_user.id
    
    # Initialize user session if not exists
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    
    # Handle different callback actions
    if data == "search_tours":
        select_departure_city(query)
    elif data.startswith("city_"):
        city_id = data.split("_")[1]
        user_sessions[user_id]["departure_city"] = city_id
        select_country(query, city_id)
    elif data.startswith("country_"):
        country_id = data.split("_")[1]
        user_sessions[user_id]["country"] = country_id
        select_dates(query, user_sessions[user_id])
    elif data.startswith("date_"):
        date_selected = data.split("_")[1]
        user_sessions[user_id]["checkin"] = date_selected
        search_tours(query, user_sessions[user_id])
    elif data.startswith("book_"):
        tour_id = data.split("_")[1]
        user_sessions[user_id]["tour_id"] = tour_id
        initiate_booking(query, tour_id)

def select_departure_city(query):
    """Show available departure cities"""
    try:
        response = requests.get(
            f"{API_URL}?samo_action=api&oauth_token={SAMO_TOKEN}&type=json&action=SearchTour_TOWNFROMS")
        response.raise_for_status()
        
        cities = response.json().get("SearchTour_TOWNFROMS", [])
        
        if not cities:
            query.message.reply_text("😔 Не удалось получить список городов. Пожалуйста, попробуйте позже.")
            return
        
        # Create a keyboard with city buttons (2 per row)
        keyboard = []
        row = []
        
        for i, city in enumerate(cities):
            row.append(InlineKeyboardButton(city["nameAlt"], callback_data=f"city_{city['id']}"))
            
            if (i + 1) % 2 == 0 or i == len(cities) - 1:
                keyboard.append(row)
                row = []
        
        query.message.reply_text("Выберите город вылета:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    except requests.RequestException as e:
        logger.error(f"API error: {e}")
        query.message.reply_text("😔 Произошла ошибка при получении списка городов. Пожалуйста, попробуйте позже.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        query.message.reply_text("😔 Произошла неизвестная ошибка. Пожалуйста, попробуйте позже.")

def select_country(query, city_id):
    """Show available countries based on selected departure city"""
    try:
        response = requests.post(
            f"{API_URL}?samo_action=api&oauth_token={SAMO_TOKEN}&type=json&action=SearchTour_STATES",
            headers={'Content-Type': 'application/xml'},
            data=f'<data><TOWNFROMINC>{city_id}</TOWNFROMINC></data>'
        )
        response.raise_for_status()
        
        countries = response.json().get("SearchTour_STATES", [])
        
        if not countries:
            query.message.reply_text("😔 Не удалось получить список стран. Пожалуйста, попробуйте позже.")
            return
        
        # Create a keyboard with country buttons (2 per row)
        keyboard = []
        row = []
        
        for i, country in enumerate(countries):
            row.append(InlineKeyboardButton(country["nameAlt"], callback_data=f"country_{country['id']}"))
            
            if (i + 1) % 2 == 0 or i == len(countries) - 1:
                keyboard.append(row)
                row = []
        
        query.message.reply_text("Выберите страну назначения:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    except requests.RequestException as e:
        logger.error(f"API error: {e}")
        query.message.reply_text("😔 Произошла ошибка при получении списка стран. Пожалуйста, попробуйте позже.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        query.message.reply_text("😔 Произошла неизвестная ошибка. Пожалуйста, попробуйте позже.")

def select_dates(query, session):
    """Show available travel dates"""
    # Generate dates for the next 30 days
    dates = [(datetime.now() + timedelta(days=i)) for i in range(1, 31)]
    
    # Create a keyboard with dates (3 per row)
    keyboard = []
    row = []
    
    for i, date in enumerate(dates[:21]):  # Limit to 21 days for cleaner interface
        formatted_date = date.strftime("%d.%m")
        raw_date = date.strftime("%Y%m%d")
        row.append(InlineKeyboardButton(formatted_date, callback_data=f"date_{raw_date}"))
        
        if (i + 1) % 3 == 0 or i == len(dates[:21]) - 1:
            keyboard.append(row)
            row = []
    
    query.message.reply_text(
        "Выберите дату заезда:\n(Даты показаны в формате ДД.ММ)",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def search_tours(query, session):
    """Search for tours based on user selections"""
    query.message.reply_text("🔎 Ищем туры, пожалуйста подождите...")
    
    try:
        params = {
            "samo_action": "api",
            "oauth_token": SAMO_TOKEN,
            "type": "json",
            "action": "SearchTour_TOURS",
            "townfrom": session["departure_city"],
            "stateinc": session["country"],
            "checkin": session["checkin"],
            "checkout": session["checkin"],  # Same as checkin for API requirements
            "nights_min": 3,
            "nights_max": 14,
            "adults": 2,
            "currency": "RUB"
        }
        
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        
        tours = response.json().get("SearchTour_TOURS", [])
        
        if not tours:
            query.message.reply_text(
                "😞 Туры по вашим параметрам не найдены.\n"
                "Попробуйте изменить даты или направление."
            )
            
            # Provide option to restart search
            keyboard = [[InlineKeyboardButton("🔍 Новый поиск", callback_data="search_tours")]]
            query.message.reply_text(
                "Хотите начать поиск заново?",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return
        
        # Store found tours in user session
        user_id = query.from_user.id
        user_sessions[user_id]["tours"] = tours
        
        query.message.reply_text(f"🏝️ Найдено {len(tours)} туров:")
        
        # Display tours (limit to 5 to avoid message length limits)
        for tour in tours[:5]:
            tour_info = format_tour_details(tour)
            
            keyboard = [[InlineKeyboardButton("📅 Забронировать", callback_data=f"book_{tour['id']}")]]
            query.message.reply_text(tour_info, reply_markup=InlineKeyboardMarkup(keyboard))
        
        # Add option for new search
        keyboard = [[InlineKeyboardButton("🔍 Новый поиск", callback_data="search_tours")]]
        query.message.reply_text(
            "Хотите начать поиск заново?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    except requests.RequestException as e:
        logger.error(f"API error: {e}")
        query.message.reply_text("😔 Произошла ошибка при поиске туров. Пожалуйста, попробуйте позже.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        query.message.reply_text("😔 Произошла неизвестная ошибка. Пожалуйста, попробуйте позже.")

def initiate_booking(query, tour_id):
    """Begin the booking process for a selected tour"""
    user_id = query.from_user.id
    
    # Find the selected tour details
    selected_tour = None
    for tour in user_sessions[user_id].get("tours", []):
        if tour["id"] == tour_id:
            selected_tour = tour
            break
    
    if not selected_tour:
        query.message.reply_text("😔 Информация о выбранном туре не найдена. Пожалуйста, начните поиск заново.")
        return
    
    # Format tour details
    tour_info = format_tour_details(selected_tour)
    user_sessions[user_id]["selected_tour_info"] = tour_info
    
    # Ask for user's name
    query.message.reply_text(
        f"Вы выбрали:\n\n{tour_info}\n\n"
        "Для оформления бронирования, пожалуйста, укажите ваше полное имя:",
        parse_mode='Markdown'
    )
    
    # Set next expected input
    user_sessions[user_id]["booking_stage"] = "name"

def process_booking_input(update: Update, context: CallbackContext):
    """Process booking information from user"""
    user_id = update.effective_user.id
    message_text = update.message.text
    
    if user_id not in user_sessions:
        update.message.reply_text("Сессия истекла. Пожалуйста, начните поиск заново с команды /start")
        return
    
    booking_stage = user_sessions[user_id].get("booking_stage")
    
    if booking_stage == "name":
        # Save name and request phone number
        user_sessions[user_id]["name"] = message_text
        user_sessions[user_id]["booking_stage"] = "phone"
        
        update.message.reply_text("Спасибо! Теперь укажите ваш номер телефона для связи:")
    
    elif booking_stage == "phone":
        # Save phone and show confirmation
        user_sessions[user_id]["phone"] = message_text
        
        # Get saved data
        tour_info = user_sessions[user_id]["selected_tour_info"]
        name = user_sessions[user_id]["name"]
        phone = user_sessions[user_id]["phone"]
        
        # Show confirmation buttons
        keyboard = [
            [InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_booking")],
            [InlineKeyboardButton("❌ Отменить", callback_data="cancel_booking")]
        ]
        
        update.message.reply_text(
            f"Пожалуйста, проверьте детали бронирования:\n\n"
            f"{tour_info}\n\n"
            f"*Имя*: {name}\n"
            f"*Телефон*: {phone}\n\n"
            f"Все верно?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
        user_sessions[user_id]["booking_stage"] = "confirmation"
    
    else:
        # Handle unexpected messages
        update.message.reply_text(
            "Не могу распознать ваш запрос. Пожалуйста, используйте кнопки или начните заново с команды /start"
        )

def finalize_booking(query):
    """Complete the booking process"""
    user_id = query.from_user.id
    
    if user_id not in user_sessions:
        query.message.reply_text("Сессия истекла. Пожалуйста, начните поиск заново с команды /start")
        return
    
    # In a real implementation, here we would send the booking to the API
    # or save it to a database for the travel agency staff
    
    query.message.reply_text(
        "✅ Ваша бронь успешно оформлена!\n\n"
        "Наш менеджер свяжется с вами в ближайшее время для подтверждения деталей и оплаты.\n\n"
        "Спасибо за выбор Crystal Bay Travel! 🏝️"
    )
    
    # Clean up session data
    del user_sessions[user_id]
    
    # Provide option to start a new search
    keyboard = [[InlineKeyboardButton("🔍 Новый поиск", callback_data="search_tours")]]
    query.message.reply_text(
        "Хотите найти еще один тур?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def format_tour_details(tour):
    """Format tour details for display in Telegram message"""
    # Default values for missing fields
    hotel_name = tour.get("nameAlt", "Отель не указан")
    tour_type = tour.get("typeAlt", "Тип не указан")
    partner = tour.get("partnerAlt", "Партнер не указан")
    nights = tour.get("nights", "?")
    meal_type = tour.get("mealAlt", "Питание не указано")
    room_type = tour.get("roomAlt", "Тип номера не указан")
    
    # Price handling - use price if available, otherwise use priceInCurrency
    price = None
    if "price" in tour and tour["price"]:
        price = f"{tour['price']} {tour.get('currency', 'RUB')}"
    elif "priceInCurrency" in tour and tour["priceInCurrency"]:
        price = f"{tour['priceInCurrency']} {tour.get('currencyInCurrency', 'RUB')}"
    else:
        price = "Цена по запросу"
    
    # Format dates
    checkin_date = tour.get("checkin", "Дата не указана")
    if checkin_date and len(checkin_date) == 8:  # Format: YYYYMMDD
        checkin_date = f"{checkin_date[6:8]}.{checkin_date[4:6]}.{checkin_date[0:4]}"
    
    # Compose message
    tour_info = (
        f"*{hotel_name}*\n"
        f"🗓 *Дата заезда:* {checkin_date}\n"
        f"🌙 *Ночей:* {nights}\n"
        f"🍽 *Питание:* {meal_type}\n"
        f"🛏 *Размещение:* {room_type}\n"
        f"🔄 *Тип тура:* {tour_type}\n"
        f"🤝 *Туроператор:* {partner}\n"
        f"💰 *Цена:* {price}"
    )
    
    return tour_info

def help_command(update: Update, context: CallbackContext):
    """Send help information"""
    help_text = (
        "🌴 *Crystal Bay Travel Bot* 🌴\n\n"
        "*Доступные команды:*\n"
        "/start - Начать общение с ботом\n"
        "/help - Показать это сообщение\n"
        "/cancel - Отменить текущее действие\n\n"
        "*Как использовать:*\n"
        "1. Выберите город вылета\n"
        "2. Выберите страну назначения\n"
        "3. Выберите даты поездки\n"
        "4. Просмотрите доступные туры\n"
        "5. Забронируйте понравившийся тур\n\n"
        "Вы также можете задать мне вопрос о турах или услугах Crystal Bay Travel, и я постараюсь помочь!"
    )
    
    update.message.reply_text(help_text, parse_mode='Markdown')

def cancel_command(update: Update, context: CallbackContext):
    """Cancel current operation and clean up user session"""
    user_id = update.effective_user.id
    
    if user_id in user_sessions:
        del user_sessions[user_id]
    
    update.message.reply_text(
        "Действие отменено. Для начала нового поиска отправьте команду /start"
    )

def handle_text_message(update: Update, context: CallbackContext):
    """Handle text messages that could be part of booking process or general queries"""
    user_id = update.effective_user.id
    
    # Check if user is in booking process
    if user_id in user_sessions and "booking_stage" in user_sessions[user_id]:
        # Process as part of booking
        process_booking_input(update, context)
    else:
        # Use OpenAI to handle general queries
        prompt = f"Пользователь спрашивает о путешествиях: {update.message.text}\nДай краткий ответ на русском языке как турагент Crystal Bay Travel."
        
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Ты — помощник туристического агентства Crystal Bay Travel. Отвечай кратко, по-русски, в дружелюбной манере."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300
            )
            
            ai_response = response.choices[0].message.content
            
            update.message.reply_text(ai_response)
            
            # Suggest search option
            keyboard = [[InlineKeyboardButton("🔍 Поиск туров", callback_data="search_tours")]]
            update.message.reply_text(
                "Хотите подобрать тур?",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            update.message.reply_text(
                "Извините, не могу обработать ваш запрос сейчас. Пожалуйста, попробуйте воспользоваться поиском туров."
            )
            
            # Suggest search option
            keyboard = [[InlineKeyboardButton("🔍 Поиск туров", callback_data="search_tours")]]
            update.message.reply_text(
                "Хотите подобрать тур?",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

def main():
    """Start the bot"""
    # Check if token is available
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set!")
        return
    
    # Create updater
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    # Add handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("cancel", cancel_command))
    dispatcher.add_handler(CallbackQueryHandler(callback_handler))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text_message))
    
    # Start the Bot
    logger.info("Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()