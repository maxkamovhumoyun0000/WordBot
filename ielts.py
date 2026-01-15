# ielts.py
import os
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes

# IELTS directory on server
IELTS_DIR = "/home/ubuntu/bot/IELTS"

# Cache for Cambridge book numbers
_cambridge_books_cache = None


def get_cambridge_books() -> list[str]:
    """Get list of Cambridge book numbers (directories 1-20)."""
    global _cambridge_books_cache
    
    if _cambridge_books_cache is not None:
        return _cambridge_books_cache
    
    if not os.path.exists(IELTS_DIR):
        _cambridge_books_cache = []
        return []
    
    books = []
    try:
        # Collect directories whose names are digits, then sort numerically
        items = [item for item in os.listdir(IELTS_DIR)
                 if os.path.isdir(os.path.join(IELTS_DIR, item)) and item.isdigit()]
        books = sorted(items, key=lambda x: int(x))
    except Exception as e:
        print(f"Error reading IELTS directory: {e}")
    
    _cambridge_books_cache = books
    return books


async def show_cambridge_books(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show Cambridge book numbers with inline number buttons."""
    books = get_cambridge_books()
    
    if not books:
        await update.message.reply_text(
            "📚 No Cambridge books found.\n\n"
            "Please add book directories to the IELTS folder.",
            reply_markup=InlineKeyboardMarkup([])
        )
        return
    
    # Get language
    import word
    uid = word.get_or_create_user(update.effective_user.id, update.effective_user.username)
    L = word.LANGS.get(word.get_ui_lang(uid), word.LANGS["UZ"])
    
    # Build buttons - 5 per row
    buttons = []
    for i in range(0, len(books), 5):
        row = []
        for j in range(i, min(i + 5, len(books))):
            book_num = books[j]
            row.append(InlineKeyboardButton(
                f"📖 {book_num}",
                callback_data=f"ielts_book:{book_num}"
            ))
        buttons.append(row)
    
    # Add computer-based test link
    buttons.append([InlineKeyboardButton(
        "💻 Computer Based Test",
        url="https://engnovate.com/ielts-tests/"
    )])
    
    text = "📚 Cambridge IELTS Books:\n\nSelect a book number:"
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))


async def handle_cambridge_book_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Cambridge book selection and show test options."""
    query = update.callback_query
    await query.answer()
    
    data = query.data.split(":")
    if len(data) < 2:
        await query.edit_message_text("❌ Error: Invalid book selection.")
        return
    
    book_num = data[1]
    book_path = os.path.join(IELTS_DIR, book_num)
    
    if not os.path.isdir(book_path):
        await query.edit_message_text("❌ Error: Book not found.")
        return
    
    # Store selected book in context
    context.user_data["selected_ielts_book"] = book_num
    
    # Build buttons for tests and book PDF
    buttons = []
    
    # Add button for book/main file
    book_file = os.path.join(book_path, f"{book_num}.pdf")
    if os.path.exists(book_file):
        buttons.append([InlineKeyboardButton(
            "📄 Book",
            callback_data=f"ielts_send:book:{book_num}"
        )])
    
    # Add buttons for tests 1-4
    for test_num in range(1, 5):
        test_dir = os.path.join(book_path, f"test {test_num}")
        if os.path.isdir(test_dir):
            buttons.append([InlineKeyboardButton(
                f"🎧 Test {test_num}",
                callback_data=f"ielts_send:test:{book_num}:{test_num}"
            )])
    
    # Add back button
    buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="ielts_back")])
    
    await query.edit_message_text(
        f"📖 Cambridge Book {book_num}\n\nSelect Book or Test:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def handle_ielts_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle sending IELTS files (book PDF or test audio)."""
    query = update.callback_query
    await query.answer()
    
    data = query.data.split(":")
    if len(data) < 3:
        await query.edit_message_text("❌ Error: Invalid request.")
        return
    
    action = data[1]  # "book" or "test"
    book_num = data[2]
    
    if action == "book":
        # Send book PDF
        book_file = os.path.join(IELTS_DIR, book_num, f"{book_num}.pdf")
        
        if not os.path.exists(book_file):
            await query.answer("❌ Book file not found.", show_alert=True)
            return
        
        try:
            with open(book_file, 'rb') as f:
                await context.bot.send_document(
                    chat_id=query.from_user.id,
                    document=f,
                    caption=f"📄 Cambridge Book {book_num}",
                    parse_mode="HTML"
                )
            await query.answer("✅ Book sent!")
        except Exception as e:
            print(f"Error sending IELTS book: {e}")
            await query.answer(f"❌ Error: {str(e)}", show_alert=True)
    
    elif action == "test":
        # Send test audio files
        if len(data) < 4:
            await query.answer("❌ Error: Invalid test number.", show_alert=True)
            return
        
        test_num = data[3]
        test_dir = os.path.join(IELTS_DIR, book_num, f"test {test_num}")
        
        if not os.path.isdir(test_dir):
            await query.answer("❌ Test not found.", show_alert=True)
            return
        
        try:
            # Get all audio files (sorted)
            audio_files = []
            for filename in sorted(os.listdir(test_dir)):
                if filename.lower().endswith(('.mp3', '.wav', '.m4a')):
                    audio_files.append(filename)
            
            if not audio_files:
                await query.answer("❌ No audio files found.", show_alert=True)
                return
            
            # Send each audio file
            for audio_file in audio_files:
                file_path = os.path.join(test_dir, audio_file)
                with open(file_path, 'rb') as f:
                    await context.bot.send_audio(
                        chat_id=query.from_user.id,
                        audio=f,
                        title=audio_file.replace('.mp3', '').replace('.wav', '').replace('.m4a', ''),
                        parse_mode="HTML"
                    )
            
            await query.answer(f"✅ Test {test_num} audio files sent!")
        except Exception as e:
            print(f"Error sending IELTS test: {e}")
            await query.answer(f"❌ Error: {str(e)}", show_alert=True)


async def handle_ielts_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Go back to Cambridge books list."""
    query = update.callback_query
    await query.answer()
    
    books = get_cambridge_books()
    
    # Build buttons - 5 per row
    buttons = []
    for i in range(0, len(books), 5):
        row = []
        for j in range(i, min(i + 5, len(books))):
            book_num = books[j]
            row.append(InlineKeyboardButton(
                f"📖 {book_num}",
                callback_data=f"ielts_book:{book_num}"
            ))
        buttons.append(row)
    
    # Add computer-based test link
    buttons.append([InlineKeyboardButton(
        "💻 Computer Based Test",
        url="https://engnovate.com/ielts-tests/"
    )])
    
    text = "📚 Cambridge IELTS Books:\n\nSelect a book number:"
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))
