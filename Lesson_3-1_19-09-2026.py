# Программа с оконным интерфейсом

from tkinter import *
from tkinter import messagebox as mb
from tkinter import ttk
import requests
import json
from datetime import date

url = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/usd.json"

base_currency = 'usd'
target_currency = 'rub'
today = date.today()
formatted_date = today.strftime("%d-%m-%Y")  # Формат: ДД-ММ-ГГГГ


def exchange():
    code = combobox.get().lower()

    if code:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Проверяем, не произошла ли ошибка HTTP

            data = response.json()
            print(data)
            if code in data[base_currency]:
                exchange_rate = data[base_currency][code]
                mb.showinfo("Курс обмена", f"Курс на {formatted_date}: \n1 USD = {exchange_rate:.2f} {code.upper()}")
            else:
                mb.showerror("Ошибка", f"Валюта {code} не найдена")

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
