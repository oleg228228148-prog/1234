from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
import asyncio

# Логирование (не хранит личные данные)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ⚙️ ВСТАВЬ СЮДА ТОКЕН ОТ @BotFather
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# 🧠 Список чатов для рассылки
subscribers = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    subscribers.add(chat_id)
    await update.message.reply_text(
        "🌌 Добро пожаловать в *Абсолютную Анонимность*.\n\n"
        "📩 Пиши что угодно — все получат это сообщение.\n"
        "👤 Никто не узнает автора. Никогда. Даже я.\n\n"
        "Готов? Начинай 👇",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    subscribers.add(chat_id)

    if update.message.text:
        content = update.message.text
        is_voice = False
    elif update.message.voice:
        content = update.message.voice.file_id
        is_voice = True
    else:
        await update.message.reply_text("Принимаю только текст и голосовые.")
        return

    # Сообщение для рассылки
    broadcast_text = "📩 Анонимное сообщение:" if not is_voice else "📩 Анонимное голосовое:"

    failed_ids = set()
    for target_id in list(subscribers):
        try:
            await context.bot.send_message(chat_id=target_id, text=broadcast_text)
            if is_voice:
                await context.bot.send_voice(chat_id=target_id, voice=content)
            else:
                await context.bot.send_message(chat_id=target_id, text=content)
        except Exception as e:
            logger.warning(f"Не удалось отправить в {target_id}: {e}")
            failed_ids.add(target_id)

    # Чистим мертвые чаты
    for bad_id in failed_ids:
        subscribers.discard(bad_id)

    await update.message.reply_text("✅ Доставлено анонимно всем.")

# 🚀 Основная функция запуска
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT | filters.VOICE, handle_message))

    logger.info("🚀 Анонимный чат-бот запущен. Никто не знает автора.")

    # Запуск с обработкой прерываний (костыль для Replit)
    try:
        application.run_polling()
    except KeyboardInterrupt:
        logger.info("Бот остановлен вручную.")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        # Перезапуск через 5 секунд (костыль для стабильности)
        asyncio.run(asyncio.sleep(5))
        main()

if __name__ == '__main__':
    main()
