import sys
import os
import json
import threading
import subprocess
import psutil
import signal
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QComboBox, QTextEdit, QTabWidget,
                             QScrollArea, QFrame, QCheckBox, QLineEdit, QMessageBox,
                             QStyleFactory, QToolTip, QGridLayout, QDialog)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette
from deepdiff import DeepDiff
from PIL import Image
import pystray
# Импортируем необходимые модули из Mouse_libs
from Mouse_libs import *

from evdev import InputDevice, categorize, ecodes, list_devices

# ВАЖНО: Убедитесь, что этот путь правильный для вашей системы.
os.environ[
 "QT_QPA_PLATFORM_PLUGIN_PATH"] = "/mnt/807EB5FA7EB5E954/софт/виртуальная машина/linux must have/python_linux/Project/myenv/lib/python3.12/site-packages/PyQt5/Qt5/plugins"

dict_save = save_dict()


def add_key_text(key, text_widget):
 add_text(key, text_widget)
 current_app = dict_save.get_cur_app()
 res = dict_save.return_jnson()
 curr_key = dict_save.get_last_key_keyboard_script()
 keyboard_script = res["keyboard_script"][current_app]["keys"]
 if text_widget.get("1.0", "end-1c"):
  keyboard_script[curr_key] = text_widget.get("1.0", "end-1c")
 dict_save.save_jnson(res)


def kill_notebook(w, n, text_widget):
 current_app = dict_save.get_cur_app()
 res = dict_save.return_jnson()
 curr_key = dict_save.get_last_key_keyboard_script()
 
 keyboard_script = res["keyboard_script"][current_app]["keys"]
 sc = text_widget.get("1.0", "end-1c")
 if sc == "":
  if curr_key in keyboard_script:
   del keyboard_script[curr_key]
 else:
  res["keyboard_script"][current_app]["keys"][curr_key] = sc
 w.destroy()
 n.destroy()
 dict_save.save_jnson(res)
 create_keyboard()


def kill_keyboard(w, n, text_widget):
 kill_notebook(w, n, text_widget)


def record_marcross(key, w):
 w.destroy()
 dict_save.set_last_key_keyboard_script(key)
 current_app = dict_save.get_cur_app()
 res = dict_save.return_jnson()
 
 res.setdefault("keyboard_script", {}).setdefault(current_app, {}).setdefault("keys", {})
 keys_active = list(res["keyboard_script"][current_app]["keys"].keys())
 
 window, buttons = create_virtial_keyboard(root)
 window.title(f"Запись макроса для клавиши {key}")
 window.geometry("1610x340+140+480")
 add_buttons_keyboard(buttons, window)
 note = Toplevel(window)
 note.title("Скрипт")
 
 notebook = ttk.Notebook(note)
 notebook.grid(row=0, column=0, sticky="nsew")
 
 tab1 = ttk.Frame(notebook)
 notebook.add(tab1, text="Окно редактора скрипта")
 keyboard_script = dict_save.return_jnson()["keyboard_script"]
 text_widget = Text(tab1, wrap='word')
 text_widget.grid(row=0, column=0, sticky="nsew")
 
 note.protocol("WM_DELETE_WINDOW", lambda: kill_notebook(window, note, text_widget))
 if key in keys_active:
  text_content = keyboard_script[current_app]["keys"][key]
  text_widget.insert('end', text_content)
 else:
  text_widget.insert("end", "#!/bin/bash\n")
 window.protocol("WM_DELETE_WINDOW", lambda: kill_keyboard(window, note, text_widget))
 for button, key in buttons.items():
  button.configure(command=lambda k=key, t=text_widget: add_key_text(k, t))


def create_keyboard():
 res = dict_save.return_jnson()
 current_app = dict_save.get_cur_app()
 if res.get("keyboard_script") is None:
  res["keyboard_script"] = {}
 if current_app not in res.get("keyboard_script", {}):
  res["keyboard_script"][current_app] = {}
 key = dict_save.get_last_key_keyboard_script()
 window, buttons = create_virtial_keyboard(root)
 window.title("Выбор клавиш")
 
 if "keys" in res["keyboard_script"][current_app]:
  keys_active = list(res["keyboard_script"][current_app]["keys"].keys())
 else:
  keys_active = []
 for button, key in buttons.items():
  button.configure(command=lambda k=key, w=window: record_marcross(k, w))
  if key != "" and key in keys_active and len(keys_active) > 0:
   style = ttk.Style()
   style.configure("Custom.TButton", background="blue", foreground="white")
   button.configure(style="Custom.TButton")
 
 dict_save.save_jnson(res)

def mouse_check_button(dict_save):
 curr_name = dict_save.get_cur_app()  #
 if curr_name == "":
  return 0
 res = dict_save.return_jnson()  # print(res["mouse_press"][curr_name])
 list_mouse_button_press = list(res["mouse_press"][curr_name])  # print(d)
 mouse_press_button = []  # список нажатых кнопок.
 cd1_y = 30
 for count, i in enumerate(list_mouse_button_press):
  mouse_press_button.append(BooleanVar())
  mouse_press_button[count].set(i)
  # cb1 = Checkbutton(root, variable=mouse_press_button[count],  # создания галочек
  #                   onvalue=1, offvalue=0, state=NORMAL, command=lambda c=count: update_mouse_check_button(c))  # Исправление здесь
  # cb1.place(x=490, y=cd1_y)
  # cd1_y = cd1_y + 30
  # CreateToolTip(cb1, text='Держать нажатой')  # вывод надписи
 dict_save.save_mouse_button_press(list_mouse_button_press, mouse_press_button)

def change_app(dict_save, game=""):  #
 # print("ch")
 # old = dict_save.get_prev_game()  # game = old
 if game == dict_save.get_cur_app() or game == "":
  dict_save.set_cur_app("")
  while True:
   if "" == dict_save.get_cur_app():
    break
 # else:
 dict_save.set_prev_game(game)  # Сохранить предыдущую игру
 dict_save.set_cur_app(game)
 while game != dict_save.get_cur_app():  # получить значение текущей активной строки.
  time.sleep(1)  # Добавьте задержку, чтобы избежать чрезмерного использования процессора
 
 res = dict_save.return_jnson()
 res['current_app'] = game  # Выбранная игра.
 mouse_check_button(dict_save)  # флаг для удержания кнопки мыши.
 create_scrypt_buttons(root)
 keys = list(res['paths'].keys())  # Получить все пути игр.
 index = keys.index(res['current_app'])  # Узнать индекс текущей игры.
 set_list_box(dict_save, index)  # Установить значения выпадающего списка.
 
 res = dict_save.return_jnson()
 res['current_app'] = game
 mouse_check_button(dict_save)
 create_scrypt_buttons(root)
 keys = list(res['paths'].keys())
 index = keys.index(res['current_app'])
 set_list_box(dict_save, index)


# --- Класс приложения ---

class MouseSettingApp(QMainWindow):
 def __init__(self):
  super().__init__()
  self.a_scrypt = []
  self.combo_box = []
  self.creat = 0
  self.devices = [InputDevice(path) for path in list_devices()]
  self.board = None
  for dev in self.devices:
   dev_str = str(dev)
   if '"Keyboard"' in dev_str and ' phys ' in dev_str:
    self.board = dev
    break
  if self.board is None:
   print("Клавиатура не найдена!")
  data = dict_save.data
  if os.path.exists(data):
   with open(data) as json_file:
    res = json.load(json_file)
    dict_save.save_old_data(res)
    dict_save.save_jnson(res)

  else:
   res = {
    'games_checkmark': {'C:/Windows/explorer.exe': True},
    'paths': {'C:/Windows/explorer.exe': 'По умолчанию'},
    'key_value': {'C:/Windows/explorer.exe': ['LBUTTON', 'RBUTTON', 'WHEEL_MOUSE_BUTTON', 'SCROLL_UP',
                                              'SCROLL_DOWN', 'SCROLL_UP', 'SCROLL_DOWN']},
    "mouse_press": {"C:/Windows/explorer.exe": [False, False, False, False, False, False, False]},
    "id": 0,
    "current_app": 'C:/Windows/explorer.exe'
   }
 
   try:
    know_id = '''#!/bin/bash
            input_list=$(xinput list)
            mouse_line=$(echo "$input_list" | head -n 1)
            if [ -n "$mouse_line" ]; then
                mouse_id=$(echo "$mouse_line" | grep -o "id=[0-9]*" | cut -d "=" -f 2)
                echo "$mouse_id"
            fi
            '''
    result = subprocess.run(['bash', '-c', know_id], capture_output=True, text=True)
  
    res["id"] = int(result.stdout.strip())
   except:
    res["id"] = 0
  dict_save.set_cur_app(res["current_app"])
  dict_save.set_prev_game(res["current_app"])
  dict_save.set_current_app_path(res['current_app'])
  dict_save.set_id(res["id"])
  self.setup_ui()
 
 def setup_ui(self):
  self.setWindowTitle("Mouse setting control for buttons python")
  self.setGeometry(440, 280, 940, 346)
  self.setFixedSize(940, 346)
  central_widget = QWidget()
  self.setCentralWidget(central_widget)
  
  main_layout = QVBoxLayout(central_widget)
  main_layout.setContentsMargins(10, 10, 10, 10)
  main_layout.setSpacing(10)
  
  top_layout = QHBoxLayout()
  top_layout.setSpacing(10)
  
  # Левая часть (scroll)
  left_widget = QWidget()
  left_widget.setFixedWidth(260)
  left_layout = QVBoxLayout(left_widget)
  left_layout.setContentsMargins(0, 0, 0, 0)
  
  self.scroll_area = QScrollArea()
  self.scroll_area.setWidgetResizable(True)
  self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
  self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
  self.scroll_area.setFixedHeight(280)
  
  self.scroll_widget = QWidget()
  self.games_layout = QVBoxLayout(self.scroll_widget)
  self.games_layout.setSpacing(5)
  self.games_layout.setContentsMargins(5, 5, 5, 5)
  
  self.scroll_area.setWidget(self.scroll_widget)
  left_layout.addWidget(self.scroll_area)
  top_layout.addWidget(left_widget, 1)
  
  # Правая часть
  right_widget = QWidget()
  right_layout = QVBoxLayout(right_widget)
  right_layout.setContentsMargins(10, 10, 10, 10)
  right_layout.setSpacing(10)
  
  # Верх: строки + кнопки + колонка управления
  rows_and_buttons_layout = QHBoxLayout()
  rows_and_buttons_layout.setSpacing(10)
  
  # Строки
  rows_layout = QVBoxLayout()
  rows_layout.setSpacing(5)
  
  self.mouse_button_labels = []
  self.mouse_button_combos = []
  self.mouse_check_buttons = []
  res = dict_save.return_jnson()
  game = res['current_app']
  box_button = list(res["key_value"][game])
  lab = []
  for i in range(7):
   row_layout = QHBoxLayout()
   row_layout.setSpacing(10)
   
   label = QLabel(LIST_MOUSE_BUTTONS[i])
   label.setStyleSheet("padding: 4px; font-weight: bold;")
   label.setFixedWidth(150)
   label.setAlignment(Qt.AlignCenter)
   lab.append(label)
   combo = QComboBox()
   combo.addItems(LIST_KEYS)  # Это кнопка выпадающего списка
   # Получаем значение из box_button для текущего индекса
   current_value = box_button[i]
   self.combo_box.append(combo)
   
   # Ищем индекс этого значения в LIST_KEYS
   if current_value in LIST_KEYS:
    i2 = LIST_KEYS.index(current_value)
    combo.setCurrentIndex(i2)
   else:
    # Если значение не найдено, можно установить дефолтное значение, например, 0
    combo.setCurrentIndex(0)
   combo.currentIndexChanged.connect(lambda idx=i: self.update_button(idx))
   checkbox = QCheckBox()
   checkbox.setToolTip("Держать нажатой")
   # checkbox.stateChanged.connect( lambda state, idx=i: self.update_mouse_check_button(idx))
   #
   self.mouse_button_labels.append(label)
   self.mouse_button_combos.append(combo)
   self.mouse_check_buttons.append(checkbox)
   
   row_layout.addWidget(label)
   row_layout.addWidget(combo, 1)
   row_layout.addWidget(checkbox)
   
   rows_layout.addLayout(row_layout)
  
  # Правая колонка с кнопками
  button_column_layout = QVBoxLayout()
  button_column_layout.setSpacing(5)
  dict_save.save_labels(lab)
  for idx, name in enumerate(LIST_MOUSE_BUTTONS):  # это кнопка для клавиатуры
   button = QPushButton(name)
   button.setFixedWidth(150)
   button.setStyleSheet("padding: 4px;")
   button_column_layout.addWidget(button)
   button.clicked.connect(lambda _, i=idx: self.button_keyboard(dict_save, i))
  # Нижний блок управления (будет справа как отдельная колонка)
  control_widget = QWidget()
  control_layout = QVBoxLayout(control_widget)
  control_layout.setContentsMargins(10, 10, 10, 10)
  control_layout.setSpacing(12)
  
  self.add_button_add = QPushButton("Добавить")
  self.add_button_add.clicked.connect(lambda: self.add_file(dict_save))
  control_layout.addWidget(self.add_button_add)
  
  self.add_button_start = QPushButton("Удалить")
  self.add_button_start.clicked.connect(lambda: self.delete(dict_save))
  control_layout.addWidget(self.add_button_start)
  
  self.move_element_up = QPushButton("Вверх")
  self.move_element_up.clicked.connect(lambda: self.move_element(dict_save, "up"))
  control_layout.addWidget(self.move_element_up)
  self.move_element_down = QPushButton("Вниз")
  self.move_element_down.clicked.connect(lambda: self.move_element(dict_save, "down"))
  control_layout.addWidget(self.move_element_down)
  
  self.Keyboard_button = QPushButton("Клавитура")
  self.Keyboard_button.clicked.connect(lambda: self.add_file(dict_save))
  control_layout.addWidget(self.Keyboard_button)
  
  self.show_devices_button = QPushButton("Показать список устройств")
  # if show_list_id_callback:
  #   self.show_devices_button.clicked.connect(show_list_id_callback)
  control_layout.addWidget(self.show_devices_button)
  
  if os.getgid() != 0:
   id_layout = QHBoxLayout()
   id_layout.setSpacing(10)
   
   id_label = QLabel("ID устройства:")
   id_label.setStyleSheet("padding: 2px;")
   
   self.id_combo = QComboBox()
   id_list = dict_save.get_list_ids() if dict_save else []
   self.id_combo.addItems([str(id) for id in id_list])
   # self.id_combo.currentIndexChanged.connect(self.update_button)
   self.id_combo.setToolTip('Выбор id устройства')
   
   id_layout.addWidget(id_label)
   id_layout.addWidget(self.id_combo)
   control_layout.addLayout(id_layout)
  
  # Добавляем все три колонки в один ряд
  rows_and_buttons_layout.addLayout(rows_layout, 3)
  rows_and_buttons_layout.addLayout(button_column_layout, 1)
  rows_and_buttons_layout.addWidget(control_widget, 1)
  
  # Добавляем общий блок
  right_layout.addLayout(rows_and_buttons_layout)
  top_layout.addWidget(right_widget, 2)
  
  # Весь top_layout → в main_layout
  main_layout.addLayout(top_layout)
  
  QTimer.singleShot(0, self.start_app)
  if os.getgid() != 0:
   pass  # QTimer.singleShot(0, self.setup_tray)
 
 def start_app(self):
  res = dict_save.return_jnson()
  id_value = res["id"]
  if os.getgid() != 0 and hasattr(self, 'id_combo'):
   self.id_combo.setCurrentText(str(res["id"]))
  box_values = []
  curr_name = dict_save.get_cur_app()
  res = dict_save.return_jnson()
  key_values = res["key_value"]
  for i in range(len(LIST_MOUSE_BUTTONS)):
   if hasattr(self, 'mouse_button_combos') and i < len(self.mouse_button_combos):
    if curr_name in key_values and i < len(key_values[curr_name]):
     self.mouse_button_combos[i].setCurrentText(key_values[curr_name][i])
  self.filling_in_fields(res)
  # self.update_mouse_check_buttons(res)
 
 def filling_in_fields(self, res):
  while self.games_layout.count():
   child = self.games_layout.takeAt(0)
   if child.widget():
    child.widget().deleteLater()
  labels = dict_save.return_labels()
  name_games = dict_save.return_name_games()
  var_list = dict_save.return_var_list()
  labels_with_checkmark = dict_save.return_labels_with_checkmark()
  labels.clear()
  name_games.clear()
  var_list.clear()
  labels_with_checkmark.clear()
  check_mark = res["games_checkmark"]
  paths = res["paths"]
  checkbutton_list = []
  for count, (path, game_name) in enumerate(paths.items()):
   game_container = QWidget()
   game_layout = QHBoxLayout(game_container)
   game_layout.setContentsMargins(0, 0, 0, 0)
   var = QCheckBox()
   var.setChecked(check_mark[path])
   var.stateChanged.connect(lambda state, c=count, p=path: self.checkbutton_changed(c, p))
   checkbutton_list.append(var)
   label = QLabel(game_name)
   label.setFixedWidth(200)
   label.setStyleSheet("background-color: white; border: 1px solid gray; padding: 5px;")
   label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
   label.mousePressEvent = lambda event, c=count: self.label_clicked(event, c)
   label.setContextMenuPolicy(Qt.CustomContextMenu)
   label.customContextMenuRequested.connect(lambda pos, c=count: self.show_change_name_menu(c))
   name_games.append(game_name)
   labels.append(label)
   labels_with_checkmark[label] = var
   game_layout.addWidget(var)
   game_layout.addWidget(label)
   self.games_layout.addWidget(game_container)
  dict_save.save_var_list(checkbutton_list)
  if res['current_app'] in paths:
   index = list(paths.keys()).index(res['current_app'])
   if index < len(labels):
    labels[index].setStyleSheet("background-color: #06c; color: white; border: 1px solid gray; padding: 5px;")

 def filling_in_fields(self, res):
  while self.games_layout.count():
   child = self.games_layout.takeAt(0)
   if child.widget():
    child.widget().deleteLater()
  labels = dict_save.return_labels()
  name_games = dict_save.return_name_games()
  var_list = dict_save.return_var_list()
  labels_with_checkmark = dict_save.return_labels_with_checkmark()
  labels.clear()
  name_games.clear()
  var_list.clear()
  labels_with_checkmark.clear()
  check_mark = res["games_checkmark"]
  paths = res["paths"]
  checkbutton_list = []
  for count, (path, game_name) in enumerate(paths.items()):
   game_container = QWidget()
   game_layout = QHBoxLayout(game_container)
   game_layout.setContentsMargins(0, 0, 0, 0)
   var = QCheckBox()
   var.setChecked(check_mark[path])
   var.stateChanged.connect(lambda state, c=count, p=path: self.checkbutton_changed(c, p))
   checkbutton_list.append(var)
   label = QLabel(game_name)
   label.setFixedWidth(200)
   label.setStyleSheet("background-color: white; border: 1px solid gray; padding: 5px;")
   label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
   label.mousePressEvent = lambda event, c=count: self.label_clicked(event, c)
   label.setContextMenuPolicy(Qt.CustomContextMenu)
   label.customContextMenuRequested.connect(lambda pos, c=count: self.show_change_name_menu(c))
   name_games.append(game_name)
   labels.append(label)
   labels_with_checkmark[label] = var
   game_layout.addWidget(var)
   game_layout.addWidget(label)
   self.games_layout.addWidget(game_container)
  dict_save.save_var_list(checkbutton_list)
  if res['current_app'] in paths:
   index = list(paths.keys()).index(res['current_app'])
   if index < len(labels):
    labels[index].setStyleSheet("background-color: #06c; color: white; border: 1px solid gray; padding: 5px;")

 def checkbutton_changed(self, count, curr_app):  # поставить и убрать галочку.
  dict_save.set_cur_app(curr_app)
  dict_save.set_count(count)
  res = dict_save.return_jnson()
  labels = dict_save.return_labels()
  var_list = dict_save.return_var_list()
  if not var_list[count].isChecked():
   labels[count].setStyleSheet("background-color: #06c; color: white; border: 1px solid gray; padding: 5px;")
   res["games_checkmark"][str(dict_save.get_cur_app())] = True
  else:
   labels[count].setStyleSheet("background-color: white; border: 1px solid gray; padding: 5px;")
   res["games_checkmark"][str(dict_save.get_cur_app())] = False
  for i in range(len(labels)):
   if i != count:
    labels[i].setStyleSheet("background-color: white; border: 1px solid gray; padding: 5px;")
  dict_save.save_jnson(res)

 def move_element(self, dict_save, direction):  # Перемещает текущий элемент (определяемый dict_save.get_cur_app())
  res = dict_save.return_jnson()  # Получаем текущий профиль и конфигурацию
  labels = dict_save.return_labels()
  keys_list = list(res["key_value"].keys())
  curr = res["current_app"]
  index_curr = keys_list.index(curr)
  new_index = 0  # Инициализация
 
  # Проверяем границы для перемещения
  if direction == 'up':
   if index_curr == 0:
    return  # Нельзя двигать вверх первый элемент
   new_index = index_curr - 1
  elif direction == 'down':
   if index_curr == len(labels) - 1:
    return  # Нельзя двигать вниз последний элемент
   new_index = index_curr + 1
  else:
   raise ValueError("direction должен быть 'up' или 'down'")
 
  print(f"Текущий индекс: {index_curr}")
 
  # Получаем layout, в котором находятся виджеты
  container_index = labels[index_curr].parentWidget()
  layout = container_index.parentWidget().layout()
 
  # Получаем контейнеры для перемещения
  container_index = labels[index_curr].parentWidget()
  container_new_index = labels[new_index].parentWidget()
 
  # Удаляем виджеты из layout-а
  layout.removeWidget(container_index)
  layout.removeWidget(container_new_index)
 
  # Меняем порядок в списке виджетов-меток
  labels.insert(new_index, labels.pop(index_curr))
 
  # Вставляем виджеты обратно в layout в новом порядке
  if direction == 'up':
   layout.insertWidget(new_index, container_index)
   layout.insertWidget(index_curr, container_new_index)
  else:  # direction == 'down'
   layout.insertWidget(index_curr, container_new_index)
   layout.insertWidget(new_index, container_index)
 
  # Обновляем стили, чтобы визуально выделить перемещенный элемент на новой позиции
  res = reorder_keys_in_dict(res, index_curr, direction)
  print(new_index)
  print(list(res["paths"])[new_index])
  labels[index_curr].setStyleSheet("background-color: white; border: 1px solid gray; padding: 5px;")
  labels[new_index].setStyleSheet("background-color: #06c; color: white; border: 1px solid gray; padding: 5px;")
 
  # Обновляем текущий профиль в соответствии с новым порядком
  # Сохраняем изменения
  dict_save.save_labels(labels)
  dict_save.save_jnson(res)

 def check_label_changed(self, labels, count, var_list):  # Поменять цвет активной строки.
  print("ch")
  res = dict_save.return_jnson()
  keys_list = list(res["key_value"].keys())
  curr = res["current_app"]
  index_curr = keys_list.index(curr)  # Текущий индекс активности
  labels[index_curr].setStyleSheet("background-color: white; border: 1px solid gray; padding: 5px;")
  game = list(res["key_value"].keys())[count]  # получить название новой игры по индексу
  labels[count].setStyleSheet("background-color: #06c; color: white; border: 1px solid gray; padding: 5px;")
  res["current_app"] = game  # Установить текущую игру
  dict_save.set_cur_app(game)
  dict_save.set_prev_game(curr)
  keys_list = list(res["key_value"].keys())
  dict_save.save_jnson(res)
  self.update_button(curr)
  # Проверяем, что count находится в допустимых пределах
  if count >= len(labels):
   # print(f"Ошибка: индекс {count} выходит за пределы списка labels длиной {len(labels)}")
   return
 
  # if res.get("keyboard_script", {}).get(game, {}).get("keys"):
  #   self.add_button_create_keyboard.setStyleSheet("background-color: #c0c0c0;")
  # else:
  #   self.add_button_create_keyboard.setStyleSheet("")
  # change_app(dict_save, game)

 def update_button(self, index):  # Изменить каждое значение выпадающего списка.
  res = dict_save.return_jnson()
  game = res["current_app"]
  box_button = list(res["key_value"][game])
 
  for i in range(7):  # Получаем значение из box_button для текущего индекса
   current_value = box_button[i]
   i2 = LIST_KEYS.index(current_value)
   self.combo_box[i].setCurrentIndex(i2)

 def label_clicked(self, event, count):
  if event.button() == Qt.LeftButton:
   labels = dict_save.return_labels()
   var_list = dict_save.return_var_list()
   self.check_label_changed(labels, count, var_list)

 def update_mouse_check_button(self, count):  # Изменение кнопок выпадающего списка
  print(count)
  res = dict_save.return_jnson()
  curr_name = dict_save.get_cur_app()
  if curr_name in res["mouse_press"]:
   res["mouse_press"][curr_name][count] = not res["mouse_press"][curr_name][count]
   dict_save.set_default_id_value()
   dict_save.save_jnson(res)

 def update_mouse_check_buttons(self, res):
  curr_name = dict_save.get_cur_app()
  if curr_name in res["mouse_press"]:
   for i, checkbox in enumerate(self.mouse_check_buttons):
    if i < len(res["mouse_press"][curr_name]):
     checkbox.setChecked(res["mouse_press"][curr_name][i])


if __name__ == "__main__":
 app = QApplication(sys.argv)
 # Создание экземпляра класса должно быть здесь
 window = MouseSettingApp()
 window.show()
 sys.exit(app.exec_())