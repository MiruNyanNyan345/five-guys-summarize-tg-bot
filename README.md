# Five Guys Summarize Telegram Bot 🤖

A witty Hong Kong Cantonese Telegram bot that brings the spirit of LIHKG discussion forums to your group chats. This bot can summarize conversations, generate compliments, create cheesy love quotes, and much more - all with authentic Hong Kong internet culture flavor.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue.svg)](https://core.telegram.org/bots)

## ✨ Features

### 🎯 Core Functions
- **Daily Chat Summarization**: Get AI-powered summaries of group conversations
- **User-Specific Summaries**: Analyze what specific users have been talking about
- **Golden Quote King**: Find the most interesting/funny speaker of the day
- **Smart Q&A**: Answer questions using AI with Hong Kong style responses

### 🎪 Entertainment Features
- **Compliment Generator**: Generate personalized compliments for users
- **Love Quote Generator**: Create cheesy pickup lines (土味情話) in Cantonese
- **Apology Generator**: Generate humorous apologies featuring 五仁月餅 references
- **Roast Function**: Playful "diu" responses for friendly banter

### ⏰ Utility Features
- **Work Countdown**: Calculate time remaining until end of work day
- **Retirement Countdown**: Count down to your retirement date
- **Timezone Aware**: All times calculated in Hong Kong timezone (HKT)

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- OpenAI API key or compatible AI service

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/MiruNyanNyan345/five-guys-summarize-tg-bot.git
   cd five-guys-summarize-tg-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```env
   BOT_TOKEN=your_telegram_bot_token_here
   DATABASE_URL=postgresql://username:password@host:port/database
   MODEL=your_ai_model_name
   API_KEY=your_openai_api_key
   BASE_URL=your_ai_service_base_url
   ```

4. **Set up database**
   
   The bot will automatically create necessary tables on first run.

5. **Run the bot**
   ```bash
   python main.py
   ```

## 🎮 Bot Commands

### Chat Management (Admin Required)
- `/summarize` - Summarize today's entire conversation
- `/summarize_user` - Summarize a specific user's messages (reply to user)
- `/golden_quote_king` - Find today's most interesting speaker

### Interactive Commands
- `/compliment` - Generate a personalized compliment (reply to user)
- `/love` - Send cheesy pickup lines (reply to user)  
- `/apologize` - Generate a humorous apology
- `/diu` - Playful roast response (reply to user)
- `/answer [question]` - Ask the AI a question

### Utility Commands
- `/countdown` - Time until end of work day (6 PM HKT)
- `/countdown_to_work` - Time until next work day starts
- `/countdown_to_retirement [year]` - Time until retirement year

## 🏗️ Project Structure

```
five-guys-summarize-tg-bot/
├── main.py              # Main bot application
├── config.py           # Configuration and AI prompts
├── ai.py               # AI integration functions
├── database.py         # Database connection pooling
├── db.py               # Database operations
├── summarize.py        # Message summarization features
├── compliment.py       # User compliment generation
├── love.py             # Love quote generation
├── fuck.py             # Roast/diu response generation
├── aplogize.py         # Apology generation
├── requirements.txt    # Python dependencies
└── .gitignore         # Git ignore rules
```

## 🧠 AI Integration

The bot uses OpenAI-compatible APIs with custom prompts designed to:
- **Mimic Hong Kong Internet Culture**: Incorporates LIHKG and JFFT YouTube channel language styles
- **Use Authentic Cantonese**: Traditional Chinese with Hong Kong slang and expressions
- **Maintain Cultural Context**: References local culture, food, and humor
- **Generate Contextual Responses**: Adapts responses based on user messages and chat history

### Supported AI Models
- OpenAI GPT models
- Any OpenAI-compatible API endpoint
- Custom base URLs supported through configuration

## 🗄️ Database Schema

The bot stores message data in PostgreSQL:

```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT,
    user_name TEXT,
    user_id BIGINT,
    text TEXT,
    timestamp TIMESTAMP,
    chat_title TEXT
);
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `BOT_TOKEN` | Telegram Bot Token from BotFather | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `MODEL` | AI model name | Yes |
| `API_KEY` | AI service API key | Yes |
| `BASE_URL` | AI service base URL | Yes |

### Bot Permissions

The bot requires the following permissions in Telegram groups:
- **Read Messages**: To analyze chat conversations
- **Send Messages**: To respond to commands
- **Admin Status**: Required for summarization features

## 🎨 Language Style

The bot is specifically designed to communicate in:
- **Traditional Chinese** (繁體中文)
- **Hong Kong Cantonese** style and vocabulary
- **LIHKG-style** internet slang and expressions
- **JFFT-inspired** humor and catchphrases
- **Local cultural references** and emoji usage

## 📝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Guidelines
- Follow existing code style and structure
- Test your changes thoroughly
- Update documentation as needed
- Respect the Hong Kong cultural context of the bot

## 🐛 Troubleshooting

### Common Issues

**Bot not responding in groups:**
- Ensure the bot has admin permissions
- Check that the bot is added to the group
- Verify the bot token is correct

**Database connection errors:**
- Verify PostgreSQL is running
- Check DATABASE_URL format
- Ensure database permissions are correct

**AI responses failing:**
- Verify API key is valid
- Check BASE_URL configuration
- Monitor API rate limits

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Built with [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- Inspired by Hong Kong internet culture and LIHKG community
- AI prompts designed to reflect authentic local language patterns

## 📞 Support

For support, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for similar problems
- Review the troubleshooting section above

## 🚧 Roadmap

- [ ] Add more entertainment commands
- [ ] Implement user preference settings  
- [ ] Add support for more AI providers
- [ ] Create web dashboard for bot management
- [ ] Add multi-language support (while maintaining HK flavor)
