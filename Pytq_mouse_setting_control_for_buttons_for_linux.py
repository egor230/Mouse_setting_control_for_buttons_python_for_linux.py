from Pyqt_libs_mouse import *
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = "/mnt/807EB5FA7EB5E954/софт/виртуальная машина/linux must have/python_linux/Project/myenv/lib/python3.12/site-packages/PyQt5/Qt5/plugins"

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
  for dev in devices:
   if "Keyboard\"" in str(dev) and ' phys ' in str(dev):
    self.board = dev#    print(dev)
    break
  if self.board is None:
   print("Клавиатура не найдена!")
  def on_press(key):  # обработчик клави.  # print(key )
   current_app = dict_save.get_cur_app()  # Получаем текущую игру
   res = dict_save.return_jnson()
   for event in self.board.read_loop():  # Подписываемся на события
    if event.type == ecodes.EV_KEY:
     key_event = categorize(event)
     if key_event.keystate == key_event.key_down: # Получаем название клавиши и преобразуем его
      key_name = key_event.keycode
      simple_name = simple_key_map.get(key_name, key_name)  # Если клавиша не в словаре, оставляем как есть
      if simple_name in ["7\nHome", "8\n↑", "9\nPgUp", "4\n←", "5\n", "6\n→", "1\nEnd", "2\n↓", "KP_Down", "3\nPgDn"]:
       key = simple_name
       break
    if "keys" in res.get("keyboard_script", {}).get(current_app, {}):  # Проверяем наличие текущего приложения в "keyboard_script"
     keys_active = res["keyboard_script"][current_app]["keys"].keys()  # Получаем полное имя клавиши без нормализации
     key = str(key).replace(" ", "").replace('\'', '').replace("Key.", "").replace("KEY.", "").lower()  # Очищаем от ненужного     print(key)
     for i in list(keys_active):  # Получаем клавиши которые являются макросами.
      i = str(i)
      if key in ru_to_en.keys():  # нужно перевести нужно перевести русскую клавишу в английскую.
       key = ru_to_en[key]
      if key.lower() == i.lower():  # теперь нужно перевести ее в нижней регистр.
       script = res["keyboard_script"][current_app]["keys"][i]  # print(script)
       listener.stop()
       t = threading.Thread(target=lambda: subprocess.call(['bash', '-c', script]))
       t.start()
       t.join()
       start_listener()

  def on_release(key):
   pass
   return True
  def start_listener():
   global listener
   listener = keyboard.Listener(on_press=on_press, on_release=on_release)
   listener.start()

  start_listener()  # Запускаем слушатель
  self.setup_ui()
 
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
  self.Keyboard_button.clicked.connect(lambda _, i=idx: self.create_keyboard_with_editor(i))
  control_layout.addWidget(self.Keyboard_button)
  self.show_devices_button = QPushButton("Показать список устройств")
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
 window = MouseSettingApp()
 window.show()
 sys.exit(app.exec_())