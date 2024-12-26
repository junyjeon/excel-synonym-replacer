import pandas as pd
import openpyxl
from title_generator import create_title_combination

def generate_titles(excel_path: str, sheet_name: str, col_selection: list, 
                   synonym_dict: dict, selected_rows=None, num_versions=3,
                   progress_callback=None, log_callback=None, model=None,
                   overwrite=True):
    """엑셀 파일의 제목들을 유의어로 변환하여 M, N, O열에 저장"""
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        wb = openpyxl.load_workbook(excel_path)
        ws = wb[sheet_name]
        
        rows_to_process = selected_rows or range(2, len(df) + 2)
        
        if log_callback:
            log_callback(f"처리 시작: 총 {len(rows_to_process)}개 행")
        
        for i, row_idx in enumerate(rows_to_process, 1):
            try:
                current_row = df.iloc[row_idx - 2]
                
                if log_callback:
                    log_callback(f"\n=== {row_idx}행 처리 중 ===")
                
                # 각 버전별로 제목 생성
                titles = []
                
                # 모든 버전을 동일한 방식으로 처리
                for version in range(num_versions):
                    new_title, total_combinations = create_title_combination(
                        current_row, col_selection, synonym_dict, version
                    )
                    if new_title and not new_title.startswith("ERROR"):
                        if new_title not in titles:  # 중복 제거
                            titles.append(new_title)
                            if log_callback:
                                log_callback(f"버전 {len(titles)}: {new_title}")
                
                # 결과 저장
                for col_idx, title in enumerate(titles[:num_versions]):
                    cell = ws.cell(row=row_idx, column=13 + col_idx)
                    if overwrite or not cell.value:
                        cell.value = title
                        if model:
                            model._modified_cells.add((row_idx-2, 12+col_idx))
                
                if progress_callback:
                    progress_callback(i, len(rows_to_process))
                
            except Exception as e:
                if log_callback:
                    log_callback(f"[오류] {row_idx}행 처리 실패: {str(e)}")
                continue
        
        wb.save(excel_path)
        if log_callback:
            log_callback("\n완료! M, N, O열에 저장되었습니다.")
        
    except Exception as e:
        if log_callback:
            log_callback(f"[오류] 처리 중단: {str(e)}")