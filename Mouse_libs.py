import time, json, os, copy, psutil, threading, re, glob, subprocess, psutil, pyautogui, signal, pystray
from tkinter import *
from tkinter.ttk import Combobox  # импортируем только то что надо
from tkinter import ttk
from PIL import Image
from PIL._tkinter_finder import tk
from tkinter import messagebox
from tkinter import filedialog
import tkinter as tk
from apport import logging
from deepdiff import DeepDiff
import keyboard as keybord_from # Управление мышью
from pynput import mouse, keyboard
from pynput.mouse import Button as Button_Controller, Controller
from pynput.keyboard import Key, Listener # Создаем экземпляр класса Controller для управления мышью
from evdev import InputDevice, categorize, ecodes, list_devices
def show_message(): # Вызов функции для отображения окна
  messagebox.showinfo("Ошибка", "Требуется запустить с root правами")
def show_message1(): # Вызов функции для отображения окна
  messagebox.showinfo("Ошибка", "Программа уже запущена")

# Создаем словари
en_to_ru = { 'a': 'ф', 'A': 'Ф', 'b': 'и', 'B': 'И', 'c': 'с', 'C': 'С', 'd': 'в', 'D': 'В', 'e': 'у', 'E': 'У', 'f': 'а', 'F': 'А', 'g': 'п', 'G': 'П',
             'h': 'р', 'H': 'Р', 'i': 'ш', 'I': 'Ш', 'j': 'о', 'J': 'О', 'k': 'л', 'K': 'Л',
    'l': 'д', 'L': 'Д', 'm': 'ь', 'M': 'Ь', 'n': 'т', 'N': 'Т', 'o': 'щ', 'O': 'Щ', 'p': 'з', 'P': 'З', 'q': 'й', 'Q': 'Й', 'r': 'к', 'R': 'К', 's': 'ы', 'S': 'Ы', 't': 'е', 'T': 'Е', 'u': 'г', 'U': 'Г', 'v': 'м', 'V': 'М',
    'w': 'ц', 'W': 'Ц', 'x': 'ч', 'X': 'Ч', 'y': 'н', 'Y': 'Н', 'z': 'я', 'Z': 'Я', '.': '-', ',': '+', ' ': ' '}

ru_to_en = { 'ф': 'a', 'Ф': 'A', 'и': 'b', 'И': 'B', 'с': 'c', 'С': 'C', 'в': 'd', 'В': 'D', 'у': 'e', 'У': 'E', 'а': 'f', 'А': 'F', 'п': 'g', 'П': 'G', 'р': 'h', 'Р': 'H', 'ш': 'i', 'Ш': 'I', 'о': 'j', 'О': 'J', 'л': 'k', 'Л': 'K',
             'д': 'l', 'Д': 'L', 'ь': 'm', 'Ь': 'M', 'т': 'n', 'Т': 'N', 'щ': 'o', 'Щ': 'O', 'з': 'p', 'З': 'P', 'й': 'q',
    'Й': 'Q', 'к': 'r', 'К': 'R', 'ы': 's', 'Ы': 'S', 'е': 't', 'Е': 'T', 'г': 'u', 'Г': 'U', 'м': 'v', 'М': 'V',
    'ц': 'w', 'Ц': 'W', 'ч': 'x', 'Ч': 'X', 'н': 'y', 'Н': 'Y', 'я': 'z', 'Я': 'Z', '-': '.', '+': ',', ' ': ' '}
KEYS = {" ": 0x0,"LBUTTON": 'mouse left', "RBUTTON": 'mouse right', "WHEEL_MOUSE_BUTTON": "mouse middle",
        "WHEEL_MOUSE_UP" : "WHEEL_MOUSE_UP", "MBUTTON": 0x04, "SCROLL_UP": "scroll_up",
        "SCROLL_DOWN" : "scroll_down", "XBUTTON1": 0x05, "XBUTTON2": 0x06, "BACKSPACE": "BackSpace",
        "TAB": "Tab", "CLEAR": 0x0C, "RETURN": "Return", "KP_Enter" : "KP_Enter",
        "Shift_L": "Shift_L", "CONTROL": "CONTROL", "MENU": 0x12, "PAUSE": 0x13, "CAPITAL": 0x14,
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
        "F22": 0x85, "F23": 0x86, "F24": 0x87,"NUMLOCK": "Num_Lock", "SCROLL": "Scroll_Lock", "OEM_FJ_JISHO": 0x92, "OEM_FJ_MASSHOU": 0x93,
        "OEM_FJ_TOUROKU": 0x94, "OEM_FJ_LOYA": 0x95, "OEM_FJ_ROYA": 0x96, "RSHIFT": "Shift_R", "LCONTROL": "ISO_Next_Group",
        "RCONTROL": "Control_R", "LMENU": 0xA4, "RMENU": 0xA5, "BROWSER_BACK": 0xA6, "BROWSER_FORWARD": 0xA7, "BROWSER_REFRESH": 0xA8,
        "BROWSER_STOP": 0xA9, "BROWSER_SEARCH": 0xAA, "BROWSER_FAVORITES": 0xAB, "BROWSER_HOME": 0xAC, "VOLUME_MUTE": 0xAD, "VOLUME_DOWN": 0xAE,
        "VOLUME_UP": 0xAF, "MEDIA_NEXT_TRACK": 0xB0, "MEDIA_PREV_TRACK": 0xB1, "MEDIA_STOP": 0xB2, "MEDIA_PLAY_PAUSE": 0xB3, "LAUNCH_MAIL": 0xB4,
        "LAUNCH_MEDIA_SELECT": 0xB5, "LAUNCH_APP1": 0xB6, "LAUNCH_APP2": 0xB7, "OEM_1": 0xBA, "OEM_PLUS": 0xBB, "OEM_COMMA": 0xBC,
        "OEM_MINUS": 0xBD, "OEM_PERIOD": 0xBE, "OEM_2": 0xBF, "OEM_3": 0xC0, "ABNT_C1": 0xC1, "ABNT_C2": 0xC2, "OEM_4": 0xDB,
        "OEM_5": 0xDC, "OEM_6": 0xDD, "OEM_7": 0xDE, "OEM_8": 0xDF, "OEM_AX": 0xE1, "OEM_102": 0xE2, "ICO_HELP": 0xE3, "PROCESSKEY": 0xE5,
        "ICO_CLEAR": 0xE6, "PACKET": 0xE7, "OEM_RESET": 0xE9, "OEM_JUMP": 0xEA, "OEM_PA1": 0xEB, "OEM_PA2": 0xEC, "OEM_PA3": 0xED,
        "OEM_WSCTRL": 0xEE, "OEM_CUSEL": 0xEF, "OEM_ATTN": 0xF0, "OEM_FINISH": 0xF1, "OEM_COPY": 0xF2, "OEM_AUTO": 0xF3, "OEM_ENLW": 0xF4,
        "OEM_BACKTAB": 0xF5, "ATTN": 0xF6, "CRSEL": 0xF7, "EXSEL": 0xF8, " EREOF": 0xF9, "PLAY": 0xFA, "ZOOM": 0xFB, "PA1": 0xFD, " OEM_CLEAR": 0xFE
        }

LIST_MOUSE_BUTTONS=["Левая кнопка","Правая кнопка","Средняя","Колесико вверх","Колесико вниз","1 боковая","2 боковая"]
LIST_KEYS = list(KEYS.keys())
defaut_list_mouse_buttons=['LBUTTON', 'RBUTTON', 'WHEEL_MOUSE_BUTTON', 'SCROLL_UP', 'SCROLL_DOWN', 'XBUTTON1', 'XBUTTON2']
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
      self.process_id_active = 0 # id активного окна
      self.pid_and_path_window={} # Словарь игр и путей к ним.
      self.current_path_game = "" # Путь к запущенной к игре.
      self.last_key_keyboard_script = ""
      self.thr=0

  def get_last_key_keyboard_script(self):  #
    return self.last_key_keyboard_script

  def set_last_key_keyboard_script(self, last_key_keyboard_script1):
    self.last_key_keyboard_script= last_key_keyboard_script1

  def get_thread(self):  #
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

  def get_current_app_path(self):# Получить путь текущего окна.
     return self.path_current_app

  def set_current_app_path(self, app):# Установить путь текущего окна.
     self.path_current_app = app
  def return_name_games(self):  # Вернуть список названия игр.
      name_games =self.name_games
      return self.name_games

  def return_mouse_button_press(self):
     return self.mouse_button_press
  def save_labels(self, labels):
     self.labels =labels

  def return_labels(self):
     return self.labels
  def save_var_list(self, var_list):
     self.var_list=var_list
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

  def save_jnson(self, jn):# сохранить новые настройки
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
     return str(self.cur_app)

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
  def set_box_values(self):  # Установить значение для выпадающего списка.
    self.reset_id_value()
    res = self.jnson
    key_values = res["key_value"]
    d = list(res["paths"].keys())  # получить словарь путей и имен файлов.  # print(self.cur_app)    # print(self.count)      # print(d[self.count])
    self.set_cur_app(d[self.count])  # установить текущую активную строку.
    self.jnson["current_app"] = d[self.count]  # Сохранить текущую активную строку.
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
    get_ids = '''#!/bin/bash
    ids=$(xinput list | grep -Ei "id=[0-9]+" | grep -oE "id=[0-9]+" | cut -d= -f2)
     for id in $ids; do
      output=$(xinput get-button-map "$id" 2>&1)
      # Исключаем сообщения об ошибках, добавляя проверки на наличие ошибок
      if [[ $output != *"device has no buttons"* && $output != *"X Error of failed request:"* ]]; then
          echo "$id:$output"
      fi
     done'''    # Команда shell для получения списка идентификаторов устройств ввода (мышей), которые подключены к системе.

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

  def set_default_id_value(self):# Вернуть значения по умолчанию
    self.thread = True  # Прервать выполнение потока обработчика нажатий.
    for id in self.dict_id_values:
      st= str(self.dict_id_values[id])
      set_button_map = '''#!/bin/bash
        sudo xinput set-button-map {0} {1}
        '''.format(id, st)
      subprocess.call(['bash', '-c', set_button_map])

  def reset_id_value(self):  # Сброс настроек текущего id устройства.       #  print(self.id)
    d = '1 2 3 4 5 6 7 8 9'  #      print("reset_id_value")
    devices_mouse=list(self.dict_id_values.keys())
    for i in devices_mouse:
     set_button_map = '''#!/bin/bash
        sudo xinput set-button-map {0} {1}
        '''.format(self.id, d)
     process = subprocess.Popen(['bash', '-c', set_button_map], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
     stdout, stderr = process.communicate()
     if process.returncode != 0:
      self.id=i
     else:
      break

  def get_default_id_value(self):#
   try:
    d = self.dict_id_values[self.get_id()]
    d_copy = copy.deepcopy(d)
    d='1 2 3 4 5 6 7 8 9'
    return d
   except Exception as ex1:
     print(ex1)
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
   time.sleep(0.08)
   t=0.0115# задержка в прокрутке.
   if self.key== "SCROLL_UP":
     thread = threading.Thread(target= key_work.mouse_wheel_up)
     thread.start()  # key_work.mouse_wheel_donw()   # keybord_from.press(self.key)
     time.sleep(t)
   if self.key== "SCROLL_DOWN":
     thread1 = threading.Thread(target= key_work.mouse_wheel_donw)
     thread1.start()      # key_work.mouse_wheel_donw()   # keybord_from.press(self.key)
     time.sleep(t)    # thread1.join()
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
def add_text(key, text_widget): # добавлять команды для клавиатуры и мысли в текстовое поле редактора.)
 
 if key == "7\nHome":
  key = "KP_Home"
 elif key == "8\n↑":
  key = "KP_Up"
 elif key == "9\nPgUp":
  key = "KP_Prior"
 elif key == "4\n←":
  key = "KP_Left"
 elif key == "5\n":
  key = "KP_Begin"
 elif key == "6\n→":
  key = "KP_Right"
 elif key == "1\nEnd":
  key = "KP_End"
 elif key == "2\n↓":
  key = "KP_Down"
 elif key == "3\nPgDn":
  key = "KP_Next"
 elif key == "Ctrl":
  key = "ISO_Next_Group"
 
 if key == "Левая":
      sc = (f'xte "mousedown 1"\n'
            f'sleep 0.23\n'
            f'xte "mouseup 1"\n')
 elif key == "Правая":
      sc = (f'xte "mousedown 3"\n'
            f'sleep 0.23\n'
            f'xte "mouseup 3"\n')
 elif key == "wheel_up":
      sc = (f'xte "mousedown 4"\n'
            f'sleep 0.23\n'
            f'xte "mouseup 4"\n')
 elif key == "mouse_middie":
      sc = (f'xte "mousedown 2"\n'
            f'sleep 0.23\n'
            f'xte "mouseup 2"\n')
 elif key == "wheel_down":
      sc = (f'xte "mousedown 5"\n'
            f'sleep 0.23\n'
            f'xte "mouseup 5"\n')
 else:
      sc = (f'xte "keydown {key}"\n'
            f'sleep 0.23\n'
            f'xte "keyup {key}"\n')
  # Вставляем текст в месте курсора
 text_widget.insert(text_widget.index("insert"), sc)

def create_virtial_keyboard(root):# создать виртуальную клавиатуру
  window = Toplevel(root)  # основа
  window.geometry("1350x340+240+580")  # Используем geometry вместо setGeometry
  keyboard_layout = [
   ['Esc', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'Insert', 'Delete', 'Home',
    'End', 'PgUp', 'PgDn']
   , ['~\n`', '!\n1', '@\n2', '#\n3', '$\n4', '%\n5', '^\n6', '&\n7', '*\n8', '(\n9', ')\n0', '_\n-', '+\n=',
      'Backspace', 'Num Lock', '/', '*', '-']
   , ['Tab', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '{\n[', '}\n]', '|\n\\', ' 7\nHome', '8\n↑', '9\nPgUp',
      '+']
   , ['Caps Lock', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ':\n;', '"\n\'', '\nEnter\n', '4\n←', '5\n', '6\n→']
   , ['Shift_L', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', '<\n,', '>\n.', '?\n/', 'Shift_R', '1\nEnd', '2\n↓', '3\nPgDn', 'KEnter']
   , ['Ctrl', 'Windows', 'Alt_L', 'space', 'Alt_r', 'Fn', 'Menu', 'Ctrl_r', 'up', '0\nIns', ' . ']
   , ['Left', 'Down', 'Right']
  ]
  buttons={}
  style = ttk.Style()  # При нажатии кнопка меняет свой цвет.
  style.configure('TButton', background='lightgray')
  style.map('TButton', background=[('active', 'blue')])
  for i, row in enumerate(keyboard_layout):  # Создаем клавиатуру.
   for j, key in enumerate(row):
    x1 = 70 * j + 6
    y1 = 50 * i + 6
    button = ttk.Button(window, text=key, width=5, style='TButton')
    buttons[button]=key
    if key == 'Backspace':  # Условие только для Backspace
     button = ttk.Button(window, text=key, width=10, style='TButton')
     buttons[button]=key
     button.place(x=x1, y=y1)
    elif i == 1 and j > 13:  # Смещение кнопок NumPad после Backspace
     button.place(x=x1 + 69, y=y1)  # Сдвигаем вправо на 80 пикселей
    else:
     button.place(x=x1, y=y1)
    if key in [' 7\nHome', '8\n↑', '9\nPgUp', '+']:
     x2 = x1 + 69
     button.place(x=x2, y=y1)
     if key == "+":
      button.config(text="\n\n" + key + "\n")
    if key in ['4\n←', '5\n', '6\n→']:
     x2 = x1 + 140
     button.place(x=x2, y=y1)
    if key in ['1\nEnd', '2\n↓', '3\nPgDn', 'KEnter']:
     x2 = x1 + 210
     button.place(x=x2, y=y1)
     if key == "KEnter":
      button.config(text="\n\n" + key + "\n")
    if i == 5:
     if key in ['Ctrl', 'Windows', 'Alt']:
      button.place(x=x1, y=y1)
     if key == "space":
      button = ttk.Button(window, text=key, width=30, style='TButton')
      button.place(x=x1, y=y1)
      buttons[button] = key
     elif key in ['Alt_r', 'Fn', 'Menu', 'Ctrl_r']:
      x2 = x1 + 210
      button.config(width=5)  # Устанавливаем ширину 15 для "0\nIns"
      button.place(x=x2, y=y1)
     elif key == 'up':
      x2 = x1 + 280
      button.config(width=5)
      button.place(x=x2, y=y1)
     elif key == "0\nIns":
      x2 = x1 + 420
      button.config(width=15)  # Устанавливаем ширину 15 для "0\nIns"
      button.place(x=x2, y=y1)
     elif key == ' . ':
      x2 = x1 + 490
      button.config(width=5)
      button.place(x=x2, y=y1)
    if i == 6:
     if key in ['Left', 'Down', 'Right']:
      x2 = x1 + 770
      button.config(width=5)
      button.place(x=x2, y=y1 - 9)
  return window, buttons

def is_path_in_list(path, path_list):#проверяет, содержится ли путь в списке путей.
    return any(path in item for item in path_list)
def get_index_of_path(path, path_list):
  index = next(index for index, item in enumerate(path_list) if path in item)
  return index #находит индекс пути в списке путей и возвращает соответствующий элемент списка.

def get_process_info():
  process_info = {}
  pattern = re.compile(r'(/mnt/.*?\.exe)|([A-Z]:/.*?\.exe)', re.IGNORECASE)
  try:
   for proc in psutil.process_iter(['pid', 'username', 'cmdline']):
    if proc.info['username'] == user and proc.info['cmdline']:
     for arg in proc.info['cmdline']:
      arg_clean = arg.replace('\\', '/').strip('"')  # Приводим к нормальному виду
      match = pattern.search(arg_clean)
      if match:
       file_path = match.group(0)
       process_info[proc.info['pid']] = file_path
  except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
   pass
  return process_info

def replace_path_in_dict(d):
  # Определяем новый префикс
  new_prefix = next(('/'.join(value.split('/')[:4]) + '/' for value in d.values() if value.startswith('/mnt/')), None)
  if new_prefix is None:
    raise ValueError("Не удалось определить новый префикс.")

  updated_dict = {}
  for key, value in d.items():
    if value.startswith('/mnt/'):    # Если путь уже начинается с /mnt/, оставляем как есть
      updated_value = value
    else:      # Заменяем X:/ на new_prefix
      updated_value = re.sub(r'^[A-Z]:/', new_prefix, value, count=1)
      # Убираем дублирование /games/games/ или других частей
      parts = updated_value.split('/') # Удаляем повторяющиеся сегменты после new_prefix
      unique_parts = []
      for part in parts:
        if not unique_parts or part != unique_parts[-1]:
          unique_parts.append(part)
      updated_value = '/'.join(unique_parts)
    # Добавляем .exe, если его нет
    if isinstance(updated_value, str) and not updated_value.lower().endswith('.exe'):
      updated_value += '.exe'
    updated_dict[key] = updated_value # Путей обновить значение путей.
  return updated_dict
get_user_name = f'''#!/bin/bash
current_user=$(whoami);
echo $current_user
exit;# Завершаем выполнение скрипта
'''
user = subprocess.run(['bash'], input=get_user_name, stdout=subprocess.PIPE, text=True).stdout.strip()# имя пользователя.

def get_visible_active_pid():
 try:  # Получаем ID активного окна в десятичном формате
    window_id_dec = subprocess.run(['xdotool', 'getactivewindow'],
    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True ).stdout.strip()
    if not window_id_dec:
        print("Не удалось получить ID активного окна")
        return 0
 
    # Преобразуем десятичное ID в шестнадцатеричное (например, 1234567 -> 0x01234567)
    window_id_hex = hex(int(window_id_dec))
 
    # Проверка: окно свернуто?
    xprop_output = subprocess.run( ['xprop', '-id', window_id_dec, '_NET_WM_STATE'],
        stdout=subprocess.PIPE,  stderr=subprocess.DEVNULL, text=True ).stdout
 
    if "_NET_WM_STATE_HIDDEN" in xprop_output:
        print("Окно свернуто")
        return 0  # Окно свернуто
 
    # Получаем список окон с PID
    wmctrl_output = subprocess.run( ['wmctrl', '-lp'],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        text=True   ).stdout
 
    # Ищем строку с нужным ID окна
    for line in wmctrl_output.splitlines():
      parts = line.split()#            print(parts)
      if len(parts) >= 3 and parts[0] == window_id_hex:
       pid = int(parts[2])  # PID — третий элемент#   print(pid)
       return pid
    return 0  # PID не найден
 
 except Exception as e:
    print(f"Ошибка: {e}")
    return 0

def is_window_minimized(window_id):
 try:
  xprop_output = subprocess.run( ['xprop', '-id', window_id, '_NET_WM_STATE'],
   stdout=subprocess.PIPE, text=True  ).stdout
  return "_NET_WM_STATE_HIDDEN" in xprop_output
 except Exception:
  return True  # Если ошибка, считаем окно свернутым
def get_pid_and_path_window():# Получаем идентификатор активного окна
 try:   # Регулярное выражение для поиска путей к .exe файлам
   pattern = re.compile(r'(\/mnt\/.*?\.exe)|([A-Z]:\\.*?\.exe)|(.*?\.sh)', re.IGNORECASE)
   data_dict = {}   # Один проход по всем процессам пользователя
   for proc in psutil.process_iter(['pid', 'username', 'cmdline']):
    if proc.info['username'] == user and proc.info['cmdline']:
     for arg in proc.info['cmdline']:
      arg_clean = arg.replace('\\', '/').strip('"')  # Приводим к нормальному виду
      match = pattern.search(arg_clean)
      if match:
       file_path = match.group(0)
       data_dict[proc.info['pid']] = file_path
       threads = proc.threads()
       for thread in threads:
        data_dict[thread.id] = file_path
   if not data_dict:# Не найдено процессов с .exe для пользователя.
    return {}
   # update_dict= replace_path_in_dict(data_dict) # Обновляем словарь с помощью внешних функций (если они есть)
   return data_dict# Обновленный словарь путей.
 except:
     pass
def get_active_window_exe(user,id_active):
 try:
  result = subprocess.run(['ps', 'aux'], stdout=subprocess.PIPE, text=True).stdout
  lines = result.split('\n')
  # Фильтруем строки по пользователю и PID
  for line in lines:
   if user in line:  # Проверяем наличие PID и имени пользователя
    parts = line.split(maxsplit=10)  # Разделяем строку, предполагая стандартный формат ps aux
    exe_path = parts[10]
    pid = int(parts[1])
    if id_active == pid:  # "PortProton" in cmdline:# and id_active==pid:
     # print(exe_path)     # print(line)
     return exe_path
  output = subprocess.check_output(['ps', '-eo', 'pid,user,args'], text=True)
  for line in output.strip().split('\n')[1:]:
   parts = line.split(None, 2)
   if len(parts) == 3:
    pid, user, exe_path = parts
    if ".exe" in exe_path and id_active == pid:     # print(exe_path)
     return exe_path
  return None
 except:
   return None
get_main_id = '''#!/bin/bash # Получаем идентификатор активного окна
# Получаем идентификатор активного окна
active_window_id=$(xdotool getactivewindow 2>/dev/null)
if [[ -n "$active_window_id" && "$active_window_id" != "0" && "$active_window_id" =~ ^[0-9]+$ ]]; then
    # Получаем PID процесса, связанного с окном
    process_id_active=$(xdotool getwindowpid "$active_window_id" 2>/dev/null)
    if [[ -n "$process_id_active" && "$process_id_active" != "0" ]]; then
        # Проверяем родительский PID
        parent_pid=$(ps -p "$process_id_active" -o ppid= | tr -d '[:space:]')
        if [[ -n "$parent_pid" && "$parent_pid" != "0" && "$parent_pid" != "1" ]] && ps -p "$parent_pid" >/dev/null 2>&1; then
            echo "$parent_pid"
            exit 0
        else
            echo "$process_id_active"
            exit 0
        fi
         echo "0"
         exit 0
    fi
     echo "0"
     exit 0
fi
exit'''

def check_current_active_window(dict_save, games_checkmark_paths):# Получаем путь  активного ок
 try:
  data_dict = get_pid_and_path_window()  # в котором есть директория игр
  id_active = int(subprocess.run(['bash'], input=get_main_id, stdout=subprocess.PIPE, text=True).stdout.strip())
  file_path = data_dict[id_active]  # получаем путь
  if data_dict[id_active] and is_path_in_list(file_path, games_checkmark_paths):  # print( games_checkmark_paths[get_index_of_path(file_path, games_checkmark_paths)])     # print(dict_save.get_pid_and_path_window()[dict_save.get_process_id_active()])     print("000000")  print(file_path)
   return games_checkmark_paths[get_index_of_path(file_path, games_checkmark_paths)]  #
  if id_active and '/PortProton/data/scripts/start.sh' in data_dict[id_active]:#  если он запущен через pp
   # print(data_dict[id_active])
   for p in data_dict.values():# пути извлекаем все пути к играм, которые запущены
    if is_path_in_list(p, games_checkmark_paths):
     return games_checkmark_paths[get_index_of_path(p, games_checkmark_paths)]  # активного окна
  if id_active and not is_window_minimized(id_active):
   return dict_save.get_prev_game()# то есть мы возвышаемся директорию из get_prev_game

  if isinstance(data_dict, dict) and data_dict and id_active !=0:
   key_paths =get_active_window_exe(user, id_active)    # print(key_paths)
   if key_paths == None or ".exe" and ".sh" not in key_paths.lower():
     return dict_save.get_prev_game()  # то есть мы возвышаемся директорию из get_prev_game
   if ".sh" in key_paths.lower():
     key_paths1 =  os.path.basename(key_paths.split()[-1])[:-3]# Берём всё после последнего '/'
     file_path2 = next((p for p in games_checkmark_paths if key_paths1.lower() in p.lower()), None)#
     if file_path2 and ".exe" in file_path2.lower():#        print(file_path2)
      return games_checkmark_paths[get_index_of_path(file_path2, games_checkmark_paths)]
  return dict_save.get_prev_game()  # то есть мы возвышаемся директорию из get_prev_game
 except Exception as e:
    pass
    return dict_save.get_prev_game()# то есть мы возвышаемся директорию из get_prev_game

def show_list_id_callback():
  show_list_id = f'''#!/bin/bash
   gnome-terminal -- bash -c 'xinput list;
   read;   exec bash' '''#показать список устройств в терминале
  subprocess.run(['bash', '-c', show_list_id])

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
        xdotool click  {0}   
         '''.format(5)
    subprocess.call(['bash', '-c', mouse_wheel])
  def mouse_right_donw(self):  #Правая кнопки мыши
    # mouse_controller.click(mouse.Button.right)
    # pyautogui.click(button='right')
    mouse_right_donw1 = '''#!/bin/bash
        xdotool click  {0}    '''.format(3)
    subprocess.call(['bash', '-c', mouse_right_donw1])
  def mouse_middle_donw(self):  #Средняя.
      pyautogui.click(button='middle')      # Нажимаем среднюю кнопку мыши
      mouse_wheel = '''#!/bin/bash
          xdotool click  {0}    '''.format(2)
      # subprocess.call(['bash', '-c', mouse_wheel])
  def key_press(self, key, number_key):# Нажать.
    press = '''#!/bin/bash
    xte 'keydown {0}'
    exit 0 '''

    release = '''#!/bin/bash
    xte 'keyup {0}'
    sleep 0.1    # Небольшая пауза для надёжности
    xte 'keyup {0}'
    exit 0 '''
    key1= key.lower()
    if key1 in self.keys_list or key in self.keys_list1:
     if number_key != 3 or number_key != 4:
      thread0 = threading.Thread(target=lambda: subprocess.call(['bash', '-c', press.format(key)]))      #thread.daemon = True  # Установка атрибута daemon в значение True
      thread0.daemon
      thread0.start()
      return 0
     if number_key ==3 or 4:
      thread = threading.Thread(target=lambda: subprocess.call(['bash', '-c', press.format(key)]))      #thread.daemon = True  # Установка атрибута daemon в значение True
      thread.start()
      thread.join()
      thread1 = threading.Thread(target=lambda: subprocess.call(['bash', '-c', release.format(key)]))
      #thread1.daemon
      thread1.start()  # print(key1)     # subprocess.call(['bash', '-c', press.format(key1)])
      thread1.join()
      return 0
    else:
      keybord_from.press(KEYS[key[number_key]])

  def key_release(self, key, number_key):# Опустить.
    # print("key_release")
    release = '''#!/bin/bash
    # Небольшая пауза для надёжности
    sleep 0.1
    xte 'keyup {0}'
    exit 0 '''
    if key in self.keys_list1:
     thread = threading.Thread(target=lambda: subprocess.call(['bash', '-c', release.format(key)]))
     if number_key != 3 or number_key != 4:# избежать зависание колесика мыши.
       thread.daemon = True  # Установка атрибута daemon в значение True
     thread.start()   # print(key)     # subprocess.call(['bash', '-c', release.format(key)])
     return 0
    key1= key.lower()
    if key1 in self.keys_list:      # subprocess.call(['bash', '-c', release.format(key1)])
     thread = threading.Thread(target=lambda: subprocess.call(['bash', '-c', release.format(key)]))
     if number_key != 3 or number_key != 4:# избежать зависание колесика мыши.
      thread.daemon = True  # Установка атрибута daemon в значение True
     thread.start()
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
    if pres == True:# колёсика мышки.
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
         mouse_controller.press(mouse.Button.right) #  Нажимаем и удерживаем правую кнопку мыши pyautogui.mouseDown(button='right')
      else:        # print("re")
        mouse_controller.release(mouse.Button.right) # Отпускаем правую кнопку мыши  pyautogui.mouseUp(button='right')
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
def remove_profile_keys(d, profile):
 # Создаем глубокую копию словаря
 d_copy = copy.deepcopy(d)
 
 keys_to_delete = []
 for key, value in d_copy.items():
  if str(key) == str(profile):
      keys_to_delete.append(key)
  elif isinstance(value, dict):
      # Рекурсивно вызываем для вложенного словаря и обновляем значение
      d_copy[key] = remove_profile_keys(value, profile)
  elif isinstance(value, list):
      # Если значение — список, обрабатываем каждый элемент
      new_list = []
      for item in value:
          if isinstance(item, dict):
              new_list.append(remove_profile_keys(item, profile))
          else:
              new_list.append(item)
      d_copy[key] = new_list
 
 # Удаляем собранные ключи
 for key in keys_to_delete:
  del d_copy[key]
 return d_copy

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
  try:  # print(script)
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
       else:#
        keyboard_press_button(key, pres, number_key, a, press_button)# Работа с клавой.
 except Exception as e:
   save_dict.write_in_log(e)
   pass

def start_startup_now(dict_save, root):# запустить после переключения окна
 dict_save.reset_id_value()  # Сброс настроек текущего id устройства.   # time.sleep(0.3)
 dictio = dict_save.return_jnson()  # Какие игры имеют галочку, получаем их список.
 games_checkmark_paths = [key for key, value in dictio['games_checkmark'].items() if value]  # Получить список путей к играм
 gp = str(dict_save.get_cur_app())  # текущая игра
 dict_save.set_current_path_game(gp)
 if gp in games_checkmark_paths or gp =="":  # Если текущая игра имеет галочку.  print("Lok")
  prepare(root, dict_save, dictio, games_checkmark_paths)
 else:  # Вывод ошибки.
  messagebox.showinfo("Ошибка", "Нужно выбрать приложенние")

list_threads=[]

def emunator_mouse(root, dict_save, key, list_buttons, press_button, string_keys, games_checkmark_paths):# Основная функция эмуляциии  print(key[1])# список ключей  меняется
  #print(key)  # ['LBUTTON', 'W', ' ', ' ', 'R', 'SPACE', 'KP_Enter']   # game=game
  def on_click(x, y, button, pres):  # print(button) # Button.left  print(key)#['LBUTTON', 'W', ' ', ' ', 'R', 'SPACE', 'KP_Enter']    print(key[1])# список ключей  меняется
    f2 = threading.Thread(target=func_mouse_press_button, args=(dict_save, key, button, pres, list_buttons, press_button, string_keys,))    # f2.daemon = True
    list_threads.append(f2)
    f2.start()
    return True
  listener = mouse.Listener(on_click=on_click)
  listener.start()  # Запуск слушателя  # print( game)#  print( dict_save.get_cur_app
  game = dict_save.get_cur_app()# какая игра сейчас текущая по вкладке.

  while 1:   #time.sleep(3)   #print(dict_save.get_flag_thread())
   new_path_game = check_current_active_window(dict_save, games_checkmark_paths) # Текущая директория активного окна игры.
   # Если никакой игры не запущено мы возвращаем предыдущую конфигурацию это директория. #   # print(new_path_game)#
   if game != new_path_game: # игра которая сейчас на активной вкладке активного окна    #
    dict_save.set_cur_app(new_path_game)#    # dict_save.set_current_path_game(new_path_game)
   if dict_save.get_current_path_game() != dict_save.get_cur_app():  # Если у нас текущий путь к игре отличает от начального
     # print(new_path_game)
     for t in list_threads:
       t.join()
       list_threads.remove(t)
     break
  print("exit")
  a=key_work.keys_list+key_work.keys_list1
  # for i in list(key):
  #   if i in defaut_list_mouse_buttons:
  #     if i=='RBUTTON':
  #       mouse_controller.release(mouse.Button.right)
  #       # pyautogui.mouseUp(button='right')
  #     if i=='LBUTTON':
  #       pyautogui.mouseUp(button='left')
  #
  #     if i=='WHEEL_MOUSE_BUTTON':
  #       key_work.mouse_middle_donw()
  #     if i in a:     # print(i)
  #      release = '''#!/bin/bash
  #      xte 'keyup {0}'    '''
  #      subprocess.call(['bash', '-c', release.format(key)])
  listener.stop()
  listener.join()  # Ожидание завершения
  dict_save.set_thread(0)

  t2 = threading.Thread(target=start_startup_now, args=(dict_save, root,))  # Запустить функцию, которая запускает эмуляцию заново.
  t2.daemon = True
  t2.start()#  print("cll")
def prepare(root, dict_save, dictio, games_checkmark_paths):  # функция эмуляций.  # games_checkmark_paths - Список игр с галочкой
  curr_name = dict_save.get_cur_app() # получить значение текущей активной строки.  # dict_save.set_current_path_game(curr_name)
  if curr_name == "":
   return 0
  t1= dict_save.get_thread() # мы получаем поток от предыдущей функции ждем когда он закончится  # print(t1)
  if t1 != 0:
    t1.join()
  if dict_save.get_id() == 0:  # # получить id устройства.Если id устройство не выбрали.
   messagebox.showinfo("Ошибка", "Вы не выбрали устройство")
   ok_button = Button(root, text="Ок", command=show_list_id_callback)
   return 0
  key, id, old, a1, a2, a3, a4, a5, a6, k, press_button, path, list_buttons = dict_save.preparation(dictio, games_checkmark_paths)
  new = ' '.join(old)   #  print(new)  # print(list_buttons)  print( type(new)  ) print(id)
  string_keys = list(key for key in list_buttons.keys() if isinstance(key, str))
  set_button_map = '''#!/bin/bash\nsudo xinput set-button-map {0} {1} '''.format(id, new)
  subprocess.call(['bash', '-c', set_button_map])  # установить конфигурацию кнопок для мыши.   print(dict_save.get_state_thread())
  dict_save.set_cur_app(path)# Текущая игра  # dict_save.set_current_path_game(game)# последний текущий путь # Запустить обработчик нажатий.  print(game, key, k, sep="\n")  #  print(key)  print(string_keys)
  dict_save.set_current_path_game(path)  # dict_save.set_prev_game(path)# мы установили путь для предыдущей игры
  # print(curr_name)
  t1 = threading.Thread(target=emunator_mouse, args =(root, dict_save, key, list_buttons, press_button, string_keys, games_checkmark_paths))  #t1.daemon = True
  t1.start()
  dict_save.set_thread(t1)# сохранить id посёлка потока
  
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

def return_file_path(dict_save):
 res=dict_save.return_jnson() # получаем настройки
 keys_values =res["key_value"][dict_save.get_cur_app()]# конфигурация кнопок от предыдущего профиля.
 mouse_press_old =res["mouse_press"][dict_save.get_cur_app()]# какие кнопки имеют залипания.
 # print(dict_save.get_current_app_path())
 cmd = ['zenity', '--file-selection', '--file-filter=EXE files | *.exe | *.EXE'] # Zenity команда для выбора одного exe файла
 # Вызов zenity и получение выбранного пути
 result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, text=True)
 path_to_file = result.stdout.strip()# новый путь к игре
 
 name_with_expansion = os.path.basename(path_to_file)# Получение базового имени файла с расширением из полного пути к файлу
 name = os.path.splitext(name_with_expansion)[0] # Отделение имени файла без расширения путем разбиения строки.
 li= list(res["paths"].keys())
 if path_to_file in li:
   return None
 res["paths"][str(path_to_file)]=str(name)
 res["games_checkmark"][str(path_to_file)]=True
 res["key_value"][str(path_to_file)]=keys_values # сохранить пред значения
 res["mouse_press"][str(path_to_file)]= list(mouse_press_old)
 res1= res["key_value"]

 dict_save.save_jnson(res)
 if path_to_file in res1:
   return path_to_file
 else:
     res["key_value"][path_to_file]=["LBUTTON","RBUTTON",  "WHEEL_MOUSE_BUTTON",
      "WHEEL_MOUSE_UP", "WHEEL_MOUSE_DOWN", 'XBUTTON1', 'XBUTTON2']
 return path_to_file

def set_list_box(dict_save, index=0):
 if index != 0:
  dict_save.set_count(index)  # Установить  индекс текущей игры.
 dict_save.set_box_values()  # Установить значения выпадающего списка.
 dict_save.set_values_box()
def hide_window():# Функция для сворачивания окна в трей
 root.withdraw()  # Скрываем окно
 icon.run()  # Запускаем значок в трее
def quit_app(icon, item):# Функция для выхода из приложения
 icon.stop()  # Останавливаем значок
 root.destroy()  # Закрываем приложение


def reorder_keys_in_dict(res, index, direction='up'):
 """
 Перемещает ключ на позицию index вверх/вниз (swap с соседним)
 во всех вложенных dict'ах, где встречаются ключи из res['paths'].
 Возвращает новый словарь (оригинал не меняется).
 """
 if 'paths' not in res or not isinstance(res['paths'], dict):
  return res
 
 orig_keys = list(res['paths'].keys())
 n = len(orig_keys)
 target = index + (-1 if direction == 'up' else 1)
 
 # границы
 if not (0 <= index < n and 0 <= target < n):
  return res
 
 # новый порядок ключей (после обмена двух соседних)
 new_order = orig_keys.copy()
 new_order[index], new_order[target] = new_order[target], new_order[index]
 
 def reorder_recursive(d):
  """Рекурсивно обрабатывает dict: сначала рекурсивно обрабатываем значения,
  затем, если текущий словарь содержит ключи из orig_keys, перестраиваем его ключи в new_order."""
  if not isinstance(d, dict):
   return d
  
  # сначала рекурсивно обработаем все вложенные значения
  processed = {}
  for k, v in d.items():
   processed[k] = reorder_recursive(v)
  
  # если в этом словаре нет ни одного ключа из orig_keys — возвращаем обработанный вариант
  if not any(k in processed for k in orig_keys):
   return processed
  
  # иначе создаём новый словарь с ключами в порядке new_order (если присутствуют),
  # затем добавляем оставшиеся ключи в их исходном порядке
  new_d = {}
  for k in new_order:
   if k in processed:
    new_d[k] = processed[k]
  for k in processed:
   if k not in new_d:
    new_d[k] = processed[k]
  return new_d
 
 # Собираем новый результат, не мутируя оригинал
 new_res = {}
 for top_k, top_v in res.items():
  if isinstance(top_v, dict):
   new_res[top_k] = reorder_recursive(top_v)
  else:
   new_res[top_k] = top_v
 
 return new_res


simple_key_map = {
    'KEY_KP7': ' 7\nHome', 'KEY_KP8': '8\n↑', 'KEY_KP9': '9\nPgUp',
    'KEY_KP4': '4\n←', 'KEY_KP5': '5\n', 'KEY_KP6': '6\n→',
    'KEY_KP1': '1\nEnd', 'KEY_KP2': '2\n↓', 'KEY_KP3': '3\nPgDn'
}

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