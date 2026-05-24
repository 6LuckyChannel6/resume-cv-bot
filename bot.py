from __future__ import annotations

import asyncio
import hashlib
import logging
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from aiohttp import web
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from cv_generator import CVData, TEMPLATES, generate_cv_pdf, split_items
from translator import build_translations


UI_LANGUAGE, TEMPLATE, PHOTO = range(3)
FIELD_OFFSET = 3

DATA_DIR = Path("data")
BASE_DIR = Path(__file__).resolve().parent

LANGUAGE_BUTTONS = [["Қазақша", "Русский", "English"]]
LANGUAGE_BY_LABEL = {
    "қазақша": "kk",
    "казахский": "kk",
    "kazakh": "kk",
    "kk": "kk",
    "русский": "ru",
    "russian": "ru",
    "ru": "ru",
    "english": "en",
    "английский": "en",
    "en": "en",
}

TEMPLATE_LABELS = {
    "kk": {
        "gray": "Сұр",
        "neon": "Неон",
        "brown": "Қоңыр",
        "navy": "Көк",
    },
    "ru": {
        "gray": "Серый",
        "neon": "Неон",
        "brown": "Коричневый",
        "navy": "Темно-синий",
    },
    "en": {
        "gray": "Gray",
        "neon": "Neon",
        "brown": "Brown",
        "navy": "Navy",
    },
}
TEMPLATE_BY_LABEL = {
    label.lower(): key
    for language_labels in TEMPLATE_LABELS.values()
    for key, label in language_labels.items()
}
TEMPLATE_BY_LABEL.update({label.lower(): key for key, label in TEMPLATES.items()})

TEXT = {
    "choose_language": (
        "Интерфейс тілін таңдаңыз.\n"
        "Выберите язык интерфейса.\n"
        "Choose interface language."
    ),
    "choose_language_error": (
        "Тілді батырма арқылы таңдаңыз: Қазақша, Русский немесе English.\n"
        "Выберите язык кнопкой: Қазақша, Русский или English.\n"
        "Choose a language using the button: Қазақша, Русский or English."
    ),
    "template_intro": {
        "kk": "Сәлем! Мен деректерді жинап, қазақша, орысша және ағылшынша PDF-резюме жасаймын.\n\nШаблон таңдаңыз:",
        "ru": "Привет! Я соберу данные и отправлю PDF-резюме на казахском, русском и английском.\n\nВыбери шаблон:",
        "en": "Hi! I will collect your details and send one PDF resume in Kazakh, Russian and English.\n\nChoose a template:",
    },
    "template_placeholder": {
        "kk": "Шаблон таңдаңыз",
        "ru": "Выберите шаблон",
        "en": "Choose a template",
    },
    "template_error": {
        "kk": "Шаблонды батырма арқылы таңдаңыз: Сұр, Неон, Қоңыр немесе Көк.",
        "ru": "Выбери шаблон кнопкой: Серый, Неон, Коричневый или Темно-синий.",
        "en": "Choose a template using the button: Gray, Neon, Brown or Navy.",
    },
    "photo_prompt": {
        "kk": "Енді резюме үшін фото жібере аласыз.\nФото қажет болмаса, /skip жіберіңіз.",
        "ru": "Теперь можешь отправить свое фото для резюме.\nЕсли фото не нужно, отправь /skip.",
        "en": "Now you can send your photo for the resume.\nIf you do not need a photo, send /skip.",
    },
    "photo_invalid": {
        "kk": "Фотоны сурет ретінде жіберіңіз немесе /skip жазыңыз.",
        "ru": "Отправь фото изображением или напиши /skip.",
        "en": "Send a photo as an image or type /skip.",
    },
    "photo_added": {
        "kk": "Фото қосылды.",
        "ru": "Фото добавлено.",
        "en": "Photo added.",
    },
    "photo_skipped": {
        "kk": "Жақсы, резюме фотосыз жасалады.",
        "ru": "Ок, сделаю резюме без фото.",
        "en": "Ok, I will create the resume without a photo.",
    },
    "translating": {
        "kk": "Мәтінді 3 тілге аударып, PDF жинап жатырмын...",
        "ru": "Перевожу текст на 3 языка и собираю PDF...",
        "en": "Translating the text into 3 languages and building the PDF...",
    },
    "done_caption": {
        "kk": "Дайын. PDF ішінде үш автоматты аударылған нұсқа бар: қазақша, русский және English.",
        "ru": "Готово. В PDF три автоматически переведенные версии: қазақша, русский и English.",
        "en": "Done. The PDF contains three automatically translated versions: Kazakh, Russian and English.",
    },
    "cancel": {
        "kk": "Жақсы, резюме жасау тоқтатылды. Қайта бастау үшін /start жіберіңіз.",
        "ru": "Ок, создание резюме отменено. Чтобы начать заново, отправь /start.",
        "en": "Ok, resume creation is cancelled. Send /start to begin again.",
    },
    "help": {
        "kk": "Командалар:\n/start - жаңа резюме жасау\n/skip - фотоны өткізіп жіберу\n/cancel - ағымдағы диалогты тоқтату\n/help - көмек\n\nБот интерфейсті қазақша, орысша немесе ағылшынша көрсетеді, мәтінді 3 тілге аударады және PDF жібереді.",
        "ru": "Команды:\n/start - создать новое резюме\n/skip - пропустить фото\n/cancel - отменить текущий диалог\n/help - помощь\n\nБот показывает интерфейс на казахском, русском или английском, переводит текст на 3 языка и отправляет PDF.",
        "en": "Commands:\n/start - create a new resume\n/skip - skip the photo\n/cancel - cancel the current dialog\n/help - help\n\nThe bot shows the interface in Kazakh, Russian or English, translates text into 3 languages and sends a PDF.",
    },
}

FIELD_FLOW = [
    (
        "full_name",
        {
            "kk": "Толық аты-жөніңізді жазыңыз.\nМысалы: Қасмұхан Абзал Ерболатұлы",
            "ru": "ФИО полностью.\nНапример: Қасмұхан Абзал Ерболатұлы",
            "en": "Enter your full name.\nExample: Qasmukhan Abzal Erbolatuly",
        },
        False,
    ),
    (
        "degree_program",
        {
            "kk": "Білім беру бағдарламасы / мамандығы.\nМысалы: 6B06103 - Ақпараттық жүйелер архитектурасы",
            "ru": "Образовательная программа / специальность.\nНапример: 6B06103 - Архитектура информационных систем",
            "en": "Educational program / major.\nExample: 6B06103 - Information Systems Architecture",
        },
        False,
    ),
    (
        "current_education",
        {
            "kk": "Қазіргі біліміңізді қысқаша жазыңыз: қала, университет, факультет, курс.",
            "ru": "Кратко опиши текущее образование: город, университет, факультет, курс.",
            "en": "Briefly describe your current education: city, university, faculty, year of study.",
        },
        False,
    ),
    ("birth_date", {"kk": "Туған күніңіз.", "ru": "Дата рождения.", "en": "Date of birth."}, False),
    ("city", {"kk": "Қала және мекенжай.", "ru": "Город и адрес.", "en": "City and address."}, False),
    (
        "marital_status",
        {"kk": "Отбасылық жағдайыңыз.", "ru": "Семейное положение.", "en": "Marital status."},
        False,
    ),
    ("phone", {"kk": "Телефон нөміріңіз.", "ru": "Телефон.", "en": "Phone number."}, False),
    ("email", {"kk": "Электрондық пошта.", "ru": "Электронная почта.", "en": "Email address."}, False),
    (
        "experience",
        {
            "kk": "Жұмыс тәжірибесі немесе оқу практикасы: лауазым, мерзім, қала, ұйым. Бірнеше жолмен жазуға болады.",
            "ru": "Опыт работы или учебная практика: должность, даты, город, организация. Можно несколькими строками.",
            "en": "Work experience or internship: role, dates, city, organization. You may use multiple lines.",
        },
        False,
    ),
    (
        "education_details",
        {
            "kk": "Білімі толық: бағдарлама, бітіру уақыты, оқу формасы, университет, GPA. Бірнеше жолмен жазуға болады.",
            "ru": "Образование подробно: программа, дата окончания, форма обучения, университет, GPA. Можно несколькими строками.",
            "en": "Education details: program, graduation date, study format, university, GPA. You may use multiple lines.",
        },
        False,
    ),
    (
        "additional_education",
        {
            "kk": "Қосымша білім, тренингтер және курстар. Егер жоқ болса, сызықша жіберіңіз: -",
            "ru": "Дополнительное образование, тренинги и курсы. Если нет, отправь прочерк: -",
            "en": "Additional education, trainings and courses. If none, send a dash: -",
        },
        False,
    ),
    (
        "qualification",
        {
            "kk": "Біліктілік. Егер жоқ болса, сызықша жіберіңіз: -",
            "ru": "Квалификация. Если нет, отправь прочерк: -",
            "en": "Qualification. If none, send a dash: -",
        },
        False,
    ),
    (
        "professional_skills",
        {
            "kk": "Кәсіби дағдылар. Үтір арқылы немесе жаңа жолмен жазыңыз.",
            "ru": "Профессиональные навыки. Пиши через запятую или с новой строки.",
            "en": "Professional skills. Separate them with commas or new lines.",
        },
        True,
    ),
    (
        "personal_qualities",
        {
            "kk": "Жеке қасиеттер. Үтір арқылы немесе жаңа жолмен жазыңыз.",
            "ru": "Личные качества. Пиши через запятую или с новой строки.",
            "en": "Personal qualities. Separate them with commas or new lines.",
        },
        True,
    ),
    (
        "achievements",
        {
            "kk": "Жетістіктер. Үтір арқылы немесе жаңа жолмен жазыңыз.",
            "ru": "Достижения. Пиши через запятую или с новой строки.",
            "en": "Achievements. Separate them with commas or new lines.",
        },
        True,
    ),
    (
        "additional_info",
        {
            "kk": "Қосымша ақпарат. Үтір арқылы немесе жаңа жолмен жазыңыз. Егер жоқ болса, сызықша жіберіңіз: -",
            "ru": "Дополнительная информация. Пиши через запятую или с новой строки. Если нет, отправь прочерк: -",
            "en": "Additional information. Separate with commas or new lines. If none, send a dash: -",
        },
        True,
    ),
]


logging.basicConfig(
    format="%(asctime)s %(name)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        TEXT["choose_language"],
        reply_markup=ReplyKeyboardMarkup(
            LANGUAGE_BUTTONS,
            resize_keyboard=True,
            one_time_keyboard=True,
            input_field_placeholder="Қазақша / Русский / English",
        ),
    )
    return UI_LANGUAGE


async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    language = LANGUAGE_BY_LABEL.get(update.message.text.strip().lower())
    if not language:
        await update.message.reply_text(TEXT["choose_language_error"])
        return UI_LANGUAGE

    context.user_data["ui_lang"] = language
    await update.message.reply_text(
        _t("template_intro", language),
        reply_markup=ReplyKeyboardMarkup(
            _template_buttons(language),
            resize_keyboard=True,
            one_time_keyboard=True,
            input_field_placeholder=_t("template_placeholder", language),
        ),
    )
    return TEMPLATE


async def choose_template(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    language = _ui_lang(context)
    template = TEMPLATE_BY_LABEL.get(update.message.text.strip().lower())
    if not template:
        await update.message.reply_text(_t("template_error", language))
        return TEMPLATE

    context.user_data["template"] = template
    await update.message.reply_text(
        _t("photo_prompt", language),
        reply_markup=ReplyKeyboardRemove(),
    )
    return PHOTO


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    language = _ui_lang(context)
    if not update.message.photo:
        await update.message.reply_text(_t("photo_invalid", language))
        return PHOTO

    user_dir = DATA_DIR / "photos" / str(update.effective_user.id)
    user_dir.mkdir(parents=True, exist_ok=True)
    photo_file = await update.message.photo[-1].get_file()
    photo_path = user_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    await photo_file.download_to_drive(photo_path)
    context.user_data["photo_path"] = str(photo_path)

    await update.message.reply_text(f"{_t('photo_added', language)}\n\n{_field_prompt(0, language)}")
    return _field_state(0)


async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    language = _ui_lang(context)
    context.user_data["photo_path"] = None
    await update.message.reply_text(f"{_t('photo_skipped', language)}\n\n{_field_prompt(0, language)}")
    return _field_state(0)


async def field_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    language = _ui_lang(context)
    field_index = _current_field_index(context)
    key, _prompts, is_list = FIELD_FLOW[field_index]
    raw_text = update.message.text.strip()

    context.user_data[key] = split_items(raw_text) if is_list else raw_text

    next_index = field_index + 1
    if next_index >= len(FIELD_FLOW):
        return await finish(update, context)

    context.user_data["field_index"] = next_index
    await update.message.reply_text(_field_prompt(next_index, language))
    return _field_state(next_index)


async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    language = _ui_lang(context)
    await update.message.reply_text(_t("translating", language))
    await update.message.chat.send_action(ChatAction.UPLOAD_DOCUMENT)
    pdf_path = await asyncio.to_thread(
        _build_pdf,
        dict(context.user_data),
        update.effective_user.id,
    )

    with pdf_path.open("rb") as pdf_file:
        await update.message.reply_document(
            document=pdf_file,
            filename=pdf_path.name,
            caption=_t("done_caption", language),
            reply_markup=ReplyKeyboardRemove(),
        )

    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    language = _ui_lang(context)
    context.user_data.clear()
    await update.message.reply_text(
        _t("cancel", language),
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(_t("help", _ui_lang(context)))


def _build_pdf(user_data: dict, user_id: int) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = DATA_DIR / f"cv_{user_id}_{timestamp}.pdf"

    cv = CVData(
        full_name=user_data["full_name"],
        degree_program=user_data["degree_program"],
        current_education=user_data["current_education"],
        birth_date=user_data["birth_date"],
        city=user_data["city"],
        marital_status=user_data["marital_status"],
        phone=user_data["phone"],
        email=user_data["email"],
        experience=user_data["experience"],
        education_details=user_data["education_details"],
        additional_education=user_data["additional_education"],
        qualification=user_data["qualification"],
        professional_skills=user_data["professional_skills"],
        personal_qualities=user_data["personal_qualities"],
        achievements=user_data["achievements"],
        additional_info=user_data["additional_info"],
        photo_path=user_data.get("photo_path"),
        template=user_data.get("template", "gray"),
    )
    cv.translations = build_translations(cv)
    return generate_cv_pdf(cv, output_path)


def _field_state(index: int) -> int:
    return FIELD_OFFSET + index


def _current_field_index(context: ContextTypes.DEFAULT_TYPE) -> int:
    return int(context.user_data.get("field_index", 0))


def _ui_lang(context: ContextTypes.DEFAULT_TYPE) -> str:
    return str(context.user_data.get("ui_lang", "ru"))


def _t(key: str, language: str) -> str:
    value = TEXT[key]
    if isinstance(value, dict):
        return value.get(language, value["ru"])
    return value


def _field_prompt(index: int, language: str) -> str:
    return FIELD_FLOW[index][1].get(language, FIELD_FLOW[index][1]["ru"])


def _template_buttons(language: str) -> list[list[str]]:
    labels = TEMPLATE_LABELS.get(language, TEMPLATE_LABELS["ru"])
    return [
        [labels["gray"], labels["neon"]],
        [labels["brown"], labels["navy"]],
    ]


def build_application(token: str) -> Application:
    app = Application.builder().token(token).build()

    field_states = {
        _field_state(index): [MessageHandler(filters.TEXT & ~filters.COMMAND, field_answer)]
        for index in range(len(FIELD_FLOW))
    }
    conversation = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            UI_LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_language)],
            TEMPLATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_template)],
            PHOTO: [
                MessageHandler(filters.PHOTO, photo),
                CommandHandler("skip", skip_photo),
                MessageHandler(filters.TEXT & ~filters.COMMAND, photo),
            ],
            **field_states,
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conversation)
    app.add_handler(CommandHandler("help", help_command))
    return app


def main() -> None:
    load_dotenv(BASE_DIR / ".env")
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is not set. Create .env from .env.example.")

    DATA_DIR.mkdir(exist_ok=True)
    logger.info("Starting CV bot")
    application = build_application(token)
    if _should_use_webhook():
        asyncio.run(_run_webhook(application, token))
    else:
        application.run_polling(allowed_updates=Update.ALL_TYPES)


def _should_use_webhook() -> bool:
    return bool(
        os.getenv("WEBHOOK_URL")
        or os.getenv("KOYEB_PUBLIC_DOMAIN")
        or os.getenv("RENDER_EXTERNAL_URL")
    )


async def _run_webhook(application: Application, token: str) -> None:
    port = int(os.getenv("PORT", "8000"))
    render_url = os.getenv("RENDER_EXTERNAL_URL", "").rstrip("/")
    public_domain = os.getenv("KOYEB_PUBLIC_DOMAIN")
    webhook_secret = os.getenv("WEBHOOK_SECRET") or hashlib.sha256(token.encode()).hexdigest()[:32]
    webhook_path = f"/telegram/{webhook_secret}"
    webhook_url = (
        os.getenv("WEBHOOK_URL")
        or (f"{render_url}{webhook_path}" if render_url else f"https://{public_domain}{webhook_path}")
    )

    if not webhook_url.startswith("https://"):
        raise RuntimeError("WEBHOOK_URL must start with https://")

    await application.initialize()
    await application.start()
    await application.bot.set_webhook(
        url=webhook_url,
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
        secret_token=webhook_secret,
    )

    async def health(_request: web.Request) -> web.Response:
        return web.Response(text="ok")

    async def telegram_webhook(request: web.Request) -> web.Response:
        if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != webhook_secret:
            return web.Response(status=403, text="forbidden")
        payload = await request.json()
        update = Update.de_json(payload, application.bot)
        await application.process_update(update)
        return web.Response(text="ok")

    server = web.Application()
    server.router.add_get("/", health)
    server.router.add_get("/health", health)
    server.router.add_post(webhook_path, telegram_webhook)
    runner = web.AppRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info("Webhook server started on port %s", port)

    try:
        await asyncio.Event().wait()
    finally:
        await runner.cleanup()
        await application.stop()
        await application.shutdown()


if __name__ == "__main__":
    main()
