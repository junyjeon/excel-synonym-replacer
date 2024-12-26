from text_cleaner import clean_text

def create_title_combination(row, col_selection, synonym_dict, version_idx):
    """단일 조합 생성"""
    col_map = {
        "브랜드": 1,    # B열
        "색상": 2,      # C열
        "패턴": 3,      # D열
        "소재": 4,      # E열
        "카테고리": 5   # F열
    }
        
    ordered_keys = ["브랜드", "색상", "패턴", "소재", "카테고리"]
    selected_lists = []  # 선택된 카테고리의 유의어 리스트
    fixed_values = []    # 선택되지 않은 카테고리의 값
    
    for key in ordered_keys:
        val = str(row.iloc[col_map[key]]).strip()
        val = clean_text(val)
        
        if not val:  # 빈 값 스킵
            continue
            
        if key in col_selection:  # 선택된 카테고리
            if key in synonym_dict and val in synonym_dict[key]:
                synonyms = synonym_dict[key][val]
                if synonyms:
                    all_synonyms = synonyms + [val]
                    selected_lists.append(all_synonyms)
                else:
                    selected_lists.append([val])
            else:
                selected_lists.append([val])
        else:  # 선택되지 않은 카테고리
            fixed_values.append(val)

    # 조합 가능한 총 개수 계산
    total_combinations = 1
    for syns in selected_lists:
        total_combinations *= len(syns)
    
    if total_combinations > 0:
        # 현재 버전에 해당하는 조합 선택
        current_idx = version_idx % total_combinations
        
        # 각 유의어 리스트에서 선택할 인덱스 계산
        selected_indices = []
        temp_idx = current_idx
        for syns in selected_lists:
            length = len(syns)
            selected_indices.append(temp_idx % length)
            temp_idx //= length
        
        # 선택된 유의어들 조합
        selected_synonyms = [
            selected_lists[i][idx] 
            for i, idx in enumerate(selected_indices)
        ]
        
        # 고정값과 선택된 유의어 합치기
        result = fixed_values + selected_synonyms
        final_text = " ".join(filter(None, result))
        
        return final_text, total_combinations
        
    return " ".join(filter(None, fixed_values)), 0 