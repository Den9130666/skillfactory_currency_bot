import requests


# Допустимые имена валют и их коды
VALUES = {
    "usd": "USD", "доллар": "USD", "доллара": "USD", "долларов": "USD",
    "eur": "EUR", "евро": "EUR",
    "rub": "RUB", "руб": "RUB", "рубль": "RUB", "рубля": "RUB", "рублей": "RUB", "рубли": "RUB",
}


class APIException(Exception):
    """Исключения по вине пользователя (неверная валюта/количество и т.д.)."""
    pass


class CurrencyConverter:
    """Статический конвертер для USD/EUR/RUB на базе API ЦБ РФ (latest.js)."""

    CBR_URL = "https://www.cbr-xml-daily.ru/latest.js"  # база — RUB

    @staticmethod
    def _fetch_rates() -> dict:
        """
        Забираем словарь rates (курсы к RUB) из ЦБ.
        Пример: {"USD": 0.0109, "EUR": 0.0101, ...} — это RUB base? Нет.
        В latest.js база — RUB, а значения — курс ИНОСТР к RUB? Наоборот:
        В latest.js поле 'rates' содержит отношение валюты к RUB (сколько валюты за 1 RUB).
        Документация: 1 RUB = rates["USD"] USD.
        Следовательно: USD_RUB = 1 / rates["USD"]; EUR_RUB = 1 / rates["EUR"].
        """
        r = requests.get(CurrencyConverter.CBR_URL, timeout=10)
        r.raise_for_status()
        data = r.json()  # используем JSON из задания
        return data["rates"]

    @staticmethod
    def get_price(base: str, quote: str, amount: str) -> float:
        """
        Возвращает сумму в валюте 'quote' за 'amount' единиц валюты 'base'.
        Работает только с USD/EUR/RUB, как требует задание.
        """
        if not (base and quote and amount):
            raise APIException("Нужно три параметра: <валюта_из> <валюта_в> <количество>")

        base = base.lower().strip()
        quote = quote.lower().strip()

        if base not in VALUES:
            raise APIException(f"Неизвестная валюта: {base}")
        if quote not in VALUES:
            raise APIException(f"Неизвестная валюта: {quote}")

        base_code = VALUES[base]
        quote_code = VALUES[quote]

        if base_code == quote_code:
            raise APIException("Нельзя переводить одинаковые валюты")

        # число
        try:
            amount_val = float(amount.replace(",", "."))
        except ValueError:
            raise APIException("Количество должно быть числом")

        # получаем курсы к RUB
        rates = CurrencyConverter._fetch_rates()

        # latest.js хранит курс как: 1 RUB = rates["USD"] USD
        # Значит USD_RUB = 1 / rates["USD"], EUR_RUB = 1 / rates["EUR"]
        def to_rub(code: str) -> float:
            if code == "RUB":
                return 1.0
            if code not in rates:
                raise APIException("Не удалось получить курс")
            return 1.0 / float(rates[code])

        # Посчитаем коэффициент base->quote через RUB
        base_to_rub = to_rub(base_code)
        quote_to_rub = to_rub(quote_code)

        # base -> RUB -> quote  =>  (amount * base_to_rub) / quote_to_rub
        result = (amount_val * base_to_rub) / quote_to_rub
        return result