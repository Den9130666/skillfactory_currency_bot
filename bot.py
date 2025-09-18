import telebot
from config import TOKEN
from extensions import APIException, CurrencyConverter, VALUES

bot = telebot.TeleBot(TOKEN)


def help_text() -> str:
    return (
        "Отправьте: <валюта_из> <валюта_в> <количество>\n"
        "Пример: доллар евро 10\n"
        "Команды: /start /help /values"
    )


@bot.message_handler(commands=["start", "help"])
def cmd_help(message: telebot.types.Message):
    bot.reply_to(message, help_text())


@bot.message_handler(commands=["values"])
def cmd_values(message: telebot.types.Message):
    groups = {
        "USD": [],
        "EUR": [],
        "RUB": [],
    }
    for k, v in VALUES.items():
        groups[v].append(k)
    lines = [
        f"USD: {', '.join(groups['USD'])}",
        f"EUR: {', '.join(groups['EUR'])}",
        f"RUB: {', '.join(groups['RUB'])}",
    ]
    bot.reply_to(message, "\n".join(lines))


@bot.message_handler(content_types=["text"])
def handle_convert(message: telebot.types.Message):
    try:
        parts = message.text.split()
        if len(parts) != 3:
            raise APIException("Нужно три параметра: <валюта_из> <валюта_в> <количество>")

        base, quote, amount = parts
        total = CurrencyConverter.get_price(base, quote, amount)
        bot.reply_to(message, f"{amount} {base} → {quote}: {total:.4f}")

    except APIException as e:
        bot.reply_to(message, f"Ошибка: {e}")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {type(e).__name__}: {e}")


if __name__ == "__main__":
    bot.polling(none_stop=True)