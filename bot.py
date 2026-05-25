import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
PUBLIC_URL = os.environ["PUBLIC_URL"].rstrip("/")
PORT = int(os.environ.get("PORT", "10000"))

SCREEN_TEXTS = {
    "start_screen": (
        "Здравствуйте 👋\n"
        "Это тестовый бот на Render.\n\n"
        "Выберите нужный раздел ниже."
    ),
    "faq_screen": "Здесь собраны шаблоны ответов на частые вопросы.",
    "objections_screen": "Здесь собраны ответы на возражения.",
    "followup_screen": "Здесь собраны сообщения, чтобы напомнить о себе клиенту.",
    "about_screen": "Это тестовая Render-версия бота.",
    "faq_price": (
        "Варианты ответа клиенту:\n\n"
        "1) Стоимость зависит от выбранной услуги. Напишите, пожалуйста, что именно вас интересует.\n\n"
        "2) Здравствуйте 🌷 С удовольствием подскажу. Напишите, какая именно услуга вас интересует."
    ),
    "obj_expensive": (
        "Варианты ответа на возражение:\n\n"
        "1) Понимаю вас. Могу подсказать, какой вариант будет комфортнее по бюджету.\n\n"
        "2) Понимаю вас 🌷 Если хотите, помогу подобрать более подходящий вариант."
    ),
    "followup_after_price": (
        "Варианты сообщения:\n\n"
        "1) Здравствуйте. Подскажите, пожалуйста, ещё актуален ли для вас вопрос по записи?\n\n"
        "2) Здравствуйте 🌷 Если для вас ещё актуально, я могу помочь с записью."
    ),
}

SCREEN_BUTTONS = {
    "start_screen": [
        [("Частые вопросы", "faq_screen"), ("Возражения", "objections_screen")],
        [("Напомнить о себе", "followup_screen"), ("О боте", "about_screen")],
    ],
    "faq_screen": [
        [("Цена", "faq_price")],
        [("В меню", "start_screen")],
    ],
    "objections_screen": [
        [("Дорого", "obj_expensive")],
        [("В меню", "start_screen")],
    ],
    "followup_screen": [
        [("Пропал после цены", "followup_after_price")],
        [("В меню", "start_screen")],
    ],
    "about_screen": [
        [("В меню", "start_screen")],
    ],
    "faq_price": [
        [("Назад к FAQ", "faq_screen"), ("В меню", "start_screen")],
    ],
    "obj_expensive": [
        [("Назад к возражениям", "objections_screen"), ("В меню", "start_screen")],
    ],
    "followup_after_price": [
        [("Назад к напоминанию", "followup_screen"), ("В меню", "start_screen")],
    ],
}

BUTTON_TO_SCREEN = {}
for screen_id, rows in SCREEN_BUTTONS.items():
    for row in rows:
        for button_text, target_screen in row:
            BUTTON_TO_SCREEN[button_text] = target_screen


def build_keyboard(screen_id: str) -> ReplyKeyboardMarkup:
    rows = SCREEN_BUTTONS.get(screen_id, [])
    keyboard = []
    for row in rows:
        keyboard.append([KeyboardButton(button_text) for button_text, _ in row])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def show_screen(update: Update, screen_id: str) -> None:
    text = SCREEN_TEXTS.get(screen_id, "Экран пока не найден.")
    keyboard = build_keyboard(screen_id)
    await update.message.reply_text(text, reply_markup=keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await show_screen(update, "start_screen")


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await show_screen(update, "start_screen")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text

    if text in BUTTON_TO_SCREEN:
        await show_screen(update, BUTTON_TO_SCREEN[text])
        return

    await update.message.reply_text(
        "Пока я понимаю только кнопки меню. Выберите нужный раздел ниже.",
        reply_markup=build_keyboard("start_screen"),
    )


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"{PUBLIC_URL}/{TOKEN}",
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()