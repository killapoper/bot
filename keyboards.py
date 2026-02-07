from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_type_keyboard():
    keyboard = [
        [InlineKeyboardButton("Официально", callback_data="type_official")],
        [InlineKeyboardButton("Неофициально", callback_data="type_unofficial")],
        [InlineKeyboardButton("Назад", callback_data="back")] # Should prompt "Back" to where? Usually to start or cancel.
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    """Generic back button for text input steps."""
    keyboard = [[InlineKeyboardButton("Назад", callback_data="back")]]
    return InlineKeyboardMarkup(keyboard)

def get_industry_keyboard():
    industries = [
        "Производство", "Хоз Парк", "Маркетинг Услуги",
        "Водоснабжения, Электроснабжение, Газоснабжение",
        "Представительские расходы", "Бонусы клиентам",
        "Услуги сотовой связи", "Аренда техники"
    ]
    keyboard = []
    for idx, ind in enumerate(industries):
        # Use index to avoid 64 byte limit
        keyboard.append([InlineKeyboardButton(ind, callback_data=f"ind_{idx}")])
    
    keyboard.append([InlineKeyboardButton("Назад", callback_data="back")])
    return InlineKeyboardMarkup(keyboard)

def get_date_keyboard():
    keyboard = [
        [InlineKeyboardButton("Сегодня", callback_data="date_today")],
        [InlineKeyboardButton("Вчера", callback_data="date_yesterday")],
        [InlineKeyboardButton("Конкретная дата", callback_data="date_custom")],
        [InlineKeyboardButton("Назад", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_confirm_keyboard():
    keyboard = [
        [InlineKeyboardButton("Вбить в базу", callback_data="save")],
        [InlineKeyboardButton("Назад", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_post_purchase_keyboard(is_admin=False):
    keyboard = [
        [InlineKeyboardButton("➕ Добавить еще", callback_data="restart")]
    ]
    if is_admin:
        keyboard.append([InlineKeyboardButton("🛠 Админ-панель", callback_data="admin_menu")])
    return InlineKeyboardMarkup(keyboard)

def get_summary_keyboard():
    keyboard = [
        [InlineKeyboardButton("✅ Все верно", callback_data="confirm_yes")],
        [InlineKeyboardButton("❌ Ошибка / Заново", callback_data="confirm_no")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_yes_no_keyboard():
    keyboard = [
        [InlineKeyboardButton("Да", callback_data="yes")],
        [InlineKeyboardButton("Нет", callback_data="no")]
    ]
    return InlineKeyboardMarkup(keyboard)
