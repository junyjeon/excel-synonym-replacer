import pytest
from PySide6.QtWidgets import QApplication
import pandas as pd
import openpyxl
import tempfile
import time
from app import MainWindow

@pytest.fixture(scope="session")
def app():
    return QApplication.instance() or QApplication([])

@pytest.fixture
def main_window(app):
    window = MainWindow()
    return window

def test_excel_file_format(main_window, qtbot):
    """엑셀 파일 포맷 관련 테스트"""
    window = main_window
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        # 1. 기본 저장 테스트
        df = pd.DataFrame({'테스트': ['데이터']})
        df.to_excel(tmp.name, index=False)
        
        # 2. openpyxl로 읽기 테스트
        wb = openpyxl.load_workbook(tmp.name)
        assert 'Sheet1' in wb.sheetnames
        wb.close()

def test_synonym_replacement(main_window, qtbot):
    """유의어 치환 관련 테스트"""
    window = main_window
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        df = pd.DataFrame({
            '브랜드': ['테스트 브랜드', '없는브랜드'],
            '색상': ['빨강', '  빨강  '],
            '패턴': ['', ''],
            '소재': ['', ''],
            '카테고리': ['', ''],
            '상품명_1': ['기존1', '기존2'],
            '상품명_2': ['', ''],
            '상품명_3': ['', '']
        })
        df.to_excel(tmp.name, index=False)
        
        # 필요한 설정 추가
        window.file_path = tmp.name
        window.current_sheet = 'Sheet1'
        window._df = df.copy()
        window._model.setDataFrame(window._df)
        
        window.synonym_dict = {
            '브랜드': {'테스트 브랜드': ['변경된브랜드']},
            '색상': {'빨강': ['레드']}
        }
        
        # 체크박스 설정
        window.chk_brand.setChecked(True)
        window.chk_color.setChecked(True)
        window.chk_overwrite.setChecked(True)
        
        # 행 선택
        window.table_view.selectRow(0)
        
        # 변환 실행
        window.transform_data()
        time.sleep(0.1)
        
        # 검증
        result_df = pd.read_excel(tmp.name)
        assert '변경된브랜드' in result_df['상품명_1'].iloc[0]

def test_file_save_load(main_window, qtbot):
    """파일 저장/읽기 관련 테스트"""
    window = main_window
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        df = pd.DataFrame({
            '브랜드': ['테스트 브랜드'],
            '상품명_1': ['기존']
        })
        
        # 1. 저장 테스트
        df.to_excel(tmp.name, index=False)
        
        # 필요한 설정 추가
        window.file_path = tmp.name
        window.current_sheet = 'Sheet1'
        window._df = df.copy()
        window._model.setDataFrame(window._df)
        
        # 유의어 사전 설정
        window.synonym_dict = {
            '브랜드': {'테스트 브랜드': ['변경된브랜드']}
        }
        
        # 체크박스 설정
        window.chk_brand.setChecked(True)
        window.chk_overwrite.setChecked(True)
        
        # 행 선택
        window.table_view.selectRow(0)
        
        # 2. 변경 후 저장
        window.transform_data()
        time.sleep(0.1)
        
        # 3. 다시 읽기
        result_df = pd.read_excel(tmp.name)
        assert result_df['상품명_1'].iloc[0] != '기존' 