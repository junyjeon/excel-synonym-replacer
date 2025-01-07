"""
데이터 전처리 모듈
"""
from .config import DEFAULT_VALUES

def prepare_data(row, ordered_columns):
    """
    컬럼 데이터 전처리
    
    Args:
        row: 현재 행 데이터
        ordered_columns: 처리할 컬럼 순서 리스트
    
    Returns:
        dict: 전처리된 데이터 딕셔너리
    """
    return {
        key: str(row.get(key, DEFAULT_VALUES['empty'])).strip()
        for key in ordered_columns
    } 