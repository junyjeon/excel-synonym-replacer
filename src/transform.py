import pandas as pd
import openpyxl
from title_generator import create_title_combination

def generate_titles(excel_path: str, sheet_name: str, col_selection: list, 
                   synonym_dict: dict, selected_rows=None, num_versions=3,
                   progress_callback=None, log_callback=None, model=None,
                   overwrite=True):
    """엑셀 파일의 제목들을 유의어로 변환하여 M, N, O열에 저장"""
    try:
        wb = openpyxl.load_workbook(excel_path)
        ws = wb[sheet_name]
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        
        titles_by_row = {}  # 행별 데이터 저장
        
        rows_to_process = selected_rows or range(2, len(df) + 2)
        
        if log_callback:
            log_callback(f"처리 시작: 총 {len(rows_to_process)}개 행")
        
        if log_callback:
            log_callback(f"\n선택된 카테고리: {col_selection}")
            log_callback(f"유의어 사전 내용: {synonym_dict}")
        
        for i, row_idx in enumerate(rows_to_process, 1):
            try:
                current_row = df.iloc[row_idx - 2]
                
                if log_callback:
                    log_callback(f"\n=== {row_idx}행 처리 중 ===")
                
                titles = []  # 각 행마다 새로운 titles 리스트
                
                # 버전 생성
                for version in range(num_versions):
                    new_title, _ = create_title_combination(
                        current_row, col_selection, synonym_dict, version
                    )
                    if new_title and not new_title.startswith("ERROR"):
                        if new_title not in titles:
                            titles.append(new_title)
                            if log_callback:
                                log_callback(f"버전 {len(titles)}: {new_title}")  # 실제 생성된 순서대로
                
                titles_by_row[row_idx] = titles  # 행별 데이터 저장
                
                # 엑셀에 저장
                for col_idx, title in enumerate(titles[:num_versions]):
                    cell = ws.cell(row=row_idx, column=13 + col_idx)
                    if overwrite or not cell.value:
                        cell.value = title
                
                if progress_callback:
                    progress_callback(i, len(rows_to_process))
                    
            except Exception as e:
                if log_callback:
                    log_callback(f"[오류] {row_idx}행 처리 실패: {str(e)}")
                continue
        
        # 파일 저장
        wb.save(excel_path)
        
        # UI 업데이트
        if model:
            for row_idx in rows_to_process:
                titles = titles_by_row.get(row_idx, [])
                for col_idx, title in enumerate(titles[:num_versions]):
                    model.update_cell(row_idx-2, 12+col_idx, title)
        
        if log_callback:
            log_callback("\n완료! M, N, O열에 저장되었습니다.")
        
    except Exception as e:
        if log_callback:
            log_callback(f"[오류] 처리 중단: {str(e)}")