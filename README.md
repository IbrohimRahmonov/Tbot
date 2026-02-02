# Tbot - 대학원 입시 도우미 (Korean Graduate School Admission Helper)

A Telegram bot that helps users find graduate school admission information for Korean universities.

## Features

- Search for university admission schedules by university name or department
- Get application start/end dates and interview dates
- Support for major Korean universities (연세대, 고려대, 서울대, 한양대, 성균관대)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/IbrohimRahmonov/Tbot.git
cd Tbot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. **IMPORTANT - Security Note**: 
   - The current `bot.py` contains a hardcoded token for demonstration purposes
   - For production use, you should:
     - Create your own bot via @BotFather on Telegram
     - Store your token in an environment variable or `.env` file
     - Never commit tokens to version control
   - Example using environment variable:
     ```python
     import os
     TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
     ```

## Usage

Run the bot:
```bash
python bot.py
```

### Bot Commands

- `/start` - Start the bot and get instructions
- Send university or department name to search for admission schedules
  - Example: "연세대 일정"
  - Example: "고려대 일반대학원"

## Data Format

The bot reads admission data from `admissions.json`. Each entry contains:
- `uni`: University name (in Korean)
- `dept`: Department name (in Korean)
- `app_start`: Application start date
- `app_end`: Application end date
- `interview`: Interview date

## Requirements

- Python 3.7+
- python-telegram-bot 20.7+
