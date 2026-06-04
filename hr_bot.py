import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

TOKEN = "8681422276:AAEZfFD91XtPVUJxvf5jpw4rCei-o_sKd9U"
ADMIN_CHAT_ID = 941204658  # ваш chat_id

logging.basicConfig(level=logging.INFO)

# Шаги диалога
(CONSENT, CITIZENSHIP, WORK_PERMIT, GENDER, AGE,
 JOB_TYPE, CRIMINAL, MED_BOOK, FIO, CONTACT) = range(10)

def kb(options):
    return ReplyKeyboardMarkup([[o] for o in options], resize_keyboard=True, one_time_keyboard=True)

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    await update.message.reply_text(
        "👋 Здравствуйте!\n\n"
        "Я помогу подобрать подходящую работу. Задам несколько коротких вопросов — "
        "это займёт около 2 минут.\n\n"
        "📋 Для продолжения необходимо ваше согласие на обработку персональных данных "
        "в соответствии с Федеральным законом №152-ФЗ «О персональных данных».\n\n"
        "Ваши данные используются исключительно для подбора вакансий и не передаются третьим лицам.\n\n"
        "Вы согласны?",
        reply_markup=kb(["✅ Согласен(на)", "❌ Не согласен(на)"])
    )
    return CONSENT

async def consent(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ Не согласен(на)":
        await update.message.reply_text(
            "Без согласия на обработку персональных данных мы не можем продолжить.\n\n"
            "Если передумаете — напишите /start.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    await update.message.reply_text(
        "✅ Спасибо! Согласие получено.\n\n"
        "🌍 Ваше гражданство?",
        reply_markup=kb(["🇷🇺 РФ", "🌐 Другое"])
    )
    return CITIZENSHIP

async def citizenship(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data['citizenship'] = update.message.text
    if update.message.text == "🌐 Другое":
        await update.message.reply_text(
            "📋 Есть ли у вас разрешение на работу в РФ?",
            reply_markup=kb(["✅ Да, есть", "❌ Нет"])
        )
        return WORK_PERMIT
    else:
        ctx.user_data['work_permit'] = "—"
        await update.message.reply_text(
            "👤 Ваш пол?",
            reply_markup=kb(["Мужчина", "Женщина"])
        )
        return GENDER

async def work_permit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data['work_permit'] = update.message.text
    await update.message.reply_text(
        "👤 Ваш пол?",
        reply_markup=kb(["Мужчина", "Женщина"])
    )
    return GENDER

async def gender(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data['gender'] = update.message.text
    await update.message.reply_text(
        "🎂 Сколько вам лет? Введите цифру:",
        reply_markup=ReplyKeyboardRemove()
    )
    return AGE

async def age(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message.text.isdigit():
        await update.message.reply_text("Пожалуйста, введите возраст цифрами (например: 25)")
        return AGE
    ctx.user_data['age'] = update.message.text
    await update.message.reply_text(
        "💼 Какой вид работы вас интересует?",
        reply_markup=kb(["Вахта", "Курьер", "Другая подработка"])
    )
    return JOB_TYPE

async def job_type(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data['job_type'] = update.message.text
    await update.message.reply_text(
        "📜 Есть ли у вас судимость?",
        reply_markup=kb(["Нет", "Да"])
    )
    return CRIMINAL

async def criminal(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data['criminal'] = update.message.text
    await update.message.reply_text(
        "🏥 Есть ли у вас медицинская книжка?",
        reply_markup=kb(["✅ Да, есть", "❌ Нет"])
    )
    return MED_BOOK

async def med_book(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data['med_book'] = update.message.text
    await update.message.reply_text(
        "✍️ Введите ваше ФИО:",
        reply_markup=ReplyKeyboardRemove()
    )
    return FIO

async def fio(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data['fio'] = update.message.text
    await update.message.reply_text(
        "📱 Введите номер телефона или ваш никнейм в Telegram\n"
        "Например: +79001234567 или @username"
    )
    return CONTACT

async def contact(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data['contact'] = update.message.text
    d = ctx.user_data
    user = update.effective_user

    citizenship_line = f"🌍 Гражданство: {d.get('citizenship', '—')}"
    permit_line = ""
    if d.get('citizenship') == "🌐 Другое":
        permit_line = f"\n📋 Разрешение на работу: {d.get('work_permit', '—')}"

    msg = (
        f"📋 <b>Новая анкета</b>\n"
        f"{'─' * 25}\n"
        f"👤 Telegram: @{user.username or '—'} (ID: {user.id})\n"
        f"{'─' * 25}\n"
        f"{citizenship_line}{permit_line}\n"
        f"⚧ Пол: {d.get('gender', '—')}\n"
        f"🎂 Возраст: {d.get('age', '—')}\n"
        f"💼 Работа: {d.get('job_type', '—')}\n"
        f"📜 Судимость: {d.get('criminal', '—')}\n"
        f"🏥 Медкнижка: {d.get('med_book', '—')}\n"
        f"{'─' * 25}\n"
        f"✍️ ФИО: {d.get('fio', '—')}\n"
        f"📱 Контакт: {d.get('contact', '—')}"
    )

    await ctx.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=msg,
        parse_mode="HTML"
    )

    await update.message.reply_text(
        "✅ Отлично! Ваша анкета отправлена.\n\n"
        "HR-специалист свяжется с вами в ближайшее время. Спасибо! 🙏"
    )
    return ConversationHandler.END

async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Анкета отменена. Напишите /start чтобы начать заново.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CONSENT:     [MessageHandler(filters.TEXT & ~filters.COMMAND, consent)],
            CITIZENSHIP: [MessageHandler(filters.TEXT & ~filters.COMMAND, citizenship)],
            WORK_PERMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, work_permit)],
            GENDER:      [MessageHandler(filters.TEXT & ~filters.COMMAND, gender)],
            AGE:         [MessageHandler(filters.TEXT & ~filters.COMMAND, age)],
            JOB_TYPE:    [MessageHandler(filters.TEXT & ~filters.COMMAND, job_type)],
            CRIMINAL:    [MessageHandler(filters.TEXT & ~filters.COMMAND, criminal)],
            MED_BOOK:    [MessageHandler(filters.TEXT & ~filters.COMMAND, med_book)],
            FIO:         [MessageHandler(filters.TEXT & ~filters.COMMAND, fio)],
            CONTACT:     [MessageHandler(filters.TEXT & ~filters.COMMAND, contact)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv)
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
