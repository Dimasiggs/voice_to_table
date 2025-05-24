import pandas as pd
from datetime import datetime

# Состояние курсора
cursor = {
    "row": 0,   # Начальная строка
    "col": 0    # Начальный столбец
}

def _reset_cursor():
    """Сброс позиции курсора"""
    global cursor
    cursor = {"row": 0, "col": 0}

def _get_col_index(col_label: str) -> int:
    """Преобразует буквенное обозначение столбца в индекс (например 'A' -> 0, 'B' -> 1 и т.д.)"""
    if isinstance(col_label, int):
        return col_label
    col_label = col_label.upper()
    result = 0
    for char in col_label:
        result = result * 26 + (ord(char) - ord('A') + 1)
    return result - 1

def _normalize_col(col: str | int) -> int:
    """Приводит столбец к числовому индексу"""
    if isinstance(col, str):
        return _get_col_index(col)
    return col

# --- Команды ---

def copy(table: pd.DataFrame, args):
    """Копирует значение из текущей ячейки в буфер"""
    global clipboard
    clipboard = table.iat[cursor["row"], cursor["col"]]

def paste(table: pd.DataFrame, args):
    """Вставляет значение из буфера в текущую ячейку"""
    global clipboard
    table.iat[cursor["row"], cursor["col"]] = clipboard

def moveto(table: pd.DataFrame, args):
    """Перемещает курсор на указанную позицию"""
    if "row" in args:
        cursor["row"] = args["row"] - 1  # Индекс начинается с 0
    if "col" in args:
        cursor["col"] = _normalize_col(args["col"])

def delete(table: pd.DataFrame, args):
    """Удаляет содержимое текущей ячейки"""
    table.iat[cursor["row"], cursor["col"]] = ""

def create(table: pd.DataFrame, args):
    """Создаёт новую ячейку/строку/столбец с указанным текстом"""
    text = args.get("text", "")
    table.iat[cursor["row"], cursor["col"]] = text

def write(table: pd.DataFrame, args):
    """Записывает текст в текущую ячейку"""
    text = args.get("text", "")
    table.iat[cursor["row"], cursor["col"]] = text

def right(table: pd.DataFrame, args):
    """Перемещает курсор вправо на N шагов"""
    steps = args.get("steps", 1)
    cursor["col"] += steps

def left(table: pd.DataFrame, args):
    """Перемещает курсор влево на N шагов"""
    steps = args.get("steps", 1)
    cursor["col"] -= steps

def up(table: pd.DataFrame, args):
    """Перемещает курсор вверх на N шагов"""
    steps = args.get("steps", 1)
    cursor["row"] -= steps

def down(table: pd.DataFrame, args):
    """Перемещает курсор вниз на N шагов"""
    steps = args.get("steps", 1)
    cursor["row"] += steps

def date(table: pd.DataFrame, args):
    """Вставляет текущую дату в формате YYYY-MM-DD"""
    today = datetime.now().strftime("%Y-%m-%d")
    table.iat[cursor["row"], cursor["col"]] = today

def create_columns(table: pd.DataFrame, args):
    """Создаёт новые столбцы с заданными названиями"""
    names = args.get("names", [])
    for name in names:
        table[name] = ""

def create_table(table: pd.DataFrame, args):
    """Создаёт новую таблицу с заданным количеством строк и столбцов"""
    cols = int(args.get("x"))
    rows = int(args.get("y"))
    new_table = pd.DataFrame("", index=range(rows), columns=range(cols))
    return new_table

# Глобальные переменные
clipboard = None