from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from config import ADMIN_IDS, EXCEL_FILE
from drive_utils import GoogleDriveManager
import os

# Initialize Drive Manager (or import existing instance if strictly singleton, 
# but creating new instance is fine as it just loads tokens)
# Better to reuse if possible, but for simplicity:
drive_manager = GoogleDriveManager()

async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        if update.message:
            await update.message.reply_text("Вам не доступна админ панель")
        return

    keyboard = [
        [InlineKeyboardButton("➕ Добавить позицию", callback_data="restart")],
        [
            InlineKeyboardButton("Скачать Excel", callback_data="admin_download"),
            InlineKeyboardButton("Загрузить на Диск", callback_data="admin_upload_drive")
        ],
        [InlineKeyboardButton("🔔 Уведомления о записях", callback_data="admin_notifications")],
        [InlineKeyboardButton("🗑️ Очистить таблицу", callback_data="admin_clear_confirm")]
    ]
    # Update message text if it's the start command
    if update.message:
        await update.message.reply_text("Админ-панель:", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        # If returning from a callback (e.g. "No" in confirmation)
        await update.callback_query.edit_message_text("Админ-панель:", reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await query.answer("Нет прав", show_alert=True)
        return

    # Don't acknowledge immediately for all scenarios as some might need specific handling
    # await query.answer() 
    
    if query.data == "admin_download":
        await query.answer()
        if os.path.exists(EXCEL_FILE):
            with open(EXCEL_FILE, 'rb') as f:
                await query.message.reply_document(document=f, filename=EXCEL_FILE)
        else:
            await query.message.reply_text("Файл базы данных не найден.")

    elif query.data == "admin_notifications":
        # Show recent purchases
        from handlers import excel_manager
        
        purchases = excel_manager.get_last_purchases(limit=5)
        
        if not purchases:
             await query.answer("Записей пока нет.", show_alert=True)
             return
             
        await query.answer()
        
        # Build message
        msg_text = "🔔 **Последние записи:**\n\n"
        for p in purchases:
             msg_text += (
                 f"🆔 {p['id']} ({p['created_at']})\n"
                 f"👤 {p['user']}\n"
                 f"🏢 {p['org']}\n"
                 f"📦 {p['position']} - {p['price']}\n"
                 f"➖➖➖➖➖➖➖➖➖➖\n"
             )
        
        # Add back button
        back_kb = InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data="admin_menu")]])
        
        # Send new message or edit? 
        # Editing might be too long if many records. New message is safer for logs.
        # But user wants "log viewer". Let's try edit first, if too long telegram will error.
        # 5 records * 5 lines ~ 25 lines. Should fit.
        
        try:
            await query.edit_message_text(msg_text, reply_markup=back_kb, parse_mode='Markdown')
        except Exception as e:
            # If edit fails (e.g. too long), send new
            await query.message.reply_text(msg_text, reply_markup=back_kb, parse_mode='Markdown')


    elif query.data == "admin_upload_drive":
        # Delete the menu message to clean up
        # await query.message.delete()
        msg = await query.message.reply_text("Начинаю загрузку на Диск...")
        
        if drive_manager.upload_file(EXCEL_FILE):
            await context.bot.edit_message_text(chat_id=user_id, message_id=msg.message_id, text="✅ Успешно загружено.")
        else:
            back_kb = InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data="admin_menu")]])
            await context.bot.edit_message_text(chat_id=user_id, message_id=msg.message_id, text="❌ Ошибка загрузки.", reply_markup=back_kb)
            
    elif query.data == "admin_clear_confirm":
        await query.answer()
        # Show confirmation dialog
        keyboard = [
            [InlineKeyboardButton("✅ ДА, УДАЛИТЬ ВСЁ", callback_data="admin_clear_yes")],
            [InlineKeyboardButton("❌ НЕТ, ОТМЕНА", callback_data="admin_clear_no")]
        ]
        await query.edit_message_text(
            "⚠️ **ВЫ УВЕРЕНЫ?**\n\nЭто удалит все записи из Excel файла. Это действие необратимо.", 
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

    elif query.data == "admin_clear_no":
        await query.answer("Отменено")
        # Go back to main menu - REUSE admin_start logic or just copy keyboard? 
        # Better copy for simplicity here or call admin_start? 
        # Calling admin_start(update, context) works if it handles callback editing. It does.
        # But allow simpler logic:
        keyboard = [
            [InlineKeyboardButton("➕ Добавить позицию", callback_data="restart")],
            [
                InlineKeyboardButton("Скачать Excel", callback_data="admin_download"),
                InlineKeyboardButton("Загрузить на Диск", callback_data="admin_upload_drive")
            ],
            [InlineKeyboardButton("🔔 Уведомления о записях", callback_data="admin_notifications")],
            [InlineKeyboardButton("🗑️ Очистить таблицу", callback_data="admin_clear_confirm")]
        ]
        await query.edit_message_text("Админ-панель:", reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif query.data == "admin_clear_yes":
        await query.answer()
        from handlers import excel_manager 
        
        # Delete confirmation message
        # await query.message.delete()
        
        status_msg = await query.message.reply_text("⏳ Очищаю таблицу...")
        
        if excel_manager.clear_data():
            # Clear Drive folder as well
            drive_manager.clear_folder_contents()
            
            await context.bot.edit_message_text(chat_id=user_id, message_id=status_msg.message_id, text="🗑️ Таблица и файлы на Диске очищены. Обновляю Excel-файл...")
            
            if drive_manager.upload_file(EXCEL_FILE):
                ok_kb = InlineKeyboardMarkup([[InlineKeyboardButton("Ок", callback_data="admin_menu")]])
                await context.bot.edit_message_text(chat_id=user_id, message_id=status_msg.message_id, text="✅ Таблица очищена и синхронизирована с Диском.", reply_markup=ok_kb)
            else:
                back_kb = InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data="admin_menu")]])
                await context.bot.edit_message_text(chat_id=user_id, message_id=status_msg.message_id, text="⚠️ Таблица очищена локально, но ошибка обновления Диска.", reply_markup=back_kb)
        else:
            back_kb = InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data="admin_menu")]])
            await context.bot.edit_message_text(chat_id=user_id, message_id=status_msg.message_id, text="❌ Ошибка при очистке файла. Возможно файл занят.", reply_markup=back_kb)
