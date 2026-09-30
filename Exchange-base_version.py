# TODO: Добавьте в проект, разработанный на уроке, вторую базовую валюту,
#       чтобы он выводил сразу два курса обмена одновременно.
#       Получайте данные в формате JSON.
#       Добавьте еще одно поле для выбора второй базовой валюты.
#       Измените функцию exchange так, чтобы она запрашивала и отображала курсы обмена для обеих базовых валют
#       относительно выбранной целевой валюты.
#       При выполнении домашнего задания используйте Git и сделайте не менее трех коммитов.

import tkinter as tk  # Подключение библиотеки Tkinter для создания графических пользовательских интерфейсов (GUI)
from tkinter import Button
from tkinter import ttk  # Модуль ttk с набором тематических виджетов (Combobox, Notebook, Progressbar, Treeview)
from PIL import Image, ImageTk  # Для работы с изображениями загружаем модули из библиотеки Pillow
from tkinter import messagebox as mb  # Модуль для отображения всплывающих окон с сообщениями пользователю
from datetime import datetime  # Загрузка класса модуля для работы с временными метками (День, месяц, год)
import requests  # Подключение библиотеки для обработки HTTP-запросов
import json  # Подключение модуля для работы с данными JSON (текстовый формат для обмена структурированными данными)

MONTHS_RU = {1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
             5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
             9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'}  # Русские названия месяцев
POPULAR_CURRENCIES = {"AUD": 'австралийский доллар', "CAD": 'канадский доллар',
                      "CHF": 'швейцарский франк', "CNY": 'китайский юань',
                      "EUR": 'евро (валюта стран еврозоны)', "GBP": 'фунт стерлингов (Великобритания)',
                      "JPY": 'японская иена', "KZT": "казахстанский тенге",
                      "RUB": 'российский рубль',
                      "USD": "американский доллар", "UZS": 'узбекский сум'}  # Список 11 популярных валют
FRAME_WIDTH = 450  # Ширина области отображения графика
FRAME_HEIGHT = 300  # Высота области отображения графика


def format_date(date_str: str) -> str:
    """Преобразует '2026-09-06' в '6 сентября'."""
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    return f"{dt.day} {MONTHS_RU[dt.month]}"


class CurrencyApp:
    def __init__(self, main):
        self.root = main  # Присвоить переменной значение экземпляра Tkinter
        self.root.title("Курс валют на сегодня")  # Название приложения
        self.root.geometry("600x400")  # Размер области окна приложения
        self.root.resizable(width=False, height=False)  # Отключить возможность менять ширину и высоту окна
        self.root.state('normal')  # Заблокировать кнопку "Развернуть"

        # Загрузка и преобразование изображения
        self.image = Image.open("world_currencies.png")  # financial-currency.png
        self.photo = ImageTk.PhotoImage(self.image)

        # Создание Label с изображением в качестве фона
        self.background_label = tk.Label(self.root, image=self.photo)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)  # Расположить поверх всего

        self.results = {}  # Данные для базовой валюты

        # Формируем список для Combobox и задаём максимальную ширину выпадающего списка
        target_text = [f"{key} - {value}" for key, value in POPULAR_CURRENCIES.items()]
        max_length = max(len(item) for item in target_text)

        # ------ # ------ # Пара виджетов (метка и Combobox) для целевой валюты # ------ # ------ #
        self.target1 = ttk.Label(text="Базовая валюта: ", font=('Arial', 10))
        self.target1.pack(padx=2, pady=(100, 2))
        self.currencies1 = ttk.Combobox(values=target_text, width=max_length)
        self.currencies1.pack(padx=2, pady=(2, 2))

        # ------ # ------ # Пара виджетов (метка и Combobox) для целевой валюты # ------ # ------ #
        self.target3 = ttk.Label(text="Целевая валюта: ", font=('Arial', 10))
        self.target3.pack(padx=2, pady=(2, 2))
        self.currencies3 = ttk.Combobox(values=target_text, width=max_length)
        self.currencies3.pack(padx=2, pady=(2, 5))

        # ------ # -- ПРОВЕРКА ДЛЯ НАПОЛНЕНИЯ ВЫПАДАЮЩИХ СПИСКОВ - ОТСУТСТВИЕ ПОВТОРЕНИЙ -- # ------ #
        self.currencies1.configure(state="readonly")  # Режим для выпадающего списка - только чтение (без ввода данных)
        self.currencies3.configure(state="disabled")  # Отключаем второй комбобокс изначально
        self.all_currencies = list(target_text)  # Сохраняем полный список значений

        Button(text="Получить курс обмена валют", command=self.exchange).pack(padx=4, pady=4)
        Button(text="Сбросить настройки", command=self.reset_currencies_set).pack(padx=4, pady=4)

        self.currencies1.bind("<<ComboboxSelected>>", self.on_select_currency1)  # Отслеживание выбора базовой валюты
        self.currencies3.bind("<<ComboboxSelected>>", self.on_select_currency3)  # Отслеживание выбора целевой валюты

    def reset_currencies_set(self):
        """Метод сброса выбранных настроек"""
        self.currencies1.set("")  # Очистить поле "Базовая валюта"
        self.currencies1.configure(state="readonly")  # Режим для выпадающего списка - только чтение (без ввода данных)
        self.currencies3.set("")  # Очистить поле "Целевая валюта"
        self.currencies3.configure(state="disabled")  # Отключаем третий комбобокс повторно

    def on_select_currency1(self, _):
        """Метод выбора для списка базовых валют"""
        selected1 = self.currencies1.get()  # Текущее значение для базовой валюты
        if not selected1:
            return

        # Обновляем список для currencies3: всё, кроме выбранного в currencies1
        remaining_for_3 = [c for c in self.all_currencies if c != selected1]
        self.currencies3.configure(values=remaining_for_3)
        # Если в currencies3 уже выбрано то же, что в currencies1 — сбрасываем
        if self.currencies3.get() == selected1:
            self.currencies3.set("")
        self.currencies3.configure(state="readonly")  # Активируем currencies3

    def on_select_currency3(self, _):
        """Метод выбора для списка целевых валют"""
        selected3 = self.currencies3.get()  # Текущее значение для целевой валюты
        if not selected3:
            return

        self.update_currency1(selected3)  # Вызов метода обновления списка базовых валют

    def update_currency1(self, selected3):
        """Обновляет список базовых валют, исключая выбранное значение из списка целевых валют"""
        remaining_for_1 = [c for c in self.all_currencies if c != selected3]
        self.currencies1.configure(values=remaining_for_1)
        # Если в currencies1 выбрано значение, которого больше нет — сбрасываем
        if self.currencies1.get() == selected3:
            self.currencies1.set("")

    def check_choice(self) -> bool:
        """
        Метод проверки заполнения полей "Базовая валюта" (впоследствии "Вторая базовая валюта") и "Целевая валюта"
        перед формированием запроса для API
        :return: True/False (с сообщением об ошибке)
        """
        error_message = ""  # Строка для информации об ошибке при формировании запроса
        if not self.currencies1.get():
            error_message += "Не выбрана базовая валюта!\n"
        if not self.currencies3.get():
            error_message += "Не выбрана целевая валюта!\n"
        if not error_message:
            return True
        else:
            mb.showerror("Ошибка!", error_message)
            return False

    def exchange(self):
        """Метод запроса данных от API на основании выбранных настроек"""
        if not self.check_choice():  # Проверка выбора параметров для формирования запроса
            return

        base_currency = self.currencies1.get()[:3]  # Код для базовой валюты
        target_currency = self.currencies3.get()[:3]  # Код для целевой валюты

        today = datetime.now().date()  # Получаем текущую дату
        self.results["Data rate"] = today.isoformat()  # Преобразование даты в формат ГГГГ-ММ-ДД
        self.results[base_currency] = None  # Курс для базовой валюты на сегодня

        try:
            url_resp = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/" \
                       f"v1/currencies/{base_currency.lower()}.json"  # Строка запроса для API

            resp = requests.get(url_resp, timeout=25)  # 25 секунд на всё соединение и ответ
            resp.raise_for_status()  # Проверка кода статуса ответа сервера после выполнения HTTP-запроса
            data = resp.json()  # Преобразование строки JSON во вложенные структуры данных - словари, списки и т.д.
            value = data[base_currency.lower()][target_currency.lower()]  # Парсинг значения целевой валюты
            self.results[base_currency] = f"{value:.2f}"  # Сохранение форматированных данных
        except Exception as e:
            mb.showerror("Ошибка интернет-соединения", f"Другая ошибка: {e}")

        rate_base_currency = 'нет данных'  # Значения курса первой базовой валюты (по умолчанию)
        if self.results[base_currency]:
            rate_base_currency = f"{self.results[base_currency]} {target_currency}"
        mb.showinfo("Курс обмена",  # Окно информации по курсу валют
                    f"Курс на сегодня ({format_date(str(self.results['Data rate']))}): "
                    f"\n        1 {base_currency} = {rate_base_currency}")


if __name__ == "__main__":
    root = tk.Tk()  # Создание экземпляра рабочего окна приложения tkinter
    app = CurrencyApp(root)  # Создание экземпляра коасса CurrencyApp
    root.mainloop()  # Активация бесконечного цикла выполнения приложения (до закрытия окна приложения)
