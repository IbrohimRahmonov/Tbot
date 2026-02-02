from telegram.ext import Application, CommandHandler, MessageHandler, filters
import json
import os

# Load your parsed data
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8506150906:AAEYnGTnmHJkQvtqOW-aJEDowkYMxIhMMuY')
with open('admissions.json', encoding='utf-8') as f:
    data = json.load(f)

async def start(update, context):
    await update.message.reply_text('대학원 입시 도우미! "연세대 일정" 입력하세요.')

async def query(update, context):
    text = update.message.text.lower()
    # Simple match: find matching uni/dept
    results = []
    for entry in data:
        # Check if the query matches university or department
        university = entry['university'].lower()
        department = entry.get('department', '').lower()
        
        # Check if university name or part of it is in the query
        # Support shortened names like "연세대" for "연세대학교"
        uni_match = False
        dept_match = False
        
        # Remove common suffixes for matching
        uni_base = university.replace('대학교', '').replace('대학', '')
        dept_base = department.replace('학과', '').replace('학부', '')
        
        # Check if university matches
        if uni_base in text or university in text:
            uni_match = True
        
        # Check if department matches
        if dept_base in text or department in text:
            dept_match = True
        
        # Check for various query patterns
        if '일정' in text or 'schedule' in text:
            if uni_match:
                results.append(f"<b>{entry['university']} {entry['department']}</b>\n{entry['schedule']}")
        elif '요구사항' in text or 'requirements' in text or '조건' in text:
            if uni_match:
                results.append(f"<b>{entry['university']} {entry['department']}</b>\n요구사항: {entry['requirements']}")
        elif '홈페이지' in text or 'website' in text:
            if uni_match:
                results.append(f"<b>{entry['university']} {entry['department']}</b>\n홈페이지: {entry['website']}")
        else:
            # General search - check if text contains university or department name
            if uni_match or dept_match:
                results.append(
                    f"<b>{entry['university']} {entry['department']}</b>\n"
                    f"일정:\n{entry['schedule']}\n\n"
                    f"요구사항: {entry['requirements']}\n"
                    f"홈페이지: {entry['website']}"
                )
    
    if results:
        response = "\n\n---\n\n".join(results)
        await update.message.reply_text(response, parse_mode='HTML')
    else:
        await update.message.reply_text(
            '검색 결과가 없습니다. 다른 대학명이나 학과명을 입력해주세요.\n'
            '예: "연세대 일정", "고려대 컴퓨터", "카이스트 요구사항"'
        )

def main():
    # Create the Application
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, query))
    
    # Run the bot
    print("Bot is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()
