# dataframe_model.py
import pandas as pd
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QColor, QBrush

class DataFrameModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self._df = pd.DataFrame()
        self._modified_cells = set()  # 수정된 셀 추적
        
    def update_cell(self, row, col, value):
        """셀 값 업데이트 및 화면 갱신"""
        self._df.iloc[row, col] = value
        self._modified_cells.add((row, col))
        top_left = self.index(row, col)
        bottom_right = self.index(row, col)
        self.dataChanged.emit(top_left, bottom_right)

    def setDataFrame(self, df: pd.DataFrame):
        self.beginResetModel()
        self._df = df.copy()
        self.endResetModel()

    def dataFrame(self) -> pd.DataFrame:
        return self._df.copy()

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._df)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._df.columns)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            return str(self._df.iloc[index.row(), index.column()])
        
        elif role == Qt.BackgroundRole:
            # M열 이후의 수정된 셀 하이라이트
            if index.column() >= 12:  # M열부터
                if not pd.isna(self._df.iloc[index.row(), index.column()]):
                    return QBrush(QColor("#E8F5E9"))  # 연한 초록색
        
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._df.columns[section]
            else:
                return str(section)
        return None

    def markModified(self, row, col):
        self._modified_cells.add((row, col))
        self.dataChanged.emit(self.index(row, col), self.index(row, col))
