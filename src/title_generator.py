from text_cleaner import clean_text
import pandas as pd

def create_title_combination(row, col_selection, synonym_dict, version_idx):
    """
    유의어 치환으로 새로운 제목 생성
    
    Args:
        row: 현재 행 데이터
        col_selection: 선택된 컬럼들
        synonym_dict: 유의어 사전
        version_idx: 버전 인덱스 (0부터 시작)
    """
    # 선택된 컬럼만 처리
    ordered_lists = []  # 유의어 리스트들
    ordered_selections = []  # 선택된 컬럼들
    fixed_values = {}  # 선택되지 않은 컬럼들의 원본 값
    
    # 선택된 컬럼에 대해서만 처리
    for key in col_selection:
        # 해당 컬럼이 row에 없으면 스킵
        if key not in row:
            continue
            
        val = str(row[key]).strip()
        if not val:  # 빈 값이면 스킵
            continue
            
        # 유의어 매칭 시도
        if key in synonym_dict:
            matched = False
            for dict_key, synonyms in synonym_dict[key].items():
                if val.strip().lower() == dict_key.strip().lower():
                    ordered_lists.append(synonyms)
                    ordered_selections.append(key)
                    matched = True
                    break
                if val.strip().lower() in [s.strip().lower() for s in synonyms]:
                    ordered_lists.append([dict_key])
                    ordered_selections.append(key)
                    matched = True
                    break
            if not matched:
                # 사전에 없는 값은 원본값 그대로 사용
                ordered_lists.append([val])
                ordered_selections.append(key)
        else:
            # 해당 컬럼에 대한 사전이 없으면 원본값 사용
            ordered_lists.append([val])
            ordered_selections.append(key)
    
    # 선택되지 않은 컬럼들은 원본값 유지
    for key in row.index:
        if key not in col_selection and pd.notna(row[key]):
            fixed_values[key] = str(row[key]).strip()
    
    # 총 조합 수 계산
    total_combinations = 1
    for syns in ordered_lists:
        total_combinations *= len(syns)
    
    if not ordered_lists:  # 선택된 카테고리 없음
        # 선택되지 않은 컬럼들의 값만으로 결과 생성
        result = []
        for key in row.index:
            if key in fixed_values:
                result.append(fixed_values[key])
        return " ".join(filter(None, result)), total_combinations
    
    # 버전별 인덱스 계산 (순환 처리)
    selected_indices = []
    remaining_version = version_idx % total_combinations
    
    for syns in ordered_lists:
        idx = remaining_version % len(syns)
        remaining_version //= len(syns)
        selected_indices.append(idx)
    
    # 결과 조합
    result = []
    current_synonym_idx = 0
    
    # 선택된 컬럼의 유의어 추가
    for key in ordered_selections:
        val = ordered_lists[current_synonym_idx][selected_indices[current_synonym_idx]]
        result.append(val.strip())
        current_synonym_idx += 1
    
    # 선택되지 않은 컬럼의 원본값 추가
    for key in row.index:
        if key in fixed_values:
            result.append(fixed_values[key])
    
    # 결과 문자열 생성 (공백으로 구분)
    final_text = ' '.join(filter(None, result))
    
    return final_text, total_combinations 