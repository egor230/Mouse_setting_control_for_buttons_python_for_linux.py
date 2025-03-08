import time, json, os, copy, psutil, threading, re,  glob, subprocess, psutil, pyautogui
from tkinter import *
from tkinter.ttk import Combobox  # импортируем только то что надо
from tkinter import ttk
from PIL._tkinter_finder import tk
from tkinter import messagebox
from tkinter import filedialog
from os import path

from apport import logging
from deepdiff import DeepDiff
import keyboard as keybord_from # Управление мышью
from pynput import mouse, keyboard
from pynput.mouse import Button as Button_Controller, Controller
from pynput.keyboard import Key, Listener # Создаем экземпляр класса Controller для управления мышью
def show_message(): # Вызов функции для отображения окна
  messagebox.showinfo("Ошибка", "Требуется запустить с root правами")
def show_message1(): # Вызов функции для отображения окна
  messagebox.showinfo("Ошибка", "Программа уже запущена")

class save_dict:
    def __init__(self):
        self.jnson = {}  # новые настройки.
        self.old_data = {} #старые настройки.
        self.name_games = []  # названия игр
        self.labels = []  # надписи.
        self.var_list = []  # галочки
        self.labels_with_checkmark = {} # словарь надписи с галочками
        self.box_values = [] # Значения боковых кнопок
        self.cur_app=""# Текущая игра.
        self.count=0 # Индекс текущей игры.
        self.id=0 # id устройство.
        self.mouse_button_press = []  # какие кнопки должны быть удержены.
        self.dict_id_values = {}
        self.data="settings control mouse buttons.json"  # файл настроек.
        self.path_current_app='' # Текущий путь к игре.
        self.add_button_start = 0
        self.process_id_active = 0 # id активного окна
        self.pid_and_path_window={} # Словарь игр и путей к ним.
        self.current_path_game = "" # Путь к запущенной к игре.
        self.prev_game = ""
        self.thr=0
    def get_thread(self):  # Сохранить текущий путь к игре
      return self.thr

    def set_thread(self, thr1):
      self.thr= thr1

    def get_current_path_game(self):  # Сохранить текущий путь к игре
      return self.current_path_game

    def set_current_path_game(self, current_path_game):
      self.current_path_game= current_path_game

    def get_prev_game(self):  # Сохранить текущий путь к игре
      return self.prev_game

    def set_prev_game(self, prev_game):
      self.prev_game= prev_game
    def get_pid_and_path_window(self):#
      return self.pid_and_path_window

    def set_pid_and_path_window(self, pid_and_path_window):  #
      self.pid_and_path_window = pid_and_path_window

    def get_process_id_active(self):
      return self.process_id_active

    def set_process_id_active(self, process_id_active):  #
      self.process_id_active = process_id_active

    def get_id(self):
       return self.id

    def get_add_button_start(self):# Получить кнопку.
       return self.add_button_start

    def set_add_button_start(self, add_button_start):# Установить кнопку.
       self.add_button_start = add_button_start

    def get_current_app_path(self):# Получить путь текущего окна.
       return self.path_current_app

    def set_current_app_path(self, app):# Установить путь текущего окна.
       self.path_current_app = app
    def return_name_games(self):  # Вернуть список названия игр.
        name_games =self.name_games
        return self.name_games

    def return_mouse_button_press(self):
       return self.mouse_button_press

    def return_labels(self):
       return self.labels

    def return_var_list(self):
       return self.var_list

    def return_labels_with_checkmark(self):
       return self.labels_with_checkmark

    def return_box_values(self):
       return self.box_values

    def return_list_mouse_button_press(self): # какие кнопки должны быть удержанны для текущий игры.
     return list(self.jnson["mouse_press"][self.cur_app])

    def save_mouse_button_press(self, list_mouse_button_press=None,  mouse_button_press=None):
      if mouse_button_press == None:
        mouse_button_press= self.mouse_button_press
      self.mouse_button_press=mouse_button_press
      if list_mouse_button_press == None:
       list_mouse_button_press=[] # Сохранить список какие кнопки должны быть удержанны.
       for i in range(len(mouse_button_press)):
         list_mouse_button_press.append(mouse_button_press[i].get())

      self.jnson["mouse_press"][self.cur_app]= list(list_mouse_button_press)

    def save_jnson(self, jn):# сохранить  новые настройки
     self.jnson= jn

    def save_old_data(self, jnson):# сохранить начальные настройки.
      self.old_data= copy.deepcopy(jnson)
      self.jnson = jnson

    def return_jnson(self):# Вернуть новые настройки.
       return self.jnson

    def return_old_data(self):
       return self.old_data

    def set_cur_app(self, cur_app):# установить текущего игру
     self.cur_app=str(cur_app)
     self.jnson["current_app"]=self.cur_app

    def get_cur_app(self):
       return self.cur_app

    def set_count(self, count):
        self.count=count
        return self.count
    def get_count(self):
       return self.count

    def set_id(self, id):
        self.id=id
    def set_values_box(self):
     box_value=self.jnson["key_value"][self.cur_app]
     for i in range(len(self.box_values)):
       self.box_values[i].set(box_value[i])
    def set_box_values(self, add_button_start):  # Установить значение для выпадающего списка.
      self.reset_id_value()
      res = self.jnson
      key_values = res["key_value"]
      d = list(res["paths"].keys())  # получить словарь путей и имен файлов.  # print(self.cur_app)    # print(self.count)      # print(d[self.count])
      self.set_cur_app(d[self.count])  # установить текущую активную строку.
      self.jnson["current_app"] = d[self.count]  # Сохранить текущую активную строку.
      if add_button_start["state"] == "disabled":  # Если выкл кнопку старт.
        add_button_start["state"] = "normal"  # вкл кнопку старт.       # print(self.jnson["current_app"])
      self.set_values_box()
      return self
    def write_to_file(self, new_data):
     json_string = json.dumps(new_data, ensure_ascii=False, indent=2)   #self.data # файл настроек.
     with open(self.data, "w", encoding="UTF-8") as w:
       w.write(json_string)  # сохранить изменения в файле настроек.
     #data1=self.data.replace(' ','\ ')# Преобразовать путь до файл настроек.
     file_relus = '''#!/bin/bash\n
                     chmod a+rw \"{0}\" '''.format(self.data)
     subprocess.call(['bash', '-c', file_relus])# Дать доступ на чтение и запись любому
     return self

    def get_list_ids(self):# Получение списка id устройств.
      # Команда shell для получения списка идентификаторов устройств ввода (мышей), которые подключены к системе.
      get_ids = '''#!/bin/bash
      ids=$(xinput list | grep -Ei "id=[0-9]+" | grep -oE "id=[0-9]+" | cut -d= -f2)
       for id in $ids; do
        output=$(xinput get-button-map "$id" 2>&1)
        # Исключаем сообщения об ошибках, добавляя проверки на наличие ошибок
        if [[ $output != *"device has no buttons"* && $output != *"X Error of failed request:"* ]]; then
            echo "$id:$output"
        fi
       done'''

      # Выполнение вышеуказанной команды shell в подпроцессе и декодирование результата в строку.
      id_list = subprocess.check_output(['bash', '-c', get_ids]).decode().splitlines()
      button_map = {}      # Создание словаря для хранения соответствия между идентификаторами устройств и их кнопками.

      # Перебор всех элементов в списке id устройств.
      for item in id_list:        # Разделение элемента на ключ (id устройства) и значение (кнопок).
        key, value = item.split(':', 1)
        button_map[int(key)] = value.strip()

     # Добавление в словарь button_map кнопок устройства с соответствующим идентификатором.

      self.dict_id_values = button_map      # Сохранение карты кнопок в атрибут объекта.
      id_list = list(button_map.keys())      # Сохранение списка идентификаторов в переменной id_list.
      self.id = id_list[0]    # Установка первого устройства в списке как текущего id для использования.
      id_list=sorted(id_list)
      return id_list      # Возвращение списка id устройств для дальнейшего использования.

    def get_state_thread(self):
       return self.thread

    def set_default_id_value(self, add_button_start):# Вернуть значения по умолчанию
      self.thread = True  # Прервать выполнение потока обработчика нажатий.
      add_button_start["state"] = "normal"  # выкл кнопку старт.
      for id in self.dict_id_values:
        st= str(self.dict_id_values[id])
        set_button_map = '''#!/bin/bash
          sudo xinput set-button-map {0} {1}
          '''.format(id, st)
        subprocess.call(['bash', '-c', set_button_map])

    def reset_id_value(self):  # Сброс настроек текущего id устройства.       #  print(self.id)
      d = '1 2 3 4 5 6 7 8 9'  #      print("reset_id_value")
      set_button_map = '''#!/bin/bash
          sudo xinput set-button-map {0} {1}
          '''.format(self.id, d)
      subprocess.call(['bash', '-c', set_button_map])

    def get_default_id_value(self):#
      d = self.dict_id_values[self.get_id()]
      d_copy = copy.deepcopy(d)
      d='1 2 3 4 5 6 7 8 9'
      return d
    def write_in_log(self, text=" error"):# Запись ошибок.
       with open("log.txt", "a") as f:
         f.write(str(text)+"\n")

       file_relus = '''#!/bin/bash
                     chmod a+rw {}   '''.format("log.txt")
       subprocess.call(['bash', '-c', file_relus])# Дать доступ на чтение и запись любому

    def preparation(self, dictio, games_checkmark_paths):  # games_checkmark_paths  список путей к играм
      id = self.get_id()  # Получаем id устройства
      old = self.get_default_id_value().split()  # Получить конфигурацию по умолчанию
      game = str(self.get_cur_app())

      key = dictio["key_value"][game]
      a1, a2, a3, a4, a5, a6, k = get_keys_buttons(key)
      list_mouse_check_button = self.return_mouse_button_press()  # print(key)  # какие кнопки будут работать.
      press_button = dictio['mouse_press'][game]
      self.reset_id_value()  # Сброс настроек текущего id устройства.
      list_buttons = {"Button.button11": a1, a1: 1, "Button.button12": a2, a2: 2,  # Правая и средняя кнопка на мыши.
                      "Button.button13": a3, a3: 3, "Button.button14": a4, a4: 4,  # Колёсико мыши вверх и вниз.
                      "Button.button16": a5, a5: 5, "Button.button15": a6, a6: 6}  # , "Button.button11"]
      if key != defaut_list_mouse_buttons:  # словарь называния кнопок мыши их значения для эмуляции
        for i in range(len(old)):
          if int(old[i]) in k:
            old[i] = k[int(old[i])]  # Преобразование списка обратно в строку
        # Обновление списка с заменой элементов из словаря
      return key, id, old, a1, a2, a3, a4, a5, a6, k, press_button, game, list_buttons
def remove_before_second_slash(path):
  if path == 'C:/Windows/explorer.exe':
    return path
  parts = path.split('/', 3)    # Split the path at the first two slashes
  if len(parts) >= 4:  # Check if there are at least two slashes
    return '/' + parts[3]    # Return the part after the second slash with a leading slash
  else:   # In case the path does not have two slashes, return an empty string
    return 'C:/Windows/explorer.exe'
def is_path_in_list(path, path_list):#проверяет, содержится ли путь в списке путей.
    return any(path in item for item in path_list)
def get_index_of_path(path, path_list):
  index = next(index for index, item in enumerate(path_list) if path in item)
  return index#находит индекс пути в списке путей и возвращает соответствующий элемент списка.
get_user_name = f'''#!/bin/bash
current_user=$(whoami);
echo $current_user
exit;# Завершаем выполнение скрипта
'''
user = subprocess.run(['bash'], input=get_user_name, stdout=subprocess.PIPE, text=True).stdout.strip()
get_main_id = '''#!/bin/bash # Получаем идентификатор активного окна
    active_window_id=$(xdotool getactivewindow 2>/dev/null)
    if [ -n "$active_window_id" ]; then
        process_id_active=$(xdotool getwindowpid "$active_window_id" 2>/dev/null)
        echo "$process_id_active"
    else
        echo "0"  # Или любое значение по умолчанию, если нет активного окна
    fi
    exit'''
def get_pid_and_path_window():# Получаем идентификатор активного окна
 try:
    process_id = int(subprocess.run(['bash'], input=get_main_id, stdout=subprocess.PIPE, text=True).stdout.strip())
    a = []
    result = str(subprocess.run(['ps', 'aux'], stdout=subprocess.PIPE, text=True).stdout)  # # print(result)
    lines = result.split('\n')
    a = [line for line in lines if user in line]  # Убираем 'root' из условия
    data_dict = {}
    pattern = r"(/mnt/.*?\.exe)"  # Регулярное выражение для поиска полного пути, начинающегося с /mnt/
    # Регулярное выражение для поиска полного пути, начинающегося с /mnt/
    for i in a:
      dir_process_name = i.split(maxsplit=10)[10].replace('\\', '/')  # Извлекаем нужную часть строки
      match = re.search(pattern, dir_process_name)

      if match:
        file_path = match.group(1)  # Получаем полный путь
        pid_id = int(i.split()[1])  # id потока
        if ".exe" in file_path:# нужно добавить только те, что имеют exe
          data_dict[pid_id] = file_path  # Добавляем в словарь pid и путь.
    # Вариант 2 ещё один поиск
    pattern = [r"(.*.exe)",r"(.*.EXE)"]
    for i in a:
     for p in pattern:      # print(i)
      dir_process_name = i.split(maxsplit=10)[10].replace('\\', '/')  # Извлекаем нужную часть строки
      match = re.search(p, dir_process_name)
      if match:
       file_path = match.group(1)  # Получаем полный путь
       pid_id = int(i.split()[1])  # id потока
       if ".exe" in file_path or ".EXE" in file_path:
        # Разделим строку после .sh
        file_path_after_sh = file_path.split('.sh', 1)[-1].strip()  # Получаем путь после .sh
        data_dict[pid_id] = file_path_after_sh  # Сохраняем только путь после .sh
    return data_dict
 except:
     pass
def check_current_active_window(dict_save, games_checkmark_paths):# Получаем путь  активного окна
 try:
  data_dict=dict_save.get_pid_and_path_window()
  process_id_active=dict_save.get_process_id_active()  # print(data_dict)
  games_checkmark_paths1 = [remove_before_second_slash(path) for path in games_checkmark_paths] # input() # print(data_dict)  print(games_checkmark_paths)
  if data_dict[process_id_active]:
    file_path=data_dict[process_id_active]#
    mnt_index = file_path.rfind('/mnt')
    if mnt_index != -1:    # Извлекаем часть строки от "/mnt" до конца
        file_path = file_path[mnt_index:]

    if is_path_in_list(file_path, games_checkmark_paths):  #     # print( games_checkmark_paths[get_index_of_path(file_path, games_checkmark_paths)])     # print(dict_save.get_pid_and_path_window()[dict_save.get_process_id_active()])     print("000000")
     return games_checkmark_paths[get_index_of_path(file_path, games_checkmark_paths)]  # активного окна
    file_path= file_path[1:].replace(':', '')  # Удаляем первую букву и ':\'    # print(file_path)    # print(games_checkmark_paths1)
    if is_path_in_list(file_path, games_checkmark_paths1):  # Portproton     print("Portproton ")     # print(file_path)  #  print(games_checkmark_paths)
     return games_checkmark_paths[get_index_of_path(file_path, games_checkmark_paths1)]
  return dict_save.get_prev_game()# если мы ничего не нашли, вернуть предыдущую конфигурацию.
 except:
   return dict_save.get_prev_game()
def show_list_id_callback():
  show_list_id = f'''#!/bin/bash
   gnome-terminal -- bash -c 'xinput list;
   read;   exec bash' '''#показать список устройств в терминале
  subprocess.run(['bash', '-c', show_list_id])

KEYS = {" ": 0x0,"LBUTTON": 'mouse left', "RBUTTON": 'mouse right', "WHEEL_MOUSE_BUTTON": "mouse middle",
        "WHEEL_MOUSE_UP" : "WHEEL_MOUSE_UP", "MBUTTON": 0x04, "SCROLL_UP": "scroll_up",
        "SCROLL_DOWN" : "scroll_down", "XBUTTON1": 0x05, "XBUTTON2": 0x06, "BACKSPACE": "BackSpace",
        "TAB": "Tab", "CLEAR": 0x0C, "RETURN": "Return", "KP_Enter" : "KP_Enter",
         "Shift_L":"Shift_L", "CONTROL": "CONTROL", "MENU": 0x12, "PAUSE": 0x13, "CAPITAL": 0x14,
        "KANA": 0x15, "JUNJA": 0x17, "FINAL": 0x18, "KANJI": 0x19, "ESCAPE": 0x1B,
        "CONVERT": 0x1C, "NONCONVERT": 0x1D, "ACCEPT": 0x1E, "MODECHANGE": 0x1F, "SPACE": "space",
        "PRIOR": 0x21, "NEXT": 0x22, "END": "0x23", "HOME": "Home", "LEFT": 0x25, "UP": 0x26,
        "RIGHT": 0x27, "DOWN": 0x28, "SELECT": 0x29, "PRINT": 0x2A, "EXECUTE": 0x2B, "SNAPSHOT": 0x2C,
        "INSERT": 0x2D, "DELETE": "Delete", "HELP": 0x2F,  "LWIN": "Super_L", "RWIN": "Super_R",

        "KEY0": 0, "KEY1": 1, "KEY2": 2, "KEY3": 3, "KEY4": 4, "KEY5": 5, "KEY6": 6,
        "KEY7": 7, "KEY8": 8, "KEY9": 9, "A": "A", "B": "B", "C": "C", "D": "D", "E": "E", "F": "F",
        "G": "G", "H": "H", "I": "I", "J": "J", "K": "K", "L": "L", "M": "M", "N": "N", "O": "O",
        "P": "P", "Q": "Q", "R": "R", "S": "S", "T": "T", "U": "U", "V": "V", "W": "W", "X": "X", "Y": "Y",
        "Z": "Z",

        "APPS": 0x5D, "SLEEP": 0x5F, "NUMPAD0": 0x60, "NUMPAD1": 79,
        "NUMPAD2": 80, "NUMPAD3": 81, "NUMPAD4": 82, "NUMPAD5": 83, "NUMPAD6": 84, "NUMPAD7": 85,
        "NUMPAD8": 86, "NUMPAD9": 87, "MULTIPLY": 0x6A, "ADD": 78, "SEPARATOR": 0x6C, "SUBTRACT": 0x6D,
        "DECIMAL": 0x6E, "DIVIDE": 0x6F, "F1": "F1", "F2": "F2", "F3": "F3", "F4": "F4", "F5": "F5",
        "F6": "F6", "F7": "F7", "F8": "F8", "F9": "F9", "F10": "F10", "F11": "F11", "F12": "F12",

        "F13": 0x7C, "F14": 0x7D, "F15": 0x7E, "F16": 0x7F, "F17": 0x80, "F18": 0x81, "F19": 0x82, "F20": 0x83, "F21": 0x84,
        "F22": 0x85, "F23": 0x86, "F24": 0x87,"NUMLOCK": "Num_Lock", "SCROLL": "Scroll_Lock",
         "OEM_FJ_JISHO": 0x92, "OEM_FJ_MASSHOU": 0x93,
        "OEM_FJ_TOUROKU": 0x94, "OEM_FJ_LOYA": 0x95, "OEM_FJ_ROYA": 0x96, "LSHIFT": "Shift_L", "RSHIFT": "Shift_R", "LCONTROL": "ISO_Next_Group",
        "RCONTROL": "Control_R",  "LMENU": 0xA4, "RMENU": 0xA5, "BROWSER_BACK": 0xA6,
        "BROWSER_FORWARD": 0xA7, "BROWSER_REFRESH": 0xA8, "BROWSER_STOP": 0xA9, "BROWSER_SEARCH": 0xAA, "BROWSER_FAVORITES": 0xAB,
        "BROWSER_HOME": 0xAC, "VOLUME_MUTE": 0xAD, "VOLUME_DOWN": 0xAE,
        "VOLUME_UP": 0xAF, "MEDIA_NEXT_TRACK": 0xB0, "MEDIA_PREV_TRACK": 0xB1, "MEDIA_STOP": 0xB2, "MEDIA_PLAY_PAUSE": 0xB3, "LAUNCH_MAIL": 0xB4, "LAUNCH_MEDIA_SELECT": 0xB5, "LAUNCH_APP1": 0xB6,
        "LAUNCH_APP2": 0xB7, "OEM_1": 0xBA, "OEM_PLUS": 0xBB, "OEM_COMMA": 0xBC, "OEM_MINUS": 0xBD, "OEM_PERIOD": 0xBE, " OEM_2": 0xBF, "OEM_3": 0xC0, "ABNT_C1": 0xC1, "ABNT_C2": 0xC2, "OEM_4": 0xDB,
        "OEM_5": 0xDC, "OEM_6": 0xDD, "OEM_7": 0xDE, "OEM_8": 0xDF, "OEM_AX": 0xE1,
        "OEM_102": 0xE2, "ICO_HELP": 0xE3, "PROCESSKEY": 0xE5, "ICO_CLEAR": 0xE6, "PACKET": 0xE7, "OEM_RESET": 0xE9, "OEM_JUMP": 0xEA, "OEM_PA1": 0xEB, "OEM_PA2": 0xEC, "OEM_PA3": 0xED,
        "OEM_WSCTRL": 0xEE, "OEM_CUSEL": 0xEF, "OEM_ATTN": 0xF0, "OEM_FINISH": 0xF1, "OEM_COPY": 0xF2, "OEM_AUTO": 0xF3, "OEM_ENLW": 0xF4, "OEM_BACKTAB": 0xF5, "ATTN": 0xF6, "CRSEL": 0xF7, "EXSEL": 0xF8, " EREOF": 0xF9, "PLAY": 0xFA, "ZOOM": 0xFB, "PA1": 0xFD, " OEM_CLEAR": 0xFE
        }

LIST_MOUSE_BUTTONS=["Левая кнопка","Правая кнопка","Средняя","Колесико вверх","Колесико вниз","1 боковая","2 боковая"]
LIST_KEYS = list(KEYS.keys())
defaut_list_mouse_buttons=['LBUTTON', 'RBUTTON', 'WHEEL_MOUSE_BUTTON', 'SCROLL_UP', 'SCROLL_DOWN', 'XBUTTON1', 'XBUTTON2']
class ToolTip(object):

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 27
        y = y + cy + self.widget.winfo_rooty() +7
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=self.text, justify=LEFT, background="#ffffe0", relief=SOLID, borderwidth=1,
                      font=("tahoma", "10", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def CreateToolTip(widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)
def hide_tooltip(self, event):
  if self.tooltip:
    self.tooltip.destroy()
    self.tooltip = None

class Job(threading.Thread):
 def __init__(self, key, *args, **kwargs):
  self.key=key
  self.sw=True
  self.hook_flag_mouse=True  # захват кнопки мыши.
  super(Job, self).__init__(*args, **kwargs)
  self.__flag = threading.Event() # The flag used to pause the thread
  self.__flag.set() # Set to True
  self.__running = threading.Event() # Used to stop the thread identification
  self.__running.set() # Set running to True

 def run(self):
  time.sleep(0.00001)
  while self.__running.is_set():
   self.__flag.wait() # return immediately when it is True, block until the internal flag is True when it is False
   time.sleep(0.008)
   if self.key== "SCROLL_UP":
     thread = threading.Thread(target= key_work.mouse_wheel_up)
     thread.daemon = True  # Установка атрибута daemon в значение True
     thread.start()      # key_work.mouse_wheel_up()
   if self.key== "SCROLL_DOWN":
     thread1 = threading.Thread(target= key_work.mouse_wheel_donw)
     thread1.daemon = True  # Установка атрибута daemon в значение True
     thread1.start()      # key_work.mouse_wheel_donw()   # keybord_from.press(self.key)
   # keybord_from.release(self.key)   # print(self.key)   # directinput.keyDown(str( self.key).lower())
 def pause(self):
  self.__flag.clear() # Set to False to block the thread

 def resume(self):
  self.__flag.set() # Set to True, let the thread stop blocking
 def stop(self):
  self.__flag.set() # Resume the thread from the suspended state, if it is already suspended
  self.__running.clear() # Set to False

 def set_sw(self, value):
   self.sw=value
 def get_sw(self):
  return self.sw
 def set_hook_flag_mouse(self, value):
   self.hook_flag_mouse=value
 def get_hook_flag_mouse(self):
  return self.hook_flag_mouse
def return_job(key, number):
  a1 = Job(key[number])
  a1.start()
  a1.pause()
  return a1
def get_keys_buttons(key):  # Получение конфигуляции кнопок.
  a1, a2, a3, a4, a5, a6, k = 0, 0, 0, 0, 0, 0, {}  # правая кнопка мыши, средняя,
  # колёсико мыши вверх, колёсико мыши вниз, первая боковая кнопка,  вторая боковая кнопка, словарь print(key)
  if key[1] == "RBUTTON":  # Если на правую кнопку нечего не назначено.        print("lk")
    pass
  else:
    a1 = return_job(key, 1)  # эмулировать правую кнопку
    k[3] = '11'
  if key[2] == " " or key[2] == "WHEEL_MOUSE_BUTTON":  # если на средную кнопку нечего не назначено.
    pass
  else:
    a2 = return_job(key, 2)  # эмулировать среднюю кнопку
    k[2] = '12'
  if key[3] == "SCROLL_UP":  # если на колёсико мыши вверх нечего не назначено.
    pass
  else:
    a3 = return_job(key, 3)  # эмулировать колёсико мыши вверх
    k[4] = '13'
  if key[4] == " " or key[4] == "SCROLL_DOWN":  # если на колёсико мыши вниз нечего не назначено.
    pass
  else:
    a4 = return_job(key, 4)  # эмулировать колёсико мыши вниз
    k[5] = '14'

  if key[5] == "XBUTTON1":  # если на боковую кнопку нечего не назначено.
    pass
  else:
    a5 = return_job(key, 5)  # эмулировать первую боковую кнопку
    k[9] = '16'
  if key[6] == "XBUTTON2":  # если на боковую кнопку нечего не назначено.
    pass
  else:
    a6 = return_job(key, 6)  # эмулировать вторую боковую кнопку
    k[8] = '15'
  return a1, a2, a3, a4, a5, a6, k
mouse_controller = mouse.Controller()
class work_key:
  def __init__(self):
    self.keys_list = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's', 'd', 'f', 'g',
                      'h', 'j', 'k', 'l', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ]
    self.keys_list1 = ['BackSpace', 'Tab', 'Return', 'KP_Enter', 'Escape', 'Delete', 'Home', 'End', 'Page_Up',
   'Page_Down', 'F1', 'Up', 'Down', 'Left', 'Right', 'Control_L', 'ISO_Next_Group', 'Control_R', 'Shift_L', 'Shift_R', 'Alt_L', 'Alt_R', 'Super_L',
    'Super_R', 'Caps_Lock', 'Num_Lock', 'Scroll_Lock', 'space', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12']

  def mouse_wheel_up(self):  #
    mouse_wheel = '''#!/bin/bash
        xdotool click  {0}    '''.format(4)
    subprocess.call(['bash', '-c', mouse_wheel])
  def mouse_wheel_donw(self):  #
    mouse_wheel = '''#!/bin/bash
        xdotool click  {0}    '''.format(5)
    subprocess.call(['bash', '-c', mouse_wheel])
  def mouse_right_donw(self):  #Правая кнопки мыши

    # mouse_controller.click(mouse.Button.right)
    # pyautogui.click(button='right')
    mouse_right_donw1 = '''#!/bin/bash
        xdotool click  {0}    '''.format(3)
    subprocess.call(['bash', '-c', mouse_right_donw1])
  def mouse_middle_donw(self):  #Средняя.
      # Нажимаем среднюю кнопку мыши
      pyautogui.click(button='middle')
      mouse_wheel = '''#!/bin/bash
          xdotool click  {0}    '''.format(2)
      # subprocess.call(['bash', '-c', mouse_wheel])
  def key_press(self, key, number_key):# Нажать.
    press = '''#!/bin/bash
    xte 'keydown {0}'  '''
    if key in self.keys_list1:
     thread1 = threading.Thread(target=lambda: subprocess.call(['bash', '-c', press.format(key)]))
     #thread1.daemon = True  # Установка атрибута daemon в значение True
     thread1.start()
     return 0
    key1= key.lower()    # print(key1)
    if key1 in self.keys_list:
      thread = threading.Thread(target=lambda: subprocess.call(['bash', '-c', press.format(key)]))
      #thread.daemon = True  # Установка атрибута daemon в значение True
      thread.start()     # print(key1)     # subprocess.call(['bash', '-c', press.format(key1)])
    else:
      keybord_from.press(KEYS[key[number_key]])

  def key_release(self, key, number_key):# Опустить.
    # print("key_release")
    release = '''#!/bin/bash
    xte 'keyup {0}'    '''
    if key in self.keys_list1:
     thread = threading.Thread(target=lambda: subprocess.call(['bash', '-c', release.format(key)]))
     if number_key != 3 or number_key != 4:# избежать зависание колесика мыши.
      thread.daemon = True  # Установка атрибута daemon в значение True
     thread.start()   # print(key)     # subprocess.call(['bash', '-c', release.format(key)])
     return 0
    key1= key.lower()
    if key1 in self.keys_list:      # subprocess.call(['bash', '-c', release.format(key1)])
     thread1 = threading.Thread(target=lambda: subprocess.call(['bash', '-c', release.format(key)]))
     if number_key != 3 or number_key != 4:# избежать зависание колесика мыши.
      thread1.daemon = True  # Установка атрибута daemon в значение True
      thread1.start()
    else:
      keybord_from.release(KEYS[key[number_key]])

  def key_press_release(self,  key, number_key):  #
    pass
    # press_release = '''#!/bin/bash
    # xte 'keydown {}' 'keyup {}'
    # '''
    # if key in self.keys_list:
    #   subprocess.call(['bash', '-c', press_release.format(key, key)])
    #
    # else:
    #
    #   keybord_from.press(KEYS[key[number_key]])

def show_tooltip(self, event):
  x, y, _, _ = self.widget.bbox("insert")
  x += self.widget.winfo_rootx() + 25
  y += self.widget.winfo_rooty() + 25

  self.tooltip = root.Toplevel(self.widget)
  self.tooltip.wm_overrideredirect(True)
  self.tooltip.wm_geometry(f"+{x}+{y}")

  label = root.Label(self.tooltip, text=self.text, background="#ffffe0", relief="solid", borderwidth=1)
  label.pack()

    #    a.resume()
    # if pres == False:
    #     a.pause()
  # else:# Флажок стоит.
   # if  pres == False:
   #     mouse1.press(list_mouse_button_names[key[number_key]])  # Нажимаем кнопку мыши.
   # else:  # Отпускаем кнопку мыши.
   #      mouse1.release(list_mouse_button_names[key[number_key]])

sticking_right_mouse=False
def mouse_key(key, number_key,press_button,list_mouse_button_names, pres, a):
 global sticking_right_mouse
 try:# list_buttons = {"Button.button10": a6}  # , "Button.button11"]
  # нет залипание кнопок мыши. Оно press_button[number_key] == False отвечает за это
  if press_button[number_key] == False and key[number_key] == "SCROLL_DOWN" or key[number_key] =="SCROLL_UP" : # print(key[number_key])
    if  pres == True:# колёсика мышки.
       a.resume()
    if pres == False:
        a.pause()
  if press_button[number_key] == False and key[number_key] != "SCROLL_DOWN" or key[number_key] != "SCROLL_UP" :
    if  pres == True:# Кнопка  мышки.
      if str(key[number_key])=='RBUTTON':
        key_work.mouse_right_donw()

      if str(key[number_key])=='WHEEL_MOUSE_BUTTON':
        key_work.mouse_middle_donw()

  # Есть ли залипание есть
  if press_button[number_key] and key[number_key] != "SCROLL_DOWN" or key[number_key] != "SCROLL_UP" :
    if pres == True:# Кнопка мышки нажата.     # print(sticking_right_mouse)
     if str(key[number_key])=='RBUTTON':
      if sticking_right_mouse == False:# нет залипание.
         sticking_right_mouse = True

         mouse_controller.press(mouse.Button.right)
         #pyautogui.mouseDown(button='right')        # Нажимаем и удерживаем правую кнопку мыши
      else:        # print("re")
        # Отпускаем правую кнопку мыши
        mouse_controller.release(mouse.Button.right)

        #pyautogui.mouseUp(button='right')
        sticking_right_mouse =False
 except Exception as e:   #save_dict.write_in_log(e)
   pass

key_work =work_key()
def keyboard_press_button(key, pres, number_key, a, press_button):
 try:
  wk = str(KEYS[key[number_key]])  #  print(wk)

  if press_button[number_key] == False:  # Не поставлен флажок.
    if pres == True:# нажата.

      key_work.key_press(wk, number_key)	# print(str(KEYS[key[number_key]]))         # print("press off")
    if pres == False:
      key_work.key_release(wk, number_key)		# keybord_from.release(KEYS[key[number_key]])  # print("reasle off")

  # поставлен флажок.

  if press_button[number_key] == True:    # print("ok")
    if pres == True and a.get_sw() == True:
      a.set_sw(False)
      key_work.key_press(wk, number_key)  # print("press off")
      return
    if pres == True and a.get_sw() == False:
      a.set_sw(True)
      key_work.key_release(wk, number_key)
 except Exception as e:   #save_dict.write_in_log(e)
   pass

def remove_profile_keys(d, profile):   # Создаем копию словаря, чтобы избежать изменения размера словаря во время итерации
  keys_to_delete = []
  for key, value in d.items():
    if str(key) == str(profile):  # Сравниваем ключ с profile
      keys_to_delete.append(key)
    elif isinstance(value, dict):
      # Рекурсивно вызываем для вложенного словаря
      remove_profile_keys(value, profile)
    elif isinstance(value, list):
      # Если значение — список, обрабатываем каждый элемент
      for item in value:
        if isinstance(item, dict):
          remove_profile_keys(item, profile)
  # Удаляем собранные ключи
  for key in keys_to_delete:
    del d[key]

def start1(dict_save, root):# Запуск всего
 if dict_save.get_id()==0:# # получить id устройства.Если id устройство не выбрали.
     messagebox.showinfo("Ошибка", "Вы не выбрали устройство")
     ok_button = Button(root, text="Ок", command=show_list_id_callback)
     return
 dictio=dict_save.return_jnson()
 # Какие игры имеют галочку, получаем их список.
 games_checkmark_paths = [key for key, value in dictio['games_checkmark'].items() if value] # Получить список путей к играм
 gp=str(dict_save.get_cur_app())# текущая игра
 if gp in games_checkmark_paths:# Если текущая игра имеет галочку.  print("Lok")
     add_button_start = dict_save.get_add_button_start()
     add_button_start["state"] = "disabled"# выкл кнопку старт.
     curr_name = dict_save.get_cur_app()  # получить значение текущей активной строки.     # dict_save.set_current_path_game(curr_name)
     prepare(root, dict_save, dictio, games_checkmark_paths)

 else: # Вывод ошибки.
   messagebox.showinfo("Ошибка", "Нужно выбрать приложенние")

def check_mouse_script(res, dict_save, defaut_list_mouse_buttons, number_key):
 try:
  key_mouse_scrypt = res["script_mouse"][dict_save.get_cur_app()][defaut_list_mouse_buttons[number_key]]
  if dict_save.get_cur_app() in res["script_mouse"]:
    mouse_button = defaut_list_mouse_buttons[number_key]
    if mouse_button in res["script_mouse"][dict_save.get_cur_app()]:
      key_mouse_scrypt = res["script_mouse"][dict_save.get_cur_app()][defaut_list_mouse_buttons[number_key]]
      if key_mouse_scrypt:
       return True
      else:
       return False
    else:
     return False
  else:
   return False
 except:
   return False
def execute_script(script):
    try:
        # print(script)
        result = subprocess.call(['bash', '-c', script])
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении скрипта: {e}")
def func_mouse_press_button(dict_save, key, button, pres, list_buttons, press_button, string_keys):
 # key - список клавиш, button - какая кнопка сейчас нажата, есть нажатие, словарь с называниями кнопкам с объектами,
 # как называется кнопка мыши для эмуляции, эту надо кнопку удерживать?
 list_mouse_button_names = {"LBUTTON": Button_Controller.left, "RBUTTON": Button_Controller.right,
 "WHEEL_MOUSE_BUTTON": Button_Controller.middle, "MBUTTON": 0x04, "SCROLL_UP": Button_Controller.scroll_up,
 "SCROLL_DOWN": Button_Controller.scroll_down}   # print(list_mouse_button_names)
 res=dict_save.return_jnson()
 try:
  for i in string_keys:   # print(i)
    a = list_buttons[i]  # объект  for i in string_keys:   # print(i)
    number_key = list_buttons[a]  # получаем номер кнопки в списке.  # and len(str(key[number_key])) > 1:    # print(key)  # print(key[number_key] ) # print(button)
    if str(key[number_key]) != ' ' and str(key[number_key]) != " "and\
      str(i) == str(button) and list_buttons[i].get_hook_flag_mouse() == True:# это кнопка нажата?
      if check_mouse_script(res, dict_save, defaut_list_mouse_buttons, number_key):# На эту кнопку назначен скрипт
        key_mouse_script = res["script_mouse"][dict_save.get_cur_app()][defaut_list_mouse_buttons[number_key]]        # print(key_mouse_script)
        thread1 = threading.Thread(target=execute_script, args=(key_mouse_script,))
        thread1.daemon = True
        thread1.start()
      else:       # print("else")       # кнопки мыши
       if key[number_key] in list(list_mouse_button_names.keys()): # если нужно эмулировать кнопку мыши
        mouse_key(key, number_key, press_button, list_mouse_button_names, pres, a)    #        print("mnouse")
      # иначе клавиши клавиатуры.
       else:# print("Кейтборд")
        keyboard_press_button(key, pres, number_key, a, press_button)# Работа с клавой.
 except Exception as e:
   save_dict.write_in_log(e)
   pass

get_main_id = '''#!/bin/bash # Получаем идентификатор активного окна
active_window_id=$(xdotool getactivewindow 2>/dev/null)
if [ -n "$active_window_id" ]; then
    process_id_active=$(xdotool getwindowpid "$active_window_id" 2>/dev/null)
    echo "$process_id_active"
else
    echo "0"  # Или любое значение по умолчанию, если нет активного окна
fi
exit '''

def start_startup_now(dict_save, root):# запустить после переключения окна
 res =dict_save.return_jnson()
 if res["start_startup"] :   # Если есть галочка запускать при старте.
   # print("start_startup_now")
   dict_save.reset_id_value()  # Сброс настроек текущего id устройства.   # time.sleep(0.3)
   start1(dict_save, root)  # Запуск всего
list_threads=[]
def a(root, dict_save, key, list_buttons, press_button, string_keys, game, games_checkmark_paths):# Основная функция эмуляциии  print(key[1])# список ключей  меняется
  #print(key)  # ['LBUTTON', 'W', ' ', ' ', 'R', 'SPACE', 'KP_Enter']   # game=game
  def on_click(x, y, button, pres):  # print(button) # Button.left  print(key)#['LBUTTON', 'W', ' ', ' ', 'R', 'SPACE', 'KP_Enter']    print(key[1])# список ключей  меняется
    f2 = threading.Thread(target=func_mouse_press_button, args=(dict_save, key, button, pres, list_buttons, press_button, string_keys,))
    # f2.daemon = True
    list_threads.append(f2)
    f2.start()
    return True
  listener = mouse.Listener(on_click=on_click)
  listener.start()  # Запуск слушателя  # print( game)#  print( dict_save.get_cur_app())

  while 1:   #time.sleep(3)   #print(dict_save.get_flag_thread())
   game = dict_save.get_cur_app()
   new_path_game = check_current_active_window(dict_save, games_checkmark_paths)  # Текущая директория активного окна игры.
   # print(new_path_game)
   if game != new_path_game:    # print(new_path_game)#
    dict_save.set_cur_app(new_path_game)
    # dict_save.set_current_path_game(new_path_game)
   # if new_path_game != "": # если путь не пустой
   #   game = new_path_game# game новый путь
   # else:
   #   game = dict_save.get_cur_app() # если путь пуст то game это последняя выбранная игра
   if dict_save.get_current_path_game() != dict_save.get_cur_app():  # Если у нас текущий путь к игре отличает от начального
     # print("user")
     for t in list_threads:
       t.join()
       list_threads.remove(t)
     dict_save.set_current_path_game(dict_save.get_cur_app()) #Остановить обработчик клави.  print("change", dict_save.get_cur_app(), sep=" = " )# если поток слушателя оставлен     #time.sleep(1.3)
     break  # key_work.key_release(key, 0)
  a=key_work.keys_list+key_work.keys_list1
  for i in list(key):
    if i in defaut_list_mouse_buttons:
      if i=='RBUTTON':
        mouse_controller.release(mouse.Button.right)
        # pyautogui.mouseUp(button='right')
      if i=='LBUTTON':
        pyautogui.mouseUp(button='left')

      if i=='WHEEL_MOUSE_BUTTON':
        key_work.mouse_middle_donw()
      if i in a:     # print(i)
       release = '''#!/bin/bash
       xte 'keyup {0}'    '''
       subprocess.call(['bash', '-c', release.format(key)])
  listener.stop()
  listener.join()  # Ожидание завершения
  dict_save.set_thread(0)

  t2 = threading.Thread(target=start_startup_now, args=(dict_save, root,))  # Запустить функцию, которая запускает эмуляцию заново.
  t2.daemon = True
  t2.start()#  print("cll")
def prepare(root, dict_save, dictio, games_checkmark_paths):  # функция эмуляций.  # games_checkmark_paths - Список игр с галочкой
  key, id, old, a1, a2, a3, a4, a5, a6, k, press_button, game, list_buttons = dict_save.preparation(dictio, games_checkmark_paths)
  new = ' '.join(old)   #  print(new)  # print(list_buttons)  print( type(new)  ) print(id)
  string_keys = list(key for key in list_buttons.keys() if isinstance(key, str))
  set_button_map = '''#!/bin/bash\nsudo xinput set-button-map {0} {1} '''.format(id, new)
  subprocess.call(['bash', '-c', set_button_map])  # установить конфигурацию кнопок для мыши.   print(dict_save.get_state_thread())
  dict_save.set_cur_app(game)# Текущая игра  # dict_save.set_current_path_game(game)# последний текущий путь # Запустить обработчик нажатий.  print(game, key, k, sep="\n")  #  print(key)  print(string_keys)
  t1= dict_save.get_thread()  # print(t1)
  if t1 != 0:
    t1.join()
  # print("threading")
  t1 = threading.Thread(target=a, args =(root, dict_save, key, list_buttons, press_button, string_keys, game, games_checkmark_paths))  #t1.daemon = True
  t1.start()
  dict_save.set_thread(t1)# сохранить id посёлка потока
def get_process(dict_save, root):# это функция получается активный процесс и pid игр.
 dict_save.set_current_path_game(dict_save.get_cur_app())
 while 1:
   try:
    time.sleep(0.1)
    process_id_active = int(subprocess.run(['bash'], input=get_main_id, stdout=subprocess.PIPE, text=True).stdout.strip())
    dict_save.set_process_id_active(process_id_active)# текущий pid активного процесса.
    dict_save.set_pid_and_path_window(get_pid_and_path_window()) # здесь мы получаем путь и pid процессов.
    # print(dict_save.get_current_path_game())    # print( dict_save.get_cur_app())

   except Exception as e:
     #print(e)
     pass
def get_path_current_active(games_checkmark_paths):# Получаем идентификатор активного окна

 try:  # Получаем идентификатор процесса, связанного с активным окном
  active_window_id = subprocess.check_output(['xdotool', 'getactivewindow']).decode().strip()
  process_id = subprocess.check_output(['xdotool', 'getwindowpid', active_window_id]).decode().strip()
  process_list = [p.info for p in psutil.process_iter(attrs=['name', 'pid', 'exe'])]
  for process in process_list:
   if int(process_id)== int(process['pid']):# нашли pid активного  окна
    if str(process['exe']) in games_checkmark_paths:
     path_game = str(process['exe'])
     return path_game# путь к игре активного окна

  return games_checkmark_paths[0]
 except :
    pass

def check_star():
 process_list = [p.info for p in psutil.process_iter(attrs=['name'])]
 a=[]
 try:
  for process in process_list:   # print(process['name'])
   if 'Mouse_setting_control_for_buttons_python_for_linux' in  process['name']:
    a.append(process)
    if len(process_list)>1:
     return False
    else:
     return True
 except psutil.NoSuchProcess:
    pass


# def run_check_current_active_window(root, t1, dict_save, game, games_checkmark_paths):  # print(game)
#   while 1:
#     new_path_game = check_current_active_window(dict_save, games_checkmark_paths)  # Текущая директория активного окна игры.
#     if new_path_game != "":
#       game = new_path_game
#     else:
#       game = dict_save.get_current_app_path()  # Последняя выбранная игра
#     if game != dict_save.get_cur_app():
#       dict_save.thread = True
#       dict_save.set_cur_app(game)
#       t1.join()  # закончить поток поиска главного окна
#       while 1:
#         time.sleep(0.001)
#         if game == dict_save.get_cur_app():
#          break
#       start_startup_now(dict_save, root)
#       break

  # t1.join()
  # start_startup_now(dict_save, root)
  # dp = threading.Thread(target=run_check_current_active_window, args =( root, t1, dict_save,  game, games_checkmark_paths))
  # dp.start()# нахождения активного окна.
# from PIL import ImageTk, Image
# # Нажатие левой клавиши Ctrl
# keyboard.press('ctrl')
#
# # Отпускание левой клавиши Ctrl
# keyboard.release('ctrl')

# Controller,
# keyboard = Controller()
#
# # Нажатие клавиши "A"
# keyboard.press(Key.ctrl_l)12
# time.sleep(0.1)  # Пауза для эмуляции удержания клавиши
# keyboard.release(Key.ctrl_l)

# import pydirectinput as directinput
# # Нажатие левой клавиши Ctrl
# directinput.keyDown('ctrl')

# Отпускание левой клавиши Ctrl
# directinput.keyUp('ctrl')

# import pyautogui
# # Нажатие левой клавиши Ctrl
# pyautogui.keyDown('ctrlleft')
#
# # Отпускание левой клавиши Ctrl
# pyautogui.keyUp('ctrlleft')
'''
keyboard: Эта библиотека предоставляет простые функции для считывания и эмуляции нажатий клавиш на клавиатуре. 
Она позволяет считывать нажатия клавиш, определять, какие клавиши были нажаты одновременно, и эмулировать 
нажатия клавиш. Однако, она не предоставляет возможности для управления мышью.

pynput: Эта библиотека предоставляет возможность управлять как клавиатурой, так и мышью на уровне операционной
системы. Она позволяет считывать и эмулировать нажатия клавиш, а также выполнять другие действия, связанные 
с мышью, такие как нажатие кнопок мыши, перемещение курсора и прокрутка колесика мыши. Она также предоставляет 
возможность мониторинга клавиатуры и мыши, а также ограничения действий пользователя.

pydirectinput: Эта библиотека предоставляет функции для эмуляции нажатий клавиш и других действий на уровне 
операционной системы. Она позволяет эмулировать нажатия клавиш, перемещение мыши, клики и другие действия. 
Она не предоставляет возможности для мониторинга клавиатуры и мыши.

pyautogui: Эта библиотека предоставляет функции для управления мышью и клавиатурой на уровне операционной системы. 
Она позволяет эмулировать нажатия клавиш, перемещение мыши, клики и другие действия. Она также предоставляет функции 
для работы с изображениями на экране и автоматизации задач на компьютере.
'''