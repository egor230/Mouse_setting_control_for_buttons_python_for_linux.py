import sys, os, json, threading, subprocess, psutil, signal, time, copy, re, pyautogui, deepdiff
from dataclasses import dataclass
import keyboard as keybord_from
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox,
                             QTextEdit, QTabWidget, QScrollArea, QFrame, QCheckBox, QLineEdit, QMessageBox, QStyleFactory,
                             QToolTip, QGridLayout, QDialog, QPlainTextEdit, QSystemTrayIcon, QMenu)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer, QObject, QEvent
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette, QTextCursor
from pynput import mouse, keyboard
from pynput.mouse import Button as Button_Controller, Controller
from pynput.keyboard import Key, Listener
from evdev import InputDevice, categorize, ecodes, list_devices, UInput

# Создаем словари (остаются без изменений)
en_to_ru = {'a': 'ф', 'A': 'Ф', 'b': 'и', 'B': 'И', 'c': 'с', 'C': 'С', 'd': 'в', 'D': 'В', 'e': 'у', 'E': 'У', 'f': 'а', 'F': 'А', 'g': 'п', 'G': 'П',
            'h': 'р', 'H': 'Р', 'i': 'ш', 'I': 'Ш', 'j': 'о', 'J': 'О', 'k': 'л', 'K': 'Л',
            'l': 'д', 'L': 'Д', 'm': 'ь', 'M': 'Ь', 'n': 'т', 'N': 'Т', 'o': 'щ', 'O': 'Щ', 'p': 'з', 'P': 'З', 'q': 'й', 'Q': 'Й', 'r': 'к', 'R': 'К', 's': 'ы', 'S': 'Ы',
            't': 'е', 'T': 'Е', 'u': 'г', 'U': 'Г', 'v': 'м', 'V': 'М',
            'w': 'ц', 'W': 'Ц', 'x': 'ч', 'X': 'Ч', 'y': 'н', 'Y': 'Н', 'z': 'я', 'Z': 'Я', '.': '-', ',': '+', ' ': ' '}
ru_to_en = {'ф': 'a', 'Ф': 'A', 'и': 'b', 'И': 'B', 'с': 'c', 'С': 'C', 'в': 'd', 'В': 'D', 'у': 'e', 'У': 'E', 'а': 'f', 'А': 'F',
            'п': 'g', 'П': 'G', 'р': 'h', 'Р': 'H', 'ш': 'i', 'Ш': 'I', 'о': 'j', 'О': 'J', 'л': 'k', 'Л': 'K',
            'д': 'l', 'Д': 'L', 'ь': 'm', 'Ь': 'M', 'т': 'n', 'Т': 'N', 'щ': 'o', 'Щ': 'O', 'з': 'p', 'З': 'P', 'й': 'q',
            'Й': 'Q', 'к': 'r', 'К': 'R', 'ы': 's', 'Ы': 'S', 'е': 't', 'Е': 'T', 'г': 'u', 'Г': 'U', 'м': 'v', 'М': 'V',
            'ц': 'w', 'Ц': 'W', 'ч': 'x', 'Ч': 'X', 'н': 'y', 'Н': 'Y', 'я': 'z', 'Я': 'Z', '-': '.', '+': ',', ' ': ' '}

KEYS = {" ": 0x0, "LBUTTON": 'mouse left', "RBUTTON": 'mouse right', "WHEEL_MOUSE_BUTTON": "mouse middle",
        "WHEEL_MOUSE_UP": "WHEEL_MOUSE_UP", "MBUTTON": 0x04, "SCROLL_UP": "scroll_up",
        "SCROLL_DOWN": "scroll_down", "XBUTTON1": 0x05, "XBUTTON2": 0x06, "BACKSPACE": "BackSpace",
        "TAB": "Tab", "CLEAR": 0x0C, "RETURN": "Return", "KP_Enter": "KP_Enter",
        "Shift_L": "Shift_L", "CONTROL": "CONTROL", "MENU": 0x12, "PAUSE": 0x13, "CAPITAL": 0x14,
        "KANA": 0x15, "JUNJA": 0x17, "FINAL": 0x18, "KANJI": 0x19, "ESCAPE": 0x1B,
        "CONVERT": 0x1C, "NONCONVERT": 0x1D, "ACCEPT": 0x1E, "MODECHANGE": 0x1F, "SPACE": "space",
        "PRIOR": 0x21, "NEXT": 0x22, "END": "0x23", "HOME": "Home", "LEFT": "Left", "UP": "Up",
        "RIGHT": "Right", "DOWN": "Down", "SELECT": 0x29, "PRINT": 0x2A, "EXECUTE": 0x2B, "SNAPSHOT": 0x2C,
        "INSERT": 0x2D, "DELETE": "Delete", "HELP": 0x2F, "LWIN": "Super_L", "RWIN": "Super_R",

        "KEY0": 0, "KEY1": 1, "KEY2": 2, "KEY3": 3, "KEY4": 4, "KEY5": 5, "KEY6": 6,
        "KEY7": 7, "KEY8": 8, "KEY9": 9, "A": "A", "B": "B", "C": "C", "D": "D", "E": "E", "F": "F",
        "G": "G", "H": "H", "I": "I", "J": "J", "K": "K", "L": "L", "M": "M", "N": "N", "O": "O",
        "P": "P", "Q": "Q", "R": "R", "S": "S", "T": "T", "U": "U", "V": "V", "W": "W", "X": "X", "Y": "Y",
        "Z": "Z",

        "APPS": 0x5D, "SLEEP": 0x5F, "NUMPAD0": 0x60, "NUMPAD1": 79, "NUMPAD2": 80, "NUMPAD3": 81, "NUMPAD4": 82,
        "NUMPAD5": 83, "NUMPAD6": 84, "NUMPAD7": 85, "NUMPAD8": 86, "NUMPAD9": 87, "MULTIPLY": 0x6A, "ADD": 78,
        "SEPARATOR": 0x6C, "SUBTRACT": 0x6D, "DECIMAL": 0x6E, "DIVIDE": 0x6F, "F1": "F1", "F2": "F2", "F3": "F3",
        "F4": "F4", "F5": "F5", "F6": "F6", "F7": "F7", "F8": "F8", "F9": "F9", "F10": "F10", "F11": "F11", "F12": "F12",

        "F13": 0x7C, "F14": 0x7D, "F15": 0x7E, "F16": 0x7F, "F17": 0x80, "F18": 0x81, "F19": 0x82, "F20": 0x83, "F21": 0x84,
        "F22": 0x85, "F23": 0x86, "F24": 0x87, "NUMLOCK": "Num_Lock", "SCROLL": "Scroll_Lock", "OEM_FJ_JISHO": 0x92, "OEM_FJ_MASSHOU": 0x93,
        "OEM_FJ_TOUROKU": 0x94, "OEM_FJ_LOYA": 0x95, "OEM_FJ_ROYA": 0x96, "RSHIFT": "Shift_R", "LCONTROL": "ISO_Next_Group",
        "RCONTROL": "Control_R", "LMENU": 0xA4, "RMENU": 0xA5, "BROWSER_BACK": 0xA6, "BROWSER_FORWARD": 0xA7, "BROWSER_REFRESH": 0xA8,
        "BROWSER_STOP": 0xA9, "BROWSER_SEARCH": 0xAA, "BROWSER_FAVORITES": 0xAB, "BROWSER_HOME": 0xAC, "VOLUME_MUTE": 0xAD, "VOLUME_DOWN": 0xAE,
        "VOLUME_UP": 0xAF, "MEDIA_NEXT_TRACK": 0xB0, "MEDIA_PREV_TRACK": 0xB1, "MEDIA_STOP": 0xB2, "MEDIA_PLAY_PAUSE": 0xB3, "LAUNCH_MAIL": 0xB4,
        "LAUNCH_MEDIA_SELECT": 0xB5, "LAUNCH_APP1": 0xB6, "LAUNCH_APP2": 0xB7, "OEM_1": 0xBA, "OEM_PLUS": 0xBB, "OEM_COMMA": 0xBC,
        "OEM_MINUS": 0xBD, "OEM_PERIOD": 0xBE, "OEM_2": 0xBF, "OEM_3": 0xC0, "ABNT_C1": 0xC1, "ABNT_C2": 0xC2, "OEM_4": 0xDB,
        "OEM_5": 0xDC, "OEM_6": 0xDD, "OEM_7": 0xDE, "OEM_8": 0xDF, "OEM_AX": 0xE1, "OEM_102": 0xE2, "ICO_HELP": 0xE3, "PROCESSKEY": 0xE5,
        "ICO_CLEAR": 0xE6, "PACKET": 0xE7, "OEM_RESET": 0xE9, "OEM_JUMP": 0xEA, "OEM_PA1": 0xEB, "OEM_PA2": 0xEC, "OEM_PA3": 0xED,
        "OEM_WSCTRL": 0xEE, "OEM_CUSEL": 0xEF, "OEM_ATTN": 0xF0, "OEM_FINISH": 0xF1, "OEM_COPY": 0xF2, "OEM_AUTO": 0xF3, "OEM_ENLW": 0xF4,
        "OEM_BACKTAB": 0xF5, "ATTN": 0xF6, "CRSEL": 0xF7, "EXSEL": 0xF8, " EREOF": 0xF9, "PLAY": 0xFA, "ZOOM": 0xFB, "PA1": 0xFD,
        " OEM_CLEAR": 0xFE}

simple_key_map = { 'KEY_KP7': ' 7\nHome', 'KEY_KP8': '8\n↑', 'KEY_KP9': '9\nPgUp',
    'KEY_KP4': '4\n←', 'KEY_KP5': '5\n', 'KEY_KP6': '6\n→', 'KEY_KP1': '1\nEnd', 'KEY_KP2': '2\n↓', 'KEY_KP3': '3\nPgDn'}
LIST_MOUSE_BUTTONS = ["Левая кнопка", "Правая кнопка", "Средняя", "Колесико вверх", "Колесико вниз", "1 боковая", "2 боковая"]
LIST_KEYS = list(KEYS.keys())
defaut_list_mouse_buttons = ['LBUTTON', 'RBUTTON', 'WHEEL_MOUSE_BUTTON', 'SCROLL_UP', 'SCROLL_DOWN', 'XBUTTON1', 'XBUTTON2']

get_user_name = f'''#!/bin/bash
current_user=$(whoami);
echo $current_user
exit;# Завершаем выполнение скрипта
'''
user = subprocess.run(['bash'], input=get_user_name, stdout=subprocess.PIPE, text=True).stdout.strip()  # имя пользователя.
list_threads = []
mouse_controller = mouse.Controller()

class save_dict:
    def __init__(self):
        self.jnson = {}  # новые настройки.
        self.old_data = {}  # старые настройки.
        self.name_games = []  # названия игр
        self.labels = []  # надписи.
        self.var_list = []  # галочки
        self.labels_with_checkmark = {}  # словарь надписи с галочками
        self.box_values = []  # Значения боковых кнопок
        self.cur_app = ""  # Текущая игра.
        self.count = 0  # Индекс текущей игры.
        self.id = 0  # id устройство.
        self.mouse_button_press = []  # какие кнопки должны быть удержаны.
        self.dict_id_values = {}
        self.data = "settings control mouse buttons.json"  # файл настроек.
        self.path_current_app = ''  # Текущий путь к игре.
        self.process_id_active = 0  # id активного окна
        self.pid_and_path_window = {}  # Словарь игр и путей к ним.
        self.current_path_game = ""  # Путь к запущенной к игре.
        self.last_key_keyboard_script = ""
        self.thr = 0
        self.thread_exit=False  # это флаг выхода из потоков
        self.prev_game = ""  # Добавляем отсутствующий атрибут

    def get_last_key_keyboard_script(self):  #
        return self.last_key_keyboard_script

    def set_last_key_keyboard_script(self, last_key_keyboard_script1):
        self.last_key_keyboard_script = last_key_keyboard_script1

    def get_thread(self):  #
        return self.thr

    def set_thread(self, thr1):
        self.thr = thr1

    def get_current_path_game(self):  # Сохранить текущий путь к игре
        return self.current_path_game

    def set_current_path_game(self, current_path_game):
        self.current_path_game = current_path_game

    def get_prev_game(self):  # Сохранить текущий путь к игре
        return self.prev_game

    def set_prev_game(self, prev_game):
        self.prev_game = prev_game

    def get_pid_and_path_window(self):  #
        return self.pid_and_path_window

    def set_pid_and_path_window(self, pid_and_path_window):  #
        self.pid_and_path_window = pid_and_path_window

    def get_process_id_active(self):
        return self.process_id_active

    def set_process_id_active(self, process_id_active):  #
        self.process_id_active = process_id_active

    def get_current_app_path(self):  # Получить путь текущего окна.
        return self.path_current_app

    def set_current_app_path(self, app):  # Установить путь текущего окна.
        self.path_current_app = app

    def return_name_games(self):  # Вернуть список названия игр.
        return self.name_games

    def return_mouse_button_press(self):
        return self.mouse_button_press

    def save_labels(self, labels):
        self.labels = labels

    def return_labels(self):
        return self.labels

    def save_var_list(self, var_list):
        self.var_list = var_list

    def return_var_list(self):
        return self.var_list

    def return_labels_with_checkmark(self):
        return self.labels_with_checkmark

    def return_box_values(self):
        return self.box_values

    def return_list_mouse_button_press(self):  # какие кнопки должны быть удержаны для текущий игры.
        return list(self.jnson["mouse_press"][self.cur_app])

    def save_mouse_button_press(self, list_mouse_button_press=None, mouse_button_press=None):
        if mouse_button_press is None:
            mouse_button_press = self.mouse_button_press
        self.mouse_button_press = mouse_button_press
        if list_mouse_button_press is None:
            list_mouse_button_press = []  # Сохранить список какие кнопки должны быть удержаны.
            for i in range(len(mouse_button_press)):
                list_mouse_button_press.append(mouse_button_press[i].isChecked())

        self.jnson["mouse_press"][self.cur_app] = list(list_mouse_button_press)

    def save_jnson(self, jn):  # сохранить новые настройки
        self.jnson = jn

    def save_old_data(self, jnson):  # сохранить начальные настройки.
        self.old_data = copy.deepcopy(jnson)
        self.jnson = jnson

    def return_jnson(self):  # Вернуть новые настройки.
        return self.jnson

    def return_old_data(self):
        return self.old_data

    def set_cur_app(self, cur_app):  # установить текущего игру
        self.cur_app = str(cur_app)
        self.jnson["current_app"] = self.cur_app

    def get_cur_app(self):
        return str(self.jnson["current_app"])

    def set_count(self, count):
        self.count = count
        return self.count

    def get_count(self):
        return self.count

    def set_values_box(self):
        box_value = self.jnson["key_value"][self.cur_app]
        for i in range(len(self.box_values)):
            self.box_values[i].setCurrentText(box_value[i])

    def set_box_values(self):  # Установить значение для выпадающего списка.
        self.reset_id_value()
        res = self.jnson
        key_values = res["key_value"]
        d = list(res["paths"].keys())  # получить словарь путей и имен файлов.
        self.set_cur_app(d[self.count])  # установить текущую активную строку.
        self.jnson["current_app"] = d[self.count]  # Сохранить текущую активную строку.
        self.set_values_box()
        return self

    def write_to_file(self, new_data):
        # Сериализуем JSON с отступами и прогоняем через _format_scripts_in_json:
        # экранированные \n внутри bash-скриптов (script_mouse / keyboard_script)
        # превращаются в НАСТОЯЩИЕ переводы строк, чтобы в текстовом редакторе
        # скрипт выглядел как есть — построчно (см. REPORT_DOCUMENTATION.md §1.1).
        # Приложение читает файл через json.load(..., strict=False) + scripts_to_text,
        # поэтому такой формат корректен и повторно не портит файл (идемпотентно).
        json_string = _format_scripts_in_json(json.dumps(new_data, ensure_ascii=False, indent=2))  # self.data # файл настроек.
        with open(self.data, "w", encoding="UTF-8") as w:
            w.write(json_string)  # сохранить изменения в файле настроек.
        file_relus = '''#!/bin/bash\n
                       chmod a+rw \"{0}\" '''.format(self.data)
        subprocess.call(['bash', '-c', file_relus])  # Дать доступ на чтение и запись любому
        return self

    def get_list_ids(self):  # Получение списка id устройств.
        get_ids = '''#!/bin/bash
        ids=$(xinput list | grep -Ei "id=[0-9]+" | grep -oE "id=[0-9]+" | cut -d= -f2)
         for id in $ids; do
          output=$(xinput get-button-map "$id" 2>&1)
          # Исключаем сообщения об ошибках, добавляя проверки на наличие ошибок
          if [[ $output != *"device has no buttons"* && $output != *"X Error of failed request:"* ]]; then
              echo "$id:$output"
          fi
         done'''  # Команда shell для получения списка идентификаторов устройств ввода (мышей), которые подключены к системе.

        # Выполнение вышеуказанной команды shell в подпроцессе и декодирование результата в строку.
        id_list = subprocess.check_output(['bash', '-c', get_ids]).decode().splitlines()
        # print(id_list)
        button_map = {}  # Создание словаря для хранения соответствия между идентификаторами устройств и их кнопками.

        # Перебор всех элементов в списке id устройств.
        for item in id_list:  # Разделение элемента на ключ (id устройства) и значение (кнопок).
            key, value = item.split(':', 1)
            button_map[int(key)] = value.strip()
        # Добавление в словарь button_map кнопок устройства с соответствующим идентификатором.
        self.dict_id_values = button_map  # Сохранение карты кнопок в атрибут объекта.
        id_list = list(button_map.keys())  # Сохранение списка идентификаторов в переменной id_list.
        id_list = sorted(id_list)
        return id_list  # Возвращение списка id устройств для дальнейшего использования.

    def get_state_thread(self):
        return self.thread

    def set_default_id_value(self):  # Вернуть значения по умолчанию
        self.thread = True  # Прервать выполнение потока обработчика нажатий.
        for id in self.dict_id_values:
            st = str(self.dict_id_values[id])
            set_button_map = '''#!/bin/bash
            sudo xinput set-button-map {0} {1}
            '''.format(id, st)
            subprocess.call(['bash', '-c', set_button_map])

    def reset_id_value(self):  # Сброс настроек текущего id устройства.
        d = '1 2 3 4 5 6 7 8 9'  # print("reset_id_value")
        devices_mouse = list(self.dict_id_values.keys())
        for i in devices_mouse:
            set_button_map = '''#!/bin/bash
            sudo xinput set-button-map {0} {1}
            '''.format(self.id, d)
            process = subprocess.Popen(['bash', '-c', set_button_map], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                self.id = i
            else:
                break

    def get_default_id_value(self, id):  #
        try:
            d = self.dict_id_values[id]
            d_copy = copy.deepcopy(d)
            d = '1 2 3 4 5 6 7 8 9'
            return d
        except Exception as ex1:
            print(ex1)

    def write_in_log(self, text=" error"):  # Запись ошибок.
        with open("log.txt", "a") as f:
            f.write(str(text) + "\n")

        file_relus = '''#!/bin/bash
                       chmod a+rw {}   '''.format("log.txt")
        subprocess.call(['bash', '-c', file_relus])  # Дать доступ на чтение и запись любому


def _format_scripts_in_json(text):
    # Преобразуем экранированные переводы строк (\n) внутри bash-скриптов
    # (ключи script_mouse / keyboard_script) в НАСТОЯЩИЕ переносы строк,
    # чтобы в обычном текстовом редакторе скрипт выглядел как есть — построчно.
    # Продолжения выравниваются вертикально по первой строке скрипта (#!/bin/bash).
    # Экранированные кавычки \" и слэши \\ оставляем как есть (они корректны для json).
    # Такой JSON читается через json.load(..., strict=False).
    json_str_re = re.compile(r'"(?:[^"\\]|\\.)*"')

    def repl(m):
        s = m.group(0)
        if "\\n" not in s:  # содержит ли строка экранированный перевод строки (это bash-скрипт)?
            return s
        # Выравниваем продолжения по первой строке скрипта: отступ = колонке начала
        # содержимого (сразу после открывающей кавычки значения) внутри СТРОКИ.
        line_start = text.rfind("\n", 0, m.start()) + 1
        col = (m.start() - line_start) + 1
        cont = " " * col
        inner = s[1:-1]  # тело без крайних кавычек
        # Заменяем ТОЛЬКО \n, не предварённый другим слэшем (lookbehind), чтобы
        # экранированный \\ (двойной слэш в JSON) не давал «висячий» слэш
        # (JSONDecodeError: Invalid \escape). Обычный перевод строки \n всегда
        # предварён не-слэшем (или началом строки), поэтому заменяется корректно.
        inner = re.sub(r'(?<!\\)\\n', "\n" + cont, inner)
        suffix = "\n" + cont  # убираем хвостовой перенос (от завершающего \n скрипта), чтобы " не уезжала
        if inner.endswith(suffix):
            inner = inner[:-len(suffix)]
        return '"' + inner + '"'

    return json_str_re.sub(repl, text)


def scripts_to_text(data):
    # Нормализация после чтения: убираем отступы продолжения строк, которые могли
    # попасть внутрь скрипта (от старых версий файла), чтобы строка была «чистой»
    # и повторная запись не накапливала лишние отступы.
    for section in ("script_mouse", "keyboard_script"):
        container = data.get(section)
        if not isinstance(container, dict):
            continue
        for app, sub in container.items():
            if section == "keyboard_script":
                keys = sub.get("keys", {}) if isinstance(sub, dict) else {}
                for k, v in list(keys.items()):
                    if isinstance(v, str) and "\n" in v:
                        lines = v.split("\n")
                        keys[k] = "\n".join([lines[0]] + [ln.lstrip() for ln in lines[1:]])
            else:
                if isinstance(sub, dict):
                    for k, v in list(sub.items()):
                        if isinstance(v, str) and "\n" in v:
                            lines = v.split("\n")
                            sub[k] = "\n".join([lines[0]] + [ln.lstrip() for ln in lines[1:]])
    return data


class SmartTyper:
    """Virtual keyboard for mouse-to-key assignments.

    Keyboard actions selected in the profile UI are emitted through evdev.UInput,
    not through xte.  The class owns a single virtual keyboard device and is safe
    to call from the listener's worker threads.  Existing bash macros are not
    modified: a macro remains an explicit user script and may still use xte.
    """

    _ACTION_TO_ECODE = {
        'BACKSPACE': 'KEY_BACKSPACE', 'TAB': 'KEY_TAB', 'RETURN': 'KEY_ENTER',
        'KP_ENTER': 'KEY_KPENTER', 'ESCAPE': 'KEY_ESC', 'SPACE': 'KEY_SPACE',
        'HOME': 'KEY_HOME', 'END': 'KEY_END', 'LEFT': 'KEY_LEFT', 'RIGHT': 'KEY_RIGHT',
        'UP': 'KEY_UP', 'DOWN': 'KEY_DOWN', 'INSERT': 'KEY_INSERT', 'DELETE': 'KEY_DELETE',
        'PRIOR': 'KEY_PAGEUP', 'NEXT': 'KEY_PAGEDOWN', 'PAGE_UP': 'KEY_PAGEUP',
        'PAGE_DOWN': 'KEY_PAGEDOWN', 'SNAPSHOT': 'KEY_SYSRQ', 'PAUSE': 'KEY_PAUSE',
        'CAPITAL': 'KEY_CAPSLOCK', 'CAPS_LOCK': 'KEY_CAPSLOCK', 'NUMLOCK': 'KEY_NUMLOCK',
        'NUM_LOCK': 'KEY_NUMLOCK', 'SCROLL': 'KEY_SCROLLLOCK', 'SCROLL_LOCK': 'KEY_SCROLLLOCK',
        'LWIN': 'KEY_LEFTMETA', 'RWIN': 'KEY_RIGHTMETA', 'SHIFT_L': 'KEY_LEFTSHIFT',
        'SHIFT_R': 'KEY_RIGHTSHIFT', 'LCONTROL': 'KEY_RIGHTALT',
        'RCONTROL': 'KEY_RIGHTCTRL', 'CONTROL': 'KEY_LEFTCTRL',
        'CONTROL_L': 'KEY_LEFTCTRL', 'CONTROL_R': 'KEY_RIGHTCTRL',
        'ALT_L': 'KEY_LEFTALT', 'ALT_R': 'KEY_RIGHTALT', 'LMENU': 'KEY_LEFTALT',
        'RMENU': 'KEY_RIGHTALT', 'MENU': 'KEY_COMPOSE', 'APPS': 'KEY_COMPOSE',
        'ISO_NEXT_GROUP': 'KEY_RIGHTALT', 'ADD': 'KEY_KPPLUS', 'SUBTRACT': 'KEY_KPMINUS',
        'MULTIPLY': 'KEY_KPASTERISK', 'DIVIDE': 'KEY_KPSLASH', 'DECIMAL': 'KEY_KPDOT',
    }

    def __init__(self):
        self._lock = threading.RLock()
        self._pressed_codes = set()
        self._ui = None
        self._create_device()

    def _create_device(self):
        try:
            self._ui = UInput(
                {ecodes.EV_KEY: list(range(1, 256))},
                name='Mouse Setting Control Virtual Keyboard',
                bustype=ecodes.BUS_USB,
                vendor=0x1209,
                product=0x0001,
            )
        except Exception as exc:
            # Do not stop mouse emulation when /dev/uinput is unavailable.  The
            # caller uses the library fallback, never xte, for this rare case.
            self._ui = None
            try:
                dict_save.write_in_log('UInput keyboard is unavailable: ' + str(exc))
            except Exception:
                pass

    @staticmethod
    def _ecodes_value(name):
        value = getattr(ecodes, name, None)
        if isinstance(value, int):
            return value
        value = ecodes.ecodes.get(name)
        return value if isinstance(value, int) else None

    def _resolve(self, action):
        if not isinstance(action, str):
            return None
        action = action.strip()
        if not action or action == ' ':
            return None
        if action.isdigit():
            code = int(action)
            if 0 < code < 256:
                return code
            return None
        normalized = action.upper()
        if len(action) == 1 and action.isalpha():
            key_name = 'KEY_' + normalized
        elif len(action) == 1 and action.isdigit():
            key_name = 'KEY_' + action
        elif normalized.startswith('F') and normalized[1:].isdigit():
            key_name = 'KEY_' + normalized
        elif normalized.startswith('NUMPAD') and normalized[6:].isdigit():
            key_name = 'KEY_KP' + normalized[6:]
        else:
            key_name = self._ACTION_TO_ECODE.get(normalized)
        return self._ecodes_value(key_name) if key_name else None

    def key_down(self, action):
        """Send one UInput key-down event for a mapped mouse action."""
        code = self._resolve(action)
        if code is None:
            return False
        if self._ui is None:
            self._create_device()
        if self._ui is None:
            return False
        try:
            with self._lock:
                if code not in self._pressed_codes:
                    self._ui.write(ecodes.EV_KEY, code, 1)
                    self._ui.syn()
                    self._pressed_codes.add(code)
            return True
        except Exception as exc:
            try:
                dict_save.write_in_log('UInput key-down failed: ' + str(exc))
            except Exception:
                pass
            return False

    def key_up(self, action):
        """Send one UInput key-up event for a mapped mouse action."""
        code = self._resolve(action)
        if code is None:
            return False
        if self._ui is None:
            self._create_device()
        if self._ui is None:
            return False
        try:
            with self._lock:
                self._ui.write(ecodes.EV_KEY, code, 0)
                self._ui.syn()
                self._pressed_codes.discard(code)
            return True
        except Exception as exc:
            try:
                dict_save.write_in_log('UInput key-up failed: ' + str(exc))
            except Exception:
                pass
            return False

    # Compatibility aliases for code outside this file.
    press = key_down
    release = key_up


smart_typer = SmartTyper()


class Job(threading.Thread):
    def __init__(self, key, *args, **kwargs):
        self.key = key
        self.sw = True
        self.hook_flag_mouse = True  # захват кнопки мыши.
        super(Job, self).__init__(*args, **kwargs)
        self.__flag = threading.Event()  # The flag used to pause the thread
        self.__flag.set()  # Set to True
        self.__running = threading.Event()  # Used to stop the thread identification
        self.__running.set()  # Set running to True

    def run(self):
        time.sleep(0.00001)
        while self.__running.is_set():
            self.__flag.wait()  # return immediately when it is True, block until the internal flag is True when it is False
            time.sleep(0.08)
            t = 0.0115  # задержка в прокрутке.
            if self.key == "SCROLL_UP":
                thread = threading.Thread(target=key_work.mouse_wheel_up)
                thread.start()  # key_work.mouse_wheel_donw()   # keybord_from.press(self.key)
                time.sleep(t)
            if self.key == "SCROLL_DOWN":
                thread1 = threading.Thread(target=key_work.mouse_wheel_donw)
                thread1.start()  # key_work.mouse_wheel_donw()   # keybord_from.press(self.key)
                time.sleep(t)  # thread1.join()
            # keybord_from.release(self.key)   # print(self.key)   # directinput.keyDown(str( self.key).lower())

    def pause(self):
        self.__flag.clear()  # Set to False to block the thread

    def resume(self):
        self.__flag.set()  # Set to True, let the thread stop blocking

    def stop(self):
        self.__flag.set()  # Resume the thread from the suspended state, if it is already suspended
        self.__running.clear()  # Set to False

    def set_sw(self, value):
        self.sw = value

    def get_sw(self):
        return self.sw

    def set_hook_flag_mouse(self, value):
        self.hook_flag_mouse = value

    def get_hook_flag_mouse(self):
        return self.hook_flag_mouse

dict_save = save_dict()  # класс

def is_path_in_list(path, path_list):  # проверяет, содержится ли путь в списке путей.
    return any(path in item for item in path_list)

def get_index_of_path(path, path_list):
    index = next(index for index, item in enumerate(path_list) if path in item)
    return index  # находит индекс пути в списке путей и возвращает соответствующий элемент списка.

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
        if value.startswith('/mnt/'):  # Если путь уже начинается с /mnt/, оставляем как есть
            updated_value = value
        else:  # Заменяем X:/ на new_prefix
            updated_value = re.sub(r'^[A-Z]:/', new_prefix, value, count=1)
            # Убираем дублирование /games/games/ или других частей
            parts = updated_value.split('/')  # Удаляем повторяющиеся сегменты после new_prefix
            unique_parts = []
            for part in parts:
                if not unique_parts or part != unique_parts[-1]:
                    unique_parts.append(part)
            updated_value = '/'.join(unique_parts)
        # Добавляем .exe, если его нет
        if isinstance(updated_value, str) and not updated_value.lower().endswith('.exe'):
            updated_value += '.exe'
        updated_dict[key] = updated_value  # Путей обновить значение путей.
    return updated_dict

def get_visible_active_pid():
    try:  # Получаем ID активного окна в десятичном формате
        window_id_dec = subprocess.run(['xdotool', 'getactivewindow'],
                                       stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True).stdout.strip()
        if not window_id_dec:
            print("Не удалось получить ID активного окна")
            return 0
        # Преобразуем десятичное ID в шестнадцатеричное (например, 1234567 -> 0x01234567)
        window_id_hex = hex(int(window_id_dec))
        # Проверка: окно свернуто?
        xprop_output = subprocess.run(['xprop', '-id', window_id_dec, '_NET_WM_STATE'],
                                      stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True).stdout

        if "_NET_WM_STATE_HIDDEN" in xprop_output:
            print("Окно свернуто")
            return 0  # Окно свернуто
        # Получаем список окон с PID
        wmctrl_output = subprocess.run(['wmctrl', '-lp'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                       text=True).stdout
        # Ищем строку с нужным ID окна
        for line in wmctrl_output.splitlines():
            parts = line.split()  # print(parts)
            if len(parts) >= 3 and parts[0] == window_id_hex:
                pid = int(parts[2])  # PID — третий элемент#   print(pid)
                return pid
        return 0  # PID не найден
    except Exception as e:
        print(f"Ошибка: {e}")
        return 0

def is_window_minimized(window_id):
    try:
        xprop_output = subprocess.run(['xprop', '-id', window_id, '_NET_WM_STATE'],
                                      stdout=subprocess.PIPE, text=True).stdout
        return "_NET_WM_STATE_HIDDEN" in xprop_output
    except Exception:
        return True  # Если ошибка, считаем окно свернутым
  
def get_active_window_exe(user, id_active):
    try:
        result = subprocess.run(['ps', 'aux'], stdout=subprocess.PIPE, text=True).stdout
        lines = result.split('\n')
        for line in lines:  # Фильтруем строки по пользователю и PID
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
                if ".exe" in exe_path and id_active == pid:  # print(exe_path)
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

def Get_pid_and_path_window():  # Получаем идентификатор активного окна
 # Имя пользователя (один раз)
 
 # Имя пользователя (один раз)
 user = (
   os.environ.get('USER')
   or os.environ.get('LOGNAME')
   or (pwd.getpwuid(os.getuid()).pw_name if hasattr(os, 'getuid') else None)
 )
 if not user:
  try:
   user = subprocess.run(
    ['whoami'], capture_output=True, text=True, timeout=1
   ).stdout.strip() or None
  except Exception:
   user = None
 
 _RE_EXE_SH = re.compile(r'.*\.(exe|sh)$', re.IGNORECASE)
 
 _BASH_GET_MAIN_ID = '''#!/bin/bash
 active_window_id=$(xdotool getactivewindow 2>/dev/null)
 if [[ -n "$active_window_id" && "$active_window_id" =~ ^[0-9]+$ && "$active_window_id" != "0" ]]; then
     process_id_active=$(xdotool getwindowpid "$active_window_id" 2>/dev/null)
     if [[ -n "$process_id_active" && "$process_id_active" != "0" ]]; then
         parent_pid=$(ps -p "$process_id_active" -o ppid= 2>/dev/null | tr -d '[:space:]')
         if [[ -n "$parent_pid" && "$parent_pid" != "0" && "$parent_pid" != "1" ]] && ps -p "$parent_pid" >/dev/null 2>&1; then
             echo "$parent_pid"
         else
             echo "$process_id_active"
         fi
         exit 0
     fi
 fi
 echo "0"
 '''
 
 # Кэш winepath (значительно ускоряет повторяющиеся вызовы)
 _winepath_cache = {}
 
 def _winepath_u(win_path: str):
  if win_path in _winepath_cache:
   return _winepath_cache[win_path]
  try:
   r = subprocess.run(
    ['winepath', '-u', win_path],
    capture_output=True, text=True, timeout=1.5
   )
   result = r.stdout.strip() if r.returncode == 0 else None
  except (subprocess.SubprocessError, FileNotFoundError, OSError):
   result = None
  _winepath_cache[win_path] = result
  return result
 
 my_pid = os.getpid()
 data_dict = {}
 
 # === Один проход по всем процессам ===
 for proc in psutil.process_iter(["pid", "username", "cmdline"]):
  try:
   info = proc.info
   pid = info["pid"]
   if pid == my_pid:
    continue
   
   # Фильтр по пользователю
   if user is not None and info.get("username") != user:
    continue
   
   cmdline_parts = info["cmdline"] or []
   
   # cwd / exe через /proc
   try:
    cwd = os.readlink(f"/proc/{pid}/cwd")
   except (FileNotFoundError, PermissionError, OSError):
    cwd = None
   
   try:
    exe_link = os.readlink(f"/proc/{pid}/exe")
   except (FileNotFoundError, PermissionError, OSError):
    exe_link = None
   
   # --- Определяем, Wine ли это ---
   is_wine = False
   if exe_link:
    low_exe = exe_link.lower()
    if (
      'wine-preloader' in low_exe
      or 'wine64-preloader' in low_exe
      or '/wine' in low_exe
    ):
     is_wine = True
   if not is_wine:
    is_wine = any('.exe' in arg.lower() for arg in cmdline_parts)
   
   resolved = None
   
   # ===== WINE-процесс =====
   if is_wine:
    win_exe = None
    for arg in cmdline_parts:
     if arg.lower().endswith('.exe'):
      win_exe = arg
      break
    
    if win_exe:
     exe_name = os.path.basename(win_exe.replace('\\', '/'))
     found = False
     
     # 1. Абсолютный Windows-путь (C:\...)
     if len(win_exe) >= 2 and win_exe[1] == ':':
      linux_path = _winepath_u(win_exe)
      if linux_path and os.path.isfile(linux_path):
       resolved = linux_path
       found = True
     
     # 2. cwd + basename
     if not found and cwd:
      candidate = os.path.join(cwd, exe_name)
      if os.path.isfile(candidate):
       resolved = candidate
       found = True
     
     # 3. Относительный путь (dx11\Game.exe)
     if not found and cwd:
      rel = win_exe.replace('\\', '/')
      candidate = os.path.normpath(os.path.join(cwd, rel))
      if os.path.isfile(candidate):
       resolved = candidate
       found = True
     
     # 4. Ещё раз basename (на случай, если предыдущие не сработали)
     if not found and cwd:
      candidate = os.path.join(cwd, exe_name)
      if os.path.isfile(candidate):
       resolved = candidate
       found = True
     
     # 5. Fallback: find (уменьшен depth и timeout)
     if not found and cwd and exe_name:
      try:
       r = subprocess.run(
        [
         'find', cwd,
         '-maxdepth', '2',
         '-iname', exe_name,
         '-type', 'f'
        ],
        capture_output=True, text=True, timeout=1.5
       )
       if r.returncode == 0 and r.stdout.strip():
        resolved = r.stdout.strip().split('\n', 1)[0]
        found = True
      except (subprocess.SubprocessError, FileNotFoundError, OSError):
       pass
   
   # ===== Обычный Linux-процесс =====
   else:
    if not cmdline_parts:
     resolved = exe_link
    else:
     relative_exe = cmdline_parts[0].replace("\\", "/")
     if relative_exe.startswith('/'):
      full_path = relative_exe
     elif cwd and relative_exe:
      full_path = os.path.normpath(os.path.join(cwd, relative_exe))
     else:
      full_path = None
     
     if full_path and os.path.isfile(full_path):
      resolved = full_path
     else:
      resolved = exe_link  # fallback
   
   # --- Доп. сканирование cmdline на .exe/.sh ---
   if not resolved:
    for arg in cmdline_parts:
     arg_clean = arg.replace('\\', '/').strip('"')
     if _RE_EXE_SH.search(arg_clean):
      resolved = arg_clean
      break
   
   if resolved:
    data_dict[pid] = resolved
    # ID потоков — только если путь найден
    try:
     for thread in proc.threads():
      data_dict[thread.id] = resolved
    except (psutil.NoSuchProcess, psutil.AccessDenied):
     pass
  
  except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
   continue
  except Exception:
   continue
 
 # === Разворачиваем словарь на родителей/потомков ===
 expanded = dict(data_dict)
 for game_pid, game_path in list(data_dict.items()):
  try:
   proc = psutil.Process(game_pid)
   # Родители
   parent = proc.parent()
   while parent is not None:
    expanded.setdefault(parent.pid, game_path)
    parent = parent.parent()
   # Потомки
   for child in proc.children(recursive=True):
    expanded.setdefault(child.pid, game_path)
  except (psutil.NoSuchProcess, psutil.AccessDenied):
   continue
 
 # === PID активного окна ===
 id_active = 0
 try:
  r = subprocess.run(
   ['bash'],
   input=_BASH_GET_MAIN_ID,
   stdout=subprocess.PIPE,
   stderr=subprocess.DEVNULL,
   text=True,
   timeout=3,
  )
  out = r.stdout.strip()
  if out and out.isdigit():
   id_active = int(out)
 except (subprocess.SubprocessError, ValueError, OSError):
  pass
 
 return expanded, id_active

def default_profile_path(store, enabled_profiles):
    """Return a valid fallback profile; prefer the explicitly named default."""
    settings = store.return_jnson()
    paths = settings.get('paths', {})
    enabled = set(enabled_profiles)
    for path, name in paths.items():
        if path in enabled and (name == 'По умолчанию' or path == 'C:/Windows/explorer.exe'):
            return path
    return next((path for path in paths if path in enabled), '')


def fallback_profile_path(store, enabled_profiles):
    """Return the saved prior profile, or a valid default if none is saved."""
    previous = store.get_prev_game()
    if previous in enabled_profiles:
        return previous
    fallback = default_profile_path(store, enabled_profiles)
    if fallback:
        store.set_prev_game(fallback)
    return fallback


def remember_fallback_before_game(store, current_profile, next_profile, enabled_profiles):
    """Keep the non-game/default profile while moving between game windows."""
    saved = fallback_profile_path(store, enabled_profiles)
    if current_profile == saved and current_profile != next_profile:
        store.set_prev_game(current_profile)


def check_current_active_window(dict_save, games_checkmark_paths):
    """Return the game profile for the active window, otherwise a safe fallback."""
    fallback = fallback_profile_path(dict_save, games_checkmark_paths)
    try:
        data_dict, id_active = Get_pid_and_path_window()
        file_path = data_dict.get(id_active, '')
        if file_path and is_path_in_list(file_path, games_checkmark_paths):
            return games_checkmark_paths[get_index_of_path(file_path, games_checkmark_paths)]

        has_portproton = any('/PortProton/data' in p and '.exe' in p for p in data_dict.values())
        if has_portproton and id_active in data_dict:
            for path in data_dict.values():
                if is_path_in_list(path, games_checkmark_paths):
                    return games_checkmark_paths[get_index_of_path(path, games_checkmark_paths)]
    except Exception as exc:
        try:
            dict_save.write_in_log(exc)
        except Exception:
            pass
    return fallback

def show_list_id_callback():
    show_list_id = f'''#!/bin/bash
   gnome-terminal -- bash -c 'xinput list;
   read;   exec bash' '''  # показать список устройств в терминале
    subprocess.run(['bash', '-c', show_list_id])

@dataclass
class MouseBinding:
    """One intercepted physical mouse control and its runtime state."""

    listener_button: str
    slot: int
    worker: Job


class MouseProfileRuntime:
    """All state required to run one active mouse profile.

    The object is intentionally created once per profile activation.  It replaces
    the former parallel parameters (`key`, `list_buttons`, `press_button`,
    `string_keys`, and `games_checkmark_paths`) with one explicit context.
    """

    # slot, physical X11 button, virtual X11 button, pynput listener button,
    # assignments that retain their normal physical behavior and are not hooked.
    INTERCEPTION_RULES = (
        (1, 3, '11', 'Button.button11', {'RBUTTON'}),
        (2, 2, '12', 'Button.button12', {' ', 'WHEEL_MOUSE_BUTTON'}),
        (3, 4, '13', 'Button.button13', {'SCROLL_UP'}),
        (4, 5, '14', 'Button.button14', {' ', 'SCROLL_DOWN'}),
        (5, 9, '16', 'Button.button16', {'XBUTTON1'}),
        (6, 8, '15', 'Button.button15', {'XBUTTON2'}),
    )
    MOUSE_ACTIONS = {
        'LBUTTON', 'RBUTTON', 'WHEEL_MOUSE_BUTTON', 'MBUTTON',
        'SCROLL_UP', 'SCROLL_DOWN',
    }

    def __init__(self, store):
        self.store = store
        self.settings = store.return_jnson()
        self.game = str(self.settings['current_app'])
        self.device_id = self.settings['id']
        self.assignments = list(self.settings['key_value'][self.game])
        self.hold_flags = list(self.settings['mouse_press'][self.game])
        self.enabled_profiles = tuple(
            path for path, enabled in self.settings['games_checkmark'].items() if enabled
        )
        self.bindings = {}
        self.virtual_by_physical_button = {}
        self.stop_requested = threading.Event()
        self._build_bindings()

    def _build_bindings(self):
        for slot, physical, virtual, listener_button, pass_through in self.INTERCEPTION_RULES:
            if self.assignments[slot] in pass_through:
                continue
            worker = Job(self.assignments[slot])
            worker.start()
            worker.pause()
            self.bindings[listener_button] = MouseBinding(listener_button, slot, worker)
            self.virtual_by_physical_button[physical] = virtual

    def apply_button_map(self):
        default_map = self.store.get_default_id_value(self.device_id).split()
        remapped_map = list(default_map)
        for index, button in enumerate(remapped_map):
            try:
                physical_button = int(button)
            except (TypeError, ValueError):
                continue
            virtual_button = self.virtual_by_physical_button.get(physical_button)
            if virtual_button is not None:
                remapped_map[index] = virtual_button

        self.store.reset_id_value()
        command = ['sudo', 'xinput', 'set-button-map', str(self.device_id), *remapped_map]
        try:
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        except OSError as exc:
            self.store.write_in_log(exc)

    def handle_listener_event(self, button, pressed):
        """Dispatch one pynput event in listener order without a competing worker."""
        if not self.stop_requested.is_set():
            self.dispatch(button, pressed)

    def join_event_workers(self):
        # Listener events are now handled synchronously, so no detached event
        # thread can lose a key-down/key-up pair during a profile change.
        return

    def stop_workers(self):
        for binding in self.bindings.values():
            binding.worker.stop()

    def stop(self):
        self.stop_requested.set()
        self.stop_workers()
        self.join_event_workers()

    def dispatch(self, button, pressed):
        if self.stop_requested.is_set():
            return
        binding = self.bindings.get(str(button))
        if binding is None or not binding.worker.get_hook_flag_mouse():
            return

        action = self.assignments[binding.slot]
        if action == ' ':
            return
        try:
            script = self._mouse_script(binding.slot)
            if script:
                threading.Thread(target=execute_script, args=(script,), daemon=True).start()
            elif action in self.MOUSE_ACTIONS:
                self._handle_mouse_action(binding, pressed)
            else:
                self._handle_keyboard_action(binding, pressed)
        except Exception as exc:
            self.store.write_in_log(exc)

    def _mouse_script(self, slot):
        current_game = self.store.get_cur_app()
        button_name = defaut_list_mouse_buttons[slot]
        return self.store.return_jnson().get('script_mouse', {}).get(current_game, {}).get(button_name, '')

    def _handle_mouse_action(self, binding, pressed):
        global sticking_right_mouse
        slot = binding.slot
        action = self.assignments[slot]
        hold = self.hold_flags[slot]

        if not hold and action in {'SCROLL_UP', 'SCROLL_DOWN'}:
            if pressed:
                binding.worker.resume()
            else:
                binding.worker.pause()
            return

        if not hold and pressed:
            if action == 'RBUTTON':
                key_work.mouse_right_donw()
            elif action == 'WHEEL_MOUSE_BUTTON':
                key_work.mouse_middle_donw()
            return

        if hold and pressed and action == 'RBUTTON':
            if sticking_right_mouse:
                mouse_controller.release(mouse.Button.right)
                sticking_right_mouse = False
            else:
                mouse_controller.press(mouse.Button.right)
                sticking_right_mouse = True

    def _handle_keyboard_action(self, binding, pressed):
        slot = binding.slot
        key_value = str(KEYS[self.assignments[slot]])
        if not self.hold_flags[slot]:
            if pressed:
                key_work.key_press(key_value, slot)
            else:
                key_work.key_release(key_value, slot)
            return

        if pressed and binding.worker.get_sw():
            binding.worker.set_sw(False)
            key_work.key_press(key_value, slot)
        elif pressed:
            binding.worker.set_sw(True)
            key_work.key_release(key_value, slot)


class work_key:
    def __init__(self):
        self.keys_list = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's', 'd', 'f', 'g',
                          'h', 'j', 'k', 'l', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ]
        self.keys_list1 = ['BackSpace', 'Tab', 'Return', 'KP_Enter', 'Escape', 'Delete', 'Home', 'End', 'Page_Up',
                           'Page_Down', 'F1', 'Up', 'Down', 'Left', 'Right', 'Control_L', 'ISO_Next_Group', 'Control_R',
                           'Shift_L', 'Shift_R', 'Alt_L', 'Alt_R', 'Super_L', 'Super_R', 'Caps_Lock', 'Num_Lock', 'Scroll_Lock',
                           'space', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12']

    def mouse_wheel_up(self):  #
        mouse_wheel = '''#!/bin/bash
        xdotool click  {0}    '''.format(4)
        subprocess.call(['bash', '-c', mouse_wheel])

    def mouse_wheel_donw(self):  #
        mouse_wheel = '''#!/bin/bash
        xdotool click  {0}
         '''.format(5)
        subprocess.call(['bash', '-c', mouse_wheel])

    def mouse_right_donw(self):  # Правая кнопки мыши
        # mouse_controller.click(mouse.Button.right)
        # pyautogui.click(button='right')
        mouse_right_donw1 = '''#!/bin/bash
        xdotool click  {0}    '''.format(3)
        subprocess.call(['bash', '-c', mouse_right_donw1])

    def mouse_middle_donw(self):  # Средняя.
        pyautogui.click(button='middle')  # Нажимаем среднюю кнопку мыши
        mouse_wheel = '''#!/bin/bash
          xdotool click  {0}    '''.format(2)
        # subprocess.call(['bash', '-c', mouse_wheel])

    def key_press(self, key, number_key):
        # Mouse-to-key assignments always go through SmartTyper/UInput.
        if not smart_typer.key_down(key):
            dict_save.write_in_log('Mapped key-down was not emitted: ' + str(key))

    def key_release(self, key, number_key):
        # The matching physical-button release goes through the same class.
        if not smart_typer.key_up(key):
            dict_save.write_in_log('Mapped key-up was not emitted: ' + str(key))

    def key_press_release(self, key, number_key):  #
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

sticking_right_mouse = False

key_work = work_key()


def remove_profile_keys(d, profile):  # Создаем глубокую копию словаря
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

def execute_script(script):
    try:  # print(script)
        result = subprocess.call(['bash', '-c', script])
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении скрипта: {e}")

def get_path_current_active(games_checkmark_paths):  # Получаем идентификатор активного окна
    try:  # Получаем идентификатор процесса, связанного с активным окном
        active_window_id = subprocess.check_output(['xdotool', 'getactivewindow']).decode().strip()
        process_id = subprocess.check_output(['xdotool', 'getwindowpid', active_window_id]).decode().strip()
        process_list = [p.info for p in psutil.process_iter(attrs=['name', 'pid', 'exe'])]
        for process in process_list:
            if int(process_id) == int(process['pid']):  # нашли pid активного  окна
                if str(process['exe']) in games_checkmark_paths:
                    path_game = str(process['exe'])
                    return path_game  # путь к игре активного окна

        return games_checkmark_paths[0]
    except:
        pass

def check_star():
    process_list = [p.info for p in psutil.process_iter(attrs=['name'])]
    a = []
    try:
        for process in process_list:  # print(process['name'])
         if 'Mouse_setting_control_for_buttons_python_for_linux' in process['name']:
          a.append(process)
          if len(process_list) > 1:
           return False
          else:
           return True
    except psutil.NoSuchProcess:
        pass

def return_file_path(dict_save):
    res = dict_save.return_jnson()  # получаем настройки
    keys_values = res["key_value"][dict_save.get_cur_app()]  # конфигурация кнопок от предыдущего профиля.
    mouse_press_old = res["mouse_press"][dict_save.get_cur_app()]  # какие кнопки имеют залипания.
    # print(dict_save.get_current_app_path())
    cmd = ['zenity', '--file-selection', '--file-filter=EXE files | *.exe | *.EXE']  # Zenity команда для выбора одного exe файла
    # Вызов zenity и получение выбранного пути
    result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, text=True)
    path_to_file = result.stdout.strip()  # новый путь к игре

    name_with_expansion = os.path.basename(path_to_file)  # Получение базового имени файла с расширением из полного пути к файлу
    name = os.path.splitext(name_with_expansion)[0]  # Отделение имени файла без расширения путем разбиения строки.
    li = list(res["paths"].keys())
    if path_to_file in li:
        return None
    res["paths"][str(path_to_file)] = str(name)
    res["games_checkmark"][str(path_to_file)] = True
    res["key_value"][str(path_to_file)] = keys_values  # сохранить пред значения
    res["mouse_press"][str(path_to_file)] = list(mouse_press_old)
    res1 = res["key_value"]

    dict_save.save_jnson(res)
    if path_to_file in res1:
        return path_to_file
    else:
        res["key_value"][path_to_file] = ["LBUTTON", "RBUTTON", "WHEEL_MOUSE_BUTTON",
                                          "WHEEL_MOUSE_UP", "WHEEL_MOUSE_DOWN", 'XBUTTON1', 'XBUTTON2']
    return path_to_file

def set_list_box(dict_save, index=0):
    if index != 0:
        dict_save.set_count(index)  # Установить  индекс текущей игры.
    dict_save.set_box_values()  # Установить значения выпадающего списка.
    dict_save.set_values_box()

def reorder_keys_in_dict(res, idx1, idx2):  # ИЗМЕНЕНО: Новая/доработанная функция (self для метода, если нужно; или статичная)
    # ИЗМЕНЕНО: Проверки на валидность
    if 'paths' not in res or not isinstance(res['paths'], dict):
        return res
    orig_keys = list(res['paths'].keys())
    n = len(orig_keys)
    if not (0 <= idx1 < n and 0 <= idx2 < n and idx1 != idx2):
        return res

    # ИЗМЕНЕНО: Простой swap по idx1 и idx2 (без direction)
    new_order = orig_keys.copy()
    new_order[idx1], new_order[idx2] = new_order[idx2], new_order[idx1]

    def reorder_recursive(d):
        if not isinstance(d, dict):
            return d
        # Рекурсивно обработаем значения сначала
        processed = {k: reorder_recursive(v) for k, v in d.items()}
        # Если нет ключей из orig_keys — возвращаем как есть
        if not any(k in processed for k in orig_keys):
            return processed
        # Иначе: новый dict с ключами в new_order (только те, что есть)
        new_d = {}
        for k in new_order:
            if k in processed:
                new_d[k] = processed[k]
        # Добавляем оставшиеся ключи (не из paths, если есть)
        for k in processed:
            if k not in new_d:
                new_d[k] = processed[k]
        return new_d

    # ИЗМЕНЕНО: Собираем новый res (рекурсивно по всем top-level dicts)
    new_res = {}
    for top_k, top_v in res.items():
        if isinstance(top_v, dict):
            new_res[top_k] = reorder_recursive(top_v)
        else:
            new_res[top_k] = top_v
    return new_res

simple_key_map = { 'KEY_KP7': ' 7\nHome', 'KEY_KP8': '8\n↑', 'KEY_KP9': '9\nPgUp',
                  'KEY_KP4': '4\n←', 'KEY_KP5': '5\n', 'KEY_KP6': '6\n→',
                  'KEY_KP1': '1\nEnd', 'KEY_KP2': '2\n↓', 'KEY_KP3': '3\nPgDn'}

keypad_map = {"7\nHome": "KP_Home", "8\n↑": "KP_Up",
              "9\nPgUp": "KP_Prior", "4\n←": "KP_Left", "5\n": "KP_Begin", "6\n→": "KP_Right", "1\nEnd": "KP_End",
              "2\n↓": "KP_Down", "3\nPgDn": "KP_Next", "Ctrl": "ISO_Next_Group",
              "KEY_KPPLUS": "KP_Add", "KEY_KPMINUS": "KP_Subtract"}

mouse_map = {  "Левая": ("mousedown 1", "mouseup 1"), "Правая": ("mousedown 3", "mouseup 3"),  "wheel_up": ("mousedown 4", "mouseup 4"),
              "mouse_middie": ("mousedown 2", "mouseup 2"), "wheel_down": ("mousedown 5", "mouseup 5")}

def add_text_pytq5(key, text_widget):
    if key is None:
        return
    k = key.replace('\r', '').strip()
    if k in keypad_map:
        k = keypad_map[k]
    if k in mouse_map:
        down, up = mouse_map[k]
        sc = f'xte "{down}"\n' \
             f'sleep 0.02\n' \
             f'xte "{up}"\n'
    else:
        key_for_xte = k.replace('"', '\\"')
        if "?\n/" in key_for_xte:
         key_for_xte="slash"
        sc = f'xte "keydown {key_for_xte}"\n' \
             f'sleep 0.02\n' \
             f'xte "keyup {key_for_xte}"\n'

    if text_widget is not None:
        cursor = text_widget.textCursor()
        cursor.insertText(sc)
        text_widget.setTextCursor(cursor)
    return sc

class KeyboardWidget(QWidget):
 def __init__(self, callback_func=None, row_shifts=None):
   super().__init__()
   self.callback_func = callback_func
   self.row_shifts = row_shifts or {}
   self.create_keyboard_layout()
 
 def create_keyboard_layout(self):
   layout = QVBoxLayout(self)
   keyboard_widget = QWidget()
   keyboard_widget.setMinimumSize(860, 340)
 
   BUTTON_WIDTH = 60
   BUTTON_HEIGHT = 40
   BASE_X_STEP = 70
   BASE_Y_STEP = 50
   X_OFFSET = 6
   Y_OFFSET = 6
 
   keyboard_layout = [['Esc', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'Insert', 'Delete', 'Home',
                       'End', 'PgUp', 'PgDn'], ['~\n`', '!\n1', '@\n2', '#\n3', '$\n4', '%\n5', '^\n6', '&\n7', '*\n8', '(\n9', ')\n0',
                       '_\n-', '+\n=', 'Backspace', 'Num Lock', '/', '*', '-']
       , ['Tab', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '{\n[', '}\n]', '|\n\\', ' 7\nHome', '8\n↑', '9\nPgUp',
          '+'], ['Caps Lock', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ':\n;', '"\n\'', '\nEnter\n', '4\n←', '5\n', '6\n→']
       , ['Shift_L', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', '<\n,', '>\n.', '?\n/', 'Shift', '1\nEnd', '2\n↓', '3\nPgDn', 'KEnter']
       , ['Ctrl', 'Windows', 'Alt_L', 'space', 'Alt_r', 'Fn', 'Menu', 'Ctrl_r', 'up', '0\nIns', ' . ']
       , ['Left', 'Down', 'Right']]
   buttons = {}
 
   style_sheet = """  QPushButton {  background-color: lightgray;
                     border: 1px solid gray; padding: 2px;    }
                 QPushButton:hover { background-color: #CCCCFF;        }
                 QPushButton:pressed {  background-color: blue;
                     color: white;   }   """
   keyboard_widget.setStyleSheet(style_sheet)
   numpad_shifts = {'first': 69, 'second': 140, 'third': 210}
   first_column_keys = [' 7\nHome', '8\n↑', '9\nPgUp', '+']
   second_column_keys = ['4\n←', '5\n', '6\n→']
   third_column_keys = ['1\nEnd', '2\n↓', '3\nPgDn', 'KEnter']
 
   for i, row in enumerate(keyboard_layout):
       current_x = X_OFFSET
       current_y = BASE_Y_STEP * i + Y_OFFSET
       last_x_end = X_OFFSET
 
       for j, key in enumerate(row):
           x1 = BASE_X_STEP * j + X_OFFSET
           y1 = BASE_Y_STEP * i + Y_OFFSET
 
           w = BUTTON_WIDTH
           h = BUTTON_HEIGHT
 
           btn = QPushButton(key, keyboard_widget)

           if self.callback_func:
               k = key.strip()
               # Нумпад + / - выделяем как отдельные клавиши (KEY_KPPLUS / KEY_KPMINUS),
               # чтобы их можно было привязать независимо от основных + / - на клавиатуре.
               if i == 2 and key == '+':
                   k = 'KEY_KPPLUS'
               elif i == 1 and key == '-':
                   k = 'KEY_KPMINUS'
               btn.effective_key = k
               btn.clicked.connect(lambda checked, kk=k: self.callback_func(kk))
           buttons[btn] = key
           x_pos = x1 + self.row_shifts.get(i, 0)
           y_pos = y1
 
           if key == 'Backspace':
               w = 120
 
           elif i == 1 and j > 13:
               x_pos = x1 + 69
 
           if i >= 2:
               if key in first_column_keys:
                   x_pos += numpad_shifts['first']
                   if key == "+":
                       btn.setText(" + ")
                       h = BUTTON_HEIGHT * 2 + 5
                       btn.resize(w, h)
                       btn.move(x_pos, y_pos)
 
               if key in second_column_keys:
                   x_pos += numpad_shifts['second']
 
               if key in third_column_keys:
                   x_pos += numpad_shifts['third']
                   if key == "KEnter":
                       h = BUTTON_HEIGHT * 2 + 5
                       btn.setText(" Enter ")
                       btn.resize(w, h)
                       btn.move(x_pos, y_pos)
                       continue
 
           if key == '\nEnter\n':
               w = 140
               h = BUTTON_HEIGHT * 2 + 5
               btn.resize(w, h)
               btn.move(x_pos, y_pos)
               continue
 
           if i == 5:
               if key in ['Ctrl', 'Windows', 'Alt_L']:
                   pass
 
               elif key == "space":
                   w = 300
                   x_pos = x1
 
               elif key in ['Alt_r', 'Fn', 'Menu', 'Ctrl_r']:
                   x_pos = x1 + 210
                   w = BUTTON_WIDTH
 
               elif key == 'up':
                   x_pos = x1 + 280
                   w = BUTTON_WIDTH
 
               elif key == "0\nIns":
                   x_pos = x1 + 420
                   w = 120
 
               elif key == ' . ':
                   x_pos = x1 + 490
                   w = BUTTON_WIDTH
 
           if i == 6:
               if key in ['Left', 'Down', 'Right']:
                   x_pos = x1 + 770
                   y_pos = y1 - 9
                   w = BUTTON_WIDTH
           btn.resize(w, h)
           btn.move(x_pos, y_pos)
 
   layout.addWidget(keyboard_widget)

class MouseSettingAppMethods:
    def __init__(self):
        self.keyboard_editor = None
        self.current_keyboard_window = None
        self.tray_icon = None
        self.create_tray_icon()  # Создаем трей-иконку при запуске
        QTimer.singleShot(0, self.hide)  # Это гарантирует, что команда скрытия.

    def create_keyboard_with_editor(self, key):  # Создает клавиатуру с блокнотом для редактирования макросов для конкретной клавиши i
        print("keyboard ")
        # Скрываем основное окно клавиатуры
        if self.current_keyboard_window:
            self.current_keyboard_window.hide()
        # Закрываем предыдущее окно редактора, если оно открыто
        if self.keyboard_editor:
            self.keyboard_editor.close()
        # Создаем окно с блокнотом сверху и клавиатурой снизу
        macro_window = QMainWindow(self)
        macro_window.setWindowTitle(f"Запись макроса для клавиши {key}")
        macro_window.setGeometry(140, 480, 1410, 600)
        central_widget = QWidget()
        macro_window.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        # 1. Блокнот (QTextEdit) - сверху
        macro_window.text_widget = QTextEdit()
        layout.addWidget(QLabel("Редактор скрипта:"))
        layout.addWidget(macro_window.text_widget)
        # Загружаем существующий скрипт для этой клавиши, если он есть
        res = dict_save.return_jnson()
        current_app = res["current_app"]
        # print(current_app)
        dict_save.set_last_key_keyboard_script(key)
        content = res.get("keyboard_script", {}).get(current_app, {}).get("keys", {}).get(key, "")
        if content:
            # print(content)
            macro_window.text_widget.setPlainText(content)
        else:
            # Инициализируем структуры если их нет
            keys_dict = res.get("keyboard_script", {}).get(current_app, {}).get("keys", {})
            # Начальный скрипт
            macro_window.text_widget.setPlainText("#!/bin/bash\n")
        # Перемещаем курсор в конец текста
        cursor = macro_window.text_widget.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        macro_window.text_widget.setTextCursor(cursor)

        # 2. Клавиатура (KeyboardWidget) - снизу
        def add_key_command_local(key_local):  # """Функция для вставки команд xte при нажатии клавиш"""
            add_text_pytq5(key_local, macro_window.text_widget)

        macro_window.keyboard_widget = KeyboardWidget(add_key_command_local)
        layout.addWidget(macro_window.keyboard_widget)
        # Переопределяем обработчик закрытия окна для сохранения
        macro_window.closeEvent = lambda event: self.kill_notebook(event, macro_window, "keyboard_script")
        macro_window.show()
        self.keyboard_editor = macro_window

    def kill_notebook(self, event, window, section):
        res = dict_save.return_jnson()
        current_app = dict_save.get_cur_app()
        # читаем содержимое
        context = window.text_widget.toPlainText().strip()
        # определяем ключ

        # обработка клавиатурных скриптов
        if section == "keyboard_script":
            key = dict_save.get_last_key_keyboard_script()
            if context and context != "#!/bin/bash":
                res.setdefault("keyboard_script", {}).setdefault(current_app, {}).setdefault("keys", {})
                res["keyboard_script"][current_app]["keys"][key] = context
            else:
                if (current_app in res.get("keyboard_script", {}) and
                    key in res["keyboard_script"][current_app].get("keys", {})):
                    del res["keyboard_script"][current_app]["keys"][key]

        # обработка мышиных скриптов
        else:
            key = section
            if context and context != "#!/bin/bash":
                res.setdefault("script_mouse", {}).setdefault(current_app, {})
                res["script_mouse"][current_app][key] = context
            else:
                if (current_app in res.get("script_mouse", {}) and
                    key in res["script_mouse"][current_app]):
                    del res["script_mouse"][current_app][key]

        dict_save.save_jnson(res)  # сохранить json
        # показываем основную клавиатуру, если нужно
        if section == "keyboard_script" and self.current_keyboard_window:
            self.current_keyboard_window.show()
            self.update_keyboard_display(dict_save)

        if event:
            event.accept()
        else:
            window.close()

    def mouse_scrpt_keyboard_with_editor(self, i):  # Создает клавиатуру с блокнотом для редактирования макросов для кнопки мыши i
        # Скрываем основное окно клавиатуры
        if self.current_keyboard_window:
            self.current_keyboard_window.hide()
        # Закрываем предыдущее окно редактора, если оно открыто
        if self.keyboard_editor:
            self.keyboard_editor.close()  #   print(i)
        key = defaut_list_mouse_buttons[i]
        # Создаем окно с блокнотом сверху и клавиатурой снизу
        macro_window = QMainWindow(self)
        print(key)
        macro_window.setWindowTitle(f"Запись макроса для клавиши мыши {key}")
        macro_window.setGeometry(140, 480, 1410, 600)
        central_widget = QWidget()
        macro_window.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        # 1. Блокнот (QTextEdit) - сверху
        macro_window.text_widget = QTextEdit()
        layout.addWidget(QLabel("Редактор скрипта:"))
        layout.addWidget(macro_window.text_widget)
        # Загружаем существующий скрипт для этой клавиши, если он есть
        res = dict_save.return_jnson()
        current_app = res["current_app"]
        # print(current_app) # dict_save.set_last_key_keyboard_script(key)  # Используем тот же метод для простоты, но логика разделена в kill_notebook
        content = res.get("script_mouse", {}).get(current_app, {}).get(key, "")
        if content:
            # print(content)
            macro_window.text_widget.setPlainText(content)
        else:
            # Инициализируем структуры если их нет
            res.setdefault("script_mouse", {}).setdefault(current_app, {}).setdefault(key, {})
            # Начальный скрипт
            macro_window.text_widget.setPlainText("#!/bin/bash\n")
        # Перемещаем курсор в конец текста
        cursor = macro_window.text_widget.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        macro_window.text_widget.setTextCursor(cursor)

        # 2. Клавиатура (KeyboardWidget) - снизу
        def add_key_command_local(key_local):  # """Функция для вставки команд xte при нажатии клавиш"""
            add_text_pytq5(key_local, macro_window.text_widget)

        macro_window.keyboard_widget = KeyboardWidget(add_key_command_local)
        layout.addWidget(macro_window.keyboard_widget)
        # Переопределяем обработчик закрытия окна для сохранения
        macro_window.closeEvent = lambda event: self.kill_notebook(event, macro_window, key)
        macro_window.show()
        self.keyboard_editor = macro_window

    def create_virtual_keyboard(self, dict_save, callback_record_macro=None):  # Создает виртуальную клавиатуру без блокнота
        # Закрываем предыдущее окно клавиатуры, если оно открыто
        if self.current_keyboard_window:
            self.current_keyboard_window.close()
        keyboard_window = QMainWindow(self)
        self.current_keyboard_window = keyboard_window
        keyboard_window.dict_save = dict_save
        keyboard_window.setGeometry(240, 580, 1350, 340)
        keyboard_window.setWindowTitle("Выбор клавиш")
        keyboard_window.central = QWidget(keyboard_window)
        keyboard_window.setCentralWidget(keyboard_window.central)
        # Создаем layout для клавиатуры
        layout = QVBoxLayout(keyboard_window.central)
        # Получаем информацию о активных клавишах с макросами
        res = dict_save.return_jnson()
        current_app = dict_save.get_cur_app()
        content = res.get("keyboard_script", {}).get(current_app, {}).get("keys", {})
        keys_active = []
        if content:
            keys_active = list(res["keyboard_script"][current_app]["keys"].keys())
        else:  # Инициализируем структуры если их нет
            res.setdefault("keyboard_script", {}).setdefault(current_app, {"keys": {}})

        # Создаем клавиатуру с callback для записи макросов
        def record_macro_callback(key):  # Открываем редактор для этой клавиши
            self.create_keyboard_with_editor(key)

        keyboard_widget = KeyboardWidget(record_macro_callback)
        layout.addWidget(keyboard_widget)
        # Подсвечиваем кнопки, которые уже имеют макросы
        self.highlight_buttons_with_macros(keyboard_widget, keys_active)
        keyboard_window.show()
        return keyboard_window

    def highlight_buttons_with_macros(self, keyboard_widget, keys_with_macros):  # Подсвечивает кнопки, для которых уже созданы макросы"""
        # Сначала сбрасываем стиль для всех кнопок
        for button in keyboard_widget.findChildren(QPushButton):
            button.setStyleSheet("")  # Сброс на стиль по умолчанию
        # Теперь подсвечиваем нужные
        for key in keys_with_macros:
            # Ищем кнопку по тексту. Текст может содержать переносы строк, поэтому используем strip()
            key_norm = key.replace('\n', ' ').strip()
            buttons = keyboard_widget.findChildren(QPushButton)
            for button in buttons:
                # Совпадение либо по отображаемому тексту, либо по эффективному ключу
                # (нумпад +/- хранятся как KEY_KPPLUS / KEY_KPMINUS, а на кнопке написано +/-).
                eff = getattr(button, 'effective_key', None)
                if (button.text().replace('\n', ' ').strip() == key_norm) or (eff is not None and eff == key):
                    button.setStyleSheet("background-color: #0078d7; color: white;")
                    break

    def update_keyboard_display(self, dict_save):  # Обновляет отображение основной клавиатуры после сохранения изменений"""
        if not self.current_keyboard_window:
            self.create_virtual_keyboard(dict_save)
            return
        # Получаем актуальный список клавиш с макросами
        current_app = dict_save.get_cur_app()
        res = dict_save.return_jnson()
        keys_active = []
        if "keyboard_script" in res and current_app in res["keyboard_script"] and "keys" in res["keyboard_script"][current_app]:
            keys_active = list(res["keyboard_script"][current_app]["keys"].keys())
        # Находим виджет клавиатуры и обновляем подсветку
        keyboard_widget = self.current_keyboard_window.findChild(KeyboardWidget)
        if keyboard_widget:
            self.highlight_buttons_with_macros(keyboard_widget, keys_active)
        # Показываем окно, если оно было скрыто
        self.current_keyboard_window.show()

    def create_tray_icon(self):  # создания трей-иконки (немного модифицированный)
        icon = QIcon("/mnt/807EB5FA7EB5E954/soft/Virtual_machine/linux must have/python_linux/Project/mouse/tmpovhwj8so.png")
        if icon.isNull():
            icon = self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon)

        self.tray_icon = QSystemTrayIcon(icon, self)
        self.tray_icon.setToolTip("Mouse Setting Control")

        tray_menu = QMenu()
        quit_action = tray_menu.addAction("Выход")
        quit_action.triggered.connect(self.close)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_clicked)
        self.tray_icon.show()  # Отображаем иконку в системном трее

    def tray_icon_clicked(self, reason):  # Метод-обработчик кликов по иконке в трее
        if reason == QSystemTrayIcon.ActivationReason.Trigger:  # Проверяем, является ли событие обычным кликом
            if self.isVisible():  # Проверяем, видно ли главное окно
                self.hide()  # Если видно, скрываем его
            else:
                self.show_normal()  # Если скрыто, восстанавливаем и показываем его

    def show_normal(self):  # Метод для восстановления и фокусировки главного окна
        self.showNormal()
        self.activateWindow()

    def close_app(self):   # Закрываем приложение полностью
        self.close()

    def closeEvent(self, event=None):  # Переопределяем закрытие окна - скрываем в трей вместо закрытия   print("ds")
        dict_save.thread_exit=True
        old_data = dict_save.return_old_data()
        new_data = dict_save.return_jnson()
        diff = deepdiff.DeepDiff(old_data, new_data)
        if diff:
         reply = QMessageBox.question(self, "Выход", "Вы хотите сохранить изменения перед выходом?", QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
         if new_data["current_app"] =="":
          new_data["current_app"]="C:/Windows/explorer.exe"

         if reply == QMessageBox.StandardButton.Save:
            dict_save.write_to_file(new_data)
        try:
            os.kill(os.getpid(), signal.SIGKILL)  # Самоубийство через kill -9
        except:
            sys.exit(0)   # Завершаем само приложение только после того, как поток завершит работу,
        # В данном случае, так как вы хотите закрыть, используем accept() и sys.exit().

    def emunator_mouse(self, runtime):
        """Run one listener until its profile is changed, stopped, or the app exits."""
        def on_click(_x, _y, button, pressed):
            runtime.handle_listener_event(button, pressed)
            return True

        listener = mouse.Listener(on_click=on_click)
        listener.start()
        try:
            while not runtime.store.thread_exit and not runtime.stop_requested.is_set():
                active_game = check_current_active_window(runtime.store, runtime.enabled_profiles)
                if runtime.game != active_game:
                    remember_fallback_before_game(
                        runtime.store, runtime.game, active_game, runtime.enabled_profiles
                    )
                    runtime.store.set_cur_app(active_game)
                if runtime.store.get_current_path_game() != runtime.store.get_cur_app():
                    runtime.join_event_workers()
                    break
                time.sleep(0.03)
        finally:
            # Save this before cleanup: a profile switch should restart the
            # listener, whereas an explicit UI replacement must not restart it.
            was_stopped_externally = runtime.stop_requested.is_set()
            listener.stop()
            # Do not join here.  Active-window discovery can be slow; waiting
            # for the old listener made the new profile appear only much later.
            runtime.stop_workers()
            if getattr(self, '_active_runtime', None) is runtime:
                self._active_runtime = None
                runtime.store.set_thread(0)

        if not runtime.store.thread_exit and not was_stopped_externally:
            threading.Thread(target=self.start_startup_now, daemon=True).start()

    def _stop_active_runtime(self, store):
        """Request old runtime shutdown without waiting for window detection."""
        runtime = getattr(self, '_active_runtime', None)
        if runtime is not None:
            runtime.stop()
        # The old listener exits on its next loop iteration.  Do not join it:
        # a slow process/window scan must never delay the new profile map.
        if getattr(self, '_active_runtime', None) is runtime:
            self._active_runtime = None
        store.set_thread(0)

    def prepare(self, store=None):
        """Replace the old profile runtime, apply its map, and start its listener."""
        store = store or dict_save
        self._stop_active_runtime(store)
        runtime = MouseProfileRuntime(store)
        runtime.apply_button_map()
        runtime.store.set_cur_app(runtime.game)
        runtime.store.set_current_path_game(runtime.game)
        self._active_runtime = runtime

        listener_thread = threading.Thread(target=self.emunator_mouse, args=(runtime,))
        runtime.store.set_thread(listener_thread)
        listener_thread.start()

    def start_startup_now(self, store=None):
        store = store or dict_save
        settings = store.return_jnson()
        current_game = str(settings['current_app'])
        if not current_game:
            return
        if settings['id'] == 0:
            self._show_missing_device_message()
            return

        enabled_profiles = [path for path, enabled in settings['games_checkmark'].items() if enabled]
        if current_game in enabled_profiles:
            self.prepare(store)
        else:
            self._stop_active_runtime(store)
            QMessageBox.information(self, 'Ошибка', 'Нужно выбрать приложение')

    def _show_missing_device_message(self):
        message = QMessageBox(self)
        message.setWindowTitle('Ошибка')
        message.setText('Вы не выбрали устройство')
        show_button = message.addButton('Ок', QMessageBox.ButtonRole.AcceptRole)
        message.buttonClicked.connect(lambda button: show_list_id_callback() if button == show_button else None)
        message.exec()

    def check_label_changed(self, count):  # установить текущую активную игру
        res = dict_save.return_jnson()
        labels = dict_save.return_labels()
        # Сброс ВСЕХ label в белый (как в Tkinter-версии, см. set_colol_white_label_changed).
        # Раньше сбрасывался только label по current_app; если фоновый монитор активного
        # окна (emunator_mouse) уже сменил current_app без обновления UI, старый синий
        # label оставался и синих накапливалось несколько.
        for label in labels:
            label.setStyleSheet("background-color: white; border: 1px solid gray; padding: 5px;")
        game = list(res["key_value"].keys())[count]
        # Selecting a row updates the UI, but must not overwrite the saved
        # non-game fallback used after a game process exits.
        res["current_app"] = game
        labels[count].setStyleSheet("background-color: #06c; color: white; border: 1px solid gray; padding: 5px;")
        list_check_buttons = res.get("mouse_press", {}).get(game, [])
        # print("ch")
        res["current_app"] = game
        for idx, check in enumerate(self.mouse_check_buttons):
            if idx < len(list_check_buttons):
                check.setChecked(list_check_buttons[idx])
            else:
                check.setChecked(False)
        script = res.get("script_mouse", {}).get(game, {})
        for button in self.buttons_script:
            button.setStyleSheet("")
        if script:
            for key, value in script.items():
                if value and key in defaut_list_mouse_buttons:  # Проверяем, что значение не пустое
                    i = defaut_list_mouse_buttons.index(key)  #  print(i)   # print(value)
                    self.buttons_script[i].setStyleSheet(""" QPushButton { border: 1px solid gray; padding: 5px;
                                    color: black;  background-color: gray; } """)
                    self.buttons_script[i].update()
                # self.Keyboard_button
        script = res.get("keyboard_script", {}).get(game, {}).get("keys", {})
        self.Keyboard_button.setStyleSheet("")
        if script:
            self.Keyboard_button.setStyleSheet(""" QPushButton { border: 1px solid gray; padding: 5px;
                                    color: black;  background-color: gray; } """)
            self.Keyboard_button.update()

        values = res["key_value"][game]  # Получить значение выпадающего списка для этой игры
        for button, value in zip(self.combo_box, values):
            # Предположим, что вы хотите установить значение value в кнопку (комбо-бокс)
            button.setCurrentText(value)  # для PyQt/PySide
        dict_save.set_cur_app(game)
        dict_save.save_jnson(res)
        # The blue profile must also become the active emulation context.
        self.start_startup_now(dict_save)

    def filling_in_fields(self, dict_save):
        while self.games_layout.count():
            child = self.games_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        res = dict_save.return_jnson()
        labels = dict_save.return_labels()
        name_games = dict_save.return_name_games()
        var_list = dict_save.return_var_list()
        labels.clear()
        name_games.clear()
        var_list.clear()
        check_mark = res["games_checkmark"]
        paths = res["paths"]
        for count, (path, game_name) in enumerate(paths.items()):
            game_container = QWidget()
            game_layout = QHBoxLayout(game_container)
            game_layout.setContentsMargins(0, 0, 0, 0)
            var = QCheckBox()
            var.setChecked(check_mark[path])
            var_list.append(var)
            var.stateChanged.connect(lambda state, c=count: self.checkbutton_changed(c))
            label = QLabel(game_name)
            label.setFixedWidth(200)
            label.setStyleSheet("background-color: white; border: 1px solid gray; padding: 5px;")
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            label.mousePressEvent = lambda event, c=count: self.label_clicked(event, c)
            label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            label.customContextMenuRequested.connect(lambda pos, c=count: self.show_change_name_menu(c))
            name_games.append(game_name)
            labels.append(label)
            game_layout.addWidget(var)
            game_layout.addWidget(label)
            self.games_layout.addWidget(game_container)
        if res['current_app'] in paths:
            index = list(paths.keys()).index(res['current_app'])
            if index < len(labels):
                labels[index].setStyleSheet("background-color: #06c; color: white; border: 1px solid gray; padding: 5px;")

    def change_app(self, game=""):
        if game == dict_save.get_cur_app() or game == "":
            dict_save.set_cur_app("")
            while True:
                if "" == dict_save.get_cur_app():
                    break
            dict_save.set_cur_app(game)
            while game != dict_save.get_cur_app():
                time.sleep(1)

        res = dict_save.return_jnson()
        res['current_app'] = game
        dict_save.save_jnson(res)

    def checkbutton_changed(self, count):  # снять и убрать галочку.
        res = dict_save.return_jnson()
        keys_list = list(res["games_checkmark"].keys())
        curr_app = str(keys_list[count])
        var_list = dict_save.return_var_list()
        res["games_checkmark"][curr_app] = var_list[count].isChecked()
        dict_save.save_jnson(res)

    def update_labels_bindings(self):  # Обновление списка игр
        labels = dict_save.return_labels()
        var_list = dict_save.return_var_list()
        for count, label in enumerate(labels):    # ИЗМЕНЕНО: Более надёжная перепривязка (lambda с default c=count захватывается правильно)
            label.mousePressEvent = lambda event, c=count: self.label_clicked(event, c)
            if count < len(var_list):
                try:    # ИЗМЕНЕНО: disconnect с try-except для безопасности (если уже отключено)
                    var_list[count].stateChanged.disconnect()
                except TypeError:
                    pass  # Нет соединений — OK
                var_list[count].stateChanged.connect(lambda state, c=count: self.checkbutton_changed(c))

    def move_element(self, dict_save, direction):  # Двигать названия игр по списку
        try:
            res = dict_save.return_jnson()
            labels = dict_save.return_labels()
            curr_app_path = res["current_app"]

            # ИЗМЕНЕНО: Используем paths для consistency (как в filling_in_fields)
            keys_list = list(res["paths"].keys())
            index_curr = keys_list.index(curr_app_path)

            new_index = -1
            if direction == 'up' and index_curr > 0:
                new_index = index_curr - 1
            elif direction == 'down' and index_curr < len(labels) - 1:
                new_index = index_curr + 1
            else:
                return

            container_curr = labels[index_curr].parentWidget()
            container_new = labels[new_index].parentWidget()
            main_layout = container_curr.parentWidget().layout()

            main_layout.removeWidget(container_curr)
            main_layout.removeWidget(container_new)

            # Перемещаем в labels (визуальный порядок)
            labels.insert(new_index, labels.pop(index_curr))

            if direction == 'up':
                main_layout.insertWidget(new_index, container_curr)
                main_layout.insertWidget(index_curr, container_new)
            else:
                main_layout.insertWidget(index_curr, container_new)
                main_layout.insertWidget(new_index, container_curr)

            # ИЗМЕНЕНО: Стили по временным индексам (после move: curr теперь на new_index, former new на index_curr)
            labels[index_curr].setStyleSheet("background-color: white; color: black; border: 1px solid gray; padding: 5px;")
            labels[new_index].setStyleSheet("background-color: #06c; color: white; border: 1px solid gray; padding: 5px;")

            # ИЗМЕНЕНО: reorder JSON по старым индексам (swap idx1=index_curr, idx2=new_index)
            res = reorder_keys_in_dict(res, index_curr, new_index)

            self.update_labels_bindings()
            dict_save.save_labels(labels)
            dict_save.save_jnson(res)

            # ИЗМЕНЕНО: Опционально — sync layout с новым JSON (перестроит, но в правильном порядке)
            # Если не нужно (чтобы не мигать), закомментируйте
            self.filling_in_fields(dict_save)

            return 0
        except Exception as e:
            print(f"Ошибка при перемещении элемента: {e}")
            return -1

    def update_button(self, index):  # обновить, когда выбираем другое значение для кнопки мыши
        res = dict_save.return_jnson()
        game = res["current_app"]
        current_value = self.combo_box[index].currentText()
        res["key_value"][game][index] = current_value
        dict_save.save_jnson(res)  # Сохранить новое значение для выпадающего списка

    def update_profile(self):  # обновить профиль
        res = dict_save.return_jnson()
        current_value = int(self.id_combo.currentText())
        if res["id"] != current_value:
            res["id"] = current_value
            dict_save.save_jnson(res)  # Сохранить новое значение для выпадающего списка
            self.change_app()

    def change(self, window, new_name, old_name, res, count, labels):  # Окно изменение названия игры
        new_name_text = new_name.text()  # print(new_name_text, old_name, end=" , ")
        if new_name_text != "" and new_name_text != old_name:
            res["paths"][list(res["paths"])[count]] = new_name_text
            labels[count].setText(new_name_text)  # res["paths"][dict_save.get_cur_app()] = new_name.get()
            dict_save.save_jnson(res)
        window.close()  # Закрытие окна после сохранения изменений

        # Обновляем привязки событий
        self.update_labels_bindings()

    def change_name_label(self, count):  # Изменить название игры
        window = QDialog()  # основа
        window.setWindowTitle("change_name")  # заголовок
        window.resize(350, 150)  # Ширина и высота
        window.move(750, 400)  # x и y координаты на экране

        labels = dict_save.return_labels()
        res = dict_save.return_jnson()
        old_name = res["paths"][list(res["paths"])[count]]  # Получить прежнее название игры

        layout = QVBoxLayout()

        new_name = QLineEdit()
        new_name.setFixedWidth(250)  # Аналог width=25 в Tkinter (примерно)
        new_name.setText(old_name)
        new_name.setFocus()  # Фокусируемся на текстовом поле
        layout.addWidget(new_name)

        # Кнопка теперь является частью нового диалогового окна `window`
        ok_button = QPushButton("Ok")
        ok_button.clicked.connect(lambda: self.change(window, new_name, old_name, res, count, labels))
        layout.addWidget(ok_button)

        # Bind Enter key to change function
        new_name.returnPressed.connect(lambda: self.change(window, new_name, old_name, res, count, labels))

        window.setLayout(layout)
        window.exec()  # Показать модальное окно (аналог grid placement)

    def label_clicked(self, event, count):
        if event.button() == Qt.MouseButton.LeftButton:
            self.check_label_changed(count)
        if event.type() == QEvent.Type.MouseButtonDblClick:  #    print(11111)
            self.change_name_label(count)  # изменить название игры

    def check_mouse_press_button(self, count, state):
        res = dict_save.return_jnson()
        curr_name = dict_save.get_cur_app()

        if curr_name not in res.get("mouse_press", {}):
            res["mouse_press"][curr_name] = [False] * 7
        res["mouse_press"][curr_name][count] = (state == Qt.CheckState.Checked)
        dict_save.save_jnson(res)

    def add_file(self):  # Добавить новые игры
        path_to_file = return_file_path(dict_save)
        if path_to_file is None:
            return 0
        res = dict_save.return_jnson()  # получаем настройки

        while self.games_layout.count():    # Очистка layout (аналог destroy и clear)
            child = self.games_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        labels = dict_save.return_labels()
        name_games = dict_save.return_name_games()
        var_list = dict_save.return_var_list()
        labels_with_checkmark = dict_save.return_labels_with_checkmark()

        # Очистка списков
        labels.clear()
        name_games.clear()
        var_list.clear()
        labels_with_checkmark.clear()
        dict_save.count += 1  # Увеличиваем счётчик (исправлена опечатка)

        res['current_app'] = path_to_file  # Выбранная игра.
        dict_save.set_cur_app(path_to_file)
        dict_save.set_current_path_game(path_to_file)
        dict_save.save_jnson(res)

        # Установить белый цвет для всех label (аналог set_colol_white_label_changed)
        for label in labels:
            if isinstance(label, QLabel):
                label.setStyleSheet("background-color: white; border: 1px solid gray; padding: 5px;")

        self.filling_in_fields(dict_save)  # Перезаполнение полей (аналог filling_in_fields(res))

        # Копирование значений из box_values (QComboBox использует currentText())
        keys_values = dict_save.return_box_values()
        old_keys_values = []
        for i in range(len(keys_values)):
            old_keys_values.append(keys_values[i].currentText())

        # Выделяем последний label синим (аналог config(background="#06c"))
        labels = dict_save.return_labels()  # Обновляем список после filling_in_fields
        if labels and len(labels) > 0:
            labels[-1].setStyleSheet("background-color: #06c; color: white; border: 1px solid gray; padding: 5px;")

        # Обновление привязок (аналог update_buttons и bindings)
        self.update_labels_bindings()
        self.set_list_box(dict_save)  # Установка значений в combo_box, если нужно

    def delete(self):  # Удалить профиль.
        if dict_save.get_cur_app() == "C:/Windows/explorer.exe":  # Получить id устройства. Если id устройство не выбрали.
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Ошибка")
            msg_box.setText("Вы выбрали профиль по умолчанию")
            ok_button = msg_box.addButton("Ок", QMessageBox.ButtonRole.AcceptRole)
            msg_box.exec()
            return
        profile = dict_save.get_cur_app()  # Текущая директория активной игры.
        res = dict_save.return_jnson()  # print(profile)
        list_paths = list(res["paths"].keys())
        del_index = list_paths.index(profile)
        res = remove_profile_keys(res, profile)  # Удаляем из JSON
        dict_save.save_jnson(res)  # Сохранить новые настройки.

        # Перестраиваем UI (удаление и сдвиг через перезаполнение)
        self.filling_in_fields(dict_save)

        # Выделяем новый активный label (первый после удаления, аналог check_label_changed(0, ...))
        labels = dict_save.return_labels()
        if labels and len(labels) > 0:
            self.check_label_changed(0)  # Выделяем индекс 0 (первый)

        # Обновляем привязки событий
        self.update_labels_bindings()

    def button_keyboard(self, index):
        pass

    def create_scrypt_buttons(self):
        pass

    def show_change_name_menu(self, count):
        pass




      # if isinstance(data_dict, dict) and data_dict and id_active != 0:
      #     key_paths = get_active_window_exe(user, id_active)  # print(key_paths)
      #     if key_paths == None or ".exe" and ".sh" not in key_paths.lower():
      #         return dict_save.get_prev_game()  # то есть мы возвышаемся директорию из get_prev_game
      #     if ".sh" in key_paths.lower():
      #         key_paths1 = os.path.basename(key_paths.split()[-1])[:-3]  # Берём всё после последнего '/'
      #         file_path2 = next((p for p in games_checkmark_paths if key_paths1.lower() in p.lower()), None)  #
      #         if file_path2 and ".exe" in file_path2.lower():  # print(file_path2)
      #             return games_checkmark_paths[get_index_of_path(file_path2, games_checkmark_paths)]
    
    
    
    