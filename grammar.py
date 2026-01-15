# grammar.py
import os
from pathlib import Path
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes

# Grammar files directory on server
GRAMMAR_DIR = "/home/ubuntu/bot/grammar"

# Cache for grammar files to avoid reading directory multiple times
_grammar_files_cache = None


def get_grammar_files() -> list[str]:
    """Get list of .docx files from grammar directory."""
    global _grammar_files_cache
    
    # Return cached files if available
    if _grammar_files_cache is not None:
        return _grammar_files_cache
    
    if not os.path.exists(GRAMMAR_DIR):
        _grammar_files_cache = []
        return []
    
    files = []
    try:
        for filename in sorted(os.listdir(GRAMMAR_DIR)):
            if filename.lower().endswith('.docx'):
                files.append(filename)
    except Exception as e:
        print(f"Error reading grammar directory: {e}")
    
    _grammar_files_cache = files
    return files


def build_grammar_files_keyboard(start_index: int = 0, total_files: int = 0) -> InlineKeyboardMarkup:
    """Build inline keyboard with number buttons and pagination."""
    buttons = []
    
    # Add number buttons (1-10) - 5 per row
    number_buttons = []
    for i in range(10):
        button_num = i + 1  # 1,2,3,4,5,6,7,8,9,10
        callback_num = start_index + i
        button = InlineKeyboardButton(
            str(button_num),
            callback_data=f"grammar_file:{callback_num}"
        )
        number_buttons.append(button)
    
    # Add number buttons in 2 rows (5 buttons each)
    buttons.append(number_buttons[0:5])
    buttons.append(number_buttons[5:10])
    
    # Add pagination buttons (Next/Previous)
    pagination_row = []
    
    if start_index > 0:
        pagination_row.append(InlineKeyboardButton(
            "⬅️ Previous",
            callback_data=f"grammar_page:{max(0, start_index - 10)}"
        ))
    
    if start_index + 10 < total_files:
        pagination_row.append(InlineKeyboardButton(
            "Next ➡️",
            callback_data=f"grammar_page:{start_index + 10}"
        ))
    
    if pagination_row:
        buttons.append(pagination_row)
    
    return InlineKeyboardMarkup(buttons)


async def show_grammar_files(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0):
    """Show list of grammar rule files with numbered buttons for pagination."""
    files = get_grammar_files()
    
    if not files:
        await update.message.reply_text(
            "📚 No grammar files found.\n\n"
            "Please add .docx files to /home/ubuntu/bot/grammar/ directory.",
            reply_markup=InlineKeyboardMarkup([])
        )
        return
    
    # Get language for proper message
    import word
    uid = word.get_or_create_user(update.effective_user.id, update.effective_user.username)
    L = word.LANGS.get(word.get_ui_lang(uid), word.LANGS["UZ"])
    
    # Calculate pagination
    items_per_page = 10
    start_index = page * items_per_page
    end_index = min(start_index + items_per_page, len(files))
    
    # Build text list
    text_list = L.get("grammar_files_list", "📚 Grammar Rules:\n\nSelect a file:\n")
    text_list += "\n"
    
    for i in range(start_index, end_index):
        display_name = files[i].replace('.docx', '').replace('.DOCX', '')
        position = (i - start_index + 1)  # 1-10
        text_list += f"{position}. {display_name}\n"
    
    # Add page info
    total_pages = (len(files) + items_per_page - 1) // items_per_page
    current_page = page + 1
    text_list += f"\n📄 Page {current_page} of {total_pages} (showing {end_index - start_index} of {len(files)} files)"
    
    kb = build_grammar_files_keyboard(start_index, len(files))
    
    await update.message.reply_text(text_list, reply_markup=kb)


async def handle_grammar_file_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle grammar file selection callback."""
    query = update.callback_query
    await query.answer()
    
    data = query.data.split(":")
    if len(data) < 2:
        await query.edit_message_text("❌ Error: Invalid file selection.")
        return
    
    try:
        file_index = int(data[1])
    except (ValueError, IndexError):
        await query.edit_message_text("❌ Error: Invalid file selection.")
        return
    
    files = get_grammar_files()
    
    if file_index < 0 or file_index >= len(files):
        await query.edit_message_text("❌ Error: File not found.")
        return
    
    filename = files[file_index]
    file_path = os.path.join(GRAMMAR_DIR, filename)
    
    if not os.path.exists(file_path):
        await query.edit_message_text("❌ Error: File not found on server.")
        return
    
    try:
        # Send the document
        with open(file_path, 'rb') as f:
            await context.bot.send_document(
                chat_id=query.from_user.id,
                document=f,
                caption=f"📄 {filename.replace('.docx', '')}",
                parse_mode="HTML"
            )
        await query.answer("✅ File sent!")
    except Exception as e:
        print(f"Error sending grammar file: {e}")
        await query.answer(f"❌ Error: {str(e)}", show_alert=True)


async def handle_grammar_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle grammar pagination (Next/Previous)."""
    query = update.callback_query
    await query.answer()
    
    data = query.data.split(":")
    if len(data) < 2:
        await query.edit_message_text("❌ Error: Invalid page.")
        return
    
    try:
        start_index = int(data[1])
    except (ValueError, IndexError):
        await query.edit_message_text("❌ Error: Invalid page.")
        return
    
    # Calculate page number
    page = start_index // 10
    
    files = get_grammar_files()
    
    # Rebuild the message with new page
    items_per_page = 10
    end_index = min(start_index + items_per_page, len(files))
    
    # Get language for proper message
    import word
    uid = word.get_or_create_user(query.from_user.id, query.from_user.username)
    L = word.LANGS.get(word.get_ui_lang(uid), word.LANGS["UZ"])
    
    # Build text list
    text_list = L.get("grammar_files_list", "📚 Grammar Rules:\n\nSelect a file:\n")
    text_list += "\n"
    
    for i in range(start_index, end_index):
        display_name = files[i].replace('.docx', '').replace('.DOCX', '')
        position = (i - start_index + 1)  # 1-10
        text_list += f"{position}. {display_name}\n"
    
    # Add page info
    total_pages = (len(files) + items_per_page - 1) // items_per_page
    current_page = page + 1
    text_list += f"\n📄 Page {current_page} of {total_pages} (showing {end_index - start_index} of {len(files)} files)"
    
    kb = build_grammar_files_keyboard(start_index, len(files))
    
    await query.edit_message_text(text_list, reply_markup=kb)
