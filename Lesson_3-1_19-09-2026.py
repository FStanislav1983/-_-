# Программа с оконным интерфейсом

from tkinter import *
from tkinter import messagebox as mb
from tkinter import ttk
import requests
import json
import pprint
from datetime import date

url = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/"  # Адрес ФЗШ

base_currency = 'usd'  # Базовая валюта для формирования запроса
target_currency = 'rub'  # Целевая валюта для парсинга ответа от API
today = date.today()  # Сегодняшняя дата
formatted_date = today.strftime("%d-%m-%Y")  # Формат: ДД-ММ-ГГГГ

pp = pprint.PrettyPrinter(
    indent=4,  # Отступ для каждого уровня вложенности
    width=50,  # Максимальная ширина строки
    compact=False  # Не использовать компактное представление (без слияния коротких элементов)
)  # Создаём объект PrettyPrinter с настройками


def exchange():
    """Функция формирования запроса и парсинга данных для получения курса базовой валюты по отношению к целевой"""
    code = combobox.get().lower()  # Получение кода базовой валюты

    if code:  # Проверка заполнения поля
        try:
            url += f"{code.lower()}.json"  # Обработка адреса для запроса
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Проверяем, не произошла ли ошибка HTTP

            data = response.json()  # Преобразование строки JSON во вложенные структуры данных - словари, списки и т.д.
            pp.pprint(data)  # Вывод полученных данных в терминал
            if code in data[base_currency]:  # Парсинг данных и вывод результата в messagebox
                exchange_rate = data[base_currency][code]
                mb.showinfo("Курс обмена", f"Курс на {formatted_date}: \n1 USD = {exchange_rate:.2f} {code.upper()}")
            else:
                mb.showerror("Ошибка", f"Валюта {code} не найдена")
        # Обработка ошибок интернет-соединения
        except requests.exceptions.Timeout:
            mb.showerror("Ошибка", "Превышено время ожидания ответа от сервера")
        except requests.exceptions.ConnectionError:
            mb.showerror("Ошибка", "Не удалось установить соединение с сервером")
        except requests.exceptions.HTTPError as e:
            mb.showerror("Ошибка", f"HTTP ошибка: {e}")
    else:
        mb.showwarning("Внимание", "Выберите код валюты")


# Создание графического интерфейса
window = Tk()
window.title("Курс обмена валюты к USD")
window.geometry("360x180")

Label(text="Выберите код валюты:").pack(padx=10, pady=10)

# Список 10 популярных валют
popular_currencies = ["EUR", "JPY", "GBP", "AUD", "CAD", "CHF", "CNY", "RUB", "KZT", "UZS"]
combobox = ttk.Combobox(values=popular_currencies)
combobox.pack(padx=10, pady=10)

Button(text="Получить курс обмена к доллару", command=exchange).pack(padx=10, pady=10)

window.mainloop()
