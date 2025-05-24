class Table:
    def __init__(self, rows_count = 0, columns_count = 0):
        self.rows = [Row(i, columns_count) for i in range(rows_count)]

    def with_values(self, rows):
        self.rows = [Row().from_values(i, row) for i, row in enumerate(rows)]


class Row:
    def __init__(self, row_index=0,  cells_count=0):
        self.row_index = row_index
        self.cells = [Cell(self, i) for i in range(cells_count)]

    def from_values(self, row_index, values):
        self.row_index = row_index
        self.cells = [Cell(self, i, value) for i, value in enumerate(values)]


class Cell:
    def __init__(self, row, cell_index, value=None):
        self.row = row
        self.index = cell_index
        self.value = value
