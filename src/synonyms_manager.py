# synonyms_manager.py
import openpyxl

def load_synonym_dict_from_sheets(excel_path: str, sheet_names=None) -> dict:
    """
    여러 시트(브랜드, 색상, 패턴, 소재, 카테고리)가
    A열=원본단어, B열=콤마 구분 유의어 로 저장되어 있다고 가정.
    """
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    if sheet_names is None:
        sheet_names = ["브랜드","색상","패턴","소재","카테고리"]

    synonym_dict = {}
    for sname in sheet_names:
        if sname not in wb.sheetnames:
            continue
        ws = wb[sname]
        max_row = ws.max_row
        for row_idx in range(2, max_row + 1):
            orig = ws.cell(row=row_idx, column=1).value  # A열
            syns_str = ws.cell(row=row_idx, column=2).value # B열
            if not orig or not syns_str:
                continue
            orig_str = str(orig).strip()
            splitted = [x.strip() for x in str(syns_str).split(",") if x.strip()]
            if orig_str not in synonym_dict:
                synonym_dict[orig_str] = set()
            for w in splitted:
                synonym_dict[orig_str].add(w)

    # set -> list
    final_dict = {}
    for k, v in synonym_dict.items():
        final_dict[k] = list(v)
    return final_dict
