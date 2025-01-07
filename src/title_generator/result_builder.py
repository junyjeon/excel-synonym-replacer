"""
결과 문자열 생성 모듈
"""

def generate_result(ordered_columns, ordered_selections, ordered_lists, 
                   selected_indices, fixed_values):
    """
    최종 결과 문자열 생성
    
    Args:
        ordered_columns: 컬럼 순서 리스트
        ordered_selections: 선택된 컬럼 리스트
        ordered_lists: 유의어 리스트들
        selected_indices: 선택된 인덱스 리스트
        fixed_values: 고정 값 딕셔너리
    
    Returns:
        str: 생성된 결과 문자열
    """
    result = []
    for key in ordered_columns:
        if key in ordered_selections:
            idx = ordered_selections.index(key)
            value = ordered_lists[idx][selected_indices[idx]]
            if value:  # 빈 값이 아닌 경우만 추가
                result.append(value)
        elif key in fixed_values and fixed_values[key]:
            result.append(fixed_values[key])
            
    return ' '.join(filter(None, result)) 