# dataframe_model.py
import pandas as pd
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QColor, QBrush
from typing import Any, Optional

class DataFrameModel(QAbstractTableModel):
    """DataFrame을 TableView에 표시하기 위한 모델"""
    
    def __init__(self):
        super().__init__()
        self._df = pd.DataFrame()
        
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """행 개수 반환"""
        return len(self._df)
        
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """열 개수 반환"""
        return len(self._df.columns)
        
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """셀 데이터 반환"""
        if not index.isValid():
            return None
            
        if role == Qt.DisplayRole:
            value = self._df.iloc[index.row(), index.column()]
            return str(value) if pd.notna(value) else ""
            
        return None
        
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Optional[str]:
        """헤더 데이터 반환"""
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                # 열 헤더
                if section < len(self._df.columns):
                    return str(self._df.columns[section])
            else:
                # 행 헤더
                if section < len(self._df.index):
                    return str(self._df.index[section])
        return None
        
    def setDataFrame(self, df: pd.DataFrame) -> None:
        """DataFrame 설정"""
        self.beginResetModel()
        self._df = df
        self.endResetModel()
        
    def update_cell(self, row: int, col: int, value: Any) -> None:
        """특정 셀 업데이트"""
        if 0 <= row < len(self._df) and 0 <= col < len(self._df.columns):
            self._df.iloc[row, col] = value
            # 변경 알림
            index = self.index(row, col)
            self.dataChanged.emit(index, index, [Qt.DisplayRole])


def test_dataframe_model():
    """DataFrameModel 테스트"""
    # 테스트용 DataFrame 생성
    test_df = pd.DataFrame({
        'A': [1, 2, 3],
        'B': ['a', 'b', 'c']
    })
    
    # 모델 생성 및 DataFrame 설정
    model = DataFrameModel()
    model.setDataFrame(test_df)
    
    # 기본 기능 테스트
    assert model.rowCount() == 3
    assert model.columnCount() == 2
    assert model.data(model.index(0, 0)) == "1"
    assert model.data(model.index(1, 1)) == "b"
    
    # 셀 업데이트 테스트
    model.update_cell(0, 0, 10)
    assert model.data(model.index(0, 0)) == "10"
