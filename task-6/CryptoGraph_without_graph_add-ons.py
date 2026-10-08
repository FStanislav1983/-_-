import json  # Подключение модуля для работы с данными JSON (текстовый формат для обмена структурированными данными)
import tkinter as tk  # Подключение библиотеки Tkinter для создания графических пользовательских интерфейсов (GUI)
from tkinter import ttk, messagebox  # Подключение модулей тематических виджетов и отображения всплывающих окон
from datetime import datetime, timezone  # Загрузка класса модуля для работы с временными метками и часовыми поясами
import urllib.request  # Модуль для открытия и чтения URL-адресов, отправки HTTP-запросов
import urllib.error  # Модуль, который содержит классы исключений, возникающих при работе с urllib.request
import threading  # Модуль для работы с потоками (обработка данных в фоне, не блокируя основной поток)
import matplotlib.pyplot as plt  # Подключение модуля для построения графиков в стиле, похожем на MATLAB
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Подключение модуля для отображения графика внутри Tk
import matplotlib.dates as mdates  # Метод для преобразования объектов datetime,а также задавать формат отображения дат
from matplotlib.ticker import FuncFormatter  # Позволяет задать собственную функцию для форматирования меток на осях
import statistics  # Функции для вычисления математических статистик (среднее, стандартное отклонение и т.д.)

BASE_URL = "https://api.coingecko.com/api/v3"  # Адес ресурса API для получения данных
MAX_DAYS = 180  # Максимальное количество дней, за которые собирается информация по изменению курса

MONTH_RUS = {
    1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
    5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
    9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь",
}  # Словарь мазваний месяцев на русском языке

CRYPTO_DICT = {
    "BTC": "bitcoin", "ETH": "ethereum", "USDT": "tether", "USDC": "usd-coin",
    "BNB": "binancecoin", "SOL": "solana", "XRP": "ripple", "ADA": "cardano",
    "MATIC": "matic-network", "TON": "the-open-network",
}  # Словарь 10-ти популярных криптовалют

CRYPTO_HISTORY = {
    "BTC": (
        "Bitcoin (BTC) — первая и крупнейшая криптовалюта, созданная Сатоси Накамото в 2009 году. "
        "Основана на технологии блокчейн, работает без центрального органа управления. "
        "Максимальная эмиссия ограничена 21 млн монет. Используется как средство сбережения, "
        "платёжное средство и основа для DeFi-приложений."
    ),
    "ETH": (
        "Ethereum (ETH) — вторая по капитализации криптовалюта, запущенная Виталиком Бутериным в 2015 году. "
        "Платформа для смарт-контрактов и децентрализованных приложений (dApps). "
        "В 2022 году перешла на proof-of-stake (Merge), что снизило энергопотребление на 99%."
    ),
    "USDT": (
        "Tether (USDT) — стейблкоин, привязанный к доллару США в соотношении 1:1. "
        "Выпущен компанией Tether Limited в 2014 году. Самый популярный стейблкоин по объёму торгов, "
        "широко используется для переводов между биржами и как «тихая гавань» при волатильности рынка."
    ),
    "USDC": (
        "USD Coin (USDC) — стейблкоин, обеспеченный долларом США 1:1. "
        "Выпущен в 2018 году консорциумом Centre (Coinbase и Circle). Считается одним из самых "
        "прозрачных стейблкоинов — резервы проходят регулярный аудит."
    ),
    "BNB": (
        "Binance Coin (BNB) — собственный токен биржи Binance, выпущенный в 2017 году. "
        "Изначально создан на базе Ethereum, позже перенесён на собственный блокчейн BNB Chain. "
        "Используется для оплаты комиссий на бирже, участия в IEO и работы в DeFi-экосистеме BNB Chain."
    ),
    "SOL": (
        "Solana (SOL) — высокопроизводительный блокчейн, запущенный Анатолием Яковенко в 2020 году. "
        "Использует гибридный консенсус proof-of-stake + proof-of-history, достигая до 65 000 TPS. "
        "Одна из самых популярных платформ для DeFi, NFT и Web3-приложений благодаря низким комиссиям."
    ),
    "XRP": (
        "Ripple (XRP) — криптовалюта платёжной сети Ripple, выпущенная в 2012 году. "
        "Ориентирована на быстрые и дешёвые международные переводы для банков и финучреждений. "
        "Максимальная эмиссия — 100 млрд монет, значительная часть удерживается компанией Ripple."
    ),
    "ADA": (
        "Cardano (ADA) — блокчейн-платформа третьего поколения, разработанная Чарльзом Хоскинсоном в 2017 году. "
        "Построена на научно-исследовательском подходе — каждый протокол проходит академическое рецензирование. "
        "Использует консенсус Ouroboros (proof-of-stake), поддерживает смарт-контракты и dApps."
    ),
    "MATIC": (
        "Polygon (MATIC) — масштабирующее решение для Ethereum, запущенное в 2019 году. "
        "Предоставляет фреймворк для построения sidechains и Layer-2 сетей, снижая нагрузку на основной блокчейн. "
        "Используется для быстрых и дешёвых транзакций в экосистеме Ethereum."
    ),
    "TON": (
        "Toncoin (TON) — криптовалюта сети The Open Network, изначально разработанной командой Telegram в 2018 году. "
        "После ухода Telegram проект поддерживается открытым сообществом TON Foundation. "
        "Блокчейн использует proof-of-stake и поддерживает смарт-контракты, микроплатежи и DeFi."
    ),
}

BASE_CURRENCY_DICT = {
    "AUD": "австралийский доллар", "CAD": "канадский доллар", "CHF": "швейцарский франк",
    "CNY": "китайский юань", "EUR": "евро (валюта стран еврозоны)", "GBP": "фунт стерлингов (Великобритания)",
    "JPY": "японская иена", "RUB": "российский рубль", "USD": "американский доллар",
}  # Словарь популярных мировых валют

PERIOD_DAYS = {
    "1 месяц": 30, "2 месяца": 60, "3 месяца": 90,
    "4 месяца": 120, "5 месяцев": 150, "6 месяцев": 180,
}  # Словарь времеенных периодов для отображения информации по изменению курса


class CryptoGraphApp:
    def __init__(self, main):
        self.root = main  # Объект основного окна приложения
        self.results = {}  # Словарь данных (crypto_id, vs_currency) → [[ts_ms, price], ...] — всегда 180 дней
        self.chart_label = None  # Переменная для справочной информации при различных режимах работы приложения
        self.chart_canvas = None  # Переменная для сопряжения объекта Matplotlib с виджетом Tkinter
        self.fetching = False  # Флаг активации процесса выборки данных от API
        self.closing = False  # Флаг закрытия приложения (корректное завершение работы)
        self.setup_gui()  # Создание графических элементов интерфейса приложения

    def setup_gui(self):
        """Метод создания графического интерфейса"""
        self.root.title("CryptoGraph: курс криптовалют")  # Название приложения
        self.root.geometry("900x600")  # Разрешение окна приложения
        self.root.resizable(False, False)  # Запрет на изменение размеров окна

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)  # Перехват закрытия окна

        panel = ttk.Frame(self.root, padding=10)  # Область для размещения списков крипто- и базовых валют, кнопок
        panel.pack(side=tk.TOP, fill=tk.X)

        # ------ # ------ # -- Строка 0: Комбобоксы "Криптовалюта" и "Базовая валюта" -- # ------ # ------ #
        ttk.Label(panel, text="Криптовалюта:", font=('Arial', 10)).grid(row=0, column=1, padx=5, pady=5, sticky="e")
        self.combo_crypto = ttk.Combobox(panel, state="readonly", width=22)
        self.combo_crypto['values'] = [f"{k} — {v}" for k, v in CRYPTO_DICT.items()]  # Наполнение списка криптовалют
        self.combo_crypto.set("")
        self.combo_crypto.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        ttk.Label(panel, text="Базовая валюта:", font=('Arial', 10)).grid(row=0, column=3, padx=5, pady=5, sticky="e")
        self.combo_base = ttk.Combobox(panel, state="readonly", width=22)
        self.combo_base['values'] = [f"{k} — {v}" for k, v in BASE_CURRENCY_DICT.items()]  # Наполнение списка валют
        self.combo_base.set("")  # Начальное значение - None
        self.combo_base.grid(row=0, column=4, padx=4, pady=5, sticky="ew")

        # ------ # --- Строка 1: кнопки "Получить данные", "Очистить кэш" и список "Период" --- # ------ #
        self.btn_get = ttk.Button(panel, text="Получить данные", command=self.on_get_data)  # Кнопка "Получить данные"
        self.btn_get.grid(row=1, column=1, padx=5, pady=5, sticky="e")

        ttk.Label(panel, text="Период:", font=('Arial', 10)).grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.combo_period = ttk.Combobox(panel, state="readonly", width=14)
        self.combo_period['values'] = list(PERIOD_DAYS.keys())  # Наполнение выпадающего списка "Период"
        self.combo_period.set("")  # Начальное значение - None
        self.combo_period.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        self.btn_clear = ttk.Button(panel, text="Очистить кэш", command=self.on_clear_cache)  # Кнопка "Очистить кэш"
        self.btn_clear.grid(row=1, column=4, padx=5, pady=5, sticky="e")

        for raw in range(2):  # Выравнивание ячеек строк
            for col in range(6):
                panel.grid_columnconfigure(col, weight=1)

        self.chart_frame = ttk.Frame(self.root, width=700, height=400)  # Область графика 700×400
        self.chart_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chart_frame.grid_propagate(False)

        self.chart_label = ttk.Label(
            self.chart_frame,
            text="Выберите криптовалюту, базовую валюту и период, за который нужно получить данные",
            font=("Arial", 12),
            justify="center",
            wraplength=600,
        )  # Стартовая подсказка
        self.chart_label.place(relx=0.5, rely=0.5, anchor="center")  # Расположение текста

    def on_close(self):
        """Метод закрытия приложения - вызывается при закрытии окна крестиком или Alt+F4"""
        self.closing = True  # Блокирует callback-и из фоновых потоков

        self.clear_chart_area()  # Очистить область графика и освоюолить ресурсы matplotlib
        plt.close('all')  # Корректно освободить ресурсы GUI и matplotlib

        self.root.destroy()  # Закрытие основного окна приложения

    def lock_combos(self):
        """Метод блокировки списков криптовалюты и базовых валют, период остаётся доступным"""
        self.combo_crypto.config(state="disabled")  # Заблокировать выпадающий список криптовалют
        self.combo_base.config(state="disabled")  # Заблокировать выпадающий список базовых валют
        self.combo_period.config(state="readonly")  # Оставить возможность выбора периода изменения курса

    def unlock_combos(self):
        """Метод разблокировки всех списков (при очистке кэша)"""
        self.combo_crypto.config(state="readonly")
        self.combo_base.config(state="readonly")
        self.combo_period.config(state="readonly")

    def clear_chart_area(self):
        """"Метод очистки области графика"""
        if self.chart_label is not None:  # Сброс текущего состояния переменной для справочной информации
            self.chart_label.destroy()
            self.chart_label = None
        if self.chart_canvas is not None:  # Сброс текущего состояния переменной для моста Matplotlib-Tkinter
            self.chart_canvas.get_tk_widget().destroy()
            self.chart_canvas = None
        plt.close('all')  # Остановить процессы Matplotlib - предотвращает утечку памяти

    def show_history(self, crypto_symbol):
        """"Метод отображения краткую историческую справку по выбранной криптовалюте при выполнении запроса к API"""
        self.clear_chart_area()  # Вызов метода очистки области графика
        text = CRYPTO_HISTORY.get(crypto_symbol, "Историческая справка недоступна.")  # Получение справки по коду валюты
        self.chart_label = ttk.Label(
            self.chart_frame,
            text=f"Загрузка данных...\n\n{text}",
            font=("Arial", 11),
            justify="center",
            wraplength=650,
        )  # Настройки отображения справочной информации
        self.chart_label.place(relx=0.5, rely=0.5, anchor="center")  # Положение текста в области графика

    def fetch_from_api(self, crypto_id, vs_currency, callback):
        """"Метод формирования запроса к API (в отдельном потоке)
                :param crypto_id: код криптовалюты
                :param vs_currency: код базовой валюты
                :param callback: метод, передаваемая в основной поток с необходимыми аргументами
        """
        url = (
            f"{BASE_URL}/coins/{crypto_id}/market_chart"
            f"?vs_currency={vs_currency}&days={MAX_DAYS}&interval=daily"
        )  # Полный url-путь запроса к API

        def get_resp():
            """"Функция запроса к API"""
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    raw = json.loads(resp.read().decode("utf-8"))  # Обработка данных в ответе от API
                prices = raw.get("prices", [])

                if not self.closing:  # Если окно закрылось — не отправляем callback в главный поток
                    self.root.after(0, lambda: callback(prices, None))
            except urllib.error.HTTPError as e:
                msg = f"HTTP {e.code}: {e.reason}" if e.code != 429 else \
                      "Превышен лимит запросов к CoinGecko. Попробуйте позже."
                if not self.closing:
                    self.root.after(0, lambda: callback(None, msg))
            except urllib.error.URLError as e:
                if not self.closing:
                    self.root.after(0, lambda: callback(None, f"Нет соединения: {e.reason}"))
            except Exception as e:
                if not self.closing:
                    self.root.after(0, lambda: callback(None, f"Не удалось получить данные: {e}"))

        thread = threading.Thread(target=get_resp, daemon=True)  # Создание нового потока для обработки запроса
        thread.start()  # Запуск/активация потока

    @staticmethod
    def slice_by_period(prices, days):
        """"Метод среза данных по заданному периоду"""
        if days >= len(prices):
            return prices
        return prices[-days:]

    def on_clear_cache(self):
        """"Метод очистки кэш (а также сбрасывание выбранных полей формы)"""
        if not self.results:
            messagebox.showinfo("Кэш", "Записей пока не существует.")
            return

        self.results.clear()  # Очистка данных по предыдущему запросу
        self.clear_chart_area()  # Очистка области графика
        self.unlock_combos()  # Разблокировка всех комбобоксов
        self.combo_crypto.set("")  # Сброс значения криптовалюты
        self.combo_base.set("")  # Сброс значения базовой валюты
        self.combo_period.set("")  # Сброс значения периода изменеиня курса криптовалюты
        self.chart_label = ttk.Label(
            self.chart_frame,
            text="Кэш очищен. Выберите параметры и нажмите «Получить данные».",
            font=("Arial", 12),
            justify="center",
            wraplength=600,
        )  # Обновление строки-подсказки
        self.chart_label.place(relx=0.5, rely=0.5, anchor="center")  # Положение строки-подсказки
        messagebox.showinfo("Кэш", f"Предыдущие данные очищены. \nВыберите новые параметры поиска.")

    def on_get_data(self):
        """"Метод обработки кнопки 'Получить данные'"""
        if self.fetching:  # Еслм выборка данных уже запущена - игнорировать нажатие
            return

        crypto_sel = self.combo_crypto.get()  # Данные по выбранной криптовалюте
        base_sel = self.combo_base.get()  # Данные по выбранной базовой валюте
        period_sel = self.combo_period.get()  # Период, за который будет отображён график изменения курса

        if not crypto_sel or not base_sel or not period_sel:  # Проверка заполнения полей формы
            messagebox.showwarning("Внимание", "Заполните все поля.")
            return

        crypto_symbol = crypto_sel.split(" — ")[0]  # Код криптовалюты
        crypto_id = CRYPTO_DICT[crypto_symbol]  # Идентификатор криптовалюты для запроса к API
        vs_currency = base_sel.split(" — ")[0]  # Код базовой валюты для запроса к API
        days = PERIOD_DAYS[period_sel]  # Количество дней, за которые будет отображен график изменения курса

        cache_key = (crypto_id, vs_currency)  # Ключ для поиска данных в словаре self.results

        if cache_key in self.results:  # Если данные уже загружены — делаем срез и формируем график изменения курса
            sliced = self.slice_by_period(self.results[cache_key], days)  # Данные за выбранный период
            self.plot_chart(sliced, crypto_symbol, vs_currency, period_sel)  # Создание графика на основе среза данных
            self.lock_combos()  # Заблокировать все комбобоксы, кроме "Период"
            return

        # ------ # -- Если данных нет — показываем историческую справку и запрашиваем асинхронно -- # ------ #
        self.fetching = True  # Изменяем флаг начала выборки данных
        self.btn_get.config(state="disabled", text="Загрузка...")  # Блокируем кнопку "Получить данные"
        self.show_history(crypto_symbol)  # Отображение исторической справки во время выполнения запроса к API

        def on_fetch_complete(prices, error):
            """Callback-метод завершения выборки данных при получении ответа от API"""
            if self.closing or not self.root.winfo_exists():  # Защита: флаг закрытия + проверка существования окна
                return

            self.fetching = False  # Исходное состояние флага начала выборки данных
            self.btn_get.config(state="normal", text="Получить данные")  # Исходное состояние кнопки "Получить данные"

            if error:  # В случае возникновения ошибки при выполнении запроса данных от API
                messagebox.showerror("Ошибка", error)  # Отобразить окно-сообщение об ошибке
                self.clear_chart_area()
                self.chart_label = ttk.Label(
                    self.chart_frame,
                    text="Ошибка загрузки. Попробуйте снова.",
                    font=("Arial", 12), justify="center", wraplength=600,
                )  # Отобразить информацию в главном окне приложения
                self.chart_label.place(relx=0.5, rely=0.5, anchor="center")
                return

            self.results[cache_key] = prices  # Сохранение результатов в переменной self.results
            results_sliced = self.slice_by_period(prices, days)  # Информация за выбранный период для построения графика
            self.plot_chart(results_sliced, crypto_symbol, vs_currency, period_sel)  # Вызов метода построения графика
            self.lock_combos()  # Заблокировать все комбобоксы, кроме "Период"

        self.fetch_from_api(crypto_id, vs_currency, on_fetch_complete)  # Вызов метода формирования запроса к API

    def plot_chart(self, prices, crypto_symbol, vs_currency, period_label):
        """Метод создания графика изменения курса криптовалюты за период времени до текущего момента
                :param prices: данные для построения графика (временные точки, значение курса)
                :param crypto_symbol: идентификатор криптовалюты для обозначения на графике
                :param vs_currency: код базовой валюты
                :param period_label: период изменения курса криптовалюты
                """
        if not prices:  # Проверка наличия данных для выполнения алгоритма построения графика
            messagebox.showerror("Ошибка", "Нет данных для построения графика.")
            return

        self.clear_chart_area()  # Очистка области графика

        dates = [datetime.fromtimestamp(ts / 1000.0, tz=timezone.utc) for ts, _ in prices]  # Преобразование точек даты
        values = [price for _, price in prices]  # Получение данных о значениях курса криптовалюты

        avg = statistics.mean(values)  # Среднее арифметическое всех значений за период
        stdev = statistics.stdev(values) if len(values) > 1 else 0  # Выборочное стандартное отклонение (не менее двух)

        # ------ # ------ # -- Поиск экстремумов и текущего значения -- # ------ # ------ #
        max_idx = values.index(max(values))  # Индекс максимального значения курса криптовалюты за период
        min_idx = values.index(min(values))  # Индекс минимального значения курса криптовалюты за период
        last_idx = len(values) - 1  # Индекс текущего значения курса криптовалюты

        max_price = values[max_idx]  # Максимальное значение курса криптовалюты за период
        min_price = values[min_idx]  # Минимальное значение курса криптовалюты за период
        last_price = values[last_idx]  # Текущее значение курса криптовалюты (сегодня)

        max_date = dates[max_idx]  # Дата максимального значения курса криптовалюты за период
        min_date = dates[min_idx]  # Дата минимального значения курса криптовалюты за период
        last_date = dates[last_idx]  # Дата текущего значения курса криптовалюты

        fig, ax = plt.subplots(figsize=(7, 4), dpi=100)  # Объект холста для графика и ось Х (7 х 4 дюймов)
        ax.plot(dates, values, linewidth=2, color="blue", label=crypto_symbol)  # Построение графика изменения курса

        ax.axhspan(avg - stdev, avg + stdev, color="orange", alpha=0.2,
                   label=f"Среднее ±1σ ({avg:.2f} ± {stdev:.2f})")  # Область разброса данных относительно ср.значения
        ax.axhline(avg, color="orange", linestyle="--", linewidth=1.5,
                   label=f"Среднее ({avg:.2f})")  # Среднее значение курса криптовалюты за период

        # ------ # ------ # --- Маркеры: максимум, минимум, текущее значение --- # ------ # ------ #
        ax.plot(max_date, max_price, marker="^", markersize=6, color="green",
                zorder=5, label=f"Максимум: {max_price:.2f}")
        ax.plot(min_date, min_price, marker="v", markersize=6, color="red",
                zorder=5, label=f"Минимум: {min_price:.2f}")
        ax.plot(last_date, last_price, marker="o", markersize=6, color="purple",
                zorder=5, label=f"Текущее: {last_price:.2f}")

        # ------ # ------ # ------ # ---- Аннотации со значениями ---- # ------ # ------ # ------ #
        date_fmt = "%d.%m.%Y"  # Формат даты для подписи

        ax.annotate(  # Максимум — подпись сверху-справа от точки
            f"{max_price:.2f}\n({max_date.strftime(date_fmt)})",
            xy=(max_date, max_price),
            xytext=(15, 12), textcoords="offset points",
            fontsize=8, color="green", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="green", alpha=0.8),
            arrowprops=dict(arrowstyle="-", color="green", lw=1),
        )

        ax.annotate(  # Минимум — подпись снизу-справа от точки
            f"{min_price:.2f}\n({min_date.strftime(date_fmt)})",
            xy=(min_date, min_price),
            xytext=(15, -25), textcoords="offset points",
            fontsize=8, color="red", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="red", alpha=0.8),
            arrowprops=dict(arrowstyle="-", color="red", lw=1),
        )

        ax.annotate(  # Текущее значение — подпись снизу-слева от точки
            f"{last_price:.2f}\n({last_date.strftime(date_fmt)})",
            xy=(last_date, last_price),
            xytext=(-70, -25), textcoords="offset points",
            fontsize=8, color="purple", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="purple", alpha=0.8),
            arrowprops=dict(arrowstyle="-", color="purple", lw=1),
        )

        def rus_month_formatter(x, _):
            """Функция преобразования названий месяцев на руссом языке по оси X"""
            dt = mdates.num2date(x)
            return MONTH_RUS.get(dt.month, "")

        ax.xaxis.set_major_formatter(FuncFormatter(rus_month_formatter))  # Позиции для основных меток
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Метка в начале каждого месяца
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=0, ha="center")  # Положение меток по оси Х

        # ax.set_title(f"{crypto_symbol} — курс за {period_label} (в {vs_currency})", fontsize=14)
        # ax.set_xlabel("Месяц", fontsize=12)
        # ax.set_ylabel(f"Цена ({vs_currency})", fontsize=12)
        ax.grid(True, linestyle="--", alpha=0.3)  # Показать сетку на области графика
        ax.legend(loc="best", fontsize=8, fancybox=True, shadow=True)  # Показать легенду в свободной области графика
        fig.tight_layout()  # Метод объекта Figure, который автоматически настраивает отступы

        self.chart_canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)  # Передача объекта Matplotlib
        self.chart_canvas.draw()  # Отображение объекта в области self.chart_frame
        self.chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)  # Заполнить всю область


if __name__ == "__main__":
    root = tk.Tk()  # Создание экземпляра рабочего окна приложения tkinter
    app = CryptoGraphApp(root)  # Создание экземпляра коасса CryptoGraphApp
    root.mainloop()  # Активация бесконечного цикла выполнения приложения (до закрытия окна приложения)
