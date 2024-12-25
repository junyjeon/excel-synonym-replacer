# synonyms_manager.py
import openpyxl

def load_synonym_dict_from_sheets(excel_path: str, sheet_names=None) -> dict:
    """유의어 사전 로드"""
    if sheet_names is None:
        sheet_names = ["브랜드", "색상", "패턴", "소재", "카테고리"]
        
    try:
        wb = openpyxl.load_workbook(excel_path, data_only=True)
        synonym_dict = {}
        
        for category in sheet_names:
            if category not in wb.sheetnames:
                continue
                
            ws = wb[category]
            synonym_dict[category] = {}
            
            # 데이터가 있는 마지막 행까지만 처리
            max_row = ws.max_row
            while max_row > 1:
                if ws.cell(row=max_row, column=1).value:
                    break
                max_row -= 1
            
            # A열=원본, B~Z열=유의어들
            for row_idx in range(2, max_row + 1):
                orig = ws.cell(row=row_idx, column=1).value
                if not orig:
                    continue
                    
                orig = str(orig).strip()
                synonyms = []
                
                # 콤마로 구분된 데이터 처리
                if ',' in orig:
                    parts = [p.strip() for p in orig.split(',')]
                    if len(parts) > 1:
                        orig = parts[0]
                        synonyms.extend(parts[1:])
                
                # B열부터 순차적으로 유의어 처리
                for col_idx in range(2, ws.max_column + 1):
                    syn = ws.cell(row=row_idx, column=col_idx).value
                    if syn:
                        syn = str(syn).strip()
                        if col_idx == 5:  # E열인 경우
                            # 콤마로 구분된 데이터를 분리
                            gpt_synonyms = [s.strip() for s in syn.split(',')]
                            synonyms.extend(gpt_synonyms)
                        else:
                            synonyms.append(syn)
                
                if synonyms:  # 유의어가 있을 때만 추가
                    synonym_dict[category][orig] = synonyms
                    
        return synonym_dict
        
    except Exception as e:
        print(f"유의어 사전 로드 실패: {str(e)}")
        return {}
