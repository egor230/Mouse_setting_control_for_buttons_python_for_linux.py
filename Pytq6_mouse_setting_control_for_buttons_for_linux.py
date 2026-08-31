from Pyqt6_libs_data import *
from Pyqt6_libs_mouse import *

class MouseSettingApp(QMainWindow, MouseSettingAppMethods):
 def __init__(self):
  super().__init__()
  self.keyboard_editor = None
  self.a_scrypt = []
  self.combo_box = []
  self.creat = 0
  self.mouse_button_labels = []
  self.mouse_button_combos = []
  self.mouse_check_buttons = []
  self.buttons_script = []
  self.board = None
  data = dict_save.data
  if os.path.exists(data):
   with open(data) as json_file:
   # strict=False: разрешаем реальные переносы строк внутри bash-скриптов (script_mouse / keyboard_script)
    res = json.load(json_file, strict=False)
    res = scripts_to_text(res)  # убрать отступы продолжения строк из скриптов (нормализация)
    dict_save.save_old_data(res)
   dict_save.save_jnson(res)
  else:
   res = {'games_checkmark': {'C:/Windows/explorer.exe': True},
    'paths': {'C:/Windows/explorer.exe': 'По умолчанию'},
    'key_value': {'C:/Windows/explorer.exe': ['LBUTTON', 'RBUTTON', 'WHEEL_MOUSE_BUTTON', 'SCROLL_UP',
    'SCROLL_DOWN', 'SCROLL_UP', 'SCROLL_DOWN']},
    "mouse_press": {"C:/Windows/explorer.exe": [False, False, False, False, False, False, False]},
    "id": 0,
    "current_app": 'C:/Windows/explorer.exe'}
   know_id = '''#!/bin/bash
               input_list=$(xinput list)
               mouse_line=$(echo "$input_list" | head -n 1)
               if [ -n "$mouse_line" ]; then
                   mouse_id=$(echo "$mouse_line" | grep -o "id=[0-9]*" | cut -d "=" -f 2)
                   echo "$mouse_id"
               fi       '''
   # result = subprocess.run(['bash', '-c', know_id], capture_output=True, text=True)
   # res["id"] = int(result.stdout.strip())
  dict_save.save_jnson(res)
  dict_save.set_cur_app(res["current_app"])
  dict_save.set_prev_game(res["current_app"])
  dict_save.set_current_app_path(res['current_app'])
  devices = [InputDevice(path) for path in list_devices()]
  # Надёжный выбор физической клавиатуры: старый фильтр ("Keyboard\"" + ' phys ')
  # первым ловил виртуальное uinput-устройство (Smart-Virtual-Keyboard), и
  # реальные нажатия терялись. Теперь берём настоящую клавиатуру: пропускаем
  # виртуальные устройства и мыши, оставляем те, у которых есть буквы/Enter,
  # и выбираем самую «полную» (больше всего клавиш EV_KEY).
  try:
   candidates = []
   for dev in devices:
    try:
     caps = dev.capabilities().get(ecodes.EV_KEY, [])
    except Exception:
     continue
    name = (dev.name or "").lower()
    phys = (dev.phys or "").lower()
    if "virtual" in name or "uinput" in phys or "mouse" in name:
     continue
    if ecodes.KEY_A in caps or ecodes.KEY_ENTER in caps or ecodes.KEY_SPACE in caps:
     candidates.append(dev)
   if candidates:
    candidates.sort(key=lambda d: len(d.capabilities().get(ecodes.EV_KEY, [])), reverse=True)
    self.board = candidates[0]
    print("Клавиатура найдена:", self.board.name)
   if self.board is None:
    print("Клавиатура не найдена!")
  except Exception as e:
   print("Ошибка поиска клавиатуры:", e)
   # Вариант B: evdev — единственный источник событий клавиатуры. Корректно
   # различает нумпад (+/-) и основную клавиатуру, не падает при отсутствии устройства.
  self.start_keyboard_listener()  # Запускаем evdev-слушатель
  self.setup_ui()

 def start_keyboard_listener(self):
 # Запуск evdev-слушателя клавиатуры в отдельном потоке (Вариант B:
 # evdev — единственный источник событий, корректно различает нумпад и основную клавиатуру).
  self.keyboard_thread_exit = True
  old = getattr(self, "keyboard_thread", None)
  if old is not None and old.is_alive():
   try:
    old.join(timeout=1)
   except Exception:
    pass
  self.keyboard_thread_exit = False
  self.keyboard_thread = threading.Thread(target=self.keyboard_evdev_loop, daemon=True)
  self.keyboard_thread.start()

 def keyboard_evdev_loop(self):
  board = self.board
  if board is None:
   print("Клавиатура (evdev) не найдена — макросы клавиатуры отключены.")
   return
  pressed = set()
  while not self.keyboard_thread_exit:
   try:
    events = board.read()
    for event in events:
     if event.type != ecodes.EV_KEY:
      continue
     ke = categorize(event)
     if ke.keystate != ke.key_down:
      pressed.discard(ke.keycode)
      continue
     code = ke.keycode
     if isinstance(code, tuple):
      code = code[0]
     if code in pressed:
      continue  # защита от автоповтора (key_hold)
     pressed.add(code)
     label = evdev_key_to_label(code)
     if label is not None:
      self.handle_keyboard_macro(label)
   except BlockingIOError:
    time.sleep(0.01)  # буфер evdev пуст — не блокируем поток/GUI
    continue
   except Exception:
    time.sleep(0.05)
    continue

 def handle_keyboard_macro(self, key_label): # Та же логика сопоставления, что была в старом on_press: ищем макрос в keyboard_script
 # для текущего приложения и запускаем bash-скрипт. Без остановки/рестарта слушателя
 # (цикл непрерывный, поэтому повторные нажатия не теряются).
 # Макросы клавиатуры должны совпадать с целью эмуляции (активное окно),
 # а не с выбранным в UI профилем — иначе они расходятся после разделения
 # current_app (выбор) и live-цели эмуляции.
  current_app = None
  _rt = getattr(self, "_active_runtime", None)
  if _rt is not None and getattr(_rt, "game", None):
   current_app = _rt.game
  if not current_app:
   _res = dict_save.return_jnson()
   _enabled = [p for p, e in _res.get("games_checkmark", {}).items() if e]
   current_app = check_current_active_window(dict_save, _enabled) or dict_save.get_cur_app()
  res = dict_save.return_jnson()
  if "keyboard_script" not in res or current_app not in res["keyboard_script"]:
   return
  if "keys" not in res["keyboard_script"][current_app]:
   return
  keys_active = res["keyboard_script"][current_app]["keys"].keys()
  key = key_label.lower().replace(" ", "_")  # 'Caps Lock' -> 'caps_lock' и т.п.
  for i in list(keys_active):
   i = str(i).replace(" ", "_")
   k = key
   # Перевод русской БУКВЫ в английскую. Символы (+, -, ,, . и т.п.) НЕ трогаем:
   # в ru_to_en есть '+' -> ',' и '-' -> '.', что ломало сопоставление с макросами
   # "+"/"-" (физическая клавиша уже дана в нейтральном виде).
   if k.isalpha() and k in ru_to_en.keys():
    k = ru_to_en[k]
   if k == i.lower():
    script = res["keyboard_script"][current_app]["keys"][i]
    t = threading.Thread(target=lambda s=script: subprocess.call(["bash", "-c", s]))
    t.start()
    t.join()
    break
  
 def eventFilter(self, watched, event):
  if watched is self.scroll_area.viewport():
   if event.type() == QEvent.Type.MouseButtonPress:
    self._scroll_locked = True
    self._scroll_lock_val = self.scroll_area.verticalScrollBar().value()
   elif event.type() == QEvent.Type.MouseButtonRelease:
    sb = self.scroll_area.verticalScrollBar()
    sb.setValue(self._scroll_lock_val)
    QTimer.singleShot(0, lambda: sb.setValue(self._scroll_lock_val))
    QTimer.singleShot(80, lambda: sb.setValue(self._scroll_lock_val))
    QTimer.singleShot(180, lambda: self._clear_scroll_lock())
  return super().eventFilter(watched, event)

 def _block_scroll_during_click(self, _val): # Жёстко подавляем любую прокрутку списка профилей во время/сразу после клика
 # (QScrollArea сам «подскролливает» кликнутый элемент в зону видимости по фокусу).
  if getattr(self, "_scroll_locked", False):
   sb = self.scroll_area.verticalScrollBar()
   sb.blockSignals(True)
   sb.setValue(self._scroll_lock_val)
   sb.blockSignals(False)

 def _clear_scroll_lock(self):
  self._scroll_locked = False

 def setup_ui(self):
  self.setWindowTitle("Mouse setting control for buttons python")
  self.setGeometry(400, 340, 910, 386)
  self.setFixedSize(940, 346)
  central_widget = QWidget()
  self.setCentralWidget(central_widget)
  
  main_layout = QVBoxLayout(central_widget)
  main_layout.setContentsMargins(10, 10, 10, 10)
  main_layout.setSpacing(10)
  
  top_layout = QHBoxLayout()
  top_layout.setSpacing(10)
  
  left_widget = QWidget()
  left_widget.setFixedWidth(260)
  left_layout = QVBoxLayout(left_widget)
  left_layout.setContentsMargins(0, 0, 0, 0)
  
  self.scroll_area = QScrollArea()
  self.scroll_area.setWidgetResizable(True)
  self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
  self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
  self.scroll_area.setFixedHeight(280)
  
  self.scroll_widget = QWidget()
  self.games_layout = QVBoxLayout(self.scroll_widget)
  self.games_layout.setSpacing(5)
  self.games_layout.setContentsMargins(5, 5, 5, 5)
  
  self.scroll_area.setWidget(self.scroll_widget)
  self._scroll_locked = False
  self._scroll_lock_val = 0
  self.scroll_area.verticalScrollBar().valueChanged.connect(self._block_scroll_during_click)
  self.scroll_area.viewport().installEventFilter(self)
  left_layout.addWidget(self.scroll_area)
  top_layout.addWidget(left_widget, 1)
  
  right_widget = QWidget()
  right_layout = QVBoxLayout(right_widget)
  right_layout.setContentsMargins(10, 10, 10, 10)
  right_layout.setSpacing(10)
  
  rows_and_buttons_layout = QHBoxLayout()
  rows_and_buttons_layout.setSpacing(10)
  
  rows_layout = QVBoxLayout()
  rows_layout.setSpacing(5)
  res = dict_save.return_jnson()
  game = res['current_app']
  box_button = list(res["key_value"][game])
  lab=[]
  for i in range(7):
   row_layout = QHBoxLayout()
   row_layout.setSpacing(10)
   label = QLabel(LIST_MOUSE_BUTTONS[i])
   label.setStyleSheet("padding: 4px; font-weight: bold;")
   label.setFixedWidth(150)
   lab.append(label)
   combo = QComboBox()# Установить все значения выпадающего списка
   combo.addItems(LIST_KEYS)
   current_value = box_button[i]
   self.combo_box.append(combo)
 
   if current_value in LIST_KEYS:
    i2 = LIST_KEYS.index(current_value)
    combo.setCurrentIndex(i2)
   else:
    combo.setCurrentIndex(0)
   combo.currentIndexChanged.connect(lambda idx, i=i: self.update_button(i))
   
   checkbox = QCheckBox()
   checkbox.setToolTip("Держать нажатой")
   checkbox.stateChanged.connect(lambda state, i=i: self.check_mouse_press_button(i, state))
   self.mouse_button_labels.append(label)
   self.mouse_button_combos.append(combo)
   self.mouse_check_buttons.append(checkbox)
   row_layout.addWidget(label)
   row_layout.addWidget(combo, 1)
   row_layout.addWidget(checkbox)
   
   rows_layout.addLayout(row_layout)
  
  button_column_layout = QVBoxLayout()
  button_column_layout.setSpacing(5)

  dict_save.save_labels(lab)
  for idx, name in enumerate(LIST_MOUSE_BUTTONS):# Кнопки для скриптов
   button = QPushButton(name)
   button.setFixedWidth(150)
   button.setStyleSheet("padding: 4px;")
   button_column_layout.addWidget(button)
   button.clicked.connect(lambda _, i=idx: self.mouse_scrpt_keyboard_with_editor(i))
   self.buttons_script.append(button)
  
  control_widget = QWidget()
  control_layout = QVBoxLayout(control_widget)
  control_layout.setContentsMargins(10, 10, 10, 10)
  control_layout.setSpacing(12)
  
  self.add_button_add = QPushButton("Добавить")
  self.add_button_add.clicked.connect(lambda: self.add_file())
  control_layout.addWidget(self.add_button_add)
  
  self.del_button = QPushButton("Удалить")
  self.del_button.clicked.connect(lambda: self.delete())
  control_layout.addWidget(self.del_button)
  
  self.move_element_up = QPushButton("Вверх")
  self.move_element_up.clicked.connect(lambda: self.move_element(dict_save, "up"))
  control_layout.addWidget(self.move_element_up)
  self.move_element_down = QPushButton("Вниз")
  self.move_element_down.clicked.connect(lambda: self.move_element(dict_save, "down"))
  control_layout.addWidget(self.move_element_down)
  
  self.Keyboard_button = QPushButton("Клавиатура")
  self.Keyboard_button.clicked.connect(lambda: self.create_virtual_keyboard(dict_save))
  control_layout.addWidget(self.Keyboard_button)
  self.show_devices_button = QPushButton("Показать список устройств")
  self.show_devices_button.clicked.connect(lambda: show_list_id_callback())

  control_layout.addWidget(self.show_devices_button)
  
  if os.getgid() != 0:
   id_layout = QHBoxLayout()
   id_layout.setSpacing(10)
   
   id_label = QLabel("ID устройства:")
   id_label.setStyleSheet("padding: 2px;")
   
   self.id_combo = QComboBox()# выпадающий список профиля
   id_list = dict_save.get_list_ids() if dict_save else []
   self.id_combo.addItems([str(id) for id in id_list])
   self.id_combo.setToolTip('Выбор id устройства')
   self.id_combo.currentIndexChanged.connect(lambda: self.update_profile()) # Используем сигнал currentIndexChanged или activated
   id_layout.addWidget(id_label)
   id_layout.addWidget(self.id_combo)
   control_layout.addLayout(id_layout)
  
  rows_and_buttons_layout.addLayout(rows_layout, 3)
  rows_and_buttons_layout.addLayout(button_column_layout, 1)
  rows_and_buttons_layout.addWidget(control_widget, 1)
  
  right_layout.addLayout(rows_and_buttons_layout)
  top_layout.addWidget(right_widget, 2)
  main_layout.addLayout(top_layout)
  
  QTimer.singleShot(0, self.start_app)
 
 def start_app(self):# Функция старта.
  res = dict_save.return_jnson()
  if os.getgid() != 0 and hasattr(self, 'id_combo'):
   self.id_combo.setCurrentText(str(res["id"]))# установить ввыпадающий список ID устройства.
  curr_name = dict_save.get_cur_app()
  key_values = res["key_value"]
  for i in range(len(LIST_MOUSE_BUTTONS)):
   if hasattr(self, 'mouse_button_combos') and i < len(self.mouse_button_combos):
    if curr_name in key_values and i < len(key_values[curr_name]):
     self.mouse_button_combos[i].setCurrentText(key_values[curr_name][i])
  self.filling_in_fields(dict_save) # Заполнения полей.
  self.start_startup_now(dict_save)# Запуск эмуляции.
  
if __name__ == "__main__":
 app = QApplication(sys.argv)
 app.setStyle("Fusion")
 palette = app.palette()
 palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
 palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
 palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
 palette.setColor(QPalette.ColorRole.AlternateBase, QColor(240, 240, 240))
 palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
 palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
 palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
 palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
 palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
 palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
 palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
 palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
 palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
 app.setPalette(palette)
 window = MouseSettingApp()
 window.show()
 sys.exit(app.exec())
