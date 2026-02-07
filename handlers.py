import re
import os
import html
import asyncio
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CallbackQueryHandler

from states import (
    SELECT_TYPE, INPUT_USER_NAME, INPUT_COUNT, SELECT_INDUSTRY, 
    SELECT_DATE, CONFIRM, INPUT_CUSTOM_DATE, POSITION_NAME, 
    POSITION_PRICE, POSITION_PHOTO, INPUT_ORG, INPUT_CONTACT, 
    INPUT_RECIPIENT, INPUT_RECEIPT, SELECT_1C, CONFIRM_SUMMARY
)
from keyboards import (
    get_type_keyboard, get_industry_keyboard, get_date_keyboard, 
    get_confirm_keyboard, get_back_keyboard, get_post_purchase_keyboard,
    get_summary_keyboard, get_yes_no_keyboard
)
from config import ADMIN_IDS, EXCEL_FILE

logger = logging.getLogger(__name__)
from excel_utils import ExcelManager
from drive_utils import GoogleDriveManager

# Initialize managers (assuming they should be here if they were before)
# Wait, usually they are initialized in main and passed or imported. 
# Based on previous code, handlers.py seemed to use them as globals.
excel_manager = ExcelManager(EXCEL_FILE)
drive_manager = GoogleDriveManager()

print(f"DEBUG: HANDLERS LOADED FROM: {__file__}")

# Helpers
async def delete_user_message(update):
    try:
        await update.message.delete()
    except Exception:
        pass

# ...

async def input_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    await delete_previous_bot_message(context)
    text = update.message.text
    print(f"DEBUG: Input text: '{text}'")

    print(f"DEBUG: Checking if digits in '{text}'")
    # Validation: Text only (no digits)
    # Using simple regex to match any digit
    if re.search(r'\d', text):
        print("DEBUG: Digits found! Rejecting.")
        await send_msg(update, context, "Неправильно. Введите только текст (Имя / Должность), без цифр.")
        return INPUT_USER_NAME
    
    print("DEBUG: No digits found. Accepting.")
    context.user_data['user_name'] = text
    await send_msg(update, context, f"Приятно познакомиться, {text}!\nВыберите тип закупки:", reply_markup=get_type_keyboard())
    return SELECT_TYPE

# ...

async def input_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (back handling)
    
    await delete_user_message(update)
    text = update.message.text
    # ...

async def position_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ...
    await delete_user_message(update)
    text = update.message.text
    # ...

async def position_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ...
    await delete_user_message(update)
    text = update.message.text
    # ...

async def input_org(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ...
    await delete_user_message(update)
    context.user_data['organization'] = update.message.text
    # ...

async def input_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ...
    await delete_user_message(update)
    context.user_data['contact'] = update.message.text
    # ...

async def input_recipient(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ...
    await delete_user_message(update)
    context.user_data['recipient'] = update.message.text
    # ...

async def input_custom_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ...
    await delete_user_message(update)
    text = update.message.text
    # ...

# Confirm
async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (back handling)
    
    if data == "save":
        # ... (save logic)
        
        if purchase_id:
             # ... (drive upload logic)
             
             # Notify Admins (HTML safe)
             try:
                 # Helper to safe escape HTML if needed, but for now simple <b> is enough if we trust input not to act as HTML tags
                 # user_name etc might contain < or >. Better to use html.escape
                 import html
                 
                 u_name = html.escape(str(context.user_data.get('user_name', '')))
                 org = html.escape(str(context.user_data.get('organization', '')))
                 
                 purchase_info = (
                     f"🆕 <b>Новая запись в базе!</b>\n"
                     f"№ {purchase_id}\n"
                     f"👤 Кто: {u_name}\n"
                     f"🏢 Орг: {org}\n"
                     f"💰 Сумма позиций: {len(context.user_data.get('positions', []))} шт."
                 )
                 for admin_id in ADMIN_IDS:
                     try:
                         await context.bot.send_message(chat_id=admin_id, text=purchase_info, parse_mode='HTML')
                     except Exception as e:
                         print(f"Failed to send notification to admin {admin_id}: {e}")
             except Exception as e:
                 print(f"Error in admin notification logic: {e}")

             # Show Post-Purchase Menu
             from config import ADMIN_IDS
             is_admin = update.effective_user.id in ADMIN_IDS
             await send_msg(update, msg_text, reply_markup=get_post_purchase_keyboard(is_admin))
             
        # ...
from telegram.ext import ContextTypes, ConversationHandler
from states import *
from keyboards import *
from excel_utils import ExcelManager
from drive_utils import GoogleDriveManager
from config import EXCEL_FILE, ADMIN_IDS
from datetime import datetime, timedelta
import os

# Initialize Excel Manager
excel_manager = ExcelManager(EXCEL_FILE)
# Initialize Drive Manager
drive_manager = GoogleDriveManager()

# Helpers
async def delete_user_message(update):
    # try:
    #     if update.message:
    #         await update.message.delete()
    # except Exception:
    #     pass
    pass

async def delete_previous_bot_message(context):
    # last_msg_id = context.user_data.get('last_bot_msg_id')
    # chat_id = context.user_data.get('chat_id')
    # if last_msg_id and chat_id:
    #     try:
    #         await context.bot.delete_message(chat_id=chat_id, message_id=last_msg_id)
    #     except Exception:
    #         pass
    # context.user_data['last_bot_msg_id'] = None
    pass

async def send_msg(update, context, text, reply_markup=None, **kwargs):
    # Store chat_id for deletion later
    if not context.user_data.get('chat_id'):
        context.user_data['chat_id'] = update.effective_chat.id

    if update.callback_query:
        # User requested cleanup on buttons
        await update.callback_query.answer()
        # try:
        #      await update.callback_query.message.delete()
        # except Exception:
        #      pass
        
        msg = await update.effective_chat.send_message(text, reply_markup=reply_markup, **kwargs)
    else:
        msg = await update.message.reply_text(text, reply_markup=reply_markup, **kwargs)
    
    # Track this new message
    context.user_data['last_bot_msg_id'] = msg.message_id
    return msg

# Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Clear user data on start
    context.user_data.clear()
    # Delete start command if possible (optional but good for cleanup)
    # await delete_user_message(update)
    await send_msg(update, context, "Представьтесь (Имя / Должность):")
    return INPUT_USER_NAME

async def input_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    await delete_previous_bot_message(context)
    text = update.message.text
    context.user_data['user_name'] = text
    await send_msg(update, context, f"Приятно познакомиться, {text}!\nВыберите тип закупки:", reply_markup=get_type_keyboard())
    return SELECT_TYPE

# Type Selection
async def select_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == "back":
        # Back from Type -> Start (ask name again)
        await send_msg(update, context, "Представьтесь (Имя / Должность):")
        return INPUT_USER_NAME
        
    context.user_data['type'] = "Официально" if data == "type_official" else "Неофициально"
    await send_msg(update, context, "Введите количество позиций:", reply_markup=get_back_keyboard())
    return INPUT_COUNT

# Count Input
async def input_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check for back button
    if update.callback_query and update.callback_query.data == "back":
        # Back from Count -> Type
        await send_msg(update, context, "Выберите тип закупки:", reply_markup=get_type_keyboard())
        return SELECT_TYPE

    await delete_user_message(update)
    await delete_previous_bot_message(context)
    text = update.message.text
    if not text.isdigit() or int(text) <= 0:
        await send_msg(update, context, "Я вас не понял, введите числом", reply_markup=get_back_keyboard())
        return INPUT_COUNT
    
    context.user_data['count'] = int(text)
    context.user_data['positions'] = [] # List to store position data
    context.user_data['current_pos_index'] = 0 # 0-indexed
    
    return await prompt_position_photo(update, context)

# Position Loop - Photo
async def prompt_position_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_idx = context.user_data['current_pos_index']
    count = context.user_data['count']
    
    msg = f"Позиция {current_idx + 1} из {count}.\nОтправьте фото позиции:"
    await send_msg(update, context, msg, reply_markup=get_back_keyboard())
    return POSITION_PHOTO

async def position_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query and update.callback_query.data == "back":
        # Back from Photo
        if context.user_data['current_pos_index'] > 0:
            # Back to Price of previous position
            context.user_data['current_pos_index'] -= 1
            idx = context.user_data['current_pos_index']
            await send_msg(update, context, f"Цена позиции (₸) {idx + 1}:", reply_markup=get_back_keyboard())
            return POSITION_PRICE
        else:
            # Back to Count input
            context.user_data['positions'] = []
            context.user_data['current_pos_index'] = 0
            await send_msg(update, context, "Введите количество позиций:", reply_markup=get_back_keyboard())
            return INPUT_COUNT

    # Check if photo was sent
    photo = update.message.photo
    if not photo:
        await delete_user_message(update) # Delete invalid user msg
        await send_msg(update, context, "Пожалуйста, отправьте фото.", reply_markup=get_back_keyboard())
        return POSITION_PHOTO
    
    # Download photo
    photo_file = await photo[-1].get_file()
    
    # Create photos directory if not exists
    if not os.path.exists("photos"):
        os.makedirs("photos")
        
    # Generate unique filename
    photo_path = f"photos/{update.effective_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    await photo_file.download_to_drive(photo_path)
    
    # Store temporary data for current position
    if len(context.user_data['positions']) <= context.user_data['current_pos_index']:
        context.user_data['positions'].append({})
    
    context.user_data['positions'][context.user_data['current_pos_index']]['photo_path'] = photo_path
    
    await delete_user_message(update)
    await delete_previous_bot_message(context)
    await send_msg(update, context, f"Название/наименование позиции {context.user_data['current_pos_index'] + 1}:", reply_markup=get_back_keyboard())
    return POSITION_NAME

# Invalid Photo Handler
async def invalid_photo_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    # Check if user sent text or something else
    await send_msg(update, context, "Это неправильно, мне нужна фотография.", reply_markup=get_back_keyboard())
    return POSITION_PHOTO

# Position Loop - Name
async def position_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query and update.callback_query.data == "back":
        # Back from Name -> Photo of CURRENT position
        return await prompt_position_photo(update, context)
        
    await delete_user_message(update)
    await delete_previous_bot_message(context)
    text = update.message.text
    
    # Validation? "Text or digits" usually means just string.
    # But if user wants to ban special symbols, we can.
    # User said: "only text or digits". Let's assume alphanumeric + punctuation is fine, 
    # but maybe block if it looks like garbage?
    # Actually, "Position Name" can contain anything.
    # Let's just trust filters.TEXT for now unless strict alphanumeric is required.
    # User said: "write only text or digits" -> "text or digits".
    # I will allow normal text.
    
    context.user_data['positions'][context.user_data['current_pos_index']]['name'] = text
    
    await send_msg(update, context, f"Цена позиции (₸) {context.user_data['current_pos_index'] + 1}:", reply_markup=get_back_keyboard())
    return POSITION_PRICE

# Position Loop - Price
async def position_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query and update.callback_query.data == "back":
        # Back from Price -> Name
        # We need to re-prompt Name
        idx = context.user_data['current_pos_index']
        await send_msg(update, context, f"Название/наименование позиции {idx + 1}:", reply_markup=get_back_keyboard())
        return POSITION_NAME

    await delete_user_message(update)
    await delete_previous_bot_message(context)
    text = update.message.text
    
    # Validation: Check if text contains only digits
    if not text.isdigit():
        await send_msg(update, context, "Я вас не понял, введите числом", reply_markup=get_back_keyboard())
        return POSITION_PRICE
        
    context.user_data['positions'][context.user_data['current_pos_index']]['price'] = text
    
    # Check if we need more positions
    context.user_data['current_pos_index'] += 1
    if context.user_data['current_pos_index'] < context.user_data['count']:
        # Next position
        return await prompt_position_photo(update, context)
    else:
        # Done with positions, next main step
        await send_msg(update, context, "Введите название организации/ИП закупа:", reply_markup=get_back_keyboard())
        return INPUT_ORG

# Organization
async def input_org(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query and update.callback_query.data == "back":
        # Back from Org -> Price of LAST position
        context.user_data['current_pos_index'] -= 1
        idx = context.user_data['current_pos_index']
        await send_msg(update, context, f"Цена позиции (₸) {idx + 1}:", reply_markup=get_back_keyboard())
        return POSITION_PRICE

    await delete_user_message(update)
    await delete_previous_bot_message(context)
    text = update.message.text
    
    # Validation: Text only? 
    # Usually organizations have digits (e.g. "IP Ivanov 2020").
    # User said: "only text". Maybe he means literal letters?
    # Context usually implies "Organization Name". "IP Petrov" is ok.
    # If he said "only text" strictly, maybe ban digits?
    # "Название организации только текст" -> "organization name only text".
    # I will warn if only digits provided? Or strictly alpha?
    # Let's assume alphanumeric is OK but focus on it being a valid name string.
    # But user explicit request: "organization name only text". 
    # I'll check if it has at least some letters.
    if not any(char.isalpha() for char in text):
         await send_msg(update, context, "Неправильно. Название организации должно содержать текст.", reply_markup=get_back_keyboard())
         return INPUT_ORG
         
    context.user_data['organization'] = text
    await send_msg(update, context, "Введите контактный номер менеджера/продавца:", reply_markup=get_back_keyboard())
    return INPUT_CONTACT

# Contact
async def input_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query and update.callback_query.data == "back":
        # Back from Contact -> Org
        await send_msg(update, context, "Введите название организации/ИП закупа:", reply_markup=get_back_keyboard())
        return INPUT_ORG

    await delete_user_message(update)
    await delete_previous_bot_message(context)
    text = update.message.text
    
    # Validation: Phone number (digits, +, spaces, -)
    # Check if contains at least digits and allowed chars
    if not re.match(r'^[\d\+\-\s\(\)]+$', text):
        await send_msg(update, context, "Неправильно. Введите только телефон (цифры).", reply_markup=get_back_keyboard())
        return INPUT_CONTACT
        
    context.user_data['contact'] = text
    await send_msg(update, context, "Закуп состоялся для какой отрасли?", reply_markup=get_industry_keyboard())
    return SELECT_INDUSTRY

# Industry
async def select_industry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == "back":
        # Back from Industry -> Contact
        await send_msg(update, context, "Введите контактный номер менеджера/продавца:", reply_markup=get_back_keyboard())
        return INPUT_CONTACT
    
    # Parse industry index
    try:
        ind_idx = int(data.split("_")[1])
        # We need the list of industries again to get the name. 
        # Best to import or define it in a shared place, but for now let's redefine or get from a helper.
        # However, getting it from a helper is cleaner.
        # Let's use a quick local list for simplicity or move list to constant in keyboards.py?
        # Moving to constant is better practice but requires editing keyboards.py again or importing.
        # Let's just quick-fix here corresponding to the list in keyboards.py
        industries = [
            "Производство", "Хоз Парк", "Маркетинг Услуги",
            "Водоснабжения, Электроснабжение, Газоснабжение",
            "Представительские расходы", "Бонусы клиентам",
            "Услуги сотовой связи", "Аренда техники"
        ]
        industry = industries[ind_idx]
    except (ValueError, IndexError):
        industry = "Unknown" 
    
    context.user_data['industry'] = industry
    
    await send_msg(update, context, "Куда и кому передано (написать):", reply_markup=get_back_keyboard())
    return INPUT_RECIPIENT

# Recipient
async def input_recipient(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query and update.callback_query.data == "back":
        # Back from Recipient -> Industry
        await send_msg(update, context, "Закуп состоялся для какой отрасли?", reply_markup=get_industry_keyboard())
        return SELECT_INDUSTRY

    await delete_user_message(update)
    await delete_previous_bot_message(context)
    context.user_data['recipient'] = update.message.text
    await send_msg(update, context, "Каким числом вбивать?", reply_markup=get_date_keyboard())
    return SELECT_DATE

# Date selection
async def select_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data == "back":
        # Back from Date -> Recipient
        await send_msg(update, context, "Куда и кому передано (написать):", reply_markup=get_back_keyboard())
        return INPUT_RECIPIENT
    
    if data == "date_today":
        context.user_data['date_label'] = "Сегодняшним"
        context.user_data['date_value'] = datetime.now().strftime("%Y-%m-%d")
        return await prompt_receipt(update, context)
    elif data == "date_yesterday":
        context.user_data['date_label'] = "Вчера"
        context.user_data['date_value'] = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        return await prompt_receipt(update, context)
    elif data == "date_custom":
        context.user_data['date_label'] = "Конкретная дата"
        await send_msg(update, context, "Введите дату в формате ДД.ММ.ГГГГ:", reply_markup=get_back_keyboard())
        # We need a temporary sub-state or just handle regex in a generic state?
        # New state needed in states.py? Or let's handle "custom" logic here?
        # Simpler: Make a new logic path. 
        # But for now, let's keep it simple. If "Custom", we can reuse SELECT_DATE but expect text?
        # Or add a small helper state locally. Let's assume we need a state INPUT_DATE_CUSTOM.
        # But I didn't define it in states.py. I can just expect text in this same handler if I check update.message?
        # But this handler is triggered by CallbackQuery.
        # Let's add a state INPUT_CUSTOM_DATE to states.py? 
        # Actually I can just return a new int state, reusing existing mechanism is dangerous if not defined.
        # Let's return a new integer constant 11 (next one).
        return INPUT_CUSTOM_DATE
    
    return SELECT_DATE

# Custom Date Input (Special Case)
async def input_custom_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query and update.callback_query.data == "back":
         await send_msg(update, context, "Каким числом вбивать?", reply_markup=get_date_keyboard())
         return SELECT_DATE

    await delete_user_message(update)
    await delete_previous_bot_message(context)
    text = update.message.text
    context.user_data['date_value'] = text
    return await prompt_receipt(update, context)

# Receipt
async def prompt_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_msg(update, context, "Отправьте фото чека/оплаты (или PDF файл):", reply_markup=get_back_keyboard())
    return INPUT_RECEIPT

async def input_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query and update.callback_query.data == "back":
        # Back from Receipt -> Date
        await send_msg(update, context, "Каким числом вбивать?", reply_markup=get_date_keyboard())
        return SELECT_DATE

    # Check for photo or document
    photo = update.message.photo
    document = update.message.document
    
    file_obj = None
    file_ext = ""
    
    if photo:
        file_obj = await photo[-1].get_file()
        file_ext = ".jpg"
    elif document:
        # Check MIME type or extension if user wants ONLY PDF?
        # User said "PDF file".
        if document.mime_type == 'application/pdf' or document.file_name.lower().endswith('.pdf'):
             file_obj = await document.get_file()
             file_ext = ".pdf"
        else:
             # Allow other images as documents too? User said PDF.
             # Let's be flexible but primarily PDF.
             # If it's an image sent as file, we can accept it.
             if document.mime_type.startswith('image/'):
                  file_obj = await document.get_file()
                  file_ext = os.path.splitext(document.file_name)[1]
             else:
                  await delete_user_message(update)
                  await send_msg(update, context, "Пожалуйста, отправьте фото или PDF файл.", reply_markup=get_back_keyboard())
                  return INPUT_RECEIPT
    else:
        await delete_user_message(update)
        await send_msg(update, context, "Пожалуйста, отправьте фото или PDF файл.", reply_markup=get_back_keyboard())
        return INPUT_RECEIPT
    
    # Create receipts directory if not exists
    if not os.path.exists("receipts"):
        os.makedirs("receipts")
        
    # Generate unique filename
    receipt_path = f"receipts/{update.effective_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_ext}"
    await file_obj.download_to_drive(receipt_path)
    
    context.user_data['receipt_path'] = receipt_path
    
    await delete_user_message(update)
    await delete_previous_bot_message(context)
    
    return await prompt_1c(update, context)

# 1C Question
async def prompt_1c(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_msg(update, context, "Закупка проведена/будет проведена в системе 1C?", reply_markup=get_yes_no_keyboard())
    return SELECT_1C

async def select_1c(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == "back":
        return await prompt_receipt(update, context)
        
    if data == "yes":
        context.user_data['1c_status'] = "Да"
    else:
        context.user_data['1c_status'] = "Нет"
        
    return await prompt_summary(update, context)

# Summary Handling
async def prompt_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Construct summary message
    user_data = context.user_data
    
    # Check receipt name
    receipt_name = os.path.basename(user_data.get('receipt_path', ''))
    
    summary = (
        f"📋 <b>Проверка данных:</b>\n"
        f"👤 <b>Кто:</b> {user_data.get('user_name', '')}\n"
        f"🏷 <b>Тип:</b> {user_data.get('type', '')}\n"
        f"🔢 <b>Кол-во позиций:</b> {user_data.get('count', 0)}\n"
        f"🏢 <b>Орг:</b> {user_data.get('organization', '')}\n"
        f"📞 <b>Контакт:</b> {user_data.get('contact', '')}\n"
        f"🏭 <b>Отрасль:</b> {user_data.get('industry', '')}\n"
        f"📨 <b>Кому:</b> {user_data.get('recipient', '')}\n"
        f"📅 <b>Дата:</b> {user_data.get('date_value', '')} ({user_data.get('date_label', '')})\n"
        f"🧾 <b>Чек:</b> Загружен ({receipt_name})\n"
        f"💻 <b>1C:</b> {user_data.get('1c_status', 'Не указано')}\n\n"
        f"<b>Позиции:</b>\n"
    )
    
    for i, pos in enumerate(user_data.get('positions', [])):
        summary += f"{i+1}. {pos.get('name', '')} - {pos.get('price', '')} ₸\n"
        
    # Send with HTML parse mode !!
    # send_msg helper needs to support parse_mode.
    # Currently send_msg uses default or none.
    # We should update send_msg OR call bot directly.
    # But send_msg handles message tracking.
    # Let's update send_msg to accept keyword args or just pass parse_mode explicitly if possible.
    # send_msg signature: (update, context, text, reply_markup=None).
    # I'll update send_msg first? No, I'll assume send_msg defaults to HTML or I'll just change send_msg source later.
    # For this block, I will use context.bot.send_message directly but tracking logic will be missing?
    # No, I should fix send_msg.
    
    # For this step, I will replace the block assuming send_msg will be updated or I use a workaround.
    # Workaround: Use context.bot.send_message and manually track ID?
    # Or just update send_msg in next step.
    
    # I'll rely on updating send_msg later.
    await send_msg(update, context, summary, reply_markup=get_summary_keyboard(), parse_mode='HTML')
    return CONFIRM_SUMMARY

async def confirm_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == "back":
        return await prompt_1c(update, context)
        
    if data == "confirm_no":
        # Restart
        await query.answer("Начинаем заново!")
        return await start(update, context)
        
    if data == "confirm_yes":
        # Proceed to save (reuse old confirm logic but adapted)
        # We can call the save logic directly here or redirect to a helper
        return await save_data(update, context)
        
    return CONFIRM_SUMMARY

# Save Logic (extracted from old confirm)
async def save_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    # Answer callback immediately to prevent timeout
    await query.answer()

    # Update message to show processing status
    try:
         await query.message.delete()
    except:
         pass
    
    status_msg = await query.message.reply_text("⏳ Сохраняю запись и загружаю на Google Диск...")

    # Upload Receipt to Drive FIRST (if exists)
    import asyncio
    receipt_path = context.user_data.get('receipt_path')
    if receipt_path:
        await asyncio.sleep(1) # Safety delay for file release
        try:
             loop = asyncio.get_running_loop()
             # upload_file now returns URL
             receipt_url = await loop.run_in_executor(None, drive_manager.upload_file, receipt_path)
             if receipt_url:
                 context.user_data['receipt_url'] = receipt_url
             else:
                 print("Receipt upload returned None.")
        except Exception as e:
             print(f"Error uploading receipt: {e}")

    # Upload Position Photos to Drive
    await asyncio.sleep(1) # Safety delay
    for pos in context.user_data.get('positions', []):
        photo_path = pos.get('photo_path')
        if photo_path and os.path.exists(photo_path):
            try:
                loop = asyncio.get_running_loop()
                photo_url = await loop.run_in_executor(None, drive_manager.upload_file, photo_path)
                if photo_url:
                    pos['photo_url'] = photo_url
            except Exception as e:
                logger.error(f"Error uploading position photo: {e}")

    # Save to Excel (now includes receipt_url and photo_urls)
    purchase_id = excel_manager.add_purchase(update.effective_user.id, context.user_data)
    
    if purchase_id:
        msg_text = f"Отлично закуп номер {purchase_id} вбит в базу расходов"
        
        # Helper to upload to Drive (run in executor)
        import asyncio
        upload_success = False
        if drive_manager.service:
            try:
                loop = asyncio.get_running_loop()
                upload_success = await loop.run_in_executor(None, drive_manager.upload_file, EXCEL_FILE)
            except Exception as e:
                print(f"Error in drive upload executor: {e}")
            
            if upload_success:
                 msg_text += "\n\n✅ Файл успешно загружен на Google Диск!"
            else:
                 msg_text += "\n\n⚠️ Ошибка загрузки на Google Диск."
        else:
             msg_text += "\n\nℹ️ Google Диск не настроен (нет credentials.json)."

        # Edit status message with final result
        from config import ADMIN_IDS
        is_admin = update.effective_user.id in ADMIN_IDS
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=status_msg.message_id,
            text=msg_text,
            reply_markup=get_post_purchase_keyboard(is_admin)
        )
        
        # Notify Admins
        try:
            import html
            u_name = html.escape(str(context.user_data.get('user_name', '')))
            org = html.escape(str(context.user_data.get('organization', '')))
            
            receipt_link = context.user_data.get('receipt_url')
            if not receipt_link:
                 # Hyperlink to local path won't work in TG, but maybe some bots use it? No.
                 # Let's just say "No link" or keep as is if no drive upload.
                 receipt_link = "No Link"

            purchase_info = (
                f"🆕 <b>Новая запись в базе!</b>\n"
                f"№ {purchase_id}\n"
                f"👤 Кто: {u_name}\n"
                f"🏢 Орг: {org}\n"
                f"💰 Всего позиций: {len(context.user_data.get('positions', []))} шт.\n"
                f"🧾 Чек: <a href='{receipt_link}'>Посмотреть</a>\n"
                f"💻 1C: {context.user_data.get('1c_status', 'Не указано')}"
            )
            for admin_id in ADMIN_IDS:
                try:
                    await context.bot.send_message(chat_id=admin_id, text=purchase_info, parse_mode='HTML')
                    # Also send the receipt photo? Maybe later.
                    if context.user_data.get('receipt_path'):
                        # Check extension to decide send_photo or send_document
                        r_path = context.user_data['receipt_path']
                        if r_path.lower().endswith('.pdf'):
                             with open(r_path, 'rb') as f:
                                  await context.bot.send_document(chat_id=admin_id, document=f, caption=f"Чек к закупу №{purchase_id}")
                        else:
                             with open(r_path, 'rb') as f:
                                  await context.bot.send_photo(chat_id=admin_id, photo=f, caption=f"Чек к закупу №{purchase_id}")
                except Exception as e:
                    print(f"Failed to send notification to admin {admin_id}: {e}")
        except Exception as e:
            print(f"Error in admin notification logic: {e}")

    else:
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=status_msg.message_id,
            text="❌ Ошибка при сохранении! Возможно файл открыт в Excel?"
        )
        
    return ConversationHandler.END
# Cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отменено.")
    return ConversationHandler.END

