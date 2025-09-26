from Pyqt_libs_mouse import *
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = "/mnt/807EB5FA7EB5E954/софт/виртуальная машина/linux must have/python_linux/Project/myenv/lib/python3.12/site-packages/PyQt5/Qt5/plugins"

dict_save = save_dict()
class MouseSettingApp(QMainWindow):
 class VirtualKeyboard(QMainWindow):
  def __init__(self, callback_record_macro=None):
   super().__init__()
   self.callback_record_macro = callback_record_macro
   self.setGeometry(240, 580, 1350, 340)
   self.setWindowTitle("Виртуальная клавиатура")
   
   self.central = QWidget(self)
   self.setCentralWidget(self.central)
   
   self.buttons = {}
   self.create_layout()
  
  def record_macro(self, key):
   if self.callback_record_macro:
    self.callback_record_macro(key, self)
 
 class MacroEditor(QDialog):
  def __init__(self, key, parent=None):
   super().__init__(parent)
   self.key = key
   self.setWindowTitle(f"Запись макроса для {key}")
   # self.setGeometry(140, 480, 800, 400)
   
   layout = QVBoxLayout(self)
   
   self.text_widget = QPlainTextEdit(self)
   self.text_widget.insertPlainText("#!/bin/bash\n")
   layout.addWidget(QLabel("Редактор скрипта:"))
   layout.addWidget(self.text_widget)
   
   res = dict_save.return_jnson()
   current_app = res["current_app"]
   if "keyboard_script" in res and current_app in res["keyboard_script"]:
    keys = res["keyboard_script"][current_app].get("keys", {})
    if key in keys:
     self.text_widget.setPlainText(keys[key])
  
  def get_script(self):
   return self.text_widget.toPlainText()
 
 class MacroKeyboardWindow(QMainWindow):  # Бывший KeyboardWithEditor
  def __init__(self, dict_save, parent=None):
   super().__init__(parent)
   self.dict_save = dict_save
   self.current_key = None
   self.text_widget = None
   self.keyboard_window = None
   self.setup_ui()
  
  def setup_ui(self):
   self.setWindowTitle("Запись макроса")
   self.setGeometry(140, 480, 1410, 600)
   
   central_widget = QWidget()
   self.setCentralWidget(central_widget)
   layout = QVBoxLayout(central_widget)
   
   self.text_widget = QTextEdit()
   self.text_widget.setPlainText("#!/bin/bash\n")
   
   # Явно перемещаем курсор в конец (на новую строчку ниже)
   cursor = self.text_widget.textCursor()
   cursor.movePosition(QTextCursor.End)
   self.text_widget.setTextCursor(cursor)
   layout.addWidget(QLabel("Редактор скрипта:"))
   layout.addWidget(self.text_widget)
   
   # Используем KeyboardWidget для создания раскладки (устранение дублирования)
   self.keyboard_widget = KeyboardWidget(self.add_key_text)
   layout.addWidget(self.keyboard_widget)
  
  def add_key_text(self, key):
   add_text_pytq5(key, self.text_widget)
   current_app = dict_save.get_cur_app()
   res = dict_save.return_jnson()
 
 def __init__(self):
  super().__init__()
  self.a_scrypt = []
  self.combo_box = []
  self.creat = 0
  self.devices = [InputDevice(path) for path in list_devices()]
  self.board = None
  self.mouse_button_labels = []
  self.mouse_button_combos = []
  self.mouse_check_buttons = []
  self.buttons_script = []
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
   res = {'games_checkmark': {'C:/Windows/explorer.exe': True},
          'paths': {'C:/Windows/explorer.exe': 'По умолчанию'},
          'key_value': {'C:/Windows/explorer.exe': ['LBUTTON', 'RBUTTON', 'WHEEL_MOUSE_BUTTON', 'SCROLL_UP',
                                                    'SCROLL_DOWN', 'SCROLL_UP', 'SCROLL_DOWN']},
          "mouse_press": {"C:/Windows/explorer.exe": [False, False, False, False, False, False, False]},
          "id": 0,
          "current_app": 'C:/Windows/explorer.exe'}
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
   dict_save.save_jnson(res)
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
  for idx, name in enumerate(LIST_MOUSE_BUTTONS):
   button = QPushButton(name)
   button.setFixedWidth(150)
   button.setStyleSheet("padding: 4px;")
   button_column_layout.addWidget(button)
   button.clicked.connect(lambda _, i=idx: self.button_keyboard(i))
   self.buttons_script.append(button)
  
  control_widget = QWidget()
  control_layout = QVBoxLayout(control_widget)
  control_layout.setContentsMargins(10, 10, 10, 10)
  control_layout.setSpacing(12)
  
  self.add_button_add = QPushButton("Добавить")
  self.add_button_add.clicked.connect(self.add_file)
  control_layout.addWidget(self.add_button_add)
  
  self.add_button_start = QPushButton("Удалить")
  self.add_button_start.clicked.connect(self.delete)
  control_layout.addWidget(self.add_button_start)
  
  self.move_element_up = QPushButton("Вверх")
  self.move_element_up.clicked.connect(lambda: self.move_element(dict_save, "up"))
  control_layout.addWidget(self.move_element_up)
  self.move_element_down = QPushButton("Вниз")
  self.move_element_down.clicked.connect(lambda: self.move_element(dict_save, "down"))
  control_layout.addWidget(self.move_element_down)
  
  self.Keyboard_button = QPushButton("Клавиатура")
  self.Keyboard_button.clicked.connect(self.create_keyboard_with_editor)
  control_layout.addWidget(self.Keyboard_button)
  self.show_devices_button = QPushButton("Показать список устройств")
  control_layout.addWidget(self.show_devices_button)
  
  if os.getgid() != 0:
   id_layout = QHBoxLayout()
   id_layout.setSpacing(10)
   
   id_label = QLabel("ID устройства:")
   id_label.setStyleSheet("padding: 2px;")
   
   self.id_combo = QComboBox()
   id_list = dict_save.get_list_ids() if dict_save else []
   self.id_combo.addItems([str(id) for id in id_list])
   self.id_combo.setToolTip('Выбор id устройства')
   
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
 
 def create_keyboard_with_editor(self):
  self.keyboard_editor = self.MacroKeyboardWindow(dict_save)
  self.keyboard_editor.show()
 
 def record_marcross(self, key):
  dict_save.set_last_key_keyboard_script(key)
  self.keyboard_editor = self.MacroKeyboardWindow(dict_save)
  self.keyboard_editor.setWindowTitle(f"Запись макроса для клавиши {key}")
  
  res = dict_save.return_jnson()
  current_app = dict_save.get_cur_app()
  res.setdefault("keyboard_script", {}).setdefault(current_app, {"keys": {}})
  keys_active = list(res["keyboard_script"][current_app]["keys"].keys())
  
  if key in keys_active:
   text_content = res["keyboard_script"][current_app]["keys"][key]
   self.keyboard_editor.text_widget.setPlainText(text_content)
  else:
   self.keyboard_editor.text_widget.setPlainText("#!/bin/bash\n")
  
  self.keyboard_editor.show()
 
 def create_keyboard(self):
  # Временная заглушка для метода create_keyboard
  pass
 
 def record_macro_callback(self, key, window):
  self.record_marcross(key)
 
 def filling_in_fields(self, res):
  while self.games_layout.count():
   child = self.games_layout.takeAt(0)
   if child.widget():
    child.widget().deleteLater()
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
   label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
   label.mousePressEvent = lambda event, c=count: self.label_clicked(event, dict_save, c)
   label.setContextMenuPolicy(Qt.CustomContextMenu)
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
   dict_save.set_prev_game(game)
   dict_save.set_cur_app(game)
   while game != dict_save.get_cur_app():
    time.sleep(1)
  
  res = dict_save.return_jnson()
  res['current_app'] = game
  # Временные заглушки для отсутствующих функций
  # mouse_check_button(dict_save)
  self.create_scrypt_buttons()
  keys = list(res['paths'].keys())
  index = keys.index(res['current_app'])
  # set_list_box(dict_save, index)
 
 def closeEvent(self, event):
  old_data = dict_save.return_old_data()
  new_data = dict_save.return_jnson()
  diff = DeepDiff(old_data, new_data)
  if diff:
   reply = QMessageBox.question(self, "Выход", "Вы хотите сохранить изменения перед выходом?",
                                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
   if reply == QMessageBox.Save:
    dict_save.write_to_file(new_data)
   elif reply == QMessageBox.Cancel:
    return
  target = "Pytq_mouse_setting_control_for_buttons_for_linux.py"
  current_pid = os.getpid()
  for p in psutil.process_iter(['pid', 'cmdline']):
   try:
    cmdline_str = ' '.join(p.info['cmdline'])
    if target in cmdline_str and p.info['pid'] != current_pid:
     os.kill(p.info['pid'], signal.SIGTERM)
   except (psutil.NoSuchProcess, psutil.AccessDenied, IndexError):
    continue
  event.accept()
  sys.exit(0)
 
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
 
 def checkbutton_changed(self, count):
  res = dict_save.return_jnson()
  keys_list = list(res["games_checkmark"].keys())
  curr_app = str(keys_list[count])
  var_list = dict_save.return_var_list()
  res["games_checkmark"][curr_app] = var_list[count].isChecked()
  dict_save.save_jnson(res)
 
 def update_labels_bindings(self):
  labels = dict_save.return_labels()
  var_list = dict_save.return_var_list()
  for count, label in enumerate(labels):
   label.mousePressEvent = lambda event, c=count: self.label_clicked(event, dict_save, c)
   if count < len(var_list):
    var_list[count].stateChanged.disconnect()
    var_list[count].stateChanged.connect(lambda state, c=count: self.checkbutton_changed(c))
 
 def move_element(self, dict_save, direction):  # Перемещает текущий выбранный элемент (приложение/игра) вверх или вниз
  try:  # 1. Получение данных и текущих позиций
   res = dict_save.return_jnson()
   labels = dict_save.return_labels()  # Список QLabel виджетов
   curr_app_path = res["current_app"]  # Путь к текущему приложению
   # Получаем ключи (пути) в том порядке, в котором они хранятся в JSON
   keys_list = list(res["key_value"].keys())
   # Определяем текущий индекс
   index_curr = keys_list.index(curr_app_path)
   
   # Вычисляем новый индекс
   new_index = -1
   if direction == 'up' and index_curr > 0:
    new_index = index_curr - 1
   elif direction == 'down' and index_curr < len(labels) - 1:
    new_index = index_curr + 1
   else:
    # Если перемещение невозможно (уже крайний элемент или неверное направление)
    return
   # print("curr ", index_curr)
   # print("new_index", new_index)
   container_curr = labels[index_curr].parentWidget()
   container_new = labels[new_index].parentWidget()
   
   # Получаем главный layout (QVBoxLayout) списка игр, в котором находятся все контейнеры
   main_layout = container_curr.parentWidget().layout()
   
   # 2. Перестановка виджетов в Layout
   main_layout.removeWidget(container_curr)
   main_layout.removeWidget(container_new)
   
   # Обновляем порядок в локальном списке labels (содержит только QLabel)
   labels.insert(new_index, labels.pop(index_curr))
   
   # Вставляем виджеты обратно в layout.
   # В Qt layout.insertWidget(индекс, виджет) вставляет виджет на указанную позицию.
   if direction == 'up':
    # На место new_index (которое меньше) вставляем старый curr,
    # а на место index_curr (которое больше) - старый new.
    main_layout.insertWidget(new_index, container_curr)
    main_layout.insertWidget(index_curr, container_new)
   else:  # direction == 'down'
    # На место index_curr (которое меньше) вставляем старый new,
    # а на место new_index (которое больше) - старый curr.
    main_layout.insertWidget(index_curr, container_new)
    main_layout.insertWidget(new_index, container_curr)
   
   # 3. Обновление данных сохранения (JSON)
   # Временная заглушка для отсутствующей функции
   # res = reorder_keys_in_dict(res, index_curr, direction)
   
   labels[index_curr].setStyleSheet("background-color: white; color: black; border: 1px solid gray; padding: 5px;")
   # Сохраняем стиль выделения для элемента, который был текущим и переместился
   # (labels[new_index]).
   labels[new_index].setStyleSheet("background-color: #06c; color: white; border: 1px solid gray; padding: 5px;")
   
   # Обновляем привязки событий (connects) для новых позиций
   self.update_labels_bindings()
   
   # 5. Сохранение и завершение
   dict_save.save_labels(labels)  # Обновляем список labels в объекте сохранения
   dict_save.save_jnson(res)
   return 0
  
  except Exception as e:
   # Выводим ошибку для отладки
   print(f"Ошибка при перемещении элемента: {e}")
   # pass (сохраняем ваш стиль)
   pass
 
 def check_label_changed(self, dict_save, count):
  res = dict_save.return_jnson()
  labels = dict_save.return_labels()
  keys_list = list(res["key_value"].keys())
  curr = res["current_app"]
  index_curr = keys_list.index(curr)
  labels[index_curr].setStyleSheet("background-color: white; border: 1px solid gray; padding: 5px;")
  game = list(res["key_value"].keys())[count]
  labels[count].setStyleSheet("background-color: #06c; color: white; border: 1px solid gray; padding: 5px;")
  res["current_app"] = game
  dict_save.set_cur_app(game)
  dict_save.set_prev_game(curr)
  
  list_check_buttons = res.get("mouse_press", {}).get(game, [])
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
    if value is not None and key in defaut_list_mouse_buttons:
     i = defaut_list_mouse_buttons.index(key)
     self.buttons_script[i].setStyleSheet("""
                QPushButton { border: 1px solid gray; padding: 5px;
                color: black;  background-color: gray; } """)
     self.buttons_script[i].update()
  
  dict_save.save_jnson(res)
  self.update_button(curr)
 
 def update_button(self, index):
  res = dict_save.return_jnson()
  game = res["current_app"]
  box_button = list(res["key_value"][game])
  
  for i in range(7):
   current_value = box_button[i]
   i2 = LIST_KEYS.index(current_value)
   self.combo_box[i].setCurrentIndex(i2)
 
 def label_clicked(self, event, dict_save, count):
  if event.button() == Qt.LeftButton:
   self.check_label_changed(dict_save, count)
 
 def check_mouse_press_button(self, count, state):
  res = dict_save.return_jnson()
  curr_name = dict_save.get_cur_app()
  
  if curr_name not in res.get("mouse_press", {}):
   res["mouse_press"][curr_name] = [False] * 7
  res["mouse_press"][curr_name][count] = (state == Qt.Checked)
  dict_save.save_jnson(res)
 
 def add_file(self):
  pass
 
 def delete(self):
  pass
 
 # Добавляем недостающие методы
 def button_keyboard(self, index):
  pass
 
 def create_scrypt_buttons(self):
  pass
 
 def show_change_name_menu(self, count):
  pass


if __name__ == "__main__":
 app = QApplication(sys.argv)
 window = MouseSettingApp()
 window.show()
 sys.exit(app.exec_())