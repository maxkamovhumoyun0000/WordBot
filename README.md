# Wordl Bot

A Telegram bot for learning English-Uzbek vocabulary with quizzes, games, and statistics tracking.

## Features

- 📚 **Word Management** - Add, edit, and organize vocabulary
- 🎯 **Quiz Mode** - Test your knowledge with interactive quizzes
- ⚡ **Blitz Mode** - Fast-paced word challenges
- 📊 **Statistics** - Track your learning progress
- 🏆 **Leaderboard** - Compete with other users
- 📁 **Import/Export** - Backup and restore your data
- ⏰ **Reminders** - Get notified to review words
- 👥 **Groups** - Organize words into categories
- 🌐 **Multilingual** - Support for Uzbek, Russian, and English

## Prerequisites

- Python 3.8+
- Telegram Bot Token
- sqlite3 (included with Python)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd wordl
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` file and add your configuration:
```
BOT_TOKEN=your_telegram_bot_token_here
DB_PATH=/path/to/bot.db
ADMIN_IDS=your_telegram_id,other_admin_ids
```

## Running the Bot

```bash
python word.py
```

## Environment Variables

Required environment variables:

- `BOT_TOKEN` - Your Telegram bot token (required)
- `DB_PATH` - Path to SQLite database (default: `/home/ubuntu/bot/bot.db`)
- `ADMIN_IDS` - Comma-separated list of admin user IDs

## Project Structure

```
wordl/
├── word.py              # Main bot application
├── test_word.py         # Unit tests
├── backup_restore.py    # Data backup and restore functionality
├── grammar.py           # Grammar-related features
├── math_quiz.py         # Math quiz module
├── math_telegram.py     # Telegram integration for math module
├── ielts.py            # IELTS exam features
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
└── IELTS/              # IELTS test materials
```

## Database Schema

The bot uses SQLite database with the following main tables:

- `users` - User profiles and statistics
- `words` - Vocabulary entries
- `user_words` - User's word collections and progress
- `groups` - Word groups/categories
- `reminders` - User reminders

## Commands

### User Commands
- `/start` - Start the bot and show main menu
- `/help` - Get help information
- `/stats` - View your statistics
- `/words` - List your words
- `/add` - Add new words
- `/quiz` - Start a quiz
- `/blitz` - Start blitz mode
- `/leader` - View leaderboard
- `/remind` - Set reminders
- `/backup` - Create backup
- `/restore` - Restore from backup

### Admin Commands
- `/admin` - Admin panel
- `/broadcast` - Send message to all users

## Testing

Run tests using pytest:

```bash
pytest test_word.py -v
```

## Security Notes

⚠️ **Never commit sensitive information:**
- Bot tokens
- Admin IDs
- Database paths with sensitive data

Always use `.env` file for local secrets and ensure `.env` is in `.gitignore`.

## Development

To contribute to this project:

1. Create a feature branch
2. Make your changes
3. Run tests to ensure nothing breaks
4. Submit a pull request

## Support & Contact

**Developer:** Maxkamov Xumoyun  
**Email:** [Elektron pochta](mailto:mahkamovhumoyun121@gmail.com)  
📧 mahkamovhumoyun121@gmail.com

For issues, questions, or feature requests, please contact the developer.

## License

This project is proprietary software. All rights reserved.

## Changelog

### Version 1.0.0
- Initial release
- Core vocabulary learning features
- Quiz and blitz modes
- User statistics and progress tracking
- Import/Export functionality
- Admin panel

---

Last Updated: January 15, 2026
