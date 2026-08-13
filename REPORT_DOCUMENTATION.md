# Отчёт по проекту `Pytq6_mouse_setting_control_for_buttons_for_linux`

> Полное описание архитектуры, принципа работы, всех переменных, функций и классов.
> Цель документа — дать исчерпывающее понимание кода, чтобы в будущем можно было
> продолжать работу, опираясь на этот отчёт как на «карту».

---

## 0. Общая архитектура и назначение

Программа — это аналог **X-Mouse Button Control** для Linux. Она позволяет
назначить на каждую из 7 кнопок мыши (левая, правая, средняя, колесо вверх,
колесо вниз, 1-я боковая, 2-я боковая) действие: клавишу клавиатуры, другую
кнопку мыши, прокрутку, либо произвольный bash-скрипт (макрос). Настройки
хранятся **на профиль** — по одному на каждую запущенную игру/приложение
(путь к `.exe`). Программа сама определяет активное окно и переключает профиль.

### Два файла

| Файл | Роль |
|------|------|
| `Pytq6_mouse_setting_control_for_buttons_for_linux.py` | Точка входа (`__main__`), класс главного окна `MouseSettingApp(QMainWindow, MouseSettingAppMethods)`, сборка GUI, обработчик нажатий физической клавиатуры (через evdev). |
| `Pyqt6_libs_mouse.py` | «Библиотека»: все словари/константы, класс `save_dict`, класс `work_key`, класс `Job`, класс `KeyboardWidget`, класс `MouseSettingAppMethods` (вся логика эмуляции + UI-методы), утилиты, функция `mouse_key`, `func_mouse_press_button` и т.д. |

Главный файл делает `from Pyqt6_libs_mouse import *`, поэтому все имена из
библиотеки доступны напрямую.

### Три уровня перехвата/эмуляции

1. **xinput `set-button-map`** — физические кнопки мыши, которые нужно
   «перехватить» (боковые, колесо), переназначаются на виртуальные номера
   `11..16`, чтобы pynput видел их под именами `Button.button11..button16`
   (отдельными от стандартных 1/2/3). Это делается в `prepare()`.
2. **pynput `mouse.Listener(on_click=...)`** — слушает реальные клики и вызывает
   `func_mouse_press_button` в отдельном потоке на каждый клик.
3. **Эмуляция** — через внешние утилиты:
   - `xdotool click N` (номера кнопок X11: 1=левая, 2=средняя, 3=правая, 4=колесо вверх, 5=вниз) — см. `work_key.mouse_right_donw` и т.п.;
   - `xte "keydown/keyup ..."` — для клавиатуры и макросов;
   - `pyautogui` — для средней кнопки (`mouse_middle_donw`);
   - `pynput.mouse.Controller` — для режима «удержание» (`mouse_key`, залипание).

### Потоковая модель

- Главный поток — Qt GUI.
- `prepare()` запускает `emunator_mouse` в потоке `t1`.
- `emunator_mouse` запускает `mouse.Listener` и крутит цикл проверки активного
  окна. При смене профиля он останавливает listener, join-ит рабочие потоки и
  рестартует `start_startup_now` (→ `prepare`) в новом потоке.
- Каждый клик → новый `threading.Thread(target=func_mouse_press_button, ...)`
  (добавляется в глобальный `list_threads`).
- Прокрутка (scroll) крутится в постоянном потоке `Job`, который
  старт-паузится методами `resume()/pause()`.

---

## 1. Структура JSON (`settings control mouse buttons.json`)

Файл `dict_save.data` (см. `save_dict.__init__`, поле `self.data`).
Загружается в `dict_save.jnson` (через `save_jnson`), копия исходника —
в `dict_save.old_data`.

| Ключ | Тип | Назначение |
|------|-----|------------|
| `games_checkmark` | `dict[str, bool]` | Путь к `.exe` → стоит ли галочка (участвует ли игра в перехвате). Только отмеченные попадают в `games_checkmark_paths`. |
| `paths` | `dict[str, str]` | Путь к `.exe` → отображаемое имя профиля (человекочитаемое). Порядок ключей = порядок в списке слева. |
| `key_value` | `dict[str, list[7]]` | Путь к `.exe` → список из 7 назначений (по одному на каждую кнопку). Значения берутся из `LIST_KEYS` (имена из `KEYS`). `" "` = «ничего не назначено». |
| `mouse_press` | `dict[str, list[7] bool]` | Путь к `.exe` → флаги «удерживать нажатой» для каждой из 7 кнопок (галочка «Держать нажатой»). |
| `id` | `int` | ID устройства мыши (из `xinput`), выбранный в выпадающем списке. По умолчанию `6` (из файла). |
| `current_app` | `str` | Путь к `.exe` текущего активного профиля. По умолчанию `"C:/Windows/explorer.exe"` (профиль «По умолчанию»). |
| `script_mouse` | `dict[str, dict[str, str]]` | Путь к `.exe` → {имя кнопки мыши (`LBUTTON`/`RBUTTON`/…/`XBUTTON1`/`XBUTTON2`) → bash-скрипт макроса}. Имеет приоритет над обычным назначением. |
| `keyboard_script` | `dict[str, dict["keys": dict[str,str]]]` | Путь к `.exe` → `{"keys": {имя клавиши: bash-скрипт}}`. Макросы клавиатуры, обрабатываемые в `on_press` (evdev) главного файла. |

### Индексы 7 кнопок (параллельны во всех списках)

```
0  Левая кнопка        -> LBUTTON
1  Правая кнопка       -> RBUTTON
2  Средняя             -> WHEEL_MOUSE_BUTTON
3  Колесико вверх      -> SCROLL_UP
4  Колесико вниз       -> SCROLL_DOWN
5  1 боковая           -> XBUTTON1
6  2 боковая           -> XBUTTON2
```

Это совпадает с `LIST_MOUSE_BUTTONS` и `defaut_list_mouse_buttons`
(Pyqt6_libs_mouse.py:63, :65).

### Пример записи `key_value` (Far Cry, строки 54-62)

```json
["LBUTTON","W"," ","F","Q","RBUTTON","SCROLL_DOWN"]
```

Значит: левая → ЛКМ (как есть), правая → клавиша `W`, средняя → ничего,
колесо вверх → `F`, колесо вниз → `Q`, 1-я боковая → `RBUTTON` (правая
кнопка мыши), 2-я боковая → прокрутка вниз.

---

## 2. Импорты и глобальные константы (`Pyqt6_libs_mouse.py`)

### Импорты (строки 1-11)
- стандартные: `sys, os, json, threading, subprocess, psutil, signal, time, copy, re`
- `pyautogui` — эмуляция средней кнопки;
- `deepdiff` — сравнение old/new JSON при выходе (`closeEvent`);
- `keyboard as keybord_from` — прямая отправка keydown/keyup (в `key_press`/`key_release`);
- PyQt6 виджеты/ядро/гуи;
- `pynput.mouse` (Controller + Button), `pynput.keyboard` (Key, Listener);
- `evdev` (InputDevice, categorize, ecodes, list_devices) — чтение физической клавиатуры.

### `en_to_ru` / `ru_to_en` (строки 14-23)
Словари транслитерации раскладки. Игры под Wine присылают английские имена
клавиш, а пользователь может назначать русские — эти словари приводят
русскую букву к английской (см. `on_press` в главном файле, где
`if key in ru_to_en.keys(): key = ru_to_en[key]`).

### `KEYS` (строки 25-59)
Огромный словарь `имя_клавиши -> значение`. Значения бывают:
- виртуальные скан-коды (`0x1B` и т.п.);
- строки для xte (`"Tab"`, `"Return"`, `"Home"`);
- для кнопок мыши — строки `'mouse left'`/`'mouse right'` (в `key_press`
  они попадают в `keybord_from.press('mouse left')`, но на практике кнопки
  мыши обрабатываются `mouse_key`, а не `keyboard_press_button`, поэтому этот
  путь для них не используется).
`LIST_KEYS = list(KEYS.keys())` — именно эти имена отображаются в выпадающих
списках combobox.

### `simple_key_map` (строки 61-62)
`evdev`-код numbpad-клавиши (`KEY_KP7` и т.д.) → строка отображения
(`' 7\nHome'`). Используется в `on_press` главного файла для распознавания
numpad.

### `keypad_map` / `mouse_map` (строки 1093-1098)
- `keypad_map`: строка отображения → имя для xte (`KP_Home` и т.д.).
- `mouse_map`: русское имя мышино-го действия → пара `("mousedown N","mouseup N")`
  для xte (1=левая, 2=средняя, 3=правая, 4=колесо вверх, 5=вниз).

### `LIST_MOUSE_BUTTONS` (строка 63)
7 русских подписей кнопок для GUI (строки 150 главного файла).

### `defaut_list_mouse_buttons` (строка 65)
`['LBUTTON','RBUTTON','WHEEL_MOUSE_BUTTON','SCROLL_UP','SCROLL_DOWN','XBUTTON1','XBUTTON2']`
— эталонные имена 7 слотов. Используется как ключ в `script_mouse`
(`check_mouse_script`, `func_mouse_press_button`) и для сравнения «это дефолт
или назначено что-то своё» (в `prepare`).

### Глобальные переменные (строки 67-74, 882)
- `get_user_name` — bash-скрипт получения имени пользователя.
- `user = subprocess.run(['bash'], input=get_user_name...)` — имя текущего
  пользователя (нужно для фильтрации процессов в `Get_pid_and_path_window`).
- `list_threads = []` — **глобальный** список потоков `func_mouse_press_button`;
  в `emunator_mouse` они join-ятся при смене профиля.
- `mouse_controller = mouse.Controller()` — pynput-контроллер для режима
  «удержание» (`mouse_key`).
- `sticking_right_mouse = False` — **глобальный** флаг переключателя залипания
  правой кнопки (используется только в `mouse_key`).
- `key_work = work_key()` — экземпляр класса эмуляции.
- `dict_save = save_dict()` — синглтон-хранилище настроек.

---

## 3. Класс `save_dict` (строки 76-298)

Хранилище всего состояния. Один экземпляр `dict_save` на всё приложение.

### Поля (`__init__`)
| Поле | Смысл |
|------|-------|
| `self.jnson` | Актуальные настройки (зеркало JSON). |
| `self.old_data` | Копия настроек на момент загрузки (для детекта изменений при выходе). |
| `self.name_games` | Список имён игр (из `paths`) для GUI. |
| `self.labels` | Список QLabel профилей (левый список GUI). |
| `self.var_list` | Список QCheckBox галочек профилей. |
| `self.labels_with_checkmark` | Словарь подписей с галочками (не используется активно). |
| `self.box_values` | Значения выпадающих списков (устаревшее, дублирует combo_box). |
| `self.cur_app` | Текущий профиль (путь `.exe`). Дублирует `jnson["current_app"]`. |
| `self.count` | Индекс текущего профиля в списке. |
| `self.id` | ID мыши (`jnson["id"]`). |
| `self.mouse_button_press` | Временный список флагов удержания. |
| `self.dict_id_values` | `{id: button_map_str}` — карта кнопок для всех мышей (из `get_list_ids`). |
| `self.data` | Имя файла настроек (`"settings control mouse buttons.json"`). |
| `self.path_current_app` | Путь текущего профиля. |
| `self.process_id_active` | PID активного окна. |
| `self.pid_and_path_window` | Словарь PID → путь. |
| `self.current_path_game` | Текущий путь к игре (для детекта смены). |
| `self.last_key_keyboard_script` | Последняя клавиша, для которой открывали редактор макроса. |
| `self.thr` | Ссылка на поток (устаревшее, дублирует `get_thread`/`set_thread`). |
| `self.thread_exit` | Флаг выхода из цикла эмуляции (`True` → остановить `emunator_mouse`). |
| `self.prev_game` | Предыдущий профиль (для возврата, если окно свёрнуто/нет игры). |

### Методы (геттеры/сеттеры)
- `get/set_last_key_keyboard_script` — запомнить клавишу редактора макроса.
- `get/set_thread` — ссылка на поток эмуляции (`self.thr`).
- `get/set_current_path_game` — текущий путь игры.
- `get/set_prev_game` — предыдущий профиль.
- `get/set_process_id_active`, `get/set_pid_and_path_window` — активное окно.
- `get/set_current_app_path` — путь профиля.
- `return_name_games / return_mouse_button_press / save_labels / return_labels /
  save_var_list / return_var_list / return_labels_with_checkmark /
  return_box_values` — доступ к спискам GUI.
- `return_list_mouse_button_press` — возвращает `jnson["mouse_press"][cur_app]`.
- `save_mouse_button_press(list_mouse_button_press, mouse_button_press)` —
  сохраняет флаги удержания в `jnson["mouse_press"][cur_app]`.
- `save_jnson(jn)` — записать `jnson`. `save_old_data(jnson)` — сохранить копию
  в `old_data` **и** в `jnson`.
- `return_jnson / return_old_data` — чтение.
- `set_cur_app(cur_app)` — ставит `cur_app` **и** `jnson["current_app"]`.
- `get_cur_app` — возвращает `str(jnson["current_app"])`.
- `set_count / get_count` — индекс профиля.
- `set_values_box / set_box_values / reset_id_value` — работа с GUI-полями и
  xinput (сброс карты кнопок к `1 2 3 4 5 6 7 8 9`).
- `write_to_file(new_data)` — сериализует JSON на диск + `chmod a+rw`.
- `get_list_ids()` — через `xinput` собирает `{id: button_map}` для всех мышей
  (исключая устройства без кнопок). Заполняет `self.dict_id_values`.
- `get_state_thread / set_default_id_value / reset_id_value / get_default_id_value`
  — управление xinput button-map (возврат к дефолту / сброс текущего id).
- `write_in_log(text)` — дозапись ошибок в `log.txt` + `chmod`.

---

## 4. Утилиты (вне классов)

### `is_path_in_list(path, path_list)` (351)
Возвращает `True`, если `path` — подстрока любого элемента `path_list`.
Используется для проверки, что путь активного окна входит в список профилей.

### `get_index_of_path(path, path_list)` (354)
Возвращает индекс первого элемента `path_list`, содержащего `path`.

### `get_process_info()` (358)
Через `psutil` перебирает процессы текущего `user`, ищет `.exe` в аргументах,
возвращает `{pid: path}`. (Вспомогательная, не основной путь детекта.)

### `replace_path_in_dict(d)` (374)
Преобразует Windows-пути (`C:/...`) в Linux `/mnt/...` по префиксу первого
найденного `/mnt/` пути, убирая дубли сегментов. Используется при миграции
настроек.

### `get_visible_active_pid()` (399)
Через `xdotool getactivewindow` → `wmctrl -lp` получает PID видимого (не
свёрнутого) активного окна. Возвращает `0`, если окно свёрнуто/не найдено.

### `is_window_minimized(window_id)` (429)
Проверяет `_NET_WM_STATE_HIDDEN` через `xprop`.

### `get_active_window_exe(user, id_active)` (437)
По PID активного окна (`ps aux`) возвращает путь к `.exe`. (Резервный путь.)

### `Get_pid_and_path_window()` (484) — **ключевая функция детекта**
Огромная функция. Делает:
1. Определяет `user` (через env / `pwd` / `whoami`).
2. `psutil.process_iter` — для каждого процесса пользователя определяет
   путь exe: для Wine — через `winepath -u`, cwd+имя, относительные пути,
   `find`; для обычных Linux — через `/proc/<pid>/exe` и cmdline.
3. Раскладывает словарь на родителей/потомков (`expanded`), чтобы один
   найденный путь покрывал весь процесс-лес игры.
4. Получает PID активного окна через `_BASH_GET_MAIN_ID` (xdotool + родитель).
5. Возвращает `(expanded, id_active)`.

Используется в `check_current_active_window`.

### `check_current_active_window(dict_save, games_checkmark_paths)` (714)
Вызывает `Get_pid_and_path_window()`, находит путь активного окна, и если он
входит в `games_checkmark_paths` (и это `.exe`) — возвращает соответствующий
профиль из `games_checkmark_paths`. Если игра не найдена / окно свёрнуто —
возвращает `dict_save.get_prev_game()` (держим предыдущий профиль).

### `show_list_id_callback()` (737)
Открывает `gnome-terminal` с `xinput list` (кнопка «Показать список
устройств»).

### `return_job(key, number)` (743)
Создаёт `Job(key[number])`, `start()`, сразу `pause()`, возвращает объект.
Используется в `get_keys_buttons` для прокрутки/боковых кнопок.

### `get_keys_buttons(key)` (749)
Вход: список `key` из 7 назначений. Для каждого слота, который **отличается
от дефолта**, создаёт `Job` и заносит в словарь `k` соответствие
`физический_номер_кнопки -> виртуальный_номер`:

| Слот | Условие | Job | `k[номер]=вирт` |
|------|---------|-----|------------------|
| 1 правая | `!= "RBUTTON"` | a1 | `k[3]='11'` |
| 2 средняя | `!= " "` и `!= "WHEEL_MOUSE_BUTTON"` | a2 | `k[2]='12'` |
| 3 колесо вверх | `!= "SCROLL_UP"` | a3 | `k[4]='13'` |
| 4 колесо вниз | `!= " "` и `!= "SCROLL_DOWN"` | a4 | `k[5]='14'` |
| 5 1-я боковая | `!= "XBUTTON1"` | a5 | `k[9]='16'` |
| 6 2-я боковая | `!= "XBUTTON2"` | a6 | `k[8]='15'` |

Возвращает `(a1..a6, k)`. Этот `k` потом используется в `prepare` для
`xinput set-button-map`, чтобы физическая кнопка перестала быть «своей» и
стала `Button.button<N>`.

### `add_text_pytq5(key, text_widget)` (1100)
Переводит имя клавиши в текст bash-скрипта (xte) и вставляет в `QTextEdit`
редактора макросов:
- если в `keypad_map` → xte-имя keypad;
- если в `mouse_map` → `mousedown/up`;
- иначе → `keydown/keyup` с `sleep 0.02`.
Возвращает сформированную строку.

### `check_mouse_script(res, dict_save, defaut_list_mouse_buttons, number_key)` (960)
Проверяет, назначен ли макрос мыши для кнопки `defaut_list_mouse_buttons[number_key]`
в `res["script_mouse"][cur_app]`. Возвращает `bool`.

### `execute_script(script)` (978)
`subprocess.call(['bash','-c',script])` — запуск макроса.

### `get_path_current_active(games_checkmark_paths)` (984)
Резервный детект активного окна через `xdotool`+`psutil`.

### `check_star()` (999)
Проверяет, не запущен ли уже второй экземпляр программы (по имени процесса).

### `return_file_path(dict_save)` (1013)
Открывает `zenite` выбор `.exe`, добавляет новый профиль во все словари
(`paths`, `games_checkmark`, `key_value`, `mouse_press`) со значениями
текущего профиля. Возвращает путь или `None`.

### `set_list_box(dict_save, index=0)` (1042)
Устанавливает `count` и обновляет значения combobox (`set_box_values`/
`set_values_box`).

### `reorder_keys_in_dict(res, idx1, idx2)` (1048)
Рекурсивно меняет порядок ключей в `res["paths"]` (и вложенных словарей) при
перемещении профиля вверх/вниз.

---

## 5. Класс `work_key` (строки 785-868)

Экземпляр `key_work`. Реализует фактическую отправку событий.

### Поля
- `self.keys_list` (787) — список простых клавиш (`q,w,e,...`) — отправляются
  через `xte` в отдельном потоке без ожидания.
- `self.keys_list1` (789) — спецклавиши (`BackSpace`, `Tab`, `Return`,
  стрелки, модификаторы, `F1..F12`, `space` и т.д.) — отправляются через
  `xte`, для scroll-слотов (3/4) с `join()` и последующим `keyup`.

### Методы
- `mouse_wheel_up()` (794) — `xdotool click 4`.
- `mouse_wheel_donw()` (799) — `xdotool click 5`.
- `mouse_right_donw()` (805) — `xdotool click 3` (правая кнопка).
- `mouse_middle_donw()` (812) — `pyautogui.click(button='middle')`.
- `key_press(key, number_key)` (818) — если клавиша в `keys_list`/`keys_list1`:
  для обычных (не 3/4) — `xte keydown` в демоне-потоке; для scroll-слотов
  (3/4) — `keydown`, `join`, затем `keyup` (отдельный поток). Иначе
  `keybord_from.press(KEYS[key[number_key]])` (прямая отправка).
- `key_release(key, number_key)` (848) — симметрично `keyup` через `xte` или
  `keybord_from.release`.
- `key_press_release(key, number_key)` (870) — **пустой** (заглушка).

---

## 6. Класс `Job` (строки 300-347)

Поток для непрерывной прокрутки. Наследует `threading.Thread`.

### Поля
- `self.key` — имя действия (`"SCROLL_UP"`/`"SCROLL_DOWN"`).
- `self.sw` — флаг переключения (для клавиатуры, не используется здесь
  активно).
- `self.hook_flag_mouse = True` — флаг «кнопка задействована» (проверяется в
  `func_mouse_press_button` через `get_hook_flag_mouse()`).
- `self.__flag` / `self.__running` — `threading.Event` для pause/resume/stop.

### `run()` (311)
Цикл пока `__running`. Каждые `0.08с`:
- если `SCROLL_UP` → поток `key_work.mouse_wheel_up()`, пауза `t=0.0115`;
- если `SCROLL_DOWN` → `key_work.mouse_wheel_donw()`, пауза `t`.
Так достигается «автоповтор» прокрутки пока кнопка удерживается.

### `pause()/resume()/stop()/set_sw()/get_sw()/set_hook_flag_mouse()/get_hook_flag_mouse()`
Управление состоянием потока и флагами.

---

## 7. Функция `mouse_key` (884) — **исправленный участок**

```python
def mouse_key(key, number_key, press_button, list_mouse_button_names, pres, a):
    global sticking_right_mouse
    try:
        if press_button[number_key] == False and (key[number_key] == "SCROLL_DOWN" or key[number_key] == "SCROLL_UP"):
            if pres == True:
                a.resume()          # начать прокрутку
            if pres == False:
                a.pause()           # остановить прокрутку
        if press_button[number_key] == False and key[number_key] != "SCROLL_DOWN" and key[number_key] != "SCROLL_UP":
            if pres == True:
                if str(key[number_key]) == 'RBUTTON':
                    key_work.mouse_right_donw()       # xdotool click 3
                if str(key[number_key]) == 'WHEEL_MOUSE_BUTTON':
                    key_work.mouse_middle_donw()      # pyautogui middle
        # Есть ли залипание
        if press_button[number_key] and key[number_key] != "SCROLL_DOWN" and key[number_key] != "SCROLL_UP":
            if pres == True:
                if str(key[number_key]) == 'RBUTTON':
                    if sticking_right_mouse == False:
                        sticking_right_mouse = True
                        mouse_controller.press(mouse.Button.right)   # удержание
                    else:
                        mouse_controller.release(mouse.Button.right)
                        sticking_right_mouse = False
    except Exception as e:
        pass
```

### Семантика после исправления (скобки расставлены верно)
- **Блок 1** (scroll, без удержания): нажатие → `a.resume()` (поток `Job`
  начинает крутить), отпускание → `a.pause()`.
- **Блок 2** (кнопка мыши, без удержания): нажатие → одиночный клик
  (`xdotool click 3` или `pyautogui` средняя). **Раньше сюда же попадал и
  блок 3 из-за ошибки приоритета `or`, что давало лишнее событие** — теперь
  блок 3 выполняется только при `press_button[number_key]==True`.
- **Блок 3** (режим «удержать», `mouse_press[game][number_key]==True`):
  переключает `sticking_right_mouse` — первое нажатие `press`, второе
  `release`. Глобальный флаг не даёт «залипнуть» дважды.

Параметры: `key` — список 7 назначений, `number_key` — индекс кнопки (1..6),
`press_button` — список флагов удержания, `list_mouse_button_names` — словарь
имён (`func_mouse_press_button` строит его локально), `pres` — `True`=нажата,
`a` — объект `Job` (для scroll).

---

## 8. `func_mouse_press_button` (1125) — диспетчер клика

```python
def func_mouse_press_button(dict_save, key, button, pres, list_buttons, press_button, string_keys):
```

1. Строит локальный `list_mouse_button_names` (имя → `Button_Controller.*`).
2. Берёт `res = dict_save.return_jnson()`.
3. Для каждого `i` в `string_keys` (имена вида `"Button.button11"`):
   - `a = list_buttons[i]` (объект `Job` или `0`);
   - `number_key = list_buttons[a]` (индекс 1..6);
   - условие срабатывания: `key[number_key] != ' '` **и** `str(i)==str(button)`
     **и** `list_buttons[i].get_hook_flag_mouse()==True`.
   - если на кнопку назначен макрос (`check_mouse_script`) → запуск скрипта в
     потоке;
   - иначе, если `key[number_key]` — имя кнопки мыши → `mouse_key(...)`;
   - иначе → `keyboard_press_button(...)`.
4. Любое исключение логируется в `log.txt` и глушится.

> Тонкость: для слотов, оставшихся в дефолте (`a=0`), обращение
> `0.get_hook_flag_mouse()` бросает `AttributeError`, который ловится
> `except` — то есть дефолтные кнопки просто пропускаются. Это «особенность»,
> а не ошибка потока.

---

## 9. `keyboard_press_button` (916)

Обрабатывает назначенные клавиши клавиатуры:
- без удержания (`press_button==False`): `pres==True` → `key_work.key_press`,
  `pres==False` → `key_work.key_release`;
- с удержанием (`press_button==True`): на каждое нажатие переключает
  `a.set_sw(True/False)` и делает `key_press`/`key_release` (toggle).

---

## 10. Класс `KeyboardWidget` (1156) — экранная клавиатура

Рисует QPushButton-клавиатуру (раскладка `keyboard_layout`, строки 1175-1182)
в виджете. `callback_func(key)` вызывается при клике по клавише и передаёт
имя в редактор макросов (`add_text_pytq5`). Используется окнами
`create_keyboard_with_editor` и `create_virtual_keyboard`.

---

## 11. Класс `MouseSettingAppMethods` (1281) — логика + UI

### Конструктор (1282)
Создаёт трей-иконку (`create_tray_icon`), планирует `self.hide()` через
`QTimer.singleShot(0,...)`.

### Методы редакторов макросов
- `create_keyboard_with_editor(key)` (1289) — окно «блокнот + клавиатура» для
  клавиши клавиатуры `key`. Грузит существующий скрипт из
  `keyboard_script[cur_app]["keys"][key]`. При закрытии → `kill_notebook`.
- `kill_notebook(event, window, section)` (1338) — сохраняет текст блокнота в
  JSON: для `"keyboard_script"` берёт ключ из `get_last_key_keyboard_script`,
  для мыши — `section` сам является именем кнопки (`XBUTTON2` и т.п.).
- `mouse_scrpt_keyboard_with_editor(i)` (1378) — то же, но для кнопки мыши
  `defaut_list_mouse_buttons[i]`. Пишет в `script_mouse[cur_app][button_name]`.
- `create_virtual_keyboard(dict_save, ...)` (1427) — окно выбора клавиш без
  блокнота, подсвечивает уже назначенные (`highlight_buttons_with_macros`).
- `highlight_buttons_with_macros` / `update_keyboard_display` — подсветка.

### Трей
- `create_tray_icon` (1491) — иконка `tmpovhwj8so.png`, меню «Выход».
- `tray_icon_clicked` (1507) / `show_normal` (1514) — показ/скрытие окна.
- `close_app` (1518) / `closeEvent` (1521) — при выходе сравнивает
  `old_data`/`jnson` через `deepdiff`; если есть изменения — предлагает
  сохранить (`write_to_file`), затем `os.kill(getpid(), SIGKILL)`.

### Движок эмуляции
- `emunator_mouse(dict_save, key, list_buttons, press_button, string_keys, games_checkmark_paths)` (1539):
  - `on_click(x,y,button,pres)` — на каждый клик шлёт
    `func_mouse_press_button` в новом потоке (`list_threads`), возвращает
    `True` (pynput продолжает слушать);
  - цикл `while not thread_exit`: опрашивает `check_current_active_window`,
    при смене профиля join-ит `list_threads`, `break`;
  - останавливает `mouse_listener`, рестартует `start_startup_now`.
- `prepare(dict_save, res, games_checkmark_paths)` (1578):
  - `id = res["id"]`; `old = get_default_id_value(id).split()` (дефолтный
    button-map, напр. `['1'..'9']`);
  - `a1..a6, k = get_keys_buttons(key)`;
  - `dict_save.reset_id_value()` — сброс карты текущего id к `1 2 3 ... 9`;
  - строит `list_buttons` (имя pynput ↔ Job ↔ индекс);
  - если `key != defaut_list_mouse_buttons` — переписывает `old[i] = k[old[i]]`
    (remap физических кнопок на виртуальные 11..16);
  - `xinput set-button-map {id} {new}` — **применяет перехват**;
  - `string_keys = [str-ключи list_buttons]`;
  - запускает `emunator_mouse` в потоке `t1`, сохраняет в `dict_save.set_thread`.
- `start_startup_now(dict_save)` (1607):
  - берёт `res`, ждёт завершения предыдущего потока (`t1.join()`);
  - если `res["id"]==0` — ошибка «Вы не выбрали устройство»;
  - `games_checkmark_paths = [пути с галочкой]`;
  - если `curr_name` в списке — `prepare(...)`, иначе ошибка.

### UI-методы профилей
- `check_label_changed(count)` (1635) — переключить активный профиль (синий
  цвет label), обновить checkbox-и удержания, подсветку скриптов, combobox-ы.
- `filling_in_fields(dict_save)` (1678) — перестроить левый список профилей
  (чекбоксы + подписи) из `paths`/`games_checkmark`.
- `change_app(game="")` (1718) — установить текущий профиль (с ожиданием
  синхронизации).
- `checkbutton_changed(count)` (1733) — переключить галочку профиля.
- `update_labels_bindings()` (1741) — перепривязать обработчики label/чекбоксов.
- `move_element(dict_save, direction)` (1753) — вверх/вниз: визуальный
  `QHBoxLayout` swap + `reorder_keys_in_dict` в JSON.
- `update_button(index)` (1808) — сохранить выбранное значение combobox в
  `key_value[game][index]`.
- `update_profile()` (1815) — смена ID мыши в выпадающем списке →
  `change_app()`.
- `change_name_label(count)` / `change(...)` — переименование профиля.
- `label_clicked(event, count)` (1863) — ЛКМ выбирает профиль, двойной клик →
  переименование.
- `check_mouse_press_button(count, state)` (1869) — сохранить флаг удержания в
  `mouse_press[cur_app][count]`.
- `add_file()` (1878) — добавить профиль (вызов `return_file_path` + перестрой
  UI).
- `delete()` (1928) — удалить профиль (`remove_profile_keys`), нельзя удалить
  дефолтный.

---

## 12. Главный файл `Pytq6_mouse_setting_control_for_buttons_for_linux.py`

### `class MouseSettingApp(QMainWindow, MouseSettingAppMethods)` (строка 2)
Наследует GUI-логику из библиотеки.

#### `__init__` (3)
1. Загрузка JSON: если файл есть — `save_old_data`+`save_jnson`; иначе создаёт
   дефолтный словарь (профиль `C:/Windows/explorer.exe` + пример
   `key_value`/`mouse_press`).
2. Через `evdev.list_devices()` ищет физическую клавиатуру (`self.board`).
3. Определяет `on_press(key)` — обработчик **клавиатуры**:
   - читает события из `self.board.read()` (evdev), при `key_down`
     нормализует имя (`simple_key_map`, `ru_to_en`);
   - если имя совпадает с ключом из `keyboard_script[cur_app]["keys"]` —
     останавливает listener, запускает скрипт в потоке (`subprocess.call`),
     `join`, перезапускает listener (`start_listener`).
4. `on_release` — пустой.
5. `start_listener()` — создаёт `keyboard.Listener(on_press, on_release)` и
   стартует.
6. `self.setup_ui()`.

#### `setup_ui()` (99)
Строит интерфейс:
- слева: `QScrollArea` со списком профилей (`filling_in_fields`);
- справа: 7 строк (label + `QComboBox` из `LIST_KEYS` + `QCheckBox` «Держать
  нажатой»); колонка кнопок скриптов мыши (`buttons_script`); кнопки
  «Добавить/Удалить/Вверх/Вниз/Клавиатура/Показать список устройств»; выпадающий
  список `id_combo` (ID мыши, только если не root).
- `QTimer.singleShot(0, self.start_app)`.

#### `start_app()` (244)
Ставит `id_combo`, заполняет combobox-ы текущими значениями, вызывает
`filling_in_fields` и `start_startup_now(dict_save)` — **запуск эмуляции**.

#### `__main__` (257)
Создаёт `QApplication`, кастомную палитру Fusion, показывает окно, `app.exec()`.

---

## 13. Полный поток данных при нажатии боковой кнопки

Пусть в профиле Far Cry `key[6] == "RBUTTON"` (2-я боковая → правая кнопка),
без удержания.

1. Старт: `prepare` → `get_keys_buttons` видит `key[6] != "XBUTTON2"` →
   `a6 = return_job(key,6)` (Job для scroll, но здесь не используется как
   scroll), `k[8]='15'`. `xinput set-button-map` переназначает физическую
   боковую (была, допустим, 7) на `15`. Теперь pynput видит её как
   `Button.button15`.
2. `emunator_mouse` → `mouse.Listener` активен.
3. Пользователь жмёт боковую → pynput `on_click(x,y,Button.button15,True)`.
4. `on_click` шлёт `func_mouse_press_button(..., button=Button.button15, pres=True, ...)`.
5. В цикле `for i in string_keys`: находится `i=="Button.button15"`,
   `a=list_buttons["Button.button15"]=a6`, `number_key=list_buttons[a6]=6`.
   Условие `key[6]=='RBUTTON' != ' '` и `str(i)==str(button)` и
   `a6.get_hook_flag_mouse()==True` → истина.
6. `check_mouse_script` для `defaut_list_mouse_buttons[6]=='XBUTTON2'` →
   `False` (макроса нет) ⇒ `key[6]=='RBUTTON'` в `list_mouse_button_names` ⇒
   `mouse_key(key, 6, press_button, ..., pres=True, a6)`.
7. В `mouse_key`: блок 1 (scroll) — `False` (RBUTTON не scroll). Блок 2
   (без удержания, не scroll) — `pres==True` и `RBUTTON` ⇒
   `key_work.mouse_right_donw()` ⇒ `xdotool click 3` — **один клик правой
   кнопкой**. Блок 3 (удержание) — `press_button[6]==False` ⇒ не выполняется.
8. Отпускание боковой → `on_click(..., pres=False)` → `mouse_key` блок 2
   `pres==False` ⇒ ничего; блок 3 не выполняется. Итог: ровно один клик.

> До исправления блок 3 срабатывал всегда (из-за `or key != "SCROLL_UP"`),
> делая лишнее `mouse_controller.press(Button.right)` — отсюда «правая
> нажимается несколько раз».

---

## 14. Известные особенности и «тёмные места»

1. **Глобальный `sticking_right_mouse`** не сбрасывается между профилями и не
   привязан к конкретной кнопке — если включить залипание правой на одной
   кнопке и не «отпустить», флаг останется `True`.
2. **Несколько `mouse.Listener`**: на каждую смену окна создаётся новый
   listener; старый останавливается асинхронно. При быстрой смене возможно
   кратковременное наложение слушателей → удвоение событий.
3. **`list_buttons[i].get_hook_flag_mouse()` для `a=0`** бросает
   `AttributeError`, который глушится `except` — дефолтные кнопки просто
   игнорируются диспетчером (это нормально, т.к. они не перехватываются
   xinput).
4. **`Get_pid_and_path_window` использует `pwd`** (строка 491), который не
   импортирован; ошибка не возникает, т.к. `USER`/`LOGNAME` обычно заданы
   (ленивое вычисление через `or`).
5. **`key_press` для имён мыши** (`LBUTTON`/`RBUTTON`) теоретически мог бы
   пойти в `keybord_from.press('mouse left')`, но на практике кнопки мыши
   перехватываются `mouse_key`, поэтому этот путь не задействован.
6. **`closeEvent` делает `os.kill(getpid(), SIGKILL)`** — жёсткое завершение,
   минуя нормальную очистку Qt.

---

## 15. Краткий словарь имён (чтобы «закинуть и понять»)

| Имя | Где | Что значит |
|-----|-----|-----------|
| `dict_save` | глобал | хранилище всех настроек (зеркало JSON) |
| `key` (в prepare/emunator) | параметр | список из 7 назначений текущего профиля |
| `number_key` | параметр | индекс 1..6 конкретной кнопки |
| `press_button` | параметр | список 7 bool «удерживать» |
| `list_buttons` | prepare | `{pynput_имя: Job, Job: индекс}` |
| `string_keys` | prepare | имена pynput-кнопок (строковые ключи `list_buttons`) |
| `a1..a6` | get_keys_buttons | объекты `Job` для scroll/боковых |
| `k` | get_keys_buttons | `{физ_номер: вирт_номер}` для xinput remap |
| `sticking_right_mouse` | глобал | флаг залипания правой кнопки |
| `mouse_controller` | глобал | pynput Controller для удержания |
| `key_work` | глобал | экземпляр `work_key` (эмуляция) |
| `list_threads` | глобал | рабочие потоки кликов (для join при смене профиля) |
| `on_click` | emunator_mouse | callback pynput на каждый клик |
| `func_mouse_press_button` | глобал | диспетчер: макрос / mouse_key / keyboard |
| `mouse_key` | глобал | логика клика мыши (scroll / клик / залипание) |
| `keyboard_press_button` | глобал | логика клавиши клавиатуры |
| `Job` | класс | поток автоповтора прокрутки |
| `games_checkmark_paths` | prepare/startup | список путей профилей с галочкой |
| `defaut_list_mouse_buttons` | глобал | эталон 7 имён слотов |
| `LIST_KEYS` | глобал | имена для combobox (ключи `KEYS`) |

---

## 16. Скрытые баги (анализ, без изменения кода)

> Ниже — логические ошибки, пропущенные условия и «тёмные места», найденные при
> доскональном разборе. Код НЕ менялся — это только диагностика для будущих
> правок. Имена переменных/функций/комментариев сохранены как есть.

### А. Утечка и недоочистка потоков кликов — `emunator_mouse` (строка 1554-1558)

```python
if dict_save.get_current_path_game() != dict_save.get_cur_app():
    for t in list_threads:
        t.join()
        list_threads.remove(t)
    break
```

Две проблемы сразу:
1. `break` стоит **после первой же итерации** → из `list_threads` удаляется и
   join-ится только **первый** поток, остальные остаются в списке навсегда.
2. Удаление элемента списка (`list_threads.remove(t)`) **во время итерации по
   этому же списку** (`for t in list_threads`) сдвигает индексы и пропускает
   элементы (плюс риск `RuntimeError`).

**Следствие:** при каждой смене активного окна рабочие потоки прошлого профиля
не очищаются, `list_threads` растёт, а старые `mouse.Listener` могут
пересекаться с новыми → удвоение/утроение событий (см. также раздел 14, п.2).
Правильно было бы скопировать список и полностью очистить его без `break`.

### Б. Режим «держать нажатой» не реализован для средней кнопки — `mouse_key` (строка 902-910)

Блок залипания проверяет только `str(key[number_key]) == 'RBUTTON'`:

```python
if press_button[number_key] and key[number_key] != "SCROLL_DOWN" and key[number_key] != "SCROLL_UP":
    if pres == True:
        if str(key[number_key]) == 'RBUTTON':   # <-- только RBUTTON
            ...
```

Если на среднюю кнопку (`WHEEL_MOUSE_BUTTON`) поставить галочку «держать», то
она **не сработает вообще**: блок 2 требует `press_button==False` (пропуск),
блок 3 заходит, но внутри `if 'RBUTTON'` ложно → нет `else` → ничего не
происходит. Средняя кнопка в режиме удержания «мёртвая».

### В. Режим «держать» полностью отключает прокрутку — `mouse_key` (блоки 1 и 3)

Прокрутка обрабатывается только в блоке 1, который требует
`press_button[number_key] == False`:

```python
if press_button[number_key] == False and (key[number_key] == "SCROLL_DOWN" or key[number_key] == "SCROLL_UP"):
```

Блок 3 (залипание) требует `key[number_key] != "SCROLL_DOWN" and key != "SCROLL_UP"`.
Итог: при `press_button==True` и `SCROLL_UP/DOWN` **оба блока ложны** →
прокрутка с галочкой «держать» не делает ничего. Назначение scroll + hold
бесполезно.

### Г. Сломанная защита от второго запуска — `check_star` (строка 999-1011)

```python
for process in process_list:          # process_list = ВСЕ процессы системы
    if 'Mouse_setting_control_for_buttons_python_for_linux' in process['name']:
        a.append(process)
        if len(process_list) > 1:     # <-- сравнивается длина ВСЕХ процессов
            return False
        else:
            return True
```

Сравнивается длина `process_list` (все процессы, всегда >> 1), а не `a`
(найденные экземпляры программы). Поэтому условие почти всегда истинно →
возвращает `False` → вторая копия программы не детектируется. Нужно
`if len(a) > 1: return False`.

### Д. Мёртвая ветка scroll-слотов в `work_key.key_press`/`key_release` (строки 830-844, 855-868)

Тот же баг приоритета, что и в `mouse_key` до исправления:

```python
if number_key != 3 or number_key != 4:        # всегда True
    thread0 ... keydown ... return 0
if number_key == 3 or 4:                       # никогда не выполняется
    ...
```

`(number_key != 3) or (number_key != 4)` истинно для любого `number_key`,
поэтому первая ветка всегда срабатывает и делает `return`, а ветка с `join`
для scroll-слотов (3/4) недостижима. Функционально клавиши работают (через
daemon-поток + `key_release`), но задуманная логика «для scroll — дождаться
keyup» не работает.

### Е. Нельзя «отключить» кнопку — `get_keys_buttons` + `prepare`

`xinput set-button-map` применяется **только** для слотов, отличающихся от
дефолта (`if key[1] == "RBUTTON": pass` и т.д.). Если пользователь ставит
`" "` (ничего не назначено) — remap не создаётся, физическая кнопка остаётся
«своей» (native), и нативное нажатие проходит насквозь. Ожидаемого «кнопка
ничего не делает» нет — кнопка продолжает работать как обычно.

### Ж. Аппаратно-зависимая инверсия 1-й/2-й боковых — `get_keys_buttons` + `prepare`

```python
key[5] (1 боковая): k[9] = '16'     # slot 5 -> physical 9
key[6] (2 боковая): k[8] = '15'     # slot 6 -> physical 8
...
list_buttons = {"Button.button16": a5, ..., "Button.button15": a6, ...}
```

После `xinput set-button-map` физическая кнопка 8 → логическая 15, 9 → 16.
pynput именует их `Button.button15`/`Button.button16`. В `list_buttons`
`Button.button16` привязан к `a5` (задание **1-й** боковой), а `Button.button15`
к `a6` (задание **2-й** боковой). То есть на мыши, где side-кнопки — физические
8 и 9, назначения **1-й и 2-й боковых меняются местами**. Кроме того, вся
логика remap жёстко предполагает нумерацию `2/3/4/5/8/9` (middle/right/wheel/
side), что верно только для конкретной мыши автора; на другой периферии
перехват боковых/колеса сломается.

### З. Ручной выбор профиля не перезапускает эмуляцию — `check_label_changed` (1635)

`check_label_changed` меняет `current_app`/`prev_game` и обновляет GUI, но
поток `emunator_mouse` продолжает следить за **активным окном**
(`check_current_active_window`), а не за ручным выбором. Поэтому клик по
профилю в списке меняет только отображение — реальная эмуляция переключится
только когда сменится активное окно. Это скорее особенность, но может
сбивать: пользователь выбрал профиль, а поведение мыши не изменилось.

### И. Гонки на общем состоянии — `dict_save.jnson`

`jnson` читается и пишется и из GUI-потока (обработчики чекбоксов/combobox),
и из потока эмуляции (restart). Блокировок (`Lock`) нет. Под GIL отдельные
присваивания атомарны, но составные изменения JSON (добавление профиля,
переименование) в теории могут быть прерваны чтением. Низкий риск, но стоит
учитывать при будущих правках.

### К. Глобальный флаг залипания не сбрасывается — `sticking_right_mouse`

`sticking_right_mouse` — глобальная переменная, не привязанная к кнопке/профилю.
Если включить удержание правой на одной кнопке и переключить профиль,
не «отпустив» (не нажав второй раз), флаг останется `True`, и следующая
правая кнопка/кнопка с RBUTTON сработает как «отпускание». Аналогично при
повторном назначении RBUTTON-hold на другую кнопку.

### Сводка приоритетов (для будущих правок)

| ID | Баг | Влияние | Локализация |
|----|-----|---------|-------------|
| А | утечка/недоочистка `list_threads` | множит события при смене окон | `emunator_mouse` :1554 |
| Б | hold не работает для средней | средняя+hold мертва | `mouse_key` :902 |
| В | hold отключает прокрутку | scroll+hold мертв | `mouse_key` :888/902 |
| Г | `check_star` сломан | нет защиты от дубля | `check_star` :1006 |
| Д | мёртвая ветка scroll-слотов | не как задумано | `work_key.key_press` :830 |
| Е | нельзя отключить кнопку | native проходит | `get_keys_buttons` |
| Ж | инверсия/зависимость side-кнопок | боковые могут меняться | `get_keys_buttons` :777-782 |
| З | ручной выбор не рестартит | UX-путаница | `check_label_changed` |
| И | гонки `jnson` | теоретич. | `save_dict` |
| К | глоб. `sticking_right_mouse` | залипание | `mouse_key` :882 |

---

*Конец отчёта.*
