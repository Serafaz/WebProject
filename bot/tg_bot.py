# Импортируем необходимые классы.
import logging
import datetime
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup
from news_for_bot.news import news
import random

TOKEN = '6138789109:AAGEK3zlOu1vXFGiTdFyob39JISZihig5SY'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


async def echo(update, context):
    await update.message.reply_text(update.message.text)


async def start_command(update, context):
    reply_keyboard = [['/start', '/help', '/news'], ['/rules', '/history', '/stop']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}! Я бот по нонограммам. Какая информация вам нужна?",
        reply_markup=markup
    )


async def help_command(update, context):
    await update.message.reply_text("Справка: \n"
                                    "Нонограмма - Японская головоломка (также японский кроссворд,"
                                    " японское рисование, нонограмма) — головоломка, в которой, в"
                                    " отличие от обычных кроссвордов, закодированы не слова,"
                                    " а изображение.")


async def news_command(update, context):
    await update.message.reply_text(f"Интересный факт: "
                                    f"А вы знали, что {random.choice(news)}")


async def rules_command(update, context):
    await update.message.reply_text(f"Правила: \n"
                                    f"Изображения закодированы числами, расположенными слева от"
                                    f" строк, а также сверху над столбцами. Количество чисел"
                                    f" показывает, сколько групп чёрных (либо своего цвета,"
                                    f" для цветных кроссвордов) клеток находятся в соответствующих"
                                    f" строке или столбце, а сами числа — сколько слитных клеток"
                                    f" содержит каждая из этих групп (например, набор из трёх"
                                    f" чисел — 4, 1, и 3 означает, что в этом ряду есть три"
                                    f" группы: первая — из четырёх, вторая — из одной,"
                                    f" третья — из трёх чёрных клеток). В чёрно-белом"
                                    f" кроссворде группы должны быть разделены, как минимум,"
                                    f" одной пустой клеткой, в цветном это правило касается"
                                    f" только одноцветных групп, а разноцветные группы могут"
                                    f" быть расположены вплотную (пустые клетки могут быть и"
                                    f" по краям рядов). Необходимо определить размещение групп"
                                    f" клеток.")


async def history_of_nonogramms_command(update, context):
    await update.message.reply_text(f"История Нонограмм: \n"
                                    f"...")


async def stop_command(update, context):
    await update.message.reply_text('Прощайте. Если будут вопросы, то обращайтесь!')
    return


def main():
    application = Application.builder().token(TOKEN).build()
    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, start_command)
    application.add_handler(text_handler)
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("news", news_command))
    application.add_handler(CommandHandler("rules", rules_command))
    application.add_handler(CommandHandler("history", history_of_nonogramms_command))
    application.add_handler(CommandHandler("stop", stop_command))
    application.run_polling()


if __name__ == '__main__':
    main()
