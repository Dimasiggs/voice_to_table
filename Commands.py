import pandas as pd
from datetime import datetime

class Commands:
    def __init__(self):
        self.df = pd.DataFrame()
        self.clipboard = None
        self.cursor_position = (0, 0)  # (row, column)

    def copy(self, args):
        """Копирование данных из указанного диапазона"""
        if isinstance(args, str):
            # Копирование значения ячейки
            row, col = self._parse_cell_reference(args)
            self.clipboard = self.df.iat[row, col]
        elif isinstance(args, dict):
            # Копирование диапазона
            start = args.get('start')
            end = args.get('end')
            self.clipboard = self.df.loc[start:end].copy()
        return self.clipboard

    def paste(self, args):
        """Вставка данных в указанную позицию"""
        if self.clipboard is None:
            return
        if isinstance(args, str):
            # Вставка в конкретную ячейку
            row, col = self._parse_cell_reference(args)
            self.df.iat[row, col] = self.clipboard
        elif isinstance(args, dict):
            # Вставка диапазона
            start = args.get('start')
            self.df.loc[start:] = self.clipboard.values

    def moveto(self, args):
        """Перемещение курсора к указанной ячейке"""
        self.cursor_position = self._parse_cell_reference(args)
        return self.cursor_position

    def delete(self, args):
        """Удаление данных"""
        if args == 'all':
            self.df = pd.DataFrame()
        elif isinstance(args, str):
            row, col = self._parse_cell_reference(args)
            self.df.iat[row, col] = None
        elif isinstance(args, list):
            for cell in args:
                row, col = self._parse_cell_reference(cell)
                self.df.iat[row, col] = None

    def create(self, args):
        """Создание нового DataFrame"""
        self.df = pd.DataFrame(args['data'])
        return self.df

    def write(self, args):
        """Запись значения в текущую позицию"""
        row, col = self.cursor_position
        self.df.iat[row, col] = args['value']
        return self.df

    def right(self, steps=1):
        """Перемещение вправо"""
        row, col = self.cursor_position
        max_col = len(self.df.columns) - 1
        self.cursor_position = (row, min(col + steps, max_col))
        return self.cursor_position

    def left(self, steps=1):
        """Перемещение влево"""
        row, col = self.cursor_position
        self.cursor_position = (row, max(col - steps, 0))
        return self.cursor_position

    def up(self, steps=1):
        """Перемещение вверх"""
        row, col = self.cursor_position
        self.cursor_position = (max(row - steps, 0), col)
        return self.cursor_position

    def down(self, steps=1):
        """Перемещение вниз"""
        row, col = self.cursor_position
        max_row = len(self.df.index) - 1
        self.cursor_position = (min(row + steps, max_row), col)
        return self.cursor_position

    def date(self, args):
        """Вставка текущей даты"""
        row, col = self._parse_cell_reference(args['cell'])
        self.df.iat[row, col] = datetime.now().strftime('%Y-%m-%d')
        return self.df

    def create_columns(self, columns):
        """Создание столбцов"""
        for col in columns:
            self.df[col] = None
        return self.df

    def create_table(self, columns):
        """Создание пустой таблицы с указанными столбцами"""
        self.df = pd.DataFrame(columns=columns)
        return self.df

    def _parse_cell_reference(self, ref):
        """Парсинг ссылки на ячейку в формате 'A1'"""
        if isinstance(ref, tuple):
            return ref
        col = ord(ref[0].upper()) - ord('A')
        row = int(ref[1:]) - 1
        return (row, col)