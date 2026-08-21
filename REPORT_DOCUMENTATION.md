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
| `script_mouse` | `dict[str, dict[str, str]]` | Путь к `.exe` → {имя кнопки мыши (`LBUTTON`/`RBUTTON`/…/`XBUTTON1`/`XBUTTON2`) → bash-скрипт макроса как строка **с настоящими `\n`** (в файле — построчно, как в редакторе)}. Имеет приоритет над обычным назначением. См. §1.1. |
| `keyboard_script` | `dict[str, dict["keys": dict[str,str]]]` | Путь к `.exe` → `{"keys": {имя клавиши → bash-скрипт (строка с настоящими `\n`)}}`. Макросы клавиатуры, обрабатываемые evdev-слушателем (`keyboard_evdev_loop`/`handle_keyboard_macro`, Вариант B) главного файла. См. §1.1 и §15. |

> **Важно:** в памяти (рантайм) скрипты всегда хранятся как **одна строка** с `\n`
> (именно так их отдаёт `QTextEdit` и исполняет `subprocess`). «Человекочитаемые»
> реальные переносы строк появляются **только в файле на диске** (см. §1.1,
> функции `_format_scripts_in_json` / `scripts_to_text`). При `json.load(..., strict=False)`
> строка читается обратно как обычная строка.

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

### 1.1 Формат хранения bash-скриптов — исправление читаемости JSON

**Проблема.** Раньше макросы мыши/клавиатуры (`script_mouse`, `keyboard_script`)
хранились в JSON как одна строка с экранированными `\n`, например:

```json
"XBUTTON2": "#!/bin/bash\nxte \"keydown E\"\nsleep 0.02\nxte \"keyup E\"\nxte \"keydown R\"\nsleep 0.02\nxte \"keyup R\"\nxte \"keydown G\"\nsleep 0.02\nxte \"keyup G\"\n"
```

`json.dumps(..., indent=2)` обязан экранировать перевод строки как `\n`, поэтому
весь bash-скрипт превращался в одну длинную «убитую» строку. Читать и править
такой файл вручную практически невозможно, и визуально он выглядит как «башкод».

**Требование.** Скрипт в файле должен выглядеть так же, как в обычном текстовом
редакторе — с НАСТОЯЩИМИ переводами строк, построчно, без кавычек/запятых массива.

**Решение (принятое, итоговое).** `write_to_file` сериализует JSON штатным
`json.dumps(..., indent=2)`, а затем модульная функция `_format_scripts_in_json(text)`
находит в полученном тексте строковые значения, содержащие экранированный `\n`
(это и есть bash-скрипты), и заменяет `\\n` (два символа) на РЕАЛЬНЫЙ перевод
строки. Результат в файле выглядит ровно как в редакторе:

```json
"XBUTTON2": "#!/bin/bash
xte "keydown F"
sleep 0.23
xte "keyup F""
```

Экранированные кавычки `\"` и слэши `\\` внутри скрипта остаются как есть
(они корректны для JSON), меняется только представление `\n`.

**Важное о чтении (strict=False).** Реальный символ переноса строки внутри
JSON-строки формально недопустим (строгий `json.load(strict=True)` упал бы).
Поэтому единственный читатель — главный файл — грузит файл через
`json.load(json_file, strict=False)` (строка ~17), который разрешает
«сырые» переносы в строках. Других парсеров JSON у проекта нет, так что это
безопасно.

**Где реализовано.**
- `Pyqt6_libs_mouse.py` (библиотека):
  - модульная функция `_format_scripts_in_json(text)` — постобработка текста
    JSON: регулярка `"(?:[^"\\]|\\.)*"` находит строковые значения, содержащие
    `\\n`, и заменяет `\\n → \n` (реальный перенос). Замена выполняется через
    `re.sub(r'(?<!\\)\\n', ...)` — НЕГАТИВНЫЙ LOOKBEHIND: `\n` заменяется только
    если он НЕ предварён другим обратным слэшем. Это защищает от «висячего»
    слэша, когда внутри скрипта есть экранированный `\\` (см. §17.7/§17.8).
    Хвостовой `\n` (от завершающего переноса скрипта) отрезается, чтобы
    закрывающая `"` не уезжала на отдельную строку;
  - модульная функция `scripts_to_text(data)` — нормализация ПОСЛЕ чтения:
    убирает отступы продолжения строк у скриптов (защита от старых/ручных
    версий файла), чтобы строка в памяти была «чистой»;
  - метод `save_dict.write_to_file(new_data)` вызывает
    `json_string = _format_scripts_in_json(json.dumps(new_data, ensure_ascii=False, indent=2))`
    перед записью.
- `Pytq6_mouse_setting_control_for_buttons_for_linux.py` (точка входа):
  - `res = json.load(json_file, strict=False)` + `res = scripts_to_text(res)`
    сразу после загрузки (в `__init__` главного файла, строки 61-62).

**Почему рантайм не пострадал.** Редактор макроса (`kill_notebook`) по-прежнему
пишет в `res["script_mouse"][...]` / `res["keyboard_script"][...]["keys"][...]`
обычную строку из `QTextEdit`. `execute_script` и обработчик клавиатуры
(`handle_keyboard_macro`) получают обычную строку с `\n`. Преобразование в
«человекочитаемые» переносы происходит только при `write_to_file` (на диск); при
`json.load` строка читается обратно как обычная строка. Имена переменных,
функций и общая структура кода сохранены.

**Идемпотентность (повторная запись не портит файл).** Продолжения строк
выравниваются вертикально по первой строке скрипта (`#!/bin/bash`): отступ
равен колонке начала содержимого значения внутри строки. Чтобы повторное
сохранение не накапливало отступы, `scripts_to_text` при загрузке снимает
отступы продолжений (lstrip). Поэтому при повторном сохранении
(`load` → `scripts_to_text` → `dumps` → `_format_scripts_in_json`) файл
получается байт-в-байт идентичным. Проверено: `file == write_to_file(load(file))` → True.

**Трудности и нюансы реализации.**
1. *Нельзя менять тип значения в памяти* — иначе сломаются `execute_script`,
   `subprocess` и редактор. Поэтому преобразование делается только на границе
   «диск ↔ память» (постобработка текста при записи + нормализация при чтении),
   а не смена модели данных.
2. *Первая попытка (массив строк) отброшена.* Сначала скрипты раскладывались на
   JSON-массив строк (`["#!/bin/bash", "xte ...", ...]`). Это валидно, но
   выглядит «не как в редакторе» (каждая строка в кавычках + запятые + отступы),
   и пользователь это отверг. От него отказались в пользу реальных переносов.
3. *Отступы продолжения можно выравнивать, но нужно снимать при чтении.* По
   требованию пользователя продолжения выравниваются вертикально по первой строке
   (`#!/bin/bash`), т.е. отступ попадает ВНУТРЬ строки скрипта. Чтобы при
   следующем сохранении отступ не удваивался (неидемпотентность), `scripts_to_text`
   при загрузке снимает отступы продолжений, возвращая «чистую» строку. Так
   повторное сохранение даёт тот же результат.
4. *Хвостовой перенос.* Исходные скрипты заканчиваются на `\n`; при записи
   завершающий `\n` отрезается, чтобы закрывающая кавычка стояла сразу после
   последней команды. При исполнении bash это неважно.
5. *strict=False.* Чтобы «сырые» переносы читались, пришлось ослабить парсер
   при загрузке. Это единственное место, затронутое в главном файле.

**Итог.** Файл `settings control mouse buttons.json` теперь хранит макросы
построчно, как в обычном редакторе; структура кода, имена и логика рантайма
не изменены, повторное сохранение не ломает форматирование.

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
русскую букву к английской (см. `handle_keyboard_macro` в главном файле, где
`if k in ru_to_en.keys(): k = ru_to_en[k]`).

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
(`' 7\nHome'`). Используется в модульной функции `evdev_key_to_label` главного
файла для распознавания numpad (цифры/навигация). Примечание: `KEY_KPPLUS` и
`KEY_KPMINUS` НАМЕРЕННО НЕ берутся из `simple_key_map` — они остаются как
`'KEY_KPPLUS'`/`'KEY_KPMINUS'`, чтобы различать нумпад +/- и основную клавиатуру.

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
- `write_to_file(new_data)` — сериализует JSON на диск (`json.dumps(..., indent=2)`),
  прогоняет через `_format_scripts_in_json` (реальные переносы строк + вертикальное
  выравнивание bash-скриптов в `script_mouse`/`keyboard_script`) и делает `chmod a+rw`.
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
  С 2026-08-15 перед подсветкой выбранного label **сбрасывает ВСЕ label в белый**
  (как `set_colol_white_label_changed` в Tkinter-версии) — иначе после авто-смены
  профиля фоновым монитором старых синих label накапливалось несколько. §17.9.
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
3. Запускает evdev-слушатель клавиатуры через `self.start_keyboard_listener()`
   (Вариант B — evdev **единственный** источник событий; pynput-клавиатура
   больше не используется). Подробности в §15.
4. `self.setup_ui()`.

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

## 17. Переписанный слушатель клавиатуры (evdev, Вариант B)

### 17.1 Проблема (почему старый код не работал)

В исходнике обработка клавиатуры (`on_press`/`on_release`/`start_listener`)
строилась на **смеси** pynput и evdev:

1. **Падение при отсутствии устройства.** `on_press` вызывал
   `self.board.read()`, но `self.board` мог оказаться `None`, если
   `evdev.list_devices()` не нашёл устройство по шаблону
   `"Keyboard\"" in str(dev) and ' phys ' in str(dev)`. Перехватывался только
   `BlockingIOError`; `AttributeError` (`'NoneType' has no attribute 'read'`)
   пробрасывался и ломал слушатель — поэтому нажатия (в т.ч. `+`) не
   обрабатывались вообще.
2. **Нумпад и основная клавиатура не различались.** evdev отдаёт
   `KEY_KPPLUS`/`KEY_KPMINUS` для нумпада и `KEY_EQUAL`/`KEY_MINUS` для основной
   клавиатуры, но старый код сворачивал всё к символу `str(key)` от pynput
   (`'+'`/`'-'`), теряя различие.
3. **Узкий набор клавиш.** `simple_key_map` покрывал лишь 9 клавиш нумпада;
   всё остальное полагалось на pynput, который дублировал чтение того же
   физического устройства (`self.board`) → двойное слушание одного источника.

Пользователь выбрал **Вариант B**: сделать evdev единственным источником
событий клавиатуры (у него уже есть свой evdev-слушатель, и он отключает
цифры нумпада), не трогая GUI и не ломая обработку мыши (pynput-мышь
остаётся).

### 17.2 Что сделано

В главном файле (`Pytq6_mouse_setting_control_for_buttons_for_linux.py`):

- Удалены вложенные `on_press`/`on_release`/`start_listener` (pynput). Вместо
  них — три метода класса `MouseSettingApp` + одна модульная функция:
  - `start_keyboard_listener(self)` — останавливает предыдущий поток
    (`self.keyboard_thread_exit = True`, `join(timeout=1)`) и запускает новый
    демон-поток `keyboard_evdev_loop`. Вызывается из `__init__`.
  - `keyboard_evdev_loop(self)` — цикл чтения `self.board.read()`:
    - `BlockingIOError` → `time.sleep(0.01)` (буфер пуст, не блокируем GUI);
    - любой другой `Exception` → `time.sleep(0.05)` (защита от падения
      потока);
    - для `EV_KEY` с `keystate == key_down` берёт `ke.keycode`
      (кортеж сворачивается к первому элементу), отслеживает `pressed`
      (защита от автоповтора — `key_hold`), нормализует через
      `evdev_key_to_label` и вызывает `handle_keyboard_macro`.
  - `handle_keyboard_macro(self, key_label)` — та же логика сопоставления, что
    была в `on_press`: берёт `dict_save.get_cur_app()`, ищет ключ в
    `keyboard_script[cur_app]["keys"]`, при совпадении (с учётом `ru_to_en` и
    приведения `'Caps Lock'→'caps_lock'` через `replace(" ", "_")`) запускает
    скрипт в потоке `subprocess.call(["bash","-c", script])` + `join`.
    **Без остановки/рестарта слушателя** (цикл непрерывный → повторные
    нажатия не теряются).
  - модульная `evdev_key_to_label(code)` — преобразует evdev-имя в метку,
    под которой макрос лежит в JSON:
    - `KEY_EQUAL`→`'+'`, `KEY_MINUS`→`'-'`;
    - `KEY_KPPLUS`→`'KEY_KPPLUS'`, `KEY_KPMINUS`→`'KEY_KPMINUS'` (**намеренно
      с префиксом**, чтобы нумпад +/- НЕ совпадали с основными +/-);
    - `KEY_KP7`→`' 7\nHome'` и т.п. через `simple_key_map` (numpad-цифры/
      навигация работают как раньше);
    - буквы→строчные, цифры→как есть, `F1`→`'f1'`, спец-клавиши
      (`SPACE`→`'space'`, `LEFTCTRL`→`'control_l'`, `CAPSLOCK`→`'caps_lock'`
      и т.д.).

### 17.3 Проверки и трудности

- **`py_compile`** обоих файлов — OK. Также проверено реальным импортом
  модуля под виртуальным окружением проекта (`myvenv`) и запуском приложения
  под `DISPLAY=:0`: окно стартует, слушатель evdev запускается, никаких
  `AttributeError`/`Traceback` при старте (процесс живёт в цикле событий до
  принудительного завершения по таймауту).
- **Отступы (вАРИАНТ B, финальная шлифовка).** Класс `MouseSettingApp`
  использует **1-пробельный** отступ для методов. При вставке новых методов
  они оказались на 2 пробелах → Python трактовал их как **вложенные функции
  внутри `__init__`** (а `setup_ui`/`start_app` — как вложенные в
  `handle_keyboard_macro`), отсюда `AttributeError: ... has no attribute
  'start_keyboard_listener'` / `'setup_ui'`. Исправлено переотступом блоков
  до 1 пробела для `def` и 2 для тела (проверено через `ast`: теперь
  `['__init__', 'start_keyboard_listener', 'keyboard_evdev_loop',
  'handle_keyboard_macro', 'setup_ui', 'start_app']`, вложенных функций нет).
- **`BlockingIOError` при итерации.** В новом evdev `board.read()` возвращает
  ленивый объект, и `BlockingIOError (Errno 11)` поднимается **во время
  `for event in events:`**, а не на самом `read()`. Старый `try` ловил только
  `read()`, поэтому поток падал с трейсбеком. Исправлено: чтение **и** цикл
  перебора перенесены внутрь одного `try`, так что `BlockingIOError` ловится и
  поток не падает (спит 0.01 с и продолжает).
- **Карта клавиш** проверена отдельным тестом (функция скопирована и
  прогнана на `KEY_EQUAL`, `KEY_KPPLUS`, `KEY_MINUS`, `KEY_KPMINUS`, `KEY_A`,
  `KEY_F1`, `KEY_SPACE`, `KEY_KP7`, `KEY_KP0`, `KEY_LEFTCTRL`, `KEY_CAPSLOCK`):
  все совпали, нумпад +/- чётко отличаются от основных.
- **`self.board is None`** → `keyboard_evdev_loop` печатает предупреждение и
  завершается (макросы клавиатуры отключаются, но GUI/мышь не падают). Это
  безопаснее старого поведения (раньше падал `AttributeError`).
- **Не тронуты**: GUI (`setup_ui` и весь `MouseSettingAppMethods`), обработка
  мыши (pynput `mouse.Listener`), структура/имена функций. Импорт по-прежнему
  `from Pyqt6_libs_mouse import *` (pynput остаётся в библиотеке для мыши).

### 17.4 Нумпад `+`/`-` как отдельные клавиши (доработка по запросу)

Пользователь подтвердил: нумпад `+`/`-` должны быть **самостоятельными**
клавишами, отличными от основных `+`/`-`. Поэтому физический нумпад `+`
(`KEY_KPPLUS`) и `-` (`KEY_KPMINUS`) НЕ должны совпадать с основным `+`/`-`.
Проблема: в on-screen клавиатуре кнопка нумпада `+` хранила ключ `'+'` (тот же,
что основная), поэтому привязать макрос к нумпаду отдельно было нельзя.

Изменения:
- `evdev_key_to_label` (главный файл) оставляет `KEY_KPPLUS`→`'KEY_KPPLUS'`,
  `KEY_KPMINUS`→`'KEY_KPMINUS'` (уже было в §17.2) — эти метки и есть ключи
  привязки.
- `KeyboardWidget.create_keyboard_layout` (`Pyqt6_libs_mouse.py`): для кнопки
  нумпада `+` (row 2, последний элемент `'+'`) callback теперь передаёт
  `'KEY_KPPLUS'`, для нумпада `-` (row 1, `'-'`) — `'KEY_KPMINUS'`. На кнопке
  сохраняется атрибут `effective_key`, равный этой метке. Так и выбор клавиши
  для макроса (через `create_keyboard_with_editor`→`set_last_key_keyboard_script`),
  и вставка keystroke в редакторе (`add_text_pytq5`) используют правильную метку.
- `keypad_map` дополнен: `'KEY_KPPLUS'→'KP_Add'`, `'KEY_KPMINUS'→'KP_Subtract'`,
  чтобы вставка нумпада в тело скрипта давала корректный `xte "keydown KP_Add"`.
- `highlight_buttons_with_macros` теперь сравнивает и по `button.effective_key`,
  поэтому нумпад `+`/`-` корректно подсвечиваются, когда на них заведён макрос.
- В `settings control mouse buttons.json` для профиля Portal 2 добавлены ключи
  `"KEY_KPPLUS"` и `"KEY_KPMINUS"` с теми же скриптами, что и `"+"`/`"-"`
  (через штатный `_format_scripts_in_json`, формат/выравнивание сохранены).
  Теперь физический нумпад `+` сразу запускает макрос, а основной `+` — свой.

 Проверено: `evdev_key_to_label('KEY_KPPLUS')=='KEY_KPPLUS'`, сопоставление в
 `handle_keyboard_macro` находит ключ `'KEY_KPPLUS'` в `keyboard_script`; основной
 `+` (`KEY_EQUAL`→`'+'`) по-прежнему идёт к ключу `'+'`. Запуск приложения под
 `DISPLAY=:0` — без `Traceback`.

 ### 17.5 Исправление реальной причины «ничего не срабатывает» (макросы `+`/`-` не запускались)

 После §17.1–§17.4 при нажатии основного `+`/`-` макросы всё равно не
 запускались (и нумпад тоже). Найдено ДВЕ независимые причины — обе устранены
 и проверены интеграционным тестом (вставка `KEY_EQUAL`/`KEY_MINUS`/`KEY_KPPLUS`/
 `KEY_KPMINUS` → метки → `handle_keyboard_macro` → реальный запуск скрипта):

 1. **Неверный выбор устройства клавиатуры (слушали «пустоту»).**
    Старый фильтр в `__init__`:
    `if "Keyboard\"" in str(dev) and ' phys ' in str(dev):` — первым
    совпадением оказывалось ВИРТУАЛЬНОЕ устройство `Smart-Virtual-Keyboard`
    (`phys="py-evdev-uinput"`), а не физическая `Logitech Logitech USB Keyboard`.
    `self.board` указывал на виртуальную клавиатуру, поэтому реальные
    нажатия физической клавиатуры (`/dev/input/event3`) слушатель не видел —
    ни `+`, ни `-`, ни нумпад не срабатывали вообще.
    Исправлено: выбор по возможностям устройства — берём устройства с `EV_KEY`
    и буквами/Enter, ИСКЛЮЧАЯ `virtual`/`uinput`/`mouse` в имени/phys, и выбираем
    самую «полную» (больше всего клавиш `EV_KEY`). Проверено на реальных
    устройствах: выбирается `event3` (Logitech USB Keyboard, есть `KEY_EQUAL`
    и `KEY_KPPLUS`).

 2. **`ru_to_en` ломал сопоставление символов `+`/`-`.**
    В `Pyqt6_libs_mouse.py` словарь `ru_to_en` содержит `'+': ','` и `'-': '.'`
    (позиции символов в русской раскладке). `handle_keyboard_macro` применял
    перевод к ЛЮБОЙ метке, поэтому физическая метка `'+'` превращалась в `','`
    и никогда не равнялась ключу `'+'` из `keyboard_script` → макрос не
    запускался. Перевод русской раскладки имеет смысл только для БУКВ.
    Исправлено: `if k.isalpha() and k in ru_to_en.keys(): k = ru_to_en[k]`.
    Символы (`+`, `-`, `,`, `.`, …) больше не искажаются; буквы по-прежнему
    переводятся (как и задумано).

 Результат интеграционного теста (профиль `C:/Windows/explorer.exe`,
 ключи `"+"`,`"-"`,`"KEY_KPPLUS"`,`"KEY_KPMINUS"`): все четыре —
 `main '+'`, `main '-'`, `numpad '+'`, `numpad '-'` — успешно запускают
 соответствующий bash-скрипт. Запуск приложения под `DISPLAY=:0` — без
 `Traceback` (выход по таймауту, процесс жив).

### 17.6 Файл настроек `settings control mouse buttons.json` был повреждён (исправлено)

 Пользователь сообщил, что другой агент/правка сломал файл настроек. Проверка
 подтвердила повреждение — и оно напрямую объясняет, почему макросы клавиатуры
 «не работали» (даже после правок кода из §17.1–§17.5).

 **Формат файла (важно для понимания причины).** При записи приложение вызывает
 `write_to_file` → `json.dumps(..., indent=2)` → `_format_scripts_in_json()`
 (`Pyqt6_libs_mouse.py`), которая превращает экранированные `\n` внутри
 bash-скриптов (`keyboard_script`/`script_mouse`) в **НАСТОЯЩИЕ переводы строк**
 с выравниванием. Поэтому файл — НЕ валидный strict-JSON; читается только через
 `json.load(..., strict=False)` (+ `scripts_to_text`). Обычный `json.load()`
 (strict) падает с `Invalid control character`.

 **Что именно было сломано (3 дефекта):**
 1. **`C:/Windows/explorer.exe` полностью отсутствовал в `keyboard_script`**
    (секция была `{}`). Макросы `+`/`-` пользователя физически отсутствовали в
    файле → даже при исправном коде они не запускались бы.
 2. **Макрос `J` из Splinter Cell был разорван.** Тело скрипта (многострочное)
    «порвалось» на границе перевода строки: первая строка стала значением ключа
    `"J"`, а остальные строки скрипта утекли в ОТДЕЛЬНЫЙ ключ со значением
    `null` (мусорный ключ вида
    `"keydown $k\"\n sleep 0.05\n xte \"keyup $k\"\n done\n done\n done\"\n "`).
 3. **Потеряна закрывающая скобка профиля** → следующие 7 профилей
    (Alien Isolation, Tomb Raider, Portal 2, Serious Sam, Cold Fear, NFS,
    Portal Stories Mel) оказались ВЛОЖЕНЫ внутрь записи Splinter Cell. Видимых
    профилей в `keyboard_script` стал ровно один (Splinter Cell), остальные
    стали «невидимы» для приложения.

 **Причина (что сделал не так другой агент).** Файл перезаписали/отредактировали
 вне штатного пути приложения — либо обычным `json.dump`/`json.load` без
 `strict=False` и `_format_scripts_in_json`, либо правкой как обычного текста.
 Из-за этого: (а) многострочные значения скриптов разорвались на переводах
 строк (п.2); (б) была утеряна/некорректно расставлена скобка (п.3); (в)
 секция `keyboard_script` была перезаписана целиком вместо слияния (merge),
 поэтому пропал профиль по умолчанию `C:/Windows/explorer.exe` (п.1).
 **Как делать правильно:** никогда не править/пересериализовывать этот JSON
 вручную; использовать загрузку/сохранение приложения (`scripts_to_text` +
 `_format_scripts_in_json`) либо минимум `json.load(..., strict=False)`/
 `json.dump` с сохранением нестрогого формата; при изменении `keyboard_script`
 делать `update` в существующий словарь, а не заменять объект целиком; не
 помещать реальные переводы строк/неэкранированные кавычки внутрь JSON-строк.

 **Как исправлено (без потери данных):**
 - Сохранён оригинальный битый файл: `settings control mouse buttons.json.
   broken_before_repair_20260814`.
 - Восстановлен `J` из двух «порванных» частей (склеены обратно в одну
   многострочную строку).
 - Распакованы 7 вложенных профилей обратно на верхний уровень `keyboard_script`.
 - Добавлен профиль `C:/Windows/explorer.exe` с макросами `+`→`xte "keydown R"`,
   `-`→`xte "keydown E"` (из предоставленного пользователем снимка JSON).
 - Перезаписано строгим `json.dumps(indent=2)`. Приложение читает через
   `json.load(strict=False)`, который корректно принимает и strict-JSON, так
   что формат полностью совместим (при следующем сохранении из GUI приложение
   само применит свой `_format_scripts_in_json`).

 **Проверка:** `json.load(strict=False)` + `scripts_to_text` — без ошибок;
 `keyboard_script` содержит 9 профилей (Splinter Cell + 7 распакованных +
 `C:/Windows/explorer.exe`); `explorer.exe` имеет ключи `"+"`/`"-"`; `J`
 присутствует; `null`-значений нет; остальные секции (`script_mouse`,
 `key_value`, `paths`, `current_app`) не тронуты (20/20/20 записей).

### 17.7 Ошибка при сохранении в программе: «Invalid \escape» (и её корень)

 После правок из §17.6 пользователь изменил настройки в самой программе и
 сохранил — при следующем запуске получил:
 `json.decoder.JSONDecodeError: Invalid \escape: line 414 column 31`.

 **Корень проблемы (два слоя):**
 1. **Содержимое скриптов было дважды экранировано.** Исходно «сломанный»
    файл (от другого агента) хранил скрипты как `\\\"` вместо `\"` и `\\n`
    вместо `\n`. `json.load(..., strict=False)` раскодирует `\\\"` → `\"`
    (буквальный обратный слэш в значении), поэтому в памяти скрипты содержат
    лишние `\`. Моя правка §17.6 скопировала эти слэши дальше.
 2. **`write_to_file` вызывал `_format_scripts_in_json`**, который превращает
    `\n` в НАСТОЯЩИЙ перевод строки внутри строкового значения. При наличии
    лишнего слэша (из п.1) он оставлял «висячий» `\` перед реальным переводом
    строки → `Invalid \escape` при последующей загрузке. (На корректном
    содержимом `_format_scripts_in_json` работает, но на дважды экранированном
    — ломается.)

 **Исправлено (первичное, временное):**
 - `write_to_file` (`Pyqt6_libs_mouse.py`) стал писать **строгий JSON**
   (`json.dumps(..., indent=2)` без `_format_scripts_in_json`). Приложение
   читает файл через `json.load(..., strict=False)`, который корректно принимает
   и строгий JSON, поэтому формат совместим, а повторой порчи при сохранении
   исключена полностью.
 - Файл восстановлен: инвертирована порча (невалидные слэши исправлены →
   файл загрузился), затем содержимое скриптов **разэкранировано на один слой**
   (`\\n`→реальный перевод строки, `\\"`→`"`, `\`+перевод строки→перевод
   строки). Результат — корректные скрипты (без лишних слэшей). Все 9 профилей
   `keyboard_script` и секция `script_mouse` сохранены, `C:/Windows/explorer.exe`
   имеет `"+"`/`"-"`. Битый сохранённый файл оставлен как
   `settings control mouse buttons.json.broken_appsave_20260814_2353`.

 **Проверка:** загрузка через штатный путь приложения (`json.load(strict=False)`
 + `scripts_to_text`) — без ошибок; запуск под `DISPLAY=:0` — без `Traceback`
 (выход по таймауту, процесс жив); симуляция сохранения (`json.dumps` строгий)
 снова загружается без ошибок.

 > **ВАЖНО (что было дальше).** Строгий JSON был временным решением: файл
 > оставался валидным, но bash-скрипты снова выглядели как одна длинная строка
 > с `\n`. Пользователь попросил вернуть «человекочитаемый» формат. Вместо
 > возврата к старой ломающейся логике корень проблемы был устранён по-настоящему
 > — см. §17.8 ниже.

---

### 17.8 Возврат «красивого» формата JSON (построчные скрипты) без риска порчи (2026-08-15)

 После того как §17.7 перевёл запись на строгий JSON, пользователь попросил
 восстановить читаемый формат файла: bash-скрипты в `script_mouse` /
 `keyboard_script` должны снова храниться в файле **построчно**, с настоящими
 переводами строк и выравниванием, «как в текстовом редакторе» (а не одной
 длинной строкой с `\n`).

 **Проблема (почему нельзя просто откатить §17.7).** Раньше `write_to_file`
 вызывал `_format_scripts_in_json`, который заменял `\n` на реальный перевод
 строки через `str.replace("\\n", "\n"+cont)`. Если внутри скрипта встречался
 экранированный обратный слэш (последовательность `\\` в JSON → один `\` в
 значении), такой `replace` мог оставить «висячий» слэш перед реальным переносом,
 и файл после сохранения переставал читаться (`JSONDecodeError: Invalid \escape`).
 Именно эта ошибка была задокументирована в §17.7.

 **Решение (итоговое, безопасное):**
 1. `Pyqt6_libs_mouse.py` → `_format_scripts_in_json`: замена `\n` теперь
    выполняется через `re.sub(r'(?<!\\)\\n', "\n" + cont, inner)` —
    **негативный lookbehind** `(?<!\\)`. Такой regex меняет на реальный перенос
    ТОЛЬКО `\n`, который НЕ предварён другим обратным слэшем. Экранированный
    слэш `\\` (а значит и возможный «висячий» слэш) больше не разрушается:
    он остаётся валидной JSON-последовательностью. Строки с `\\` в скриптах
    просто остаются без подмены переноса на этой позиции — файл гарантированно
    остаётся корректным.
 2. `Pyqt6_libs_mouse.py` → `save_dict.write_to_file`: возвращён вызов
    `_format_scripts_in_json(json.dumps(...))` (красивый формат на диске),
    но уже поверх укреплённой функции. Комментарий в коде обновлён и описывает
    цепочку «диск ↔ память».
 3. Файл `settings control mouse buttons.json` переформатирован на диске:
    применена та же цепочка `json.load(strict=False)` → `scripts_to_text` →
    `json.dumps(indent=2)` → `_format_scripts_in_json`. Скрипты теперь выглядят
    построчно с вертикальным выравниванием по первой строке (`#!/bin/bash`).

 **Что проверено:**
 - `json.load(..., strict=False)` читает переформатированный файл без ошибок;
   структура (ключи верхнего уровня, списки `key_value`/`mouse_press`,
   `id`, `current_app`) совпадает с исходной (20 профилей в `paths`);
 - единственное отличие данных «до/после» — срезанный хвостовой `\n` в конце
   скриптов (это штатное поведение `_format_scripts_in_json`, §1.1, п.4);
 - идемпотентность: повторный прогон той же цепочки даёт файл байт-в-байт
   идентичным (`True`);
 - краевой случай: скрипт, содержащий экранированный `\\`, корректно
   обрабатывается укреплённой функцией и читается через `strict=False`
   без `Invalid \escape`;
 - эмуляция нового `write_to_file` (load → scripts_to_text → dumps →
   `_format_scripts_in_json`) воспроизводит текущий файл байт-в-байт —
   значит, при следующем сохранении из GUI красивый формат сохранится.

**Итог.** Проблема из §17.7 устранена на уровне причины (lookbehind), а не
  обойдена (отказом от красивого формата). Теперь и при изменении настроек через
  программу, и при ручной перезаписи файл остаётся и читаемым, и человекочитаемым.

---

## 18. Сессия 2026-08-15: переключение профилей и баги клавиатурного редактора / Portal 2

### 18.1 Исправлено: при переключении профилей синими оставалось несколько label

**Симптом.** Клик по профилю в левом списке подсвечивал синим не только
выбранный label, но и несколько прежних (синих накапливалось много).

**Причина (найдена).** Фоновый монитор активного окна `emunator_mouse`
(Pyqt6_libs_mouse.py:1632) при смене активного окна сам вызывает
`dict_save.set_cur_app(new_path_game)` — меняет `current_app` БЕЗ обновления UI.
Прежний `check_label_changed` (Pyqt6_libs_mouse.py:1714) сбрасывал подсветку
только у ОДНОГО label — того, что соответствовал `current_app` на момент клика.
Если монитор уже сменил `current_app`, старый синий label не сбрасывался, и
синих накапливалось несколько. Tkinter-версия такого бага не имела: её
`set_colol_white_label_changed` сбрасывала ВСЕ label в белый перед подсветкой.

**Исправление** (Pyqt6_libs_mouse.py:1717-1726): `check_label_changed` теперь
сначала сбрасывает ВСЕ label в белый, затем подсвечивает выбранный — та же
логика, что в Tkinter-версии.

**Проверено:**
- синтаксис и запуск приложения без `Traceback` (выход по таймауту);
- JSON не повреждён: `key_value`/`paths`/`current_app` в порядке, 20 профилей,
  34 bash-скрипта `#!/bin/bash`;
- offscreen-тест цикла GUI: «открыть клавиатуру → редактор → удалить → закрыть»
  сбрасывает стиль кнопки в `''`.

### 18.2 Баг 1 (клавиатура): кнопка остаётся синей после удаления привязки

**Симптом.** У профиля на клавиатуре есть синие кнопки (привязки). Пользователь
нажимает такую кнопку → открывается редактор скрипта → удаляет привязку →
закрывает редактор → кнопка остаётся синей «как будто что-то назначено».

**Что разобрано (механика редактора):**
- `create_keyboard_with_editor(key)` (Pyqt6_libs_mouse.py:1364) — открывает
  окно с QTextEdit сверху и `KeyboardWidget` снизу; запоминает ключ через
  `set_last_key_keyboard_script`; берёт `current_app = res["current_app"]`.
- `kill_notebook(event, window, section)` (Pyqt6_libs_mouse.py:1413) — при
  закрытии читает текст; если он пуст или `#!/bin/bash` — удаляет ключ из
  `keyboard_script[cur_app]["keys"]`, иначе сохраняет; затем
  `update_keyboard_display(dict_save)` пересчитывает подсветку.
- `update_keyboard_display` (Pyqt6_libs_mouse.py:1553) — берёт
  `current_app = dict_save.get_cur_app()` ЗАНОВО и подсвечивает кнопки по
  текущему профилю.
- `highlight_buttons_with_macros` (Pyqt6_libs_mouse.py:1536) — сбрасывает
  стиль ВСЕХ кнопок на `""`, затем красит те, что есть в актуальном списке
  (по тексту кнопки либо по `effective_key`, что и даёт подсветку нумпада
  `KEY_KPPLUS`/`KEY_KPMINUS`).

**Вывод (root cause).** Кнопка «остаётся синей» в реальном сценарии — следствие
той же гонки, что и §18.1: `kill_notebook` и `update_keyboard_display` читают
`current_app` в момент ЗАКРЫТИЯ, а не в момент открытия редактора. Если фоновый
монитор (`emunator_mouse`) между открытием и закрытием сменил профиль,
удаление/сохранение и обновление подсветки выполняются для ДРУГОГО профиля,
а в исходном профиле привязка и подсветка остаются. В простом тесте без
фонового монитора удаление работает корректно (кнопка сбрасывается).

Рекомендуемое будущее исправление: зафиксировать профиль при открытии редактора
и клавиатуры (например, хранить `editor_app = current_app` в объекте окна и
использовать его в `kill_notebook`/`update_keyboard_display` вместо повторного
`get_cur_app()`), либо приостанавливать монитор на время редактирования.

### 18.3 Баг 2 (клавиатура): профиль без привязок всё равно показывает кнопку «Клавиатура» серой

**Симптом.** У профиля удалены все назначенные клавиши (скриптов нет), но кнопка
«Клавиатура» в главном окне остаётся выделенной серым, как будто привязка есть.

**Причина.** `check_label_changed` (Pyqt6_libs_mouse.py:1746-1751) решает
подсвечивать кнопку по условию `if script:`, где
`script = res.get("keyboard_script", {}).get(game, {}).get("keys", {})`.
Непустой словарь `keys` — даже с «пустыми»/остаточными записями — даёт истину и
серую подсветку. Если удаление из §18.2 не дошло до профиля (гонка с
монитором), либо в `keys` остались пустые строки, кнопка «Клавиатура» остаётся
серой даже при отсутствии реальных скриптов.

### 18.4 Баг 3 (Portal 2): консоль открывается, но команды не печатаются

**Симптом.** Профиль Portal 2: скрипты на нумпад `+`/`-` открывают консоль
игры (`xdotool key grave`), но `xdotool type "sv_cheats 1"` / `xdotool type
"host_timescale $TIMESCALE"` в консоли НЕ печатаются.

**Что проверено в окружении:**
- `xdotool`, `xte`, `xinput` установлены; `DISPLAY=:0` (X11, не Wayland);
  `xdotool version 3.20160805.1`.
- Системная раскладка клавиатуры: **`ru,us,ru` — русская первичная**
  (`setxkbmap -query`). Это ключевой факт.

**Вывод (root cause).** `xdotool type` вводит текст через XTEST по активной
раскладке. При первичной русской раскладке `xdotool type "sv_cheats 1"`
печатает в консоль кириллицу (символы на тех же физических клавишах), команда
не распознаётся движком Source → «команды не пишутся». При этом
`xdotool key grave` (открытие консоли) раскладко-независим и работает — отсюда
«консоль открывается, но команды не вводятся».

**Рекомендуемые пути исправления (проверять в игре):**
1. В скрипте перед `xdotool type` временно переключать раскладку на US и
   возвращать обратно:
   `setxkbmap us` → `xdotool type "..."` → `setxkbmap ru,us`.
   (Либо `xdotool type --clearmodifiers "..."` — но это не меняет раскладку.)
2. Вводить команды посимвольно через `xte "keydown s"/"keyup s"` (xte тоже
   раскладко-зависим на уровне keysym, но можно использовать `xdotool key`
   с именами латинских клавиш в US-раскладке).
3. Проверить на профиле `Portal Stories Mel` (там `KEY_KPPLUS` использует ту же
   схему `xdotool type "sv_cheats 1"` + `host_timescale`) — баг воспроизводится
   одинаково.

**Статус.** Баги §18.2-§18.4 диагностированы; код в этой сессии НЕ менялся
(только §18.1 — исправление подсветки профилей). Исправления §18.2-§18.4
остаются следующими шагами (см. §18.5).

### 18.5 Следующие шаги

1. Зафиксировать профиль при открытии клавиатуры/редактора (использовать
   сохранённый `current_app` в `kill_notebook`/`update_keyboard_display`), чтобы
   удаление/сохранение всегда шло в тот профиль, который редактируется.
2. Чистить «остаточные» записи в `keyboard_script[..]["keys"]` (пустые строки),
   чтобы `if script:` в `check_label_changed` давал серую подсветку только при
   реальных непустых скриптах.
3. Для Portal 2 — переключать раскладку на US перед `xdotool type` (или вводить
   через `xdotool key` по символам) и проверить в игре.

---

*Конец отчёта.*
