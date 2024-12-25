# synonyms_manager.py
import openpyxl

def load_synonym_dict_from_sheets(excel_path: str, sheet_names=None) -> dict:
    """
    여러 시트(브랜드, 색상, 패턴, 소재, 카테고리)에서
    A열=원본단어, B,C,D열=유의어1,2,3 을 읽어옴
    반환되는 사전의 구조:
    {
        "색상": {
            "블랙": ["블랙", "검정", "진검정"],  # 첫 번째는 항상 원본 단어
            "네이비": ["네이비", "곤색"]
        },
        "소재": {
            "면": ["면", "코튼", "순면"]
        }
    }
    """
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    if sheet_names is None:
        sheet_names = ["브랜드","색상","패턴","소재","카테고리"]

    # 카테고리별로 유의어 사전 생성
    synonym_dict = {sname: {} for sname in sheet_names}
    
    for sname in sheet_names:
        if sname not in wb.sheetnames:
            continue
            
        ws = wb[sname]
        max_row = ws.max_row
        
        for row_idx in range(2, max_row + 1):
            orig = ws.cell(row=row_idx, column=1).value  # A열
            if not orig:
                continue
            
            orig_str = str(orig).strip()
            synonyms = [orig_str]  # 원본 단어를 첫 번째로 포함
            
            # B,C,D열(유의어1,2,3) 모두 읽기
            for col_idx in range(2, 5):
                syn = ws.cell(row=row_idx, column=col_idx).value
                if syn:
                    synonyms.append(str(syn).strip())
            
            # 항상 사전에 추가 (유의어가 없어도)
            synonym_dict[sname][orig_str] = synonyms

    return synonym_dict
