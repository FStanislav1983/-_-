import tkinter as tk  # Подключение библиотеки Tkinter для создания графических пользовательских интерфейсов (GUI)
from tkinter import Button
from tkinter import ttk  # Модуль ttk с набором тематических виджетов (Combobox, Notebook, Progressbar, Treeview)
from tkinter import messagebox as mb  # Модуль для отображения всплывающих окон с сообщениями пользователю
from PIL import Image, ImageTk  # Для работы с изображениями загружаем модули из библиотеки Pillow
import matplotlib.pyplot as plt  # Подключение модуля для построения графиков в стиле, похожем на MATLAB
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Подключение модуля для отображения графика внутри Tk
from matplotlib.figure import Figure  # Корневой объект, который содержит все компоненты визуализации:
#                                       области для рисования (Axes), заголовки, легенды, метки осей и другие элементы
from datetime import datetime, timedelta  # Загрузка класса модуля для работы с временными метками (День, месяц, год)
import requests  # Подключение библиотеки для обработки HTTP-запросов
import json  # Подключение модуля для работы с данными JSON (текстовый формат для обмена структурированными данными)
import threading  # Модуль для работы с потоками (обработка данных в фоне, не блокируя основной поток)
import pprint
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
DPI = 100  # Разрешение точек на дюйм
FRAME_WIDTH = 450  # Ширина области отображения графика
FRAME_HEIGHT = 300  # Высота области отображения графика
FIG_WIDTH_IN = FRAME_WIDTH / DPI  # ~4.5 дюйма
FIG_HEIGHT_IN = FRAME_HEIGHT / DPI  # ~3.0 дюйма

pp = pprint.PrettyPrinter(
    indent=4,  # Отступ для каждого уровня вложенности
    width=50,  # Максимальная ширина строки
    compact=False  # Не использовать компактное представление (без слияния коротких элементов)
)  # Создаём объект PrettyPrinter с настройками


def format_date(date_str: str) -> str:
    """Преобразует '2026-09-06' в '6 сентября'."""
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    return f"{dt.day} {MONTHS_RU[dt.month]}"


def week_lst() -> list:
    """Функция создания списка из семи дат, включая сегодняшее число"""
    today = datetime.now().date()  # Получаем текущую дату
    dates_list = [today - timedelta(days=i) for i in range(7)]  # Создаём список дат
    iso_dates = [date.isoformat() for date in dates_list]  # Преобразуем каждую дату в строку в формате ISO

    return sorted(iso_dates)  # Результат — список строк в формате ISO


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

        self.results = {'2026-09-06': {'USD': '86.56', 'EUR': '100.56'},
                        '2026-09-07': {'USD': '86.61', 'EUR': '100.25'},
                        '2026-09-08': {'USD': '86.24', 'EUR': '99.85'},
                        '2026-09-09': {'USD': None, 'EUR': '98.92'},
                        '2026-09-10': {'USD': '85.00', 'EUR': '97.41'},
                        '2026-09-11': {'USD': '83.96', 'EUR': '97.65'},
                        '2026-09-12': {'USD': '84.19', 'EUR': '97.76'}
                        }  # Данные курсов базовых валют за неделю (Только для отладки приложения)

        # ------ # ------ # ------ # ------ # Панель кнопок # ------ # ------ # ------ # ------ #
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(side=tk.TOP, pady=10)  # Контейнер для кнопок взаимодействия

        self.btn_get = ttk.Button(self.button_frame, text="Получить данные",
                                  command=self.start_request)
        self.btn_get.pack(side=tk.LEFT, padx=2)  # Кнопка "Получить данные"
        self.btn_reset = ttk.Button(self.button_frame, text="Вернуться к настройкам",
                                    command=self.reset_view, state=tk.DISABLED)
        self.btn_reset.pack(side=tk.LEFT, padx=2)  # Кнопка "Вернуться к настройкам"
        # ------ # ------ # ------ # ------ # ------ # ------ # ------ # ------ # ------ # ------ #
        self.menu_settings()  # Вызов метода создания меню настроек

        self.canvas = None  # Область основного окна приложения для построения графика
        self.figure = None  # Фигура с объектами построения графика matplotlib

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)  # Обработка закрытия окна

    def menu_settings(self):
        """Метод создания виджетов для основного окна приложения - меню настроек"""
        # Удаляем старые фреймы, если они уже есть
        if hasattr(self, 'chart_frame') and self.chart_frame is not None:
            self.chart_frame.destroy()
        if hasattr(self, 'hint_frame') and self.hint_frame is not None:
            self.hint_frame.destroy()
        if hasattr(self, 'status_frame') and self.status_frame is not None:
            self.status_frame.destroy()
        if hasattr(self, 'bottom_frame') and self.bottom_frame is not None:
            self.bottom_frame.destroy()

        # ------ # ------ # ------ # Создаём новые фреймы для меню настроек # ------ # ------ # ------ #
        self.chart_frame = ttk.Frame(self.root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
        self.chart_frame.pack(padx=82, pady=2, fill=tk.BOTH, expand=False)  # Контейнер для виджетов выбора валют

        # Центрируем пары метка-Combobox по горизонтали
        self.chart_frame.columnconfigure(0, weight=1)  # пустой слева
        self.chart_frame.columnconfigure(1, weight=0)  # метка — ширина по содержимому
        self.chart_frame.columnconfigure(2, weight=0)  # Combobox — ширина по содержимому
        self.chart_frame.columnconfigure(3, weight=1)  # пустой справа

        # Формируем список для Combobox и задаём максимальную ширину выпадающего списка
        target_text = [f"{key} - {value}" for key, value in POPULAR_CURRENCIES.items()]
        max_length = max(len(item) for item in target_text)

        # ------ # ------ # Пара виджетов (метка и Combobox) для первой базовой валюты # ------ # ------ #
        self.target1 = ttk.Label(self.chart_frame, text="Первая базовая валюта: ", font=('Arial', 10))
        self.target1.grid(row=1, column=1, padx=2, pady=2, sticky=tk.E)
        self.currencies1 = ttk.Combobox(self.chart_frame, values=target_text, width=max_length)
        self.currencies1.grid(row=1, column=2, padx=2, pady=2, sticky=tk.W)

        # ------ # ------ # Пара виджетов (метка и Combobox) для второй базовой валюты # ------ # ------ #
        self.target2 = ttk.Label(self.chart_frame, text="Вторая базовая валюта: ", font=('Arial', 10))
        self.target2.grid(row=2, column=1, padx=2, pady=5, sticky=tk.E)
        self.currencies2 = ttk.Combobox(self.chart_frame, values=target_text, width=max_length)
        self.currencies2.grid(row=2, column=2, padx=2, pady=2, sticky=tk.W)

        # ------ # ------ # --- Пара виджетов (метка и Combobox) для целевой валюты --- # ------ # ------ #
        self.target3 = ttk.Label(self.chart_frame, text="Целевая валюта: ", font=('Arial', 10))
        self.target3.grid(row=3, column=1, padx=2, pady=5, sticky=tk.E)
        self.currencies3 = ttk.Combobox(self.chart_frame, values=target_text, width=max_length)
        self.currencies3.grid(row=3, column=2, padx=2, pady=2, sticky=tk.W)

        self.hint_frame = ttk.Frame(self.root, padding=(1, 1))
        self.hint_frame.pack(side=tk.TOP, pady=10)  # Контейнер для справочной строки

        self.placeholder_label = ttk.Label(
            self.hint_frame,
            text="Выберите базовые и целевую валюты"
                 "\nКурс - это отношение базовой и целевой валюты"
                 "\nНажмите «Получить данные» для отображения курса валют",
            font=('Arial', 10),  # Шрифт и размер текста
            justify='center'  # Выравнивание текста - по центру
        )  # Справочная строка (минимальные значения курса валюты с указание даты)
        self.placeholder_label.pack(pady=(1, 2), side=tk.TOP)

        # Кнопки интерфейса управления приложением и строка состояния обработки запроса
        self.status_frame = ttk.Frame(self.root, padding=(1, 1))
        self.status_frame.pack(side=tk.TOP, pady=(4, 35))  # Контейнер для справочной строки

        self.status_label = ttk.Label(self.status_frame, text="Ожидание запуска...")
        self.status_label.pack(pady=(1, 1))  # Статусная строка
        self.progress = ttk.Progressbar(self.status_frame, length=252, maximum=14, mode='determinate')
        self.progress.pack(pady=(1, 1))  # Прогресс-бар

        self.bottom_frame = ttk.Frame(self.root, padding=(0, 0))
        self.bottom_frame.pack(side=tk.TOP, pady=(25, 2))  # Контейнер для справочной строки
        self.btn_clear = ttk.Button(self.bottom_frame,
                                    text="Сбросить настройки", command=self.reset_currencies_set).pack(pady=(1, 1))

        # ------ # -- ПРОВЕРКА ДЛЯ НАПОЛНЕНИЯ ВЫПАДАЮЩИХ СПИСКОВ - ОТСУТСТВИЕ ПОВТОРЕНИЙ -- # ------ #
        self.currencies1.configure(state="readonly")  # Режим для выпадающего списка - только чтение (без ввода данных)
        self.currencies2.configure(state="disabled")  # Заблокировать выбор второй базовой валюты до выбора первой
        self.currencies3.configure(state="disabled")  # Заблокировать выбор целевой валюты до выбора базовых валют
        self.all_currencies = list(target_text)  # Сохраняем полный список значений валют

        self.currencies1.bind("<<ComboboxSelected>>", self.on_select_currency1)  # Отслеживание выбора базовой валюты 1
        self.currencies2.bind("<<ComboboxSelected>>", self.on_select_currency2)  # Отслеживание выбора базовой валюты 2
        self.currencies3.bind("<<ComboboxSelected>>", self.on_select_currency3)  # Отслеживание выбора целевой валюты

        # self.root.protocol("WM_DELETE_WINDOW", self.on_close)  # Обработка закрытия окна

    def reset_currencies_set(self):
        """Метод сброса выбранных настроек"""
        self.currencies1.set("")  # Очистить поле "Первая базовая валюта
        self.currencies1.configure(state="readonly")  # Режим для выпадающего списка - только чтение (без ввода данных)
        self.currencies2.set("")  # Очистить поле "Вторая базовая валюта"
        self.currencies2.configure(state="disabled")  # Отключаем второй комбобокс повторно
        self.currencies3.set("")  # Очистить поле "Целевая валюта"
        self.currencies3.configure(state="disabled")  # Отключаем третий комбобокс повторно
        self.progress.config(value=0)  # Сбрасывание состояния прогресс-бар
        self.status_label.config(text="Ожидание запуска...")  # Возврат строки статуса в исходное состояние

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
        week_before_today = week_lst()  # Список семи дат, включая сегодняшнее число
        total = len(data_currencies[:-1]) * len(week_before_today)  # Общее количество запросов
        success = 0  # Счётчик успешных ответов от API
        fail = 0  # Счётчик ошибок при запросах от API
        self.results = {day: {data_currencies[0]: None, data_currencies[1]: None} for day in week_before_today}

        for i, currency in enumerate(data_currencies[:-1], 1):
            for d, day in enumerate(week_before_today):
                try:
                    url_resp = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{day}" \
                               f"/v1/currencies/{currency.lower()}.json"  # Строка запроса для API
                    # TODO: ВАЖНО! Данные API обновляются с 0:00 до 6:00, поэтому следует изменить системную дату
                    resp = requests.get(url_resp, timeout=25)  # 25 секунд на всё соединение и ответ
                    resp.raise_for_status()  # Метод, который проверяет код ответа сервера после выполнения HTTP-запроса
                    data = resp.json()  # Преобразование JSON во вложенные структуры данных - словари, списки и т.д.
                    value = data[currency.lower()].get(data_currencies[-1].lower())  # Парсинг значения целевой валюты
                    # Сохранение данных курса базовой валюты ([дата]:{[код]: округлённое значение Х.хх})
                    self.results[day][currency] = f"{value:.2f}"
                    success += 1  # Увеличиваем счётчик успешных запросов

                except Exception as e:
                    fail += 1  # Увеличить счётчик ошибок
                    mb.showerror("Ошибка интернет-соединения", f"Другая ошибка: {e}")

                self.progress.config(value=d + 7 * (i - 1))  # Отобразить изменение на прогресс-бар
                self.status_label.config(
                    text=f"Выполнено: {d + 7 * (i - 1)}/{total} (успешно: {success}, ошибок: {fail})")
                self.progress.update()  # Обновляем прогресс-бар
                self.status_label.update()  # Обновляем статусную метку
                pause(0.5)  # Небольшая задержка, чтобы не перегружать CPU
        pp.pprint(self.results)  # Данные для построения графика курсов валют за неделю (для отладки)

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

        # ------ # ------ # ---- ФОРМИРОВАНИЕ СООБЩЕНИЯ О КУРСЕ ВАЛЮТ НА СЕГОДНЯ ---- # ------ # ------ #
        rate_base_currency1 = 'нет данных'  # Значения курса первой базовой валюты (по умолчанию)
        rate_base_currency2 = 'нет данных'  # Значения курса второй базовой валюты (по умолчанию)
        today = list(self.results.keys())[-1]
        if self.results[today][base_currency1] and self.results[today][base_currency2]:
            rate_base_currency1 = f"{self.results[today][base_currency1]} {target_currency}"
            rate_base_currency2 = f"{self.results[today][base_currency2]} {target_currency}"
            self.show_graph()  # Показать графики для двух базовых валют
        elif self.results[today][base_currency1] and not self.results[today][base_currency2]:
            rate_base_currency1 = f"{self.results[today][base_currency1]} {target_currency}"
            self.show_graph()  # Показать график для первой базовой валюты
        elif not self.results[today][base_currency1] and self.results[today][base_currency2]:
            rate_base_currency2 = f"{self.results[today][base_currency2]} {target_currency}"
            self.show_graph()  # Показать график для второй базовой валюты
        mb.showinfo("Курс обмена",  # Окно информации по курсу валют
                    f"Курс на сегодня ({format_date(today)}): "
                    f"\n        1 {base_currency1} = {rate_base_currency1}"
                    f"\n        1 {base_currency2} = {rate_base_currency2}")

    def show_graph(self):
        """Отрисовка графиков изменения курсов базовых валют с подписями точек"""
        if not self.check_choice():  # Проверка выбора параметров для формирования графика
            return

        currency1 = self.currencies1.get()[:3]  # Код для первой базовой валюты
        currency2 = self.currencies2.get()[:3]  # Код для второй базовой валюты
        currency3 = self.currencies3.get()[:3]  # Код для целевой валюты
        week_rate = sorted(self.results.keys())  # Список дат запросов курса базовой валюты

        rate_first_currency = [float(self.results[day][currency1]) for day in week_rate
                               if self.results[day][currency1]]  # Значения для первой базовой валюты
        rate_second_currency = [float(self.results[day][currency2]) for day in week_rate
                                if self.results[day][currency2]]  # Значения для второй базовой валюты

        labels = [format_date(d) for d in week_rate]  # Список преобразованных подписей по оси Х

        # ------ # ------ # ------ # -- ФОРМИРОВАНИЕ ГРАФИКОВ БАЗОВЫХ ВАЛЮТ -- # ------ # ------ # ------ #
        self.figure, ax = plt.subplots(figsize=(FIG_WIDTH_IN, FIG_HEIGHT_IN),
                                       dpi=DPI)  # Объект холста для графика и ось Х (6 х 4 дюймов)
        self.figure.tight_layout()  # Метод объекта Figure, который автоматически настраивает отступы

        self.clear_chart_area()  # Вызов метода для полной очистки области графика
        index_date = list(range(len(week_rate)))  # Список индексов дат запросов курса базовой валюты
        if len(rate_first_currency) > 6:
            ax.plot(index_date, rate_first_currency, marker='o', color='yellow', linewidth=2,
                    markersize=5)  # График первой базовой валюты
        if len(rate_second_currency) > 6:
            ax.plot(index_date, rate_second_currency,  # Данные для построения графика
                    marker='o', color='green',  # Тип маркера ('o', 's', '*', 'd', '+', 'v', '^'), цвет графика
                    linewidth=2, markersize=5)  # Толщина линий графика, размер маркера
        ax.tick_params(axis='y', labelsize=6)  # Размер шрифта по оси Y

        for cur_label in (rate_first_currency, rate_second_currency):  # Значения для точек графиков базовых валют
            for i, (label, val) in enumerate(zip(index_date, cur_label)):
                ax.text(
                    label, val, f"{val:.2f}",
                    ha='center', va='top',  # Размещение текста - по центру верхней границы
                    fontsize=8, color='black'  # Размер и цвет шрифта
                )  # Подпись значения под каждой точкой

        ax.set_xticks(index_date)  # Метод, который задаёт позиции по оси Х (день и месяц буквенно)
        ax.set_xticklabels(labels, rotation=0, ha='center', fontsize=6)  # Настройка отображения новых меток по оси Х

        ax.set_title(f"Курс {currency1}/{currency2} к {currency3} за 7 дней",
                     fontsize=8, loc='left')  # Название графика
        ax.set_ylabel(f"Значение {currency3} за {currency1}/{currency2}",
                      fontsize=6, labelpad=1)  # Название оси Y (значения базовой валюты)

        ax.grid(True, which='major',  # Включаем сетку для основных линий (оси Х и Y)
                axis='both', linestyle='--',  # Стиль линий сетки - пунктирная, для обеих осей графика
                color='gray',  # Цвет линий сетки - серый
                linewidth=0.5, alpha=0.7)  # Толщина и прозрачность линий сетки
        legend_lst = [currency1, currency2]  # Изменение порядка списка для легенды
        if len(rate_first_currency) < 7 and len(rate_second_currency) > 6:
            legend_lst = [currency2, currency1]

        plt.legend(labels=legend_lst,  # список меток для легенды
                   loc='upper left',  # начальное расположение легенды в верхнем левом углу
                   fontsize=8,  # размер шрифта для элементов легенды
                   bbox_to_anchor=(0.5, 1.05),  # координаты точки привязки легенды в координатах осей
                   borderaxespad=0,  # убирает отступы (padding) между границей легенды и краями осей
                   ncol=2,  # располагает элементы легенды в два столбца
                   fancybox=True,  # рамка легенды со скруглёнными углами
                   shadow=True)  # добавляет тень за легендой для объёмного эффекта

        # ------ # ------ # ------ # Встраиваем график Matplotlib в Tkinter # ------ # ------ # ------ #
        self.canvas = FigureCanvasTkAgg(self.figure,  # Создаётся объект-мост между Figure (график в Matplotlib)
                                        master=self.chart_frame)  # и виджетом Tkinter (chart_frame)
        self.canvas.draw()  # Метод заставляет виджет Tkinter перерисовать себя на основе данных из объекта Figure
        widget = self.canvas.get_tk_widget()  # Возвращает нативный виджет Tkinter, который и будет отображать график
        widget.pack(fill=tk.BOTH, expand=True)  # Метод pack() размещает этот виджет в контейнере (chart_frame)

        # ------ # ------ # ------ # Обработка состояний кнопок приложения # ------ # ------ # ------ #
        self.btn_get.config(state=tk.DISABLED)  # Сделать кнопку "Получить данные" неактивной
        self.btn_reset.config(state=tk.NORMAL)  # Сделать кнопку "Вернуться к настройкам" активной

        # ------ # ------ # ------ Анализ данных по изменению курсов валют за неделю ------ # ------ #
        min_val1 = min(rate_first_currency)  # Минимальное значение курса первой базовой валюты за 7-мь дней
        date_min_val1 = week_rate[rate_first_currency.index(min_val1)]  # Дата минимального курса первой базовой валюты
        min_val2 = min(rate_second_currency)  # Минимальное значение курса второй базовой валюты за 7-мь дней
        date_min_val2 = week_rate[rate_second_currency.index(min_val2)]  # Дата минимального курса второй базовой валюты

        # ------ # ------ # ---- ФОРМИРОВАНИЕ РЕЗЮМЕ ДЛЯ ГРАФИКОВ ИЗМЕНЕНИЯ КУРСОВ ВАЛЮТ ---- # ------ # ------ #
        min_rate_hints = f"Минимальный курс {currency1} = {min_val1}{currency3} был {format_date(date_min_val1)}" \
                         f"\nМинимальный курс {currency2} = {min_val2}{currency3} был {format_date(date_min_val2)}"
        if len(rate_first_currency) > 6 and len(rate_second_currency) < 7:
            min_rate_hints = f"Минимальный курс {currency1} = {min_val1}{currency3} был {format_date(date_min_val1)}" \
                             f"\nМинимальный курс {currency2} = нет данных"
        if len(rate_second_currency) > 6 and len(rate_first_currency) < 7:
            min_rate_hints = f"Минимальный курс {currency1} = нет данных" \
                             f"\nМинимальный курс {currency2} = {min_val2}{currency3} был {format_date(date_min_val2)}"
        self.placeholder_label = ttk.Label(  # Справочная строка
            self.chart_frame, text=min_rate_hints,
            font=('Arial', 9),  # Шрифт и размер текста
            justify='center')  # Выравнивание текста - по центру
        self.placeholder_label.pack(padx=2, pady=2, side=tk.TOP)

    def reset_view(self):
        """Возврат к исходному виду"""
        self.clear_chart_area()  # Вызов метода для полной очистки области графика
        self.menu_settings()  # Вызов метода создания меню настроек

        self.btn_get.config(state=tk.NORMAL)  # Сделать кнопку "Получить данные" активной
        self.btn_reset.config(state=tk.DISABLED)  # Сделать кнопку "Вернуться к настройкам" неактивной

    def clear_chart_area(self):
        """Полная очистка области графика"""
        for widget in self.chart_frame.winfo_children():
            widget.destroy()  # Удалить объекты из контейнера chart_frame
        for label in self.hint_frame.winfo_children():
            label.destroy()  # Удалить метки из контейнера hint_frame
        for status_bar in self.status_frame.winfo_children():
            status_bar.destroy()
        for button in self.bottom_frame.winfo_children():
            button.destroy()
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()  # Освобождаем ресурсы matplotlib
            self.canvas.figure.clear()  # Очистка данных в объекте график
            self.canvas = None  # Присвоение исходного значения для области графика

    def on_close(self):
        """Метод обработки закрытия окна"""
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()  # Удаление элемента интерфейса и освобождение ресурсов matplotlib
        if self.figure is not None:
            plt.close(self.figure)  # Закрыть фигуру matplotlib и освобождение памяти, занятую ресурсами
        self.root.destroy()  # Остановка основного цикла и закрытие основного окна
        self.root.quit()  # Альтернативный способ остановки цикла


if __name__ == "__main__":
    root = tk.Tk()  # Создание экземпляра рабочего окна приложения tkinter
    app = CurrencyApp(root)  # Создание экземпляра коасса CurrencyApp
    root.mainloop()  # Активация бесконечного цикла выполнения приложения (до закрытия окна приложения)
