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
    try:
        # 선택된 컬럼별 유의어 리스트
        ordered_lists = []
        ordered_selections = []
        fixed_values = {}
        
        # 순서가 있는 컬럼 처리 (브랜드 → 색상 → 패턴 → 소재 → 카테고리)
        ordered_columns = ['브랜드', '색상', '패턴', '소재', '카테고리']
        
        # 각 컬럼 처리
        for key in ordered_columns:
            # 컬럼이 없거나 값이 비어있는 경우 빈 문자열로 처리
            value = str(row.get(key, '')).strip()
            
            # 유의어 확인 - 선택된 컬럼만 치환
            if key in synonym_dict and key in col_selection and value:  # 값이 있는 경우만 치환 시도
                synonyms = []
                
                # 직접 매칭 확인
                for dict_key, syn_list in synonym_dict[key].items():
                    # 대소문자 구분 없이 매칭
                    if value.lower().strip() == dict_key.lower().strip():
                        if isinstance(syn_list, str):  # 단일 문자열이면 리스트로 변환
                            synonyms = [syn_list]
                        else:
                            synonyms = syn_list
                        break
                
                if synonyms:
                    ordered_lists.append(synonyms)
                    ordered_selections.append(key)
                else:
                    fixed_values[key] = value  # 사전에 없으면 원본값
            else:
                fixed_values[key] = value  # 선택 안된 컬럼은 원본값
        
        # 버전에 따른 인덱스 계산
        total_combinations = 1
        for synonyms in ordered_lists:
            total_combinations *= len(synonyms)
            
        selected_indices = []
        remaining = version_idx % total_combinations if ordered_lists else 0
        
        for synonyms in ordered_lists:
            idx = remaining % len(synonyms)
            selected_indices.append(idx)
            remaining //= len(synonyms)
        
        # 결과 문자열 생성 - ordered_columns 순서 유지
        result = []
        for key in ordered_columns:
            if key in ordered_selections:
                idx = ordered_selections.index(key)
                value = ordered_lists[idx][selected_indices[idx]]
                if value:  # 빈 값이 아닌 경우만 추가
                    result.append(value)
            elif key in fixed_values and fixed_values[key]:  # 빈 값이 아닌 경우만 추가
                result.append(fixed_values[key])
        
        final_text = ' '.join(filter(None, result))
        final_text = clean_text(final_text)  # 불필요 단어 제거
        
        return final_text, total_combinations if ordered_lists else 1
        
    except Exception as e:
        print(f"[ERROR] create_title_combination: {str(e)}")
        return f"ERROR: {str(e)}", 0 