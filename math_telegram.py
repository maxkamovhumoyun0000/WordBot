"""
Math Quiz - Telegram Bot Integration Module
Handles all Telegram interactions for the math quiz
"""

try:
    from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
    from telegram.ext import ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError:
    # Allow import for testing without telegram installed
    TELEGRAM_AVAILABLE = False
    Update = None
    InlineKeyboardMarkup = None
    InlineKeyboardButton = None
    ContextTypes = type('ContextTypes', (), {'DEFAULT_TYPE': None})()

from typing import Optional
import random

from math_quiz import MathQuiz
from math_db import MathDatabase, init_math_tables
# If this module is used inside the main bot, we can create/get user records
try:
    from word import get_or_create_user
except Exception:
    # If running standalone for tests, get_or_create_user may not be available
    def get_or_create_user(tg_id: int, username: Optional[str]) -> Optional[int]:
        return None


class MathBotHandler:
    """Handler for math quiz in Telegram bot"""
    
    def __init__(self, db_path: str):
        self.db = MathDatabase(db_path)
        self.db_path = db_path
        init_math_tables(db_path)
        self.active_quizzes = {}  # {user_id: MathQuiz instance}
    
    def get_unlock_keyboard(self) -> InlineKeyboardMarkup:
        """Get keyboard for asking secret code"""
        keyboard = [
            [InlineKeyboardButton("🔓 Kodni kiriting", callback_data="trig_enter_code")],
            [InlineKeyboardButton("❓ Yordam", callback_data="trig_help")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_topic_selection_keyboard(self) -> InlineKeyboardMarkup:
        """Get keyboard for selecting quiz topic after unlock"""
        keyboard = [
            [InlineKeyboardButton("📐 Trigonometriya Testi", callback_data="trig_select_trigonometry")],
            [InlineKeyboardButton("📊 Qiymatlari Ko'rish", callback_data="trig_view_values")],
            [InlineKeyboardButton("📊 Statistikani Ko'rish", callback_data="trig_view_stats")],
            [InlineKeyboardButton("🏆 Reyting", callback_data="trig_leaderboard")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="trig_back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_angle_selection_keyboard(self) -> InlineKeyboardMarkup:
        """Get keyboard for selecting angle to view values"""
        keyboard = [
            [InlineKeyboardButton("0°", callback_data="trig_angle_0"),
             InlineKeyboardButton("30°", callback_data="trig_angle_30"),
             InlineKeyboardButton("45°", callback_data="trig_angle_45")],
            [InlineKeyboardButton("60°", callback_data="trig_angle_60"),
             InlineKeyboardButton("90°", callback_data="trig_angle_90"),
             InlineKeyboardButton("120°", callback_data="trig_angle_120")],
            [InlineKeyboardButton("135°", callback_data="trig_angle_135"),
             InlineKeyboardButton("150°", callback_data="trig_angle_150"),
             InlineKeyboardButton("180°", callback_data="trig_angle_180")],
            [InlineKeyboardButton("210°", callback_data="trig_angle_210"),
             InlineKeyboardButton("225°", callback_data="trig_angle_225"),
             InlineKeyboardButton("240°", callback_data="trig_angle_240")],
            [InlineKeyboardButton("270°", callback_data="trig_angle_270"),
             InlineKeyboardButton("300°", callback_data="trig_angle_300"),
             InlineKeyboardButton("315°", callback_data="trig_angle_315")],
            [InlineKeyboardButton("330°", callback_data="trig_angle_330"),
             InlineKeyboardButton("360°", callback_data="trig_angle_360")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="trig_back_select")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_quiz_mode_keyboard(self) -> InlineKeyboardMarkup:
        """Get keyboard for selecting number of questions"""
        keyboard = [
            [
                InlineKeyboardButton("5 ⭐", callback_data="trig_quiz_5"),
                InlineKeyboardButton("10 ⭐⭐", callback_data="trig_quiz_10"),
            ],
            [
                InlineKeyboardButton("15 ⭐⭐⭐", callback_data="trig_quiz_15"),
                InlineKeyboardButton("20 ⭐⭐⭐⭐", callback_data="trig_quiz_20"),
            ],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="trig_back_select")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_quiz_answer_keyboard(self, options: list, option_letters: list) -> ReplyKeyboardMarkup:
        """Get reply-keyboard for quiz question answers (non-inline)

        Returns a ReplyKeyboardMarkup where each option is a visible button the user
        can tap; this sends a normal message which the main dispatcher will forward
        to `handle_incoming_message` for processing.
        """
        # Build rows: one button per option
        rows = []
        for i, (option, letter) in enumerate(zip(options, option_letters)):
            rows.append([KeyboardButton(f"{letter}) {option}")])

        # Add control buttons (Next / Quit will be shown after answering)
        # We don't include Next here to avoid confusion before answering.
        return ReplyKeyboardMarkup(rows, one_time_keyboard=True, resize_keyboard=True)

    def get_quiz_feedback_keyboard(self) -> ReplyKeyboardMarkup:
        """Keyboard shown after answering to allow next question or quitting"""
        rows = [
            [KeyboardButton("⬇️ Keyingi Savol")],
            [KeyboardButton("❌ Testni Tugatish")]
        ]
        return ReplyKeyboardMarkup(rows, one_time_keyboard=True, resize_keyboard=True)

    async def _require_unlocked(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Ensure the user has unlocked the math module; if not, prompt for code and return False."""
        db_user_id = context.user_data.get('db_user_id')
        if not db_user_id:
            try:
                await update.message.reply_text("❌ Foydalanuvchi ma'lumotlari topilmadi. Iltimos /start ni bosing.")
            except Exception:
                pass
            return False

        if not self.db.is_user_unlocked(db_user_id):
            try:
                # Prompt for code entry flow
                if getattr(update, 'callback_query', None):
                    await update.callback_query.edit_message_text(
                        "🔒 Bu bo'lim maxfiy. Iltimos, kodni kiriting:",
                        reply_markup=self.get_unlock_keyboard()
                    )
                else:
                    await update.message.reply_text(
                        "🔒 Bu bo'lim maxfiy. Iltimos, kodni kiriting:",
                        reply_markup=self.get_unlock_keyboard()
                    )
            except Exception:
                pass
            return False

        return True
    
    async def send_welcome_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send welcome message for trigonometry module"""
        user = update.effective_user
        user_id = user.id
        
        # Check if user is unlocked
        try:
            # Get db_user_id from context
            db_user_id = context.user_data.get('db_user_id')
            if not db_user_id:
                # This should be set by main bot
                await update.message.reply_text(
                    "❌ Xato: Foydalanuvchi ma'lumotlari topilmadi. Iltimos, /start ni bosing."
                )
                return
            
            is_unlocked = self.db.is_user_unlocked(db_user_id)
            
            if is_unlocked:
                await update.message.reply_text(
                    "📐 **TRIGONOMETRIYA MODULI**\n\n"
                    "Maxfiy bo'lim ochildi! Amaliyot qilishga tayyor?",
                    reply_markup=self.get_topic_selection_keyboard(),
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(
                    "🔒 **MAXFIY BO'LIM - TRIGONOMETRIYA**\n\n"
                    "Bu bo'lim maxfiy! Faqat maxfiy kod bilan ochiladi.\n\n"
                    "Kod kiriting yoki yordam so'rayin.",
                    reply_markup=self.get_unlock_keyboard(),
                    parse_mode="Markdown"
                )
        except Exception as e:
            await update.message.reply_text(f"❌ Xato: {str(e)}")
    
    async def request_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ask user to enter unlock code"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "🔐 Maxfiy kodni kiriting:\n\n"
            "*(Kodi admin bilan oling)*",
            parse_mode="Markdown"
        )
        
        context.user_data['waiting_for_code'] = True
    
    async def process_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Process entered code"""
        user_message = update.message.text.strip()
        db_user_id = context.user_data.get('db_user_id')
        
        # If db_user_id is missing, attempt to create/get it from main user table
        if not db_user_id:
            try:
                uid = get_or_create_user(update.effective_user.id, update.effective_user.username)
                if uid:
                    db_user_id = uid
                    context.user_data['db_user_id'] = uid
            except Exception:
                db_user_id = None

        if not db_user_id:
            await update.message.reply_text("❌ Xato: Foydalanuvchi ma'lumotlari topilmadi. Iltimos /start ni bosing.")
            return False
        
        if user_message == "0107":
            # Unlock user
            self.db.unlock_user(db_user_id, update.effective_user.id)
            context.user_data['waiting_for_code'] = False
            
            await update.message.reply_text(
                "✅ **MAXFIY BO'LIM OCHILDI!**\n\n"
                "📐 Trigonometriya moduliga xush kelibsiz!\n"
                "Endi testlarni boshlashingiz mumkin.",
                reply_markup=self.get_topic_selection_keyboard(),
                parse_mode="Markdown"
            )
            return True
        else:
            await update.message.reply_text(
                "❌ Kod noto'g'ri!\n\n"
                "Yana urinib ko'ring yoki /trigonometriya komandasini bosing."
            )
            context.user_data['waiting_for_code'] = False
            return False
    
    async def start_quiz(self, update: Update, context: ContextTypes.DEFAULT_TYPE, num_questions: int):
        """Start a new quiz session"""
        # Require unlock before starting
        if not await self._require_unlocked(update, context):
            return

        query = update.callback_query
        await query.answer()
        
        db_user_id = context.user_data.get('db_user_id')
        user_id = update.effective_user.id
        
        if not db_user_id:
            await query.edit_message_text("❌ Xato: Foydalanuvchi ma'lumotlari topilmadi.")
            return
        
        # Create quiz
        quiz = MathQuiz()
        quiz.unlock_hidden_section("0107")
        questions = quiz.generate_quiz_session(num_questions)
        
        if not questions:
            await query.edit_message_text("❌ Test yaratib bo'lmadi. Iltimos, qayta urinib ko'ring.")
            return
        
        # Create database session
        session_id = self.db.create_quiz_session(db_user_id, user_id, num_questions)
        
        # Store in context
        context.user_data['math_quiz_session'] = {
            'session_id': session_id,
            'quiz': quiz,
            'questions': questions,
            'current_index': 0,
            'correct_count': 0,
            'wrong_count': 0
        }
        
        # Send first question
        await self.send_next_question(update, context)
    
    async def send_next_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send next question in quiz"""
        quiz_data = context.user_data.get('math_quiz_session')
        
        if not quiz_data:
            if update.callback_query:
                await update.callback_query.edit_message_text("❌ Test topilmadi.")
            else:
                await update.message.reply_text("❌ Test topilmadi.")
            return
        
        quiz = quiz_data['quiz']
        questions = quiz_data['questions']
        current_index = quiz_data['current_index']
        
        # Check if quiz is finished
        if current_index >= len(questions):
            await self.finish_quiz(update, context)
            return
        
        # Get current question
        question = questions[current_index]
        progress = quiz.get_current_progress()
        
        message_text = (
            f"📍 **{progress['message']}**\n\n"
            f"❓ {question['question_text']}\n"
        )
        
        keyboard = self.get_quiz_answer_keyboard(question['options'], question['option_letters'])

        # Use reply messages for quiz flow (non-inline). If this was triggered
        # by a callback_query we try to edit the message, otherwise send a new
        # message. For consistency with reply-keyboard flow, prefer sending a
        # new message so the reply keyboard appears correctly.
        try:
            await update.message.reply_text(
                message_text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        except Exception:
            # Fallback if update.message is not available
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    message_text,
                    parse_mode="Markdown"
                )
    
    async def process_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE, answer_index: int):
        """Process user's answer"""
        # Support both callback_query-based and message-based invocations
        query = getattr(update, 'callback_query', None)
        if query:
            try:
                await query.answer()
            except Exception:
                pass

        quiz_data = context.user_data.get('math_quiz_session')
        if not quiz_data:
            # If we can't find session, reply back via message or callback
            if query:
                await query.edit_message_text("❌ Test topilmadi.")
            else:
                await update.message.reply_text("❌ Test topilmadi.")
            return
        
        quiz = quiz_data['quiz']
        questions = quiz_data['questions']
        current_index = quiz_data['current_index']
        session_id = quiz_data['session_id']
        
        question = questions[current_index]
        
        # Check answer
        is_correct, feedback = quiz.check_answer(question, answer_index)
        
        # Save to database
        self.db.save_quiz_answer(
            session_id=session_id,
            question_num=current_index + 1,
            angle=question['angle'],
            function=question['function'],
            correct_answer=question['correct_answer'],
            user_answer=question['options'][answer_index],
            is_correct=is_correct
        )
        
        # Update quiz data
        if is_correct:
            quiz_data['correct_count'] += 1
        else:
            quiz_data['wrong_count'] += 1
        
        quiz_data['current_index'] += 1
        
        # Show feedback and present a reply-keyboard to continue or quit
        feedback_message = (
            f"{feedback}\n\n"
            f"⏱️ Keyingi savol uchun "
        )

        # Send feedback as a new message with a small reply keyboard
        try:
            await update.message.reply_text(
                feedback_message,
                reply_markup=self.get_quiz_feedback_keyboard(),
                parse_mode="Markdown"
            )
        except Exception:
            if query:
                await query.edit_message_text(
                    feedback_message,
                    parse_mode="Markdown"
                )
    
    async def next_question_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Move to next question"""
        query = update.callback_query
        await query.answer()
        
        await self.send_next_question(update, context)
    
    async def finish_quiz(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Finish quiz and show results"""
        query = update.callback_query if update.callback_query else None
        quiz_data = context.user_data.get('math_quiz_session')
        
        if not quiz_data:
            if query:
                await query.edit_message_text("❌ Test ma'lumotlari topilmadi.")
            else:
                await update.message.reply_text("❌ Test ma'lumotlari topilmadi.")
            return
        
        session_id = quiz_data['session_id']
        quiz = quiz_data['quiz']
        correct_count = quiz_data['correct_count']
        wrong_count = quiz_data['wrong_count']
        
        # Finish session in database
        results = self.db.finish_quiz_session(session_id, correct_count, wrong_count)
        
        # Format results
        emoji_rating = "⭐" * max(1, int(results['percentage'] // 20))
        
        results_text = (
            f"📈 **TEST NATIJALARI**\n\n"
            f"✅ To'g'ri: {results['correct']}/{results['correct'] + results['wrong']}\n"
            f"❌ Noto'g'ri: {results['wrong']}/{results['correct'] + results['wrong']}\n"
            f"📊 Foiz: {results['percentage']:.1f}%\n"
            f"🏆 Baho: {emoji_rating}\n\n"
            f"📊 **JAMI STATISTIKA**\n"
            f"• Sessionlar: {results['total_sessions']}\n"
            f"• O'rtacha: {results['average_percentage']:.1f}%\n"
            f"• Eng yaxshi: {results['best_score']:.1f}%"
        )
        
        keyboard = [
            [InlineKeyboardButton("🔄 Qayta Test", callback_data="trig_back_select")],
            [InlineKeyboardButton("📊 Statistika", callback_data="trig_view_stats")],
            [InlineKeyboardButton("🏠 Asosiy Menu", callback_data="trig_back_main")]
        ]
        
        if query:
            await query.edit_message_text(
                results_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                results_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        
        # Clear quiz data
        context.user_data['math_quiz_session'] = None
    
    async def show_statistics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user's statistics"""
        if not await self._require_unlocked(update, context):
            return

        query = update.callback_query
        await query.answer()
        
        db_user_id = context.user_data.get('db_user_id')
        
        if not db_user_id:
            await query.edit_message_text("❌ Xato: Foydalanuvchi ma'lumotlari topilmadi.")
            return
        
        stats = self.db.get_user_stats(db_user_id)
        
        if not stats or stats['total_sessions'] == 0:
            await query.edit_message_text(
                "📊 Hali statistika yo'q. Birinchi testni boshlang!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Orqaga", callback_data="trig_back_select")]
                ])
            )
            return
        
        stats_text = (
            f"📊 **SHAXSIY STATISTIKA**\n\n"
            f"📝 Jami Sessionlar: {stats['total_sessions']}\n"
            f"❓ Jami Savollar: {stats['total_questions']}\n"
            f"✅ To'g'ri Javoblar: {stats['total_correct']}\n"
            f"❌ Noto'g'ri Javoblar: {stats['total_wrong']}\n"
            f"📊 O'rtacha Foiz: {stats['average_percentage']:.1f}%\n"
            f"🏆 Eng Yaxshi Skor: {stats['best_score']:.1f}%\n"
            f"⏰ Oxirgi Test: {stats['last_quiz_date']}"
        )
        
        keyboard = [
            [InlineKeyboardButton("📐 Savol Bo'yicha Statistika", callback_data="trig_question_stats")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="trig_back_select")]
        ]
        
        await query.edit_message_text(
            stats_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    
    async def show_question_statistics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show statistics for each question type"""
        if not await self._require_unlocked(update, context):
            return

        query = update.callback_query
        await query.answer()
        
        db_user_id = context.user_data.get('db_user_id')
        
        if not db_user_id:
            await query.edit_message_text("❌ Xato: Foydalanuvchi ma'lumotlari topilmadi.")
            return
        
        question_stats = self.db.get_question_stats(db_user_id)
        
        if not question_stats:
            await query.edit_message_text(
                "📊 Hali statistika yo'q.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Orqaga", callback_data="trig_view_stats")]
                ])
            )
            return
        
        # Show worst performing questions
        stats_text = "📐 **SAVOL BO'YICHA STATISTIKA (ENG QIYIN)**\n\n"
        
        for i, qs in enumerate(question_stats[:10], 1):
            stats_text += (
                f"{i}. {qs['function'].upper()}({qs['angle']}°): "
                f"{qs['correct_attempts']}/{qs['total_attempts']} ({qs['accuracy']:.1f}%)\n"
            )
        
        keyboard = [
            [InlineKeyboardButton("🔙 Orqaga", callback_data="trig_view_stats")]
        ]
        
        await query.edit_message_text(
            stats_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    
    async def show_trig_values(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show angle selection for viewing trigonometric values"""
        if not await self._require_unlocked(update, context):
            return

        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "📐 **TRIGONOMETRIYA QIYMATLARI**\n\n"
            "Gradusni tanlang:",
            reply_markup=self.get_angle_selection_keyboard(),
            parse_mode="Markdown"
        )
    
    async def show_angle_values(self, update: Update, context: ContextTypes.DEFAULT_TYPE, angle: int):
        """Show sin, cos, tan, ctg values for selected angle"""
        if not await self._require_unlocked(update, context):
            return

        query = update.callback_query
        await query.answer()
        
        from math_quiz import MATH_TRIGONOMETRY_DATA
        
        if angle not in MATH_TRIGONOMETRY_DATA:
            await query.edit_message_text("❌ Burchak topilmadi")
            return
        
        data = MATH_TRIGONOMETRY_DATA[angle]
        
        message_text = (
            f"📐 **{angle}° - TRIGONOMETRIYA QIYMATLARI**\n\n"
            f"🔹 sin({angle}°) = {data['sin']}\n"
            f"🔹 cos({angle}°) = {data['cos']}\n"
            f"🔹 tg({angle}°) = {data['tan']}\n"
            f"🔹 ctg({angle}°) = {data['ctg']}\n"
        )
        
        keyboard = [
            [InlineKeyboardButton("🔙 Boshqa gradus", callback_data="trig_view_values")],
            [InlineKeyboardButton("❌ Yopish", callback_data="trig_back_select")]
        ]
        
        await query.edit_message_text(
            message_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    
    async def show_leaderboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show leaderboard"""
        if not await self._require_unlocked(update, context):
            return

        query = update.callback_query
        await query.answer()
        
        leaderboard = self.db.get_leaderboard(10)
        
        if not leaderboard:
            await query.edit_message_text(
                "🏆 Hali leaderboard yo'q.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Orqaga", callback_data="trig_back_select")]
                ])
            )
            return
        
        leaderboard_text = "🏆 **TRIGONOMETRIYA REYTING (TOP 10)**\n\n"
        
        medals = ["🥇", "🥈", "🥉"]
        
        for i, user in enumerate(leaderboard, 1):
            medal = medals[i-1] if i <= 3 else f"{i}."
            username = user['username'] or f"User{user['tg_id']}"
            leaderboard_text += (
                f"{medal} @{username}\n"
                f"   📊 {user['average_percentage']:.1f}% | "
                f"Session: {user['total_sessions']} | "
                f"Best: {user['best_score']:.1f}%\n\n"
            )
        
        keyboard = [
            [InlineKeyboardButton("🔙 Orqaga", callback_data="trig_back_select")]
        ]
        
        await query.edit_message_text(
            leaderboard_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    async def handle_incoming_message(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        """
        Central handler for incoming text messages related to the math module.
        Accepts the secret code `0107` directly (so user can just type it),
        and also preserves the existing waiting_for_code behavior.
        """
        # Only handle text messages
        if not getattr(update, 'message', None) or not getattr(update.message, 'text', None):
            return False

        text = update.message.text.strip()

        # If user is in a quiz session, treat incoming text as quiz input
        quiz_data = context.user_data.get('math_quiz_session')
        if quiz_data:
            try:
                # Determine current question
                current_index = quiz_data.get('current_index', 0)
                questions = quiz_data.get('questions', [])
                if current_index < len(questions):
                    question = questions[current_index]
                    options = question.get('options', [])
                    option_letters = question.get('option_letters', [])

                    # Normalize incoming text
                    txt = text.strip()

                    # Handle control buttons
                    if txt in ("⬇️ Keyingi Savol", "Keyingi Savol", "next", "Next", "⬇️ keyingi savol"):
                        await self.send_next_question(update, context)
                        return True
                    if "Tugat" in txt or "tugat" in txt or "Testni Tugatish" in txt or "Tugatish" in txt:
                        await self.finish_quiz(update, context)
                        return True

                    # Try to parse lettered answer like 'A) ...' or 'A'
                    answer_idx = None
                    if len(txt) >= 1 and txt[0].upper() in [c.upper() for c in option_letters]:
                        letter = txt[0].upper()
                        try:
                            answer_idx = option_letters.index(letter)
                        except ValueError:
                            answer_idx = None

                    # Try patterns like 'A) option' or full option text
                    if answer_idx is None:
                        for i, letter in enumerate(option_letters):
                            if txt.startswith(f"{letter})") or txt.startswith(f"{letter}) "):
                                answer_idx = i
                                break
                        if answer_idx is None:
                            # direct match with option text
                            for i, opt in enumerate(options):
                                if txt == opt or txt == f"{option_letters[i]}) {opt}":
                                    answer_idx = i
                                    break

                    if answer_idx is not None:
                        try:
                            await self.process_answer(update, context, answer_idx)
                        except Exception as e:
                            try:
                                await update.message.reply_text(f"❌ Xato: {e}")
                            except Exception:
                                pass
                        return True

                    # If no match, ask user to choose one of the options
                    try:
                        await update.message.reply_text("Iltimos, variantlardan birini tanlang (masalan: A) yoki A).)")
                    except Exception:
                        pass
                    return True
            except Exception as e:
                try:
                    await update.message.reply_text(f"❌ Xato ichida quiz handling: {e}")
                except Exception:
                    pass
                return True

        # If user explicitly typed the code or waiting_for_code flag is set, process it
        if text == '0107' or context.user_data.get('waiting_for_code'):
            # call existing process_code
            try:
                return await self.process_code(update, context)
            except Exception as e:
                # fallback reply
                try:
                    await update.message.reply_text(f"❌ Xato: {e}")
                except Exception:
                    pass
                return False

        # Not handled here
        return False


if __name__ == "__main__":
    print("Telegram integration module loaded successfully")
