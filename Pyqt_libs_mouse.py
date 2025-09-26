import sys, os, json, threading, subprocess, psutil, signal, time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QComboBox, QTextEdit, QTabWidget,
                             QScrollArea, QFrame, QCheckBox, QLineEdit, QMessageBox,
                             QStyleFactory, QToolTip, QGridLayout, QDialog, QPlainTextEdit,
                             QTextEdit)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette, QTextCursor
from deepdiff import DeepDiff
from PIL import Image
import pystray
from Mouse_libs import *
from evdev import InputDevice, categorize, ecodes, list_devices

dict_save = save_dict()
def add_text_pytq5(key, text_widget):
 if key is None:
  return
 k = key.replace('\r', '').strip()
 
 keypad_map = {
  "7\nHome": "KP_Home", "8\n↑": "KP_Up",
  "9\nPgUp": "KP_Prior", "4\n←": "KP_Left", "5\n": "KP_Begin", "6\n→": "KP_Right", "1\nEnd": "KP_End",
  "2\n↓": "KP_Down", "3\nPgDn": "KP_Next", "Ctrl": "ISO_Next_Group",
 }
 if k in keypad_map:
  k = keypad_map[k]
 
 mouse_map = {
  "Левая": ("mousedown 1", "mouseup 1"),
  "Правая": ("mousedown 3", "mouseup 3"),
  "wheel_up": ("mousedown 4", "mouseup 4"),
  "mouse_middie": ("mousedown 2", "mouseup 2"),
  "wheel_down": ("mousedown 5", "mouseup 5"),
 }
 
 if k in mouse_map:
  down, up = mouse_map[k]
  sc = f'xte "{down}"\n' \
       f'sleep 0.23\n' \
       f'xte "{up}"\n'
 else:
  key_for_xte = k.replace('"', '\\"')
  sc = f'xte "keydown {key_for_xte}"\n' \
       f'sleep 0.23\n' \
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
  keyboard_widget.setMinimumSize(850, 340)
  
  # В PyQt мы используем абсолютное позиционирование, чтобы имитировать tk.place
  # Задаем базовые размеры и отступы (Tkinter width=5, height=1 - соответствует ~60x40 в PyQt)
  BUTTON_WIDTH = 60
  BUTTON_HEIGHT = 40
  BASE_X_STEP = 70  # 70 * j
  BASE_Y_STEP = 50  # 50 * i
  X_OFFSET = 6  # + 6
  Y_OFFSET = 6  # + 6
  
  keyboard_layout = [
   ['Esc', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'Insert', 'Delete', 'Home',
    'End', 'PgUp', 'PgDn']
   , ['~\n`', '!\n1', '@\n2', '#\n3', '$\n4', '%\n5', '^\n6', '&\n7', '*\n8', '(\n9', ')\n0', '_\n-', '+\n=',
      'Backspace', 'Num Lock', '/', '*', '-']
   , ['Tab', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '{\n[', '}\n]', '|\n\\', ' 7\nHome', '8\n↑', '9\nPgUp',
      '+']
   , ['Caps Lock', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ':\n;', '"\n\'', '\nEnter\n', '4\n←', '5\n', '6\n→']
   , ['Shift_L', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', '<\n,', '>\n.', '?\n/', 'Shift', '1\nEnd', '2\n↓', '3\nPgDn', 'KEnter']
   , ['Ctrl', 'Windows', 'Alt_L', 'space', 'Alt_r', 'Fn', 'Menu', 'Ctrl_r', 'up', '0\nIns', ' . ']
   , ['Left', 'Down', 'Right']
  ]
  
  buttons = {}
  
  # Имитация стиля Tkinter (акцент на синий при нажатии/активности)
  # В PyQt это делается через QPalette или QSS (QStyleSheet)
  style_sheet = """
            QPushButton {
                background-color: lightgray;
                border: 1px solid gray;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: #CCCCFF; /* Более светлый синий */
            }
            QPushButton:pressed {
                background-color: blue;
                color: white;
            }
        """
  keyboard_widget.setStyleSheet(style_sheet)
  
  # Сдвиги для колонок NumPad (оригинальные значения)
  numpad_shifts = {   'first': 69,  # Для 7,8,9,+
   'second': 140,  # Для 4,5,6
   'third': 210  # Для 1,2,3,KEnter
  }
  
  first_column_keys = [' 7\nHome', '8\n↑', '9\nPgUp', '+']
  second_column_keys = ['4\n←', '5\n', '6\n→']
  third_column_keys = ['1\nEnd', '2\n↓', '3\nPgDn', 'KEnter']
  
  for i, row in enumerate(keyboard_layout):  # Создаем клавиатуру.
   current_x = X_OFFSET
   current_y = BASE_Y_STEP * i + Y_OFFSET
   
   # Переменная для отслеживания текущей X-позиции с учетом сдвигов
   last_x_end = X_OFFSET
   
   for j, key in enumerate(row):
    x1 = BASE_X_STEP * j + X_OFFSET
    y1 = BASE_Y_STEP * i + Y_OFFSET
    
    # Устанавливаем базовые размеры для кнопки
    w = BUTTON_WIDTH
    h = BUTTON_HEIGHT
    
    # Создаем кнопку
    btn = QPushButton(key, keyboard_widget)
    
    # Привязка функции (если предоставлена)
    if self.callback_func:
     btn.clicked.connect(lambda checked, k=key.strip(): self.callback_func(k))
    buttons[btn] = key
    x_pos = x1 + self.row_shifts.get(i, 0)  # Добавляем сдвиг для всего ряда
    y_pos = y1
    
    # 1. Backspace
    if key == 'Backspace':
     w = 120
    
    # 2. Смещение кнопок NumPad после Backspace (i=1, j>13)
    elif i == 1 and j > 13:
     x_pos = x1 + 69  # Сдвиг вправо на 69
    
    # 3. Сдвиги в рядах NumPad (убираем условие j>=14, проверяем по ключам)
    # NumPad начинается с i=2, j=14
    if i >= 2:
     # 3a. Первая колонка NumPad ( 7, 8, 9, +)
     if key in first_column_keys:
      x_pos += numpad_shifts['first']  # Сдвиг на 69
      if key == "+":
       btn.setText(" + ")
     
     # 3b. Вторая колонка NumPad (4, 5, 6)
     if key in second_column_keys:
      x_pos += numpad_shifts['second']  # Сдвиг на 140
     
     # 3c. Третья колонка NumPad (1, 2, 3, KEnter)
     if key in third_column_keys:
      x_pos += numpad_shifts['third']  # Сдвиг на 210
      if key == "KEnter":
       h = BUTTON_HEIGHT * 2 + 5  # Увеличиваем высоту на 2 ряда
       btn.setText(" Enter ")
       btn.resize(w, h)
       btn.move(x_pos, y_pos)
       continue  # Пропускаем стандартный .move() в конце цикла
    
    # 4. Enter
    if key == '\nEnter\n':
     w = 140  # Расчетная ширина для Enter
     h = BUTTON_HEIGHT * 2 + 5  # Увеличиваем высоту на 2 ряда
     btn.resize(w, h)
     btn.move(x_pos, y_pos)
     continue  # Пропускаем стандартный .move() в конце цикла
    
    # 5. Нижний ряд (i=5)
    if i == 5:
     # Простые кнопки в начале ряда
     if key in ['Ctrl', 'Windows', 'Alt_L']:
      pass
     
     elif key == "space":
      w = 300
      x_pos = x1
     
     # Группа Alt_r, Fn, Menu, Ctrl_r (сдвиг и ширина)
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
    
    # 6. Последний ряд (стрелки Left, Down, Right) (i=6)
    if i == 6:
     if key in ['Left', 'Down', 'Right']:
      x_pos = x1 + 770
      y_pos = y1 - 9  # Сдвиг вверх на 9 пикселей
      w = BUTTON_WIDTH
    # Устанавливаем размер и позицию для текущей кнопки
    btn.resize(w, h)
    btn.move(x_pos, y_pos)
  
  layout.addWidget(keyboard_widget)