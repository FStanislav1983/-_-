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
import threading  # Модуль для работы с потоками (обработка данных в фоне, не блокируя основной поток)
from time import sleep as pause  # Подключение модуля для применения задержки в выполнении программы

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

        # Формируем список для Combobox и задаём максимальную ширину выпадающего списка
        target_text = [f"{key} - {value}" for key, value in POPULAR_CURRENCIES.items()]
        max_length = max(len(item) for item in target_text)

        # ------ # ---- Пара виджетов (метка и Combobox) для первой целевой валюты ---- # ------ #
        self.target1 = ttk.Label(text="Первая базовая валюта: ", font=('Arial', 10))
        self.target1.pack(padx=2, pady=(70, 2))
        self.currencies1 = ttk.Combobox(values=target_text, width=max_length)
        self.currencies1.pack(padx=2, pady=(2, 2))

        # ------ # ---- Пара виджетов (метка и Combobox) для второй целевой валюты ---- # ------ #
        self.target2 = ttk.Label(text="Вторая базовая валюта: ", font=('Arial', 10))
        self.target2.pack(padx=2, pady=(2, 2))
        self.currencies2 = ttk.Combobox(values=target_text, width=max_length)
        self.currencies2.pack(padx=2, pady=(2, 2))

        # ------ # ------ # Пара виджетов (метка и Combobox) для целевой валюты # ------ # ------ #
        self.target3 = ttk.Label(text="Целевая валюта: ", font=('Arial', 10))
        self.target3.pack(padx=2, pady=(2, 2))
        self.currencies3 = ttk.Combobox(values=target_text, width=max_length)
        self.currencies3.pack(padx=2, pady=(2, 5))

        # ------ # -- ПРОВЕРКА ДЛЯ НАПОЛНЕНИЯ ВЫПАДАЮЩИХ СПИСКОВ - ОТСУТСТВИЕ ПОВТОРЕНИЙ -- # ------ #
        self.currencies1.configure(state="readonly")  # Режим для выпадающего списка - только чтение (без ввода данных)
        self.currencies2.configure(state="disabled")  # Отключаем второй комбобокс изначально
        self.currencies3.configure(state="disabled")  # Отключаем третий комбобокс изначально
        self.all_currencies = list(target_text)  # Сохраняем полный список значений

        # Кнопки интерфейса управления приложением и строка состояния обработки запроса
        Button(text="Получить курс обмена валют", command=self.start_request).pack(padx=4, pady=(15, 60))
        self.progress = ttk.Progressbar(length=300, maximum=2, mode='determinate')
        self.progress.pack(pady=2)  # Прогресс-бар
        self.status_label = ttk.Label(text="Ожидание запуска...")
        self.status_label.pack(pady=2)  # Статусная строка
        self.results = {}  # Данные курсов базовых валют на сегодняшний день
        Button(text="Сбросить настройки", command=self.reset_currencies_set).pack(padx=4, pady=4)

        self.currencies1.bind("<<ComboboxSelected>>", self.on_select_currency1)  # Отслеживание выбора 1 базовой валюты
        self.currencies2.bind("<<ComboboxSelected>>", self.on_select_currency2)  # Отслеживание выбора 2 базовой валюты
        self.currencies3.bind("<<ComboboxSelected>>", self.on_select_currency3)  # Отслеживание выбора целевой валюты

    def reset_currencies_set(self):
        """Метод сброса выбранных настроек"""
        self.currencies1.set("")  # Очистить поле "Первая базовая валюта
        self.currencies1.configure(state="readonly")  # Режим для выпадающего списка - только чтение (без ввода данных)
        self.currencies2.set("")  # Очистить поле "Вторая базовая валюта"
        self.currencies2.configure(state="disabled")  # Отключаем второй комбобокс повторно
        self.currencies3.set("")  # Очистить поле "Целевая валюта"
        self.currencies3.configure(state="disabled")  # Отключаем третий комбобокс повторно
        self.progress.config(value=0)
        self.status_label.config(text="Ожидание запуска...")

    def on_select_currency1(self, _):
        """Метод выбора для списка первой базовой валюты"""
        selected1 = self.currencies1.get()  # Текущее значение для первой базовой валюты
        if not selected1:
            return

        # Обновляем список для второй базовой валюты: всё, кроме выбранного в списке для первой базовой валюты
        remaining_for_2 = [c for c in self.all_currencies if c != selected1]
        self.currencies2.configure(values=remaining_for_2)

        # Если в списке для второй базовой валюты уже выбрано то же, что в списке для первой базовой валюты — сбрасываем
        if self.currencies2.get() == selected1:
            self.currencies2.set("")

        self.currencies2.configure(state="readonly")  # Активируем список для второй базовой валюты

        self.currencies3.set("")  # Сбрасываем значение целевой валюты, так как ситуация изменилась
        self.currencies3.configure(state="disabled")  # Список для целевой валюты заблокирован

        # Если в currencies2 уже что-то выбрано — обновляем currencies3
        selected2 = self.currencies2.get()  # Текущее значение для второй базовой валюты
        if selected2:
            self.update_currency3(selected1, selected2)  # Обновить список целевой валюты

    def on_select_currency2(self, _):
        """Метод выбора для списка второй базовой валюты"""
        selected1 = self.currencies1.get()  # Текущее значение для первой базовой валюты
        selected2 = self.currencies2.get()  # Текущее значение для второй базовой валюты
        if not selected2:
            return

        self.update_currency3(selected1, selected2)  # Обновить список целевой валюты

    def update_currency3(self, selected1, selected2):
        """Обновляет список для целевой валюты, исключая выбранные значения из списков для базовых валют"""
        remaining_for_3 = [
            c for c in self.all_currencies
            if c != selected1 and c != selected2
        ]
        self.currencies3.configure(values=remaining_for_3)

        # Если в списке для целевой валюты выбрано значение, которого больше нет — сбрасываем
        current3 = self.currencies3.get()  # Текущее значение для целевой валюты
        if current3 in (selected1, selected2):
            self.currencies3.set("")

        self.currencies3.configure(state="readonly")  # Активировать список для целевой валюты

    def on_select_currency3(self, _):
        """Метод выбора для списка целевой валюты"""
        selected1 = self.currencies1.get()  # Текущее значение для первой базовой валюты
        selected2 = self.currencies2.get()  # Текущее значение для второй базовой валюты
        selected3 = self.currencies3.get()  # Текущее значение для целевой валюты

        if selected3 in (selected1, selected2):  # Проверяем, что значение для целевой валюты не совпадает с базовыми
            self.currencies3.set("")

    def check_choice(self) -> bool:
        """
        Метод проверки заполнения полей "Первая базовая валюта", "Вторая базовая валюта" и "Целевая валюта"
        перед формированием запроса для API
        :return: True/False (с сообщением об ошибке)
        """
        error_message = ""  # Строка для информации об ошибке при формировании запроса
        if not self.currencies1.get():
            error_message += "Не выбрана первая базовая валюта!\n"
        if not self.currencies2.get():
            error_message += "Не выбрана вторая базовая валюта!\n"
        if not self.currencies3.get():
            error_message += "Не выбрана целевая валюта!"
        if not error_message:
            return True
        else:
            mb.showerror("Ошибка!", error_message)
            return False

    def exchange(self, data_currencies: list):
        """
            Метод сбора данных на основании выбранных параметров - базовые и целевая валюты
            :param data_currencies: целевые валюты (индекс - 0, 1) - для поиска нужной информации в ответе от API
                                    базовая валюта (индекс -1) - для формирования запроса
            """
        total = len(data_currencies[:-1])  # Общее количество запросов
        success = 0  # Счётчик успешных ответов от API
        fail = 0  # Счётчик ошибок при запросах от API
        today = datetime.now().date()  # Получаем текущую дату
        self.results["Data rate"] = today.isoformat()  # Преобразование даты в формат ГГГГ-ММ-ДД
        self.results[data_currencies[0]] = None  # Курс для первой базовой валюты на сегодня
        self.results[data_currencies[1]] = None  # Курс для второй базовой валюты на сегодня

        for i, currency in enumerate(data_currencies[:-1], 1):
            try:
                url_resp = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/" \
                           f"v1/currencies/{currency.lower()}.json"  # Строка запроса для API

                resp = requests.get(url_resp, timeout=25)  # 25 секунд на всё соединение и ответ
                resp.raise_for_status()  # Проверка кода статуса ответа сервера после выполнения HTTP-запроса
                data = resp.json()  # Преобразование строки JSON во вложенные структуры данных - словари, списки и т.д.
                value = data[currency.lower()][data_currencies[-1].lower()]  # Парсинг значения целевой валюты
                # if i == 2:  # Моделирование ситуации с ошибкой данных
                #     value = data[currency.lower()][data_currencies[-1]]  # Ошибка в парсинге значения целевой валюты

                self.results[currency] = f"{value:.2f}"  # Сохранение форматированных данных
                success += 1  # Увеличиваем счётчик успешных запросов
            except Exception as e:
                fail += 1  # Увеличить счётчик ошибок
                mb.showerror("Ошибка интернет-соединения", f"Другая ошибка: {e}")

            self.progress.config(value=i)  # Отобразить изменение на прогресс-бар
            self.status_label.config(text=f"Выполнено: {i}/{total} (успешно: {success}, ошибок: {fail})")
            self.progress.update()  # Обновляем прогресс-бар
            self.status_label.update()  # Обновляем статусную метку
            pause(1)  # Небольшая задержка, чтобы не перегружать CPU

    def start_request(self):
        if not self.check_choice():  # Проверка выбора параметров для формирования запроса
            return

        base_currency1 = self.currencies1.get()[:3]  # Код для первой базовой валюты
        base_currency2 = self.currencies2.get()[:3]  # Код для второй базовой валюты
        target_currency = self.currencies3.get()[:3]  # Код для целевой валюты

        self.results.clear()  # Очистка словаря данных
        thread = threading.Thread(target=self.exchange([base_currency1, base_currency2,
                                                        target_currency]))  # Создаём поток для метода self.exchange
        thread.start()  # Запускаем поток с обработкой функции self.exchange
        thread.join()  # Теперь главный поток будет ждать завершения этого потока

        rate_base_currency1 = 'нет данных'  # Значения курса первой базовой валюты (по умолчанию)
        rate_base_currency2 = 'нет данных'  # Значения курса второй базовой валюты (по умолчанию)
        if self.results[base_currency1] and self.results[base_currency2]:
            rate_base_currency1 = f"{self.results[base_currency1]} {target_currency}"
            rate_base_currency2 = f"{self.results[base_currency2]} {target_currency}"
        elif self.results[base_currency1] and not self.results[base_currency2]:
            rate_base_currency1 = f"{self.results[base_currency1]} {target_currency}"
        elif not self.results[base_currency1] and self.results[base_currency2]:
            rate_base_currency2 = f"{self.results[base_currency2]} {target_currency}"
        mb.showinfo("Курс обмена",  # Окно информации по курсу валют
                    f"Курс на сегодня ({format_date(str(self.results['Data rate']))}): "
                    f"\n        1 {base_currency1} = {rate_base_currency1}"
                    f"\n        1 {base_currency2} = {rate_base_currency2}")


if __name__ == "__main__":
    root = tk.Tk()  # Создание экземпляра рабочего окна приложения tkinter
    app = CurrencyApp(root)  # Создание экземпляра коасса CurrencyApp
    root.mainloop()  # Активация бесконечного цикла выполнения приложения (до закрытия окна приложения)
