from Mouse_libs import *
def run_scrypt(i):
  res= dict_save.return_jnson()
  if "script_mouse" not in res:
    res.setdefault("script_mouse", {})
  if res["script_mouse"].get(dict_save.get_cur_app()) is None:
      res["script_mouse"].setdefault(dict_save.get_cur_app(), {})

  if res["script_mouse"][dict_save.get_cur_app()].get(defaut_list_mouse_buttons[i]) is None:
      res["script_mouse"][dict_save.get_cur_app()].setdefault(defaut_list_mouse_buttons[i], "#!/bin/bash\n")

  root.title("Скрипт")
  notebook = ttk.Notebook(root)
  notebook.grid(row=0, column=0, sticky="nsew")

  tab1 = ttk.Frame(notebook)  # Создаем одну вкладку для текста
  notebook.add(tab1, text="Редактор")

  # Добавляем виджет Text на вкладку для ввода текста
  text_widget = Text(tab1, wrap='word')
  text_widget.grid(row=0, column=0, sticky="nsew")
  key_mouse_scrypt = res["script_mouse"][dict_save.get_cur_app()].get(defaut_list_mouse_buttons[i])
  # Вставляем текст только если он не равен "#!/bin/bash\n"
  if key_mouse_scrypt and key_mouse_scrypt != "#!/bin/bash\n":
      text_widget.insert("end", key_mouse_scrypt)
  else:
      text_widget.insert("end", "#!/bin/bash\n")
    # Функция для закрытия окна
  def close_window(i, key_mouse_scrypt, win):
    text_content = text_widget.get("1.0", "end-1c")  # Извлекаем текст из text_widget
    res["script_mouse"][dict_save.get_cur_app()][defaut_list_mouse_buttons[i]]=text_content
    dict_save.save_jnson(res)
    notebook.destroy()  # Создаем вкладку с кнопкой "Закрыть"
    win.destroy()

  # Создаем окно клавиатуры
  win = keyboard_scrypt(root, text_widget)

  # Установка обработчика закрытия окна
  win.protocol("WM_DELETE_WINDOW", lambda: close_window(i, key_mouse_scrypt, win))
creat = 0  # Глобальная переменная для контроля создания кнопок
a_scrypt = []  # Список для хранения созданных кнопок

def create_scrypt_buttons():
  global creat
  y_place = 23  # Начальная координата для кнопок
  res = dict_save.return_jnson()  # Получение данных из dict_save
  for i in range(7):
    if creat == 0:    # Проверяем, нужно ли создавать кнопки
      scrypt_button = Button( text=str(LIST_MOUSE_BUTTONS[i]),     # Создание кнопки
        font=("Arial", 9),  width=10, height=1,        command=lambda i1=i: run_scrypt(i1)
      )
      scrypt_button.place(x=520, y=y_place)  # Размещение кнопки
      a_scrypt.append(scrypt_button)  # Добавление кнопки в список

    # Проверяем состояние кнопки и устанавливаем стиль
    if i < len(a_scrypt) and check_mouse_script(res, dict_save, defaut_list_mouse_buttons, i):      # print("Кнопка активирована")
      a_scrypt[i].config(relief=SUNKEN)  # Изменение стиля кнопки
    else:
      a_scrypt[i].config(relief=RAISED)
    y_place += 31  # Увеличение координаты по вертикали

  creat = 1  # Обновляем флаг, чтобы кнопки не создавались повторно
def update_buttons(event=0):# Изменение назначения кнопок.
  dict_save.set_current_path_game(" ")
  dict_save.set_default_id_value(add_button_start)
  box_value = dict_save.return_box_values() # Получить значения выпадающего списка
  res=dict_save.return_jnson()
  box_values=[box_value[0].get(), box_value[1].get(), box_value[2].get(),
              box_value[3].get(),box_value[4].get(),box_value[5].get(),box_value[6].get()]
  res["key_value"][str(dict_save.get_cur_app())]=box_values
  dict_save.set_id(id_value.get())

  res["current_app"]=str(dict_save.get_cur_app())  # add_button_start["state"] = "normal"
  res["id"]=id_value.get()
  dict_save.save_jnson(res)  # Сохранить новые настройки.  # print("change color label")
  start_startup_now(dict_save, root)

def update_check_button(event):# Галочка запускать при старте.
 dict_save.set_default_id_value(add_button_start)
 res= dict_save.return_jnson()
 if start_startup.get():
  res["start_startup"]= False  #
 else:
  res["start_startup"]= True  #
 dict_save.save_jnson(res)# Сохранить изменения

def checkbutton_changed(event, var_list, count, name_games, labels, curr_app):  # галочки
  dict_save.set_cur_app(curr_app)# Установить текущий путь к игре напротив галочки
  dict_save.set_count(count)
  res = dict_save.return_jnson()
  if var_list[count].get() == False:
    labels[count].config(background="#06c")  # текстовое поле и кнопка для добавления в список
    res["games_checkmark"][str(dict_save.get_cur_app())] = True
  else:
    labels[count].config(background="white")  # текстовое поле и кнопка для добавления в список
    res["games_checkmark"][str(dict_save.get_cur_app())] = False
  for i in range(len(labels)):
    if i != count:
      labels[i].config(background="white")

  update_buttons(event)# Обновить кнопки.

def update_mouse_check_button(count):# сохранение после установки флажков.  print(count)
  res=dict_save.return_jnson()
  curr_name=dict_save.get_cur_app()#  print(count)  print(len(res["mouse_press"][curr_name]))
  # Проверка наличия ключа перед его обновлением
  if curr_name in res["mouse_press"]:
    # Изменение значения на противоположное
    res["mouse_press"][curr_name][count] = not res["mouse_press"][curr_name][count]
    list_mouse_button_press = res["mouse_press"][curr_name]  # print(list_mouse_button_press)  # Обновить список флажков.
    dict_save.set_default_id_value(add_button_start)
    dict_save.save_jnson(res)
def mouse_check_button(dict_save, res,curr_name):
  list_mouse_button_press = list(res["mouse_press"][curr_name])#  print(d)
  mouse_press_button = []# список нажатых кнопок.
  cd1_y = 30
  for count, i in enumerate(list_mouse_button_press):
    mouse_press_button.append(BooleanVar())
    mouse_press_button[count].set(i)
    cb1 = Checkbutton(root, variable=mouse_press_button[count],  # создания галочек
                      onvalue=1, offvalue=0, state=NORMAL,  command=lambda c=count: update_mouse_check_button(c))  # Исправление здесь
    cb1.place(x=490, y=cd1_y)
    cd1_y = cd1_y + 30
    CreateToolTip(cb1, text='Держать нажатой')  # вывод надписи
  dict_save.save_mouse_button_press(list_mouse_button_press, mouse_press_button)

def set_colol_white_label_changed(labels):# Установить белый цвет для всех label
  for i in range(len(labels)):
    labels[i].config(background="white")  # у всех надписей снять выделения

def change(event, window, new_name, old_name, res, count, labels):# Окно изменение названия игры
  new_name = new_name.get()  # print(new_name, old_name, end=" , ")
  if new_name != "" and new_name != old_name:
    res["paths"][list(res["paths"])[count]]=new_name
    labels[count].config(text=new_name)#  res["paths"][dict_save.get_cur_app()] = new_name.get()
  window.destroy()  # Закрытие окна после сохранения изменений
def change_name_label(event, count): #Изменить название игры
  window = Toplevel(root)  # основа
  window.title("change_name")  # заголовок
  window.geometry("350x150+750+400")  # Первые 2 определяют ширину высоту. Пос 2 x и y координаты на экране.
  window.configure(bg='DimGray')  # Цвет фона окна
  labels = dict_save.return_labels()
  res = dict_save.return_jnson()
  old_name=res["paths"][list(res["paths"])[count]]# Получить прежнее название игры
  new_name = StringVar()
  e = Entry(window, width=25, textvariable=new_name)
  e.grid(column=2, row=0, padx=50, pady=5)
  e.focus()  # Фокусируемся на текстовом поле
  new_name.set(old_name)
  # Кнопка теперь является частью нового диалогового окна `window`, а не исходного `root`
  Button(window, text="Ok", command=lambda: change(None, window, new_name, old_name, res, count,  labels)) \
    .grid(column=2, row=1, padx=50, pady=30)  # кнопка, откроется новое окно.
  e.bind('<Return>', lambda event: change(event, window, new_name, old_name, res, count,labels))

def check_label_changed(event, labels, count, var_list):# изменение цвета label
 set_colol_white_label_changed(labels)  # Установить белый цвет для всех label print(count)
 if count != dict_save.get_count() :
  dict_save.set_count(count)
  res = labels[count].cget("background")
  for i in range(len(labels)):
   if i != count:
    labels[i].config(background="white")
   if str(res) =="white":
     labels[count].config(background="#06c")
     var_list[count].set(True)
 else:
     if "white" == labels[count].cget("background"):
      labels[count].config(background="#06c")
     else: # в белый
      labels[count].config(background="white")
 res=dict_save.return_jnson()
 game=list(res['paths'].keys())[count]
 res['current_app'] = game# Выбранная игра.
 dict_save.set_prev_game(game)
 # print(game)
 while game!=dict_save.get_cur_app(): # получить значение текущей активной строки.
    dict_save.set_cur_app(game)

 # dict_save.set_box_values(add_button_start)
 # update_buttons(event)# Изменение назначения кнопок.
 dict_save.set_values_box()# установить значения клавиш.
 # print(dict_save.get_cur_app())
 mouse_check_button(dict_save, res, dict_save.get_cur_app()) # флаг для удержания кнопки мыши.
 # print(dict_save.get_current_path_game()) # номер записи.
 # Если мы переключили надпись, стоит флажок запускать старте.
 # start_startup_now(dict_save, root)
 create_scrypt_buttons()
def add_file(dict_save):# Добавить новые игры
 res=dict_save.return_jnson() # получаем настройки
 keys_values =res["key_value"][dict_save.get_cur_app()]# конфигурация кнопок от предыдущего профиля.
 mouse_press_old =res["mouse_press"][dict_save.get_cur_app()]# какие кнопки имеют залипания.

 # print(dict_save.get_current_app_path())
 cmd = ['zenity', '--file-selection', '--file-filter=EXE files | *.exe'] # Zenity команда для выбора одного exe файла
 # Вызов zenity и получение выбранного пути
 result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, text=True)
 path_to_file = result.stdout.strip()# новый путь к игре

 name_with_expansion = path.basename(path_to_file)# Получение базового имени файла с расширением из полного пути к файлу
 name = path.splitext(name_with_expansion)[0] # Отделение имени файла без расширения путем разбиения строки.
 li= list(res["paths"].keys())
 if path_to_file in li:
   return 0
 res["paths"][str(path_to_file)]=str(name)
 res["games_checkmark"][str(path_to_file)]=True
 res["key_value"][str(path_to_file)]=keys_values # сохранить пред значения
 res["mouse_press"][str(path_to_file)]= list(mouse_press_old)
 res1= res["key_value"]
 if path_to_file in res1:
     pass
 else:
     res["key_value"][path_to_file]=["LBUTTON","RBUTTON",  "WHEEL_MOUSE_BUTTON",
      "WHEEL_MOUSE_UP", "WHEEL_MOUSE_DOWN", 'XBUTTON1', 'XBUTTON2']

 dict_save.save_jnson(res)
 labels=dict_save.return_labels()
 for i in range(len(labels)):
   labels[i].destroy()

 labels.clear()
 name_games = dict_save.return_name_games()
 name_games.clear()
 var_list = dict_save.return_var_list()
 var_list.clear()
 labels_with_checkmark = dict_save.return_labels_with_checkmark()
 labels_with_checkmark.clear()
 labels=dict_save.return_labels()
 dict_save.count=+1
 filling_in_fields(res)
 set_colol_white_label_changed(labels)  # Установить белый цвет для всех label

 # keys_values= dict_save.return_box_values()
 # old_keys_values=[]
 # for i in range(len(keys_values)):
 #     old_keys_values.append(keys_values[i].get())

 labels[len(labels)-1].config(background="#06c")  # текстовое поле и кнопка для добавления в список
checkbutton_list=[]
def fill_labes(res, name_games,labels,var_list, labels_with_checkmark):# Заполнение полей надписи и галочки.
  check_mark = res["games_checkmark"]
  d=res["paths"]
  for count, i in enumerate(d):    # print(count)
    name_game = StringVar()    # i это пути к играм
    name_game = d[i] # называния игр.
    box_key = StringVar()    # dict_save.set_cur_app(i)
    name_games.append(name_game)
    labels.append(Label(root, background="white", text=name_games[count], width=28, relief=GROOVE, justify="left"))
    y1 = (count + 1) * 25 + 1

    # галочки
    var_list.append(BooleanVar())
    check_mark = res["games_checkmark"]
    bool_check_mark = check_mark[i]
    var_list[count].set(bool_check_mark)
    labels_with_checkmark[labels[count]] = var_list[count]
    cb = Checkbutton(root, variable=var_list[count],  # создания галочек
                     onvalue=1, offvalue=0, state=ACTIVE)
    cb.bind("<Button-1>", lambda event, agr=var_list, agr1=count, agr2=name_games, agr3=labels, agr4=i:
    checkbutton_changed(event, agr, agr1, agr2, agr3, agr4))
    cb.place(x=7, y=y1 - 2)
    checkbutton_list.append(cb)
    # надписи
    labels[count].bind("<Button-1>", lambda event, agr=labels, agr1=count, agr2=var_list:
    check_label_changed(event, agr, agr1, agr2))
    labels[count].bind('<Button-3>', lambda event, agr=count: change_name_label(event, agr))
    labels[count].place(x=10, y=y1)  # текстовое поле и кнопка для добавления в список

  keys = list(res['paths'].keys())# Получить все пути игр.
  index = keys.index(res['current_app'])# Узнать индекс текущей игры.

  #активное приложение.
  labels[index].config(background="#06c") # Установить cиний цвет.  print(index)
  dict_save.set_count(index)# Установить  индекс текущей игры.
  dict_save.set_box_values(add_button_start)  # Установить значения выпадающего списка.
  dict_save.set_values_box()
def filling_in_fields(res):# заполнения всех полей.
    labels=dict_save.return_labels()
    name_games=dict_save.return_name_games()# имя игр
    var_list=dict_save.return_var_list()
    labels_with_checkmark= dict_save.return_labels_with_checkmark()
    boxs = dict_save.return_box_values()
    fill_labes(res, name_games, labels, var_list, labels_with_checkmark)    # if dict_save.get_count()==0:    #    print("ok")    #  labels[dict_save.get_count()].config(background="#06c")
    dict_save.set_box_values(add_button_start)  # Установить значения выпадающего списка.
    dict_save.set_values_box()
def start(root, dict_save):# запуск.
 data = dict_save.data  # файл настроек. print(data)
 if os.path.exists(data):  # есть ли этот файл.
   with open(data) as json_file:# загрузка настроек из файла.
    res = json.load(json_file)
 else:  # Если нет файла создать настройки.
    res ={ 'games_checkmark': {'C:/Windows/explorer.exe': True},
   'paths': {'C:/Windows/explorer.exe': 'По умолчанию'        },
   'key_value': {'C:/Windows/explorer.exe': ['LBUTTON', 'RBUTTON', 'WHEEL_MOUSE_BUTTON', 'SCROLL_UP',
                 'SCROLL_DOWN', 'SCROLL_UP', 'SCROLL_DOWN']   },
   "mouse_press": {  "C:/Windows/explorer.exe": [ False, False,
     False, False, False, False, False ] },
   "start_startup" : False,# Флаг запускать при старте.
   "id": 0, # Какой id устройства
   "current_app" : 'C:/Windows/explorer.exe'}

    know_id = f'''#!/bin/bash
     input_list=$(xinput list)  # Получаем список устройств ввода
     # Исключаем линию с 'Consumer Control' и выбираем первую подходящую строку
     mouse_line=$(echo "$input_list" | head -n 1)
  
     if [ -n "$mouse_line" ]; then  # Если строка найдена, извлекаем ID
          mouse_id=$(echo "$mouse_line" | grep -o "id=[0-9]*" | cut -d "=" -f 2)
          echo "$mouse_id"
     fi
     '''  # Запускаем скрипт нахождения id мыши.
    res["id"] = int(subprocess.run(['bash', '-c', know_id], capture_output=True, text=True).stdout.strip())# print(type(res["id"])) print(res["id"])

 d = list(res["paths"].keys()) # получить словарь путей и имен файлов.
 start_startup.set(res["start_startup"]) # print(res['id']) # input()
 dict_save.save_old_data(res) # сохранить значения настроек из файла.
 dict_save.set_cur_app(res["current_app"])  # установить текущую активную строку.

 dict_save.set_prev_game(res["current_app"])
 dict_save.set_current_app_path(res['current_app'])# установит текущий путь к игре.
 box_values = dict_save.return_box_values()  # получить список значения боксов.
 curr_name=dict_save.get_cur_app() # получить значение текущей активной строки.
 key_values = res["key_value"] # получить значения настроек для каждой кнопки мыши.

 box_values.clear()# Очистить значения кнопок.
 id_value.set(res["id"])# Установить id устройства в списке.
 dict_save.set_id(res["id"]) #сохранить текущий id устройства
 for i in range(len(LIST_MOUSE_BUTTONS)):  # создания выпадающих списков.
  y1 = (i + 1) * 30 + 1
  box_value = StringVar()
  Label(root, background="#ededed", text=LIST_MOUSE_BUTTONS[i]).place(x=250, y=y1 - 2)
  box = Combobox(root, width=12, textvariable=box_value, values=LIST_KEYS, state='readonly') #
  box.place(x=380, y=y1)
  box_values.append(box_value)
  box.bind('<<ComboboxSelected>>', update_buttons)# Если изменяется значения кнопок

 filling_in_fields(res) # заполнения всех полей.
 mouse_check_button(dict_save, res, curr_name) # флаг для удержания кнопки мыши.

 create_scrypt_buttons()# создание углубление кнопок скрипта.
 # print("fill")
def move_last_key_to_front(d):
   """
   Рекурсивно перемещает последний ключ словаря в начало.
   Если значение является словарём, функция применяется и к нему.
   """
   # Если d не словарь – возвращаем как есть
   if not isinstance(d, dict):
     return d

   keys = list(d.keys())
   if not keys:
     return d

   # Сначала обрабатываем последний ключ
   new_d = {keys[-1]: move_last_key_to_front(d[keys[-1]])}
   # Затем остальные ключи в исходном порядке
   for key in keys[:-1]:
     new_d[key] = move_last_key_to_front(d[key])
   return new_d

def scrolling_list(event):# прокрутка списка игр.
 a =[]
 labels=dict_save.return_labels()
 for i in range(len(labels)):
   info = labels[i].place_info()
   a.append(int(info["y"]))

 var_list = dict_save.return_var_list()
 a = a[1:] + a[:1]  # Перемещаем первый элемент в конец
 for i in range(len(labels)):
   labels[i].place(x=labels[i].winfo_x(), y=a[i])  # Используем winfo_x для получения текущей координаты x
   cb = Checkbutton(root, variable=var_list[i],  # создания галочек
                     onvalue=1, offvalue=0, state=ACTIVE)
   cb.place(x=7, y=a[i] - 2)

 res=dict_save.return_jnson()

 res = move_last_key_to_front(res)
 #print(res["games_checkmark"])
 dict_save.save_jnson(res)

def on_close():# Функция закрытия программы.  # print("exit")
  dict_save.set_default_id_value(add_button_start)
  old_data = dict_save.return_old_data()  # старые значения настроек.
  new_data = dict_save.return_jnson()  # новые значения настроек.
  # print(new_data["key_value"]["C:/Windows/explorer.exe"])
  #print(new_data["games_checkmark"])
  if new_data != old_data or list(old_data["games_checkmark"].keys())[0] != list(new_data["games_checkmark"].keys())[0]:# Если ли какие-то изменения
   if (messagebox.askokcancel("Quit", "Do you want to save the changes?")):
        dict_save.write_to_file(new_data)  # записать настройки в файл.
  dict_save.reset_id_value()
  root.destroy()
  exit()
  sys.exit()

def delete(dict_save, root):# Удалить профиль.
 if dict_save.get_cur_app()=="C:/Windows/explorer.exe":# # получить id устройства.Если id устройство не выбрали.
     messagebox.showinfo("Ошибка", "Вы выбрали профиль по умолчанию")
     ok_button = Button(root, text="Ок")
     return
 else:
   profile = dict_save.get_cur_app()# Текущая директория активной игры.
   res = dict_save.return_jnson()   # print(profile)
   list_paths=list(res["paths"].keys())
   del_index=(list_paths.index(profile))
   labels = dict_save.return_labels()
   var_list = dict_save.return_var_list()
   for i in range(len(labels)):
     if i == del_index: # индекс какой нужно удалить
      info = labels[i].place_info()
      info2= checkbutton_list[i].place_info()
      old_y = int(info["y"])

      old_y2 = int(info2["y"])
     if i > del_index:# индекс больше удалённого
       info = labels[i].place_info()
       new_y = int(info["y"])
       labels[i].place(x=labels[i].winfo_x(), y=old_y)
       old_y=new_y

       info2 = checkbutton_list[i].place_info()
       new_y2 = int(info2["y"])
       checkbutton_list[i].place(x=checkbutton_list[i].winfo_x(), y=old_y2)
       old_y2 = new_y2

   labels.pop()
   checkbutton_list.pop()
   remove_profile_keys(res, profile)
   del_index= del_index-1
   dict_save.save_jnson(res)  # Сохранить новые настройки.
   check_label_changed(0, labels, del_index, var_list)  # изменение цвета label
   #current_app
   # print(dict_save.return_jnson())

def reorder_keys_in_dict(res, index, direction='up'):
  lst = list(res["paths"].keys())
  if direction == 'up' and 0 < index < len(lst):
    lst[index], lst[index - 1] = lst[index - 1], lst[index]
  elif direction == 'down' and 0 <= index < len(lst) - 1:
    lst[index], lst[index + 1] = lst[index + 1], lst[index]
  else:
    return res
  updated_paths = {key: res["paths"][key] for key in lst}
  res["paths"] = updated_paths
  return res
def move_element(dict_save, root, direction='up'):
  """
  Перемещает текущий элемент (определяемый dict_save.get_cur_app())
  вверх или вниз в списке, меняя положение виджетов и порядок ключей в JSON.

  :param dict_save: Объект для работы с настройками (с методами get_cur_app, return_jnson, return_labels, set_cur_app, save_jnson)
  :param root: Корневой виджет Tkinter (используется, если требуется)
  :param direction: 'up' для перемещения вверх, 'down' для перемещения вниз
  """
  # Получаем текущий профиль и конфигурацию
  res = dict_save.return_jnson()
  profile = dict_save.get_cur_app()  # Текущая директория/приложение
  list_paths = list(res["paths"].keys())

  try:
    index = list_paths.index(profile)
  except ValueError:
    # Если профиль не найден, выходим
    return
  labels = dict_save.return_labels()

  # Проверяем границы для перемещения
  if direction == 'up':
    if index == 0:
      return  # Нельзя двигать вверх первый элемент
    new_index = index - 1
  elif direction == 'down':
    if index == len(labels) - 1:
      return  # Нельзя двигать вниз последний элемент
    new_index = index + 1
  else:
    raise ValueError("direction должен быть 'up' или 'down'")
  # Получаем текущие позиции элементов (предполагается, что используется .place())
  info_current = labels[index].place_info()
  info_neighbor = labels[new_index].place_info()
  y_current = int(info_current.get("y", 0))
  y_neighbor = int(info_neighbor.get("y", 0))
  # Меняем местами y-координаты для labels
  labels[index].place(x=labels[index].winfo_x(), y=y_neighbor)
  labels[new_index].place(x=labels[new_index].winfo_x(), y=y_current)

  # Меняем порядок элементов в списке labels
  element = labels.pop(index)
  labels.insert(new_index, element)


  info_current = checkbutton_list[index].place_info()
  info_neighbor = checkbutton_list[new_index].place_info()
  y_current = int(info_current.get("y", 0))
  y_neighbor = int(info_neighbor.get("y", 0))
  # Меняем местами y-координаты для labels
  checkbutton_list[index].place(x=checkbutton_list[index].winfo_x(), y=y_neighbor)
  checkbutton_list[new_index].place(x=checkbutton_list[new_index].winfo_x(), y=y_current)

  # Меняем порядок элементов в списке labels
  element = checkbutton_list.pop(index)
  checkbutton_list.insert(new_index, element)
  res =reorder_keys_in_dict(res, index, direction)  # Меняем порядок в списке
  # Обновляем текущий профиль в соответствии с новым порядком

  list_paths = list(res["paths"].keys())
  dict_save.set_cur_app(list_paths[new_index])
  # Обновляем цвета: сначала сбрасываем, затем выделяем перемещённый элемент
  set_colol_white_label_changed(labels)
  labels[new_index].config(background="#06c")
  dict_save.save_jnson(res)



dict_save=save_dict()
root = Tk()
id_value =  IntVar()
start_startup = BooleanVar()# запускать при старте.
f1 = Frame()
root.title("Mouse setting control for buttons python")  # заголовок
root.geometry("940x346+440+280")  # Первые 2 определяют ширину высоту. Пос 2 x и y координаты на экране.
root.configure(bg='DimGray')  # Цвет фона окна
root.resizable(width=False, height=False)
f1.grid(column=0, row=0, padx=10, pady=10)
container = Frame(root)
canvas = Canvas(container,width=700, height=480)
canvas.create_window((0, 0), window=f1, anchor="n")
container.grid()
canvas.grid(sticky=N+W)
scrollbar = Scrollbar(container, orient="vertical", command=canvas.yview)
scrollable_frame = Frame(canvas)
scrollable_frame.bind( "<Configure>",  lambda e: canvas.configure( scrollregion=canvas.bbox("all")    ))
canvas.configure(yscrollcommand=scrollbar.set)
scrollbar.grid(column=0, row=0,sticky=N+S+E)# полоса прокрутки.
scrollbar.bind("<ButtonRelease-1>", lambda event : scrolling_list(event))
add_button_add = Button(text=" Добавить", command= lambda:add_file(dict_save)).grid(column=1, row=0, padx=25, pady=5,sticky=N)
add_button_start = Button(text=" Пуск",  command= lambda:start1(dict_save, root))
add_button_start.place(x=780, y=300)
up_button = Button(text=" Вверх",  command= lambda:move_element(dict_save, root, 'up'))
up_button.place(x=520, y=250)
down_button = Button(text=" Вниз",  command= lambda:move_element(dict_save, root, 'down'))
down_button.place(x=520, y=300)
dict_save.set_add_button_start(add_button_start)
id_list =dict_save.get_list_ids()
start(root, dict_save)
add_button_start = Button(text=" Удалить",  command= lambda:delete(dict_save, root))
add_button_start.place(x=760, y=140)
r1 = Checkbutton(variable=start_startup) # Галочка запускать при старте.
r1.bind("<Button-1>", update_check_button)
CreateToolTip(r1, text='Запускать при открытий')  # вывод надписи
r1.place(x=720, y=105)
root.protocol("WM_DELETE_WINDOW", on_close)

process= threading.Thread(target=get_process, args=(dict_save, root,))
process.start()
Button(root, text="Показать список устройств", command=show_list_id_callback).place(x=710, y=220)

# win = keyboard_scrypt(root, " ")
if os.getgid() != 0:# if os.getgid() == 0:# start1() с root правами"
 box = Combobox(root, width=12, textvariable=id_value, values=id_list, state='readonly')  #
 box.grid(column=1, row=0, padx=10, pady=60,sticky=N)
 box.bind('<<ComboboxSelected>>', update_buttons)# Если изменяется значения id.
 CreateToolTip(box, text='Выбор id устройства')  # вывод надписи
 if start_startup.get()==True:# Если галочка стоит запускать
  root.iconify()  # Свернуть окно
  # root.withdraw()# свернуть панель подсказок.
  t2 =  threading.Thread(target=start1, args=(dict_save, root, ))
  t2.start()
else:
 show_message()# Создание кнопки "Ок"
 ok_button = Button(root, text="Ок", command=on_close())
root.mainloop()

# Get the ID of the main window
main_window_id = root.winfo_id()


