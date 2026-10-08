import json  # Подключение модуля для работы с данными JSON (текстовый формат для обмена структурированными данными)
import tkinter as tk  # Подключение библиотеки Tkinter для создания графических пользовательских интерфейсов (GUI)
from tkinter import ttk, messagebox  # Подключение модулей тематических виджетов и отображения всплывающих окон
from datetime import datetime, timezone, timedelta  # Классы модуля для работы с временными метками и часовыми поясами
import matplotlib.pyplot as plt  # Подключение модуля для построения графиков в стиле, похожем на MATLAB
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Подключение модуля для отображения графика внутри Tk
import matplotlib.dates as mdates  # Метод для преобразования объектов datetime,а также задавать формат отображения дат
import statistics  # Функции для вычисления математических статистик (среднее, стандартное отклонение и т.д.)

FILE_PATH = "crypto_prices_6m.json"  # Дата-файл (результат работы test-request.py) для отладки функций

CRYPTO_DICT = {
    "BTC": "bitcoin", "ETH": "ethereum", "USDT": "tether",
    "USDC": "usd-coin", "BNB": "binancecoin",
}  # # Словарь 5-ти популярных криптовалют

BASE_CURRENCY_DICT = {
    "AUD": "австралийский доллар", "CAD": "канадский доллар", "CHF": "швейцарский франк",
    "CNY": "китайский юань", "EUR": "евро (валюта стран еврозоны)", "GBP": "фунт стерлингов (Великобритания)",
    "JPY": "японская иена", "RUB": "российский рубль", "USD": "американский доллар",
}  # Словарь популярных мировых валют - ИСПОЛЬЗУЕТСЯ ТОЛЬКО USD

PERIOD_LIST = ["1 месяц", "2 месяца", "3 месяца", "4 месяца", "5 месяцев", "6 месяцев"]


# --- Функции для обработки алгоритма приложения ---
def unix_ms_to_datetime(ms):
    """Функция переводит Unix‑таймстамп в миллисекундах в удобный объект даты и времени (datetime)
        в часовом поясе UTC"""
    return datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc)


def get_period_start_end(period_str):
    """Функция возвращает (start_dt, end_dt) для заданного периода
            :param period_str: количество дней, за которые нужно получить данные
            :return: начальная временная метка, конечная временная метка
    """
    months_map = {
        "1 месяц": 1, "2 месяца": 2, "3 месяца": 3,
        "4 месяца": 4, "5 месяцев": 5, "6 месяцев": 6
    }  # Словарь период: количество месяцев
    months = months_map.get(period_str, 6)  # Преобразование словаря
    end_dt = datetime.now(timezone.utc)  # Определение конечной временной метки
    start_dt = end_dt - timedelta(days=months * 30)
    return start_dt, end_dt


def load_data_from_file(path):
    """"Функция загружает и проверяет JSON‑файл с данными о курсах криптовалют
            :param path: путь к файлу с данными изменения курса криптовалют
            :return: список данных за период 6 месяцев
    """
    try:
        with open(path, "r", encoding="utf-8") as f:  # Открываем файл в кодировке UTF‑8 и читаем JSON
            data = json.load(f)
        if "BTC" not in data or not isinstance(data["BTC"], list):  # Проверяем, что в данных есть ключ "BTC" — список
            raise ValueError("В файле нет ключа 'BTC' или он не является списком.")
        return data
    # Обрабатываем ошибки при чтении данных
    except FileNotFoundError:
        messagebox.showerror("Ошибка", f"Файл не найден: {path}")
        return None
    except json.JSONDecodeError:
        messagebox.showerror("Ошибка", "Некорректный JSON в файле.")
        return None
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))
        return None


def filter_points_by_period(points, start_dt, end_dt):
    """Функция среза данных за ппериод: оставляет только точки в диапазоне [start_dt, end_dt].
            :param points: ключ словаря данных (код криптовалюты)
            :param start_dt: начальная временная точка
            :param end_dt: конечная временная точка
            :return: список данных за определённый период
    """
    filtered = []  # Список данных для значений изменения курса
    for ts, price in points:
        dt = unix_ms_to_datetime(ts)  # Переводим таймстамп в дату
        if start_dt <= dt <= end_dt:  # Проверяем, попадает ли точка в диапазон
            filtered.append((ts, price))
    return filtered  # Возвращаем отфильтрованный список


def plot_crypto_chart(data, crypto_symbol="BTC", base_currency="USD", period="6 месяцев"):
    """Функция построения графика по заданным параметрам для отображения изменения курса криптовалюты
            :param data: словарь данных из файла
            :param crypto_symbol: идентификатор криптовалюты для обозначения на графике
            :param base_currency: код базовой валюты
            :param period: период изменения курса криптовалюты
            :return: график изменения курса криптовалюты
    """
    points = data.get(crypto_symbol, data.get("BTC", []))  # Получаем данные для кода выбранной криптовалюты
    if not points:  # Проверка данных перед построением графика
        messagebox.showerror("Ошибка", f"Нет данных для {crypto_symbol}")
        return None

    # ------ # ------ # -- Фильтрация данных за указанный период -- # ------ # ------ #
    start_dt, end_dt = get_period_start_end(period)  # Вычисление начальной и конечной временной точки
    filtered_points = filter_points_by_period(points, start_dt, end_dt)  # Получение списка значений курса криптовалюты

    if len(filtered_points) < 2:  # Проверка количества значений в списке (не менее двух значений)
        messagebox.showwarning("Внимание", "Недостаточно данных для выбранного периода. Попробуйте больший период.")
        points_to_plot = filtered_points if filtered_points else points
    else:
        points_to_plot = filtered_points

    dates = [unix_ms_to_datetime(ts) for ts, _ in points_to_plot]  # Список дат для значений по оси Х
    prices = [price for _, price in points_to_plot]  # Список значений курса криптовалюты для оси Y

    avg_price = statistics.mean(prices)  # Среднее арифметическое всех значений за период
    stdev_price = statistics.stdev(prices) if len(prices) > 1 else 0  # Выборочное отклонение (не менее двух значений)

    fig, ax = plt.subplots(figsize=(7, 4), dpi=100)  # Объект холста для графика и ось Х (7 х 4 дюймов)
    ax.plot(dates, prices, marker='', linestyle='-', linewidth=2, color='blue', label=crypto_symbol)

    # ------ # ------ # ------ # --- Область среднего значения (±1σ) --- # ------ # ------ # ------ #
    ax.axhspan(avg_price - stdev_price, avg_price + stdev_price,    # Область разброса данных относительно ср.значения
               color='orange', alpha=0.2, label=f"Среднее ±1σ ({avg_price:.0f} ± {stdev_price:.0f})")
    ax.axhline(avg_price, color='orange', linestyle='--', linewidth=1.5,
               label=f"Среднее ({avg_price:.0f})")  # Среднее значение курса криптовалюты за период

    # ------ # ------ # ------ # -- Форматирование оси Х: только месяцы на оси X -- # ------ # ------ #
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))  # Позиции для основных меток
    ax.xaxis.set_major_locator(mdates.MonthLocator())  # Метка в начале каждого месяца
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')  # Положение меток по оси Х

    ax.grid(True, linestyle='--', alpha=0.3)  # Показать сетку на области графика
    ax.legend(loc="best", fontsize=8, fancybox=True, shadow=True)  # Показать легенду в свободной области графика
    fig.tight_layout()  # Метод объекта Figure, который автоматически настраивает отступы
    return fig


# ------ # ------ # --- Глобальные переменные --- # ------ # ------ #
chart_canvas = None  # Переменная для сопряжения объекта Matplotlib с виджетом Tkinter
chart_label = None  # Переменная для справочной информации при различных режимах работы приложения
data_cache = None  # Словарь данных (crypto_id, vs_currency) → [[ts_ms, price], ...] — всегда 180 дней


def show_initial_hint():
    """Функция для отображения стартовой подсказки в chart_frame"""
    global chart_label
    if chart_label is not None:  # Проверка состояния переменной chart_label
        chart_label.destroy()
        chart_label = None

    chart_label = ttk.Label(
        chart_frame,
        text="Выберите криптовалюту, базовую валюту и период, за который нужно получить данные",
        font=("Arial", 12),
        justify="center"
    )  # Стартовая подсказка
    chart_label.place(relx=0.5, rely=0.5, anchor="center")  # Расположение текста


def on_get_data():
    """"Функция получения данных из файла crypto_prices_6m.json"""
    global chart_canvas, chart_label, data_cache

    crypto_symbol_full = combo_crypto.get()  # Данные по выбранной криптовалюте
    base_currency_full = combo_base.get()  # Данные по выбранной базовой валюте
    period = combo_period.get()  # Период, за который будет отображён график изменения курса

    if not crypto_symbol_full or not base_currency_full or not period:  # Проверка заполнения полей формы
        messagebox.showwarning("Внимание", "Заполните все поля перед получением данных.")
        return

    # Извлекаем короткие коды из строк вида "BTC — bitcoin"
    crypto_symbol = crypto_symbol_full.split(" — ")[0]  # Форматирование кода криптовалюты
    base_currency = base_currency_full.split(" — ")[0]  # Форматирование кода базовой валюты

    if data_cache is None:  # Загружаем данные, если ещё нет в кэше
        data_cache = load_data_from_file(FILE_PATH)
        if data_cache is None:
            return

    if chart_label is not None:  # Удаляем подсказку, если она есть
        chart_label.destroy()
        chart_label = None

    if chart_canvas is not None:  # Если уже есть график — удаляем его
        chart_canvas.get_tk_widget().destroy()
        chart_canvas = None

    fig = plot_crypto_chart(data_cache, crypto_symbol, base_currency, period)  # Получение графика изменения курса
    if fig is None:  # Проверка данных перед отобоажением
        show_initial_hint()  # Возвращаем подсказку
        return

    chart_canvas = FigureCanvasTkAgg(fig, master=chart_frame)  # Передача объекта Matplotlib
    chart_canvas.draw()  # Отображение объекта в области chart_frame
    chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)  # Заполнить всю область


def on_clear_cache():
    """"Функция очистки кэш"""
    global data_cache, chart_canvas, chart_label

    data_cache = None  # Сброс словаря данных

    if chart_canvas is not None:  # Удаляем график, если он есть
        chart_canvas.get_tk_widget().destroy()
        chart_canvas = None

    show_initial_hint()  # Возвращаем подсказку

    messagebox.showinfo("Кэш очищен", "Данные из файла будут загружены заново "
                                      "\nпри следующем нажатии «Получить данные».")  # Выводим окно-сообщение


# --- GUI ---
root = tk.Tk()  # Создание экземпляра рабочего окна приложения tkinter
root.title("CryptoGraph: курс криптовалют")  # Название приложения
root.geometry("900x600")  # Разрешение окна приложения
root.resizable(False, False)  # Запрет на изменение размеров окна

# Панель выбора данных их выпадающих списков
btn_panel = ttk.Frame(root, padding=10)
btn_panel.pack(side=tk.TOP, fill=tk.X)

# Строка 0: Криптовалюта и Базовая валюта
ttk.Label(btn_panel, text="Криптовалюта:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
combo_crypto = ttk.Combobox(btn_panel, state="readonly", width=22)
combo_crypto['values'] = [f"{k} — {v}" for k, v in CRYPTO_DICT.items()]
combo_crypto.current(0)
combo_crypto.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

ttk.Label(btn_panel, text="Базовая валюта:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
combo_base = ttk.Combobox(btn_panel, state="readonly", width=22)
combo_base['values'] = [f"{k} — {v}" for k, v in BASE_CURRENCY_DICT.items()]
combo_base.current(8)  # USD по умолчанию
combo_base.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

# Строка 1: Период
ttk.Label(btn_panel, text="Период:").grid(row=1, column=1, padx=5, pady=5, sticky="e")
combo_period = ttk.Combobox(btn_panel, state="readonly", width=22)
combo_period['values'] = PERIOD_LIST
combo_period.current(5)  # "6 месяцев" по умолчанию
combo_period.grid(row=1, column=2, padx=5, pady=5, sticky="ew")

# Растягивание колонок для центрирования
btn_panel.grid_columnconfigure(0, weight=1)
btn_panel.grid_columnconfigure(1, weight=1)
btn_panel.grid_columnconfigure(2, weight=1)
btn_panel.grid_columnconfigure(3, weight=1)

# Кнопки "Получить данные" и "Очистить кэш"
get_btn_frame = ttk.Frame(root)
get_btn_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

btn_get = ttk.Button(get_btn_frame, text="Получить данные", command=on_get_data)
btn_get.pack(side=tk.LEFT, padx=(320, 10))

btn_clear = ttk.Button(get_btn_frame, text="Очистить кэш", command=on_clear_cache)
btn_clear.pack(side=tk.LEFT)

# Область графика
chart_frame = ttk.Frame(root, width=700, height=400)
chart_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
chart_frame.grid_propagate(False)

show_initial_hint()  # Стартовая подсказка

root.mainloop()  # Активация бесконечного цикла выполнения приложения (до закрытия окна приложения)
