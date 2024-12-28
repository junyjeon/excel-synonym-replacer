from text_cleaner import clean_text

def create_title_combination(row, col_selection, synonym_dict, version_idx):
    col_map = {
        "브랜드": 1, "색상": 2, "패턴": 3, "소재": 4, "카테고리": 5
    }
    ordered_keys = ["브랜드", "색상", "패턴", "소재", "카테고리"]
    
    ordered_lists = []
    ordered_selections = []
    fixed_values = {}
    
    for key in ordered_keys:
        val = str(row.iloc[col_map[key]]).strip()
        
        # 1. 먼저 원본값으로 패턴 체크
        if not val or (key == "패턴" and val == "무지"):
            continue
            
        # 2. clean_text 실행
        val = clean_text(val)
        if not val:  # clean_text로 제거되면 스킵
            continue
            
        # 3. 유의어 매칭
        if key in col_selection:
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
            val = ordered_lists[current_synonym_idx][selected_indices[current_synonym_idx]]
            result.append(val.strip())  # 앞뒤 공백 제거
            current_synonym_idx += 1
        else:
            # 선택되지 않은 카테고리는 원본 값 사용
            val = fixed_values.get(key, '')
            if val:
                result.append(val.strip())  # 앞뒤 공백 제거
    
    # 결과 문자열 생성 (공백으로 구분)
    final_text = ' '.join(result)  # filter(None, result) 제거
    
    return final_text, total_combinations 