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
        
        if not val:  # 빈 값 스킵
            continue
            
        if key in col_selection:  # 선택된 카테고리
            if key in synonym_dict and val in synonym_dict[key]:
                synonyms = synonym_dict[key][val]
                if synonyms:
                    # 유의어를 먼저 넣고, 원본은 나중에
                    all_synonyms = synonyms + [val]  # 다시 원래대로 변경
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
        divisor = total_combinations
        for syns in selected_lists:
            divisor //= len(syns)
            idx = (temp_idx // divisor) % len(syns)
            selected_indices.append(idx)
            temp_idx %= divisor
        
        # 선택된 유의어들 조합
        selected_synonyms = [
            selected_lists[i][idx] 
            for i, idx in enumerate(selected_indices)
        ]
        
        # 최종 결과를 만들 때 카테고리 순서대로 정렬
        ordered_result = []
        
        # 선택된 유의어와 고정값을 순서대로 배치
        current_synonym_idx = 0
        for key in ordered_keys:
            if key in col_selection:
                val = str(row.iloc[col_map[key]]).strip()
                if not val:  # 빈 값이면 스킵
                    continue
                ordered_result.append(selected_synonyms[current_synonym_idx])
                current_synonym_idx += 1
            else:
                val = str(row.iloc[col_map[key]]).strip()
                if val:  # 빈 값이 아닌 경우만 추가
                    ordered_result.append(val)
        
        final_text = " ".join(filter(None, ordered_result))
        final_text = clean_text(final_text)  # 최종 결과에 clean_text 적용
        return final_text, total_combinations
        
    return " ".join(filter(None, fixed_values)), 0 