РАЗБОР ЗАДАНИЯ НА УРОКЕ (19.09)
```
# Программа с оконным интерфейсом 
from tkinter import * 
from tkinter 
import messagebox as mb 
import requests 
import json 

def exchange(): 
    code = entry.get().upper() 
    if code: 
        try: 
            response = requests.get(f'https://open.er-api.com/v6/latest/USD') 
            response.raise_for_status() 
            data = response.json() 
            if code in data['rates']: 
                exchange_rate = data['rates'][code] 
                mb.showinfo("Курс обмена", f"Курс к доллару: {exchange_rate:.1f} {code} за 1 доллар") 
            else:
                mb.showerror("Ошибка", f"Валюта {code} не найдена") 
        except Exception as e: 
            mb.showerror("Ошибка", f"Ошибка: {e}") 
      else: 
          mb.showwarning("Внимание", "Введите код валюты") 
          
# Создание графического интерфейса 
window = Tk() 
window.title("Курс обмена валюты к доллару") 
window.geometry("360x180") 

Label(text="Введите код валюты:").pack(padx=10, pady=10) 
entry = Entry() entry.pack(padx=10, pady=10) 
Button(text="Получить курс обмена к доллару", command=exchange).pack(padx=10, pady=10) 
window.mainloop()
```


ЗАДАНИЕ 5.  
Добавьте в проект, разработанный на уроке, вторую базовую валюту, чтобы он выводил сразу два курса обмена одновременно.   
Получайте данные в формате JSON.  
Добавьте еще одно поле для выбора второй базовой валюты.  
Измените функцию exchange так, чтобы она запрашивала и отображала курсы обмена для обеих базовых валют  
относительно выбранной целевой валюты.  
При выполнении домашнего задания используйте Git и сделайте не менее трех коммитов.  

Азбука цифры. Профессия Python-программист (ОБУЧЕНИЕ)
