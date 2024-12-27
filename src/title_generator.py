from text_cleaner import clean_text

def create_title_combination(row, col_selection, synonym_dict, version_idx):
    col_map = {
        "브랜드": 1, "색상": 2, "패턴": 3, "소재": 4, "카테고리": 5
    }
    ordered_keys = ["브랜드", "색상", "패턴", "소재", "카테고리"]
    
    # 1. ordered_keys 순서로 유의어 리스트 구성
    ordered_lists = []  # ordered_keys 순서대로 유의어 저장
    ordered_selections = []  # ordered_keys 순서대로 선택된 카테고리 저장
    fixed_values = {}  # 선택되지 않은 값 저장
    
    for key in ordered_keys:
        val = str(row.iloc[col_map[key]]).strip()
        if not val or (key == "패턴" and val == "무지"):
            continue
            
        if key in col_selection:
            if key in synonym_dict and val in synonym_dict[key]:
                ordered_lists.append(synonym_dict[key][val])
                ordered_selections.append(key)
            else:
                ordered_lists.append([val])
                ordered_selections.append(key)
        else:
            fixed_values[key] = val

    # 2. 총 조합 수 계산
    total_combinations = 1
    for syns in ordered_lists:
        total_combinations *= len(syns)
    
    if not ordered_lists:  # 선택된 카테고리 없음
        result = [fixed_values.get(k, '') for k in ordered_keys]
        return " ".join(filter(None, result)), 0
        
    # 3. 버전별 인덱스 계산 (ordered_keys 순서 기준)
    selected_indices = []
    remaining_version = version_idx
    
    for syns in ordered_lists:
        idx = remaining_version % len(syns)
        remaining_version //= len(syns)
        selected_indices.append(idx)
    
    # 4. 결과 조합
    result = []
    current_synonym_idx = 0
    
    for key in ordered_keys:
        if key in ordered_selections:
            # 선택된 카테고리는 유의어 사용
            result.append(ordered_lists[current_synonym_idx][selected_indices[current_synonym_idx]])
            current_synonym_idx += 1
        else:
            # 선택되지 않은 카테고리는 원본 값 사용
            result.append(fixed_values.get(key, ''))
    
    final_text = " ".join(filter(None, result))
    final_text = clean_text(final_text)
    
    return final_text, total_combinations 