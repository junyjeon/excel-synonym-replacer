import pandas as pd
import re
from itertools import product

# transform.py
def replace_with_synonyms_in_row(row, col_selection, synonym_dict):
    """
    row: pandas.Series (한 행)
    col_selection: ["브랜드","색상","패턴","소재","카테고리"] 중 사용자가 체크한 항목
    synonym_dict: {원본단어: [유의어1, ...], ...}

    B열=1(브랜드), C열=2(색상), D열=3(패턴), E열=4(소재), F열=5(카테고리)
    -> 해당 항목만 유의어 치환, 그리고 'M열'에 들어갈 문자열로 합침
    """
    col_map = {
        "브랜드": 1,
        "색상": 2,
        "패턴": 3,
        "소재": 4,
        "카테고리": 5
    }

    pieces = []
    for key in ["브랜드","색상","패턴","소재","카테고리"]:
        val = str(row[col_map[key]]) if col_map[key] < len(row) else ""
        val = val.strip()
        if key in col_selection:
            # 유의어 치환 (첫 번째만)
            if val in synonym_dict:
                replacement = synonym_dict[val][0]
                pieces.append(replacement)
            else:
                pieces.append(val)
        else:
            # 선택 안 된 열은 그대로
            pieces.append(val)

    # M열: 단순히 " "로 join
    new_title = " ".join(pieces)
    return new_title

def clean_text(text: str) -> str:
    """특수문자와 불필요한 단어 제거"""
    # 제거할 패턴들
    patterns = [
        r'\s*\[[^\]]+\]',  # [S], [없음] 등 대괄호 내용
        r'\^+',            # ^ 기호
        r'&+',             # & 기호
        r'폴리\b',         # 폴리 (단어 끝)
        r'\b무지\b',       # 무지 (단어)
        r'\b패턴\b',       # 패턴 (단어)
        r'\(.*?\)',        # (in&out) 등 괄호 내용
    ]
    
    result = text
    for pattern in patterns:
        result = re.sub(pattern, '', result)
    
    # 연속된 공백을 하나로
    result = ' '.join(result.split())
    return result.strip()

def replace_with_synonyms_in_row_v(row, col_selection, synonym_dict, version_idx):
    """
    주어진 행의 선택된 열들에 대해 가능한 모든 유의어 조합을 생성
    
    Args:
        row: 처리할 데이터 행 (pandas.Series)
        col_selection: 유의어 치환을 수행할 열 목록 ["색상", "패턴" 등]
        synonym_dict: 각 열별 유의어 사전 {"색상": {"블랙": ["검정", "진검정"]} 등}
        version_idx: 조합 버전 인덱스 (0부터 시작)
    """
    try:
        # 1. 열 위치 매핑
        col_map = {
            "색상": 2,
            "패턴": 3,
            "소재": 4,
            "카테고리": 5
        }
            
        # 2. 각 키별 유의어 리스트 수집
        ordered_keys = ["색상", "패턴", "소재", "카테고리"]
        synonym_lists = []
        original_values = []
        
        for key in ordered_keys:
            if key not in col_selection:
                continue
                
            val = str(row.iloc[col_map[key]]).strip()
            val = clean_text(val)
            
            if not val:
                continue
                
            original_values.append(val)
            
            if key in synonym_dict:
                if val in synonym_dict[key]:
                    synonyms = synonym_dict[key][val]
                    if synonyms:
                        synonym_lists.append(synonyms)
                    else:
                        synonym_lists.append([val])
                else:
                    synonym_lists.append([val])
            else:
                synonym_lists.append([val])

        # 3. 모든 가능한 조합 생성
        all_combinations = list(product(*synonym_lists))
        total_combinations = len(all_combinations)
        
        # 4. 현재 version에 해당하는 조합 선택
        if total_combinations > 0:
            current_combination = all_combinations[version_idx % total_combinations]
            print(f"조합 {version_idx % total_combinations + 1}/{total_combinations}: {' '.join(current_combination)}")
            return " ".join(current_combination)
        
        return " ".join(original_values)
        
    except Exception as e:
        print(f"Error in replacement: {e}")
        return f"ERROR: {str(e)}"