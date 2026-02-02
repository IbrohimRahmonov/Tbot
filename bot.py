from telegram.ext import Application, CommandHandler, MessageHandler, filters
import json  # Load your parsed data

TOKEN = '8506150906:AAEYnGTnmHJkQvtqOW-aJEDowkYMxIhMMuY'  # Get from @BotFather
with open('admissions.json', encoding='utf-8') as f:
    data = json.load(f)  # Parsed PDF info

async def start(update, context):
    await update.message.reply_text('대학원 입시 도우미! "연세대 일정" 입력하세요.')

async def query(update, context):
    text = update.message.text
    # Simple match: find matching uni/dept
    for entry in data:
        if any(word in text for word in [entry['uni'], entry['dept']]):
            msg = f"{entry['uni']} {entry['dept']}: 지원 {entry['app_start']} ~ {entry['app_end']}, 면접 {entry['interview']}"
            await update.message.reply_text(msg)
            return
    await update.message.reply_text('지원대상 대학/학과 이름을 더 정확히 입력하세요. 예: "고려대 일반대학원"')

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler('start', start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, query))
app.run_polling()
