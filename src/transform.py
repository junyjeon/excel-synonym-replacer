import pandas as pd
import re

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
    row: 한 행
    col_selection: 체크된 항목
    synonym_dict: {원본단어: [유의어1,...]}
    version_idx: 0,1,2,... => 유의어 인덱스
    """
    try:
        # 입력 검증
        if not isinstance(row, (pd.Series, dict)):
            raise ValueError("Invalid row type")
            
        # 열 매핑 검증
        col_map = {
            # "브랜드": 1,  # 브랜드 주석처리
            "색상": 2,
            "패턴": 3,
            "소재": 4,
            "카테고리": 5
        }
        
        pieces = []
        # for key in ["브랜드","색상","패턴","소재","카테고리"]:  # 브랜드 제외
        for key in ["색상","패턴","소재","카테고리"]:
            try:
                # 값 가져오고 전처리
                val = str(row.iloc[col_map[key]]).strip()
                val = clean_text(val)
                
                if not val:  # 전처리 후 빈 문자열이면 스킵
                    continue
                    
            except:
                continue
                
            if key in col_selection:  # 선택된 카테고리만 치환
                if val in synonym_dict:
                    syn_list = synonym_dict[val]
                    if syn_list:
                        idx = version_idx % len(syn_list)
                        pick = syn_list[idx]
                        pieces.append(pick)
                        print(f"치환: {val} -> {pick} (버전 {version_idx})")  # 디버깅용
                    else:
                        pieces.append(val)
                else:
                    pieces.append(val)
            else:
                pieces.append(val)
                
        return " ".join(filter(None, pieces))  # 빈 문자열 제거
        
    except Exception as e:
        print(f"Error in replacement: {e}")
        return f"ERROR: {str(e)}"