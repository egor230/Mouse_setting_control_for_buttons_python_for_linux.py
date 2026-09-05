# -*- coding: utf-8 -*-
# ТРЕТИЙ СКРИПТ: модуль ДАННЫХ и чистых функций.
# Здесь собраны все списки, словари и простые функции, с которыми работают
# интерфейс (Pytq6_mouse_setting_control_for_buttons_for_linux.py) и логика
# (Pyqt6_libs_mouse.py). Импортируется обоими:  from Pyqt6_libs_data import *
# Правило отступа: 1 пробел за уровень. Комментарии только через #.
# ==== ДАННЫЕ: списки и словари ====

import copy, re

# Словари транслитерации (en<->ru) для поиска макроса по введённой клавише.
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

# Коды/имена клавиш и кнопок мыши.
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

# Карта нумпада и списки кнопок/клавиш.
simple_key_map = { 'KEY_KP7': ' 7\nHome', 'KEY_KP8': '8\n↑', 'KEY_KP9': '9\nPgUp',
 'KEY_KP4': '4\n←', 'KEY_KP5': '5\n', 'KEY_KP6': '6\n→', 'KEY_KP1': '1\nEnd', 'KEY_KP2': '2\n↓', 'KEY_KP3': '3\nPgDn'}
LIST_MOUSE_BUTTONS = ["Левая кнопка", "Правая кнопка", "Средняя", "Колесико вверх", "Колесико вниз", "1 боковая", "2 боковая"]
LIST_KEYS = list(KEYS.keys())
defaut_list_mouse_buttons = ['LBUTTON', 'RBUTTON', 'WHEEL_MOUSE_BUTTON', 'SCROLL_UP', 'SCROLL_DOWN', 'XBUTTON1', 'XBUTTON2']

# Карты для редактора Xte-скриптов (keypad / mouse).
keypad_map = {"7\nHome": "KP_Home", "8\n↑": "KP_Up",
 "9\nPgUp": "KP_Prior", "4\n←": "KP_Left", "5\n": "KP_Begin", "6\n→": "KP_Right", "1\nEnd": "KP_End",
 "2\n↓": "KP_Down", "3\nPgDn": "KP_Next", "Ctrl": "ISO_Next_Group",
 "KEY_KPPLUS": "KP_Add", "KEY_KPMINUS": "KP_Subtract"}
mouse_map = {  "Левая": ("mousedown 1", "mouseup 1"), "Правая": ("mousedown 3", "mouseup 3"),  "wheel_up": ("mousedown 4", "mouseup 4"),
 "mouse_middie": ("mousedown 2", "mouseup 2"), "wheel_down": ("mousedown 5", "mouseup 5")}

# ==== ЧИСТЫЕ ФУНКЦИИ ====

# Простые проверки путей из настроек.
def is_path_in_list(path, path_list):  # проверяет, содержится ли путь в списке путей.
 return any(path in item for item in path_list)
def get_index_of_path(path, path_list):
 index = next(index for index, item in enumerate(path_list) if path in item)
 return index  # находит индекс пути в списке путей и возвращает соответствующий элемент списка.

# Очистка и нормализация настроек (JSON читается через json.load(strict=False)).
def cleanup_empty_script_entries(data):
 """Удалить пустые записи и конфликтующие скрипты из настроек."""
 # ЗАМЕТКА (исправление): раньше здесь безусловно удалялись скрипты боковых
 # кнопок XBUTTON1/XBUTTON2, если в key_value[профиль][5]/[6] было непустое
 # значение. Но слоты 5 и 6 по умолчанию заполнены SCROLL_UP/SCROLL_DOWN, то
 # есть «непустые» почти всегда — из-за этого сохранённый через редактор
 # скрипт боковой кнопки стирался сразу же при сохранении и никогда не
 # работал. Очистка конфликта ключ/скрипт выполняется точечно в update_button
 # (когда пользователь выбирает клавишу для боковой кнопки), поэтому здесь
 # блок не нужен и удалён.

 for section in ("script_mouse", "keyboard_script"):
  container = data.get(section)
  if not isinstance(container, dict):
   continue
  for profile in list(container):
   profile_data = container.get(profile)
   if not isinstance(profile_data, dict):
    container.pop(profile, None)
    continue
   if section == "script_mouse":
    for button in list(profile_data):
     value = profile_data.get(button)
     if not isinstance(value, str) or not value.strip() or value.strip() == "#!/bin/bash":
      profile_data.pop(button, None)
   else:
    keys = profile_data.get("keys")
    if isinstance(keys, dict):
     for key in list(keys):
      value = keys.get(key)
      if not isinstance(value, str) or not value.strip() or value.strip() == "#!/bin/bash":
       keys.pop(key, None)
     if not keys:
      profile_data.pop("keys", None)
    if not profile_data:
     container.pop(profile, None)
   if section == "script_mouse" and not profile_data:
    container.pop(profile, None)
  if not container:
   data.pop(section, None)
 return data
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

# Служебные функции для работы со словарём настроек.
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

# evdev-имя клавиши -> нормализованная метка макроса (защищены нумпад +/-).
def evdev_key_to_label(code):
# Преобразует evdev-имя клавиши (напр. 'KEY_EQUAL') в нормализованную метку,
# под которой макросы лежат в keyboard_script.
# Нумпад +/- НАМЕРЕННО оставляем с префиксом 'KEY_', чтобы они НЕ совпадали
# с основными +/- (требование пользователя: различать нумпад и основную клавиатуру).
 if not isinstance(code, str) or not code.startswith("KEY_"):
  return None
 name = code[4:]
 # Нумпад: цифры/навигация -> метки как в simple_key_map (совместимо со старым поведением),
 # но +/- выделяем отдельно.
 if name.startswith("KP"):
  if name in ("KPPLUS", "KPMINUS"):
   return code  # 'KEY_KPPLUS' / 'KEY_KPMINUS' — не совпадают с '+' / '-'
  return simple_key_map.get(code, name)  # напр. 'KEY_KP7' -> ' 7\nHome'
 special = {
  "SPACE": "space", "ENTER": "enter", "KPENTER": "enter", "TAB": "tab",
  "ESC": "esc", "GRAVE": "`", "MINUS": "-", "EQUAL": "+",
  "LEFTBRACE": "[", "RIGHTBRACE": "]", "BACKSLASH": "\\",
  "SEMICOLON": ";", "APOSTROPHE": "'", "COMMA": ",", "DOT": ".",
  "SLASH": "/", "KPASTERISK": "*", "BACKSPACE": "backspace",
  "DELETE": "delete", "HOME": "home", "END": "end",
  "PAGEUP": "page_up", "PAGEDOWN": "page_down", "INSERT": "insert",
  "LEFT": "left", "RIGHT": "right", "UP": "up", "DOWN": "down",
  "LEFTSHIFT": "shift_l", "RIGHTSHIFT": "shift_r",
  "LEFTCTRL": "control_l", "RIGHTCTRL": "control_r",
  "LEFTALT": "alt_l", "RIGHTALT": "alt_r",
  "LEFTMETA": "meta_l", "RIGHTMETA": "meta_r",
  "CAPSLOCK": "caps_lock", "NUMLOCK": "num_lock",
  "SCROLLLOCK": "scroll_lock", "PRINT": "print", "PAUSE": "pause",
  }
 if name in special:
  return special[name]
 if len(name) == 1 and name.isalpha():
  return name.lower()
 if len(name) == 1 and name.isdigit():
  return name
 if name.startswith("F") and name[1:].isdigit():
  return name.lower()
 return name.lower()
