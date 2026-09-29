# Отладка функции получения данных от API

import requests
import json
import pprint

# url = "https://open.er-api.com/v6/latest/USD"  # Превышено время ожидания ответа от сервера
# url_history = "https://v6.exchangerate-api.com/v6/YOUR-API-KEY/history/USD/YEAR/MONTH/DAY"
# url = "https://api.frankfurter.dev/v2/?base=USD"  # — с указанием базы (USD)
# https://api.frankfurter.dev/v2/rate/USD/RUB — конкретная пара
# url = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/eur.json"
# url_history = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@2026-09-10/v1/currencies/eur.json"

pp = pprint.PrettyPrinter(
    indent=4,  # Отступ для каждого уровня вложенности
    width=50,  # Максимальная ширина строки
    compact=False  # Не использовать компактное представление (без слияния коротких элементов)
)  # Создаём объект PrettyPrinter с настройками


def get_exchange_rate(base_cur: str, target_cur: str):
    """Функция получения данных от двух различных API с целью определения более стабильного соединения"""
    url_er = f"https://open.er-api.com/v6/latest/{base_cur}"  # URL первого API
    url_cdn = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/" \
              f"v1/currencies/{base_cur.lower()}.json"  # URL второго API
    try:  # Пробуем получить ответ от первого API
        resp = requests.get(url_er, timeout=10)
        resp.raise_for_status()  # выбросит ошибку для HTTP-кодов 4xx/5xx
        payload = resp.json()  # Преобразование строки JSON во вложенные структуры данных - словари, списки и т.д.

        # У open.er-api структура: payload['rates'][target_currency]
        if "rates" in payload and target_cur in payload["rates"]:
            print(f"Данные с ресурса {url_er} загружены")
            pp.pprint(payload)  # Вывод полученных данных в терминал
            data = payload["rates"][target_cur]
        else:
            raise ValueError(f"Целевая валюта не найдена в ответе первого API")
    except Exception as e1:
        try:  # Если первый не сработал — пробуем второй API
            print(f"Ошибка при ожидании ответа от {url_er}:\n{e1}")
            resp = requests.get(url_cdn, timeout=10)
            resp.raise_for_status()
            payload = resp.json()
            base_cur = base_cur.lower()  # Преобразование текста в нижний регистр
            target_cur = target_cur.lower()  # Преобразование текста в нижний регистр

            # У currency-api структура: payload[base_currency][target_currency]
            if base_cur in payload and target_cur in payload[base_cur]:
                print(f"Данные с ресурса {url_cdn} загружены")
                pp.pprint(payload)  # Вывод полученных данных в терминал
                data = payload[base_cur][target_cur]
            else:
                raise ValueError(f"{e1}\nЦелевая валюта не найдена в ответе второго API")
        except Exception as e2:  # Если оба не сработали — можно либо пробросить ошибку, либо вернуть None
            print(f"Не удалось получить курс: {e2}")
            return None

    return data


# Пример использования
base_currency = "USD"  # Базовая валюта
target_currency = "RUB"  # Целевая валюта

rate_data = get_exchange_rate(base_currency, target_currency)

if rate_data is not None:
    pp.pprint(rate_data)
else:
    print("Курс не удалось получить ни из одного источника.")
