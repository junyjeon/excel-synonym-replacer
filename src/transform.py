import pandas as pd
import openpyxl
from title_generator import create_title_combination

def generate_titles(file_path, sheet_name, col_selection, synonym_dict, selected_rows, 
                   version_count, progress_callback, log_callback, model, overwrite=True):
    """
    유의어 치환으로 새로운 제목 생성
    
    Args:
        ...
        overwrite (bool): 기존 제목을 덮어쓸지 여부
    """
    try:
        wb = openpyxl.load_workbook(file_path)
        ws = wb[sheet_name]
        
        # 문자열로 읽기
        df = pd.read_excel(file_path, sheet_name=sheet_name, dtype=str)
        
        # 상품명 열이 없으면 추가
        for ver in range(1, version_count + 1):
            col_name = f'상품명_{ver}'
            if col_name not in df.columns:
                df[col_name] = ''
        
        df = df.astype(str)  # 모든 열을 문자열로 변환
        
        rows_to_process = selected_rows or range(2, len(df) + 2)
        
        if log_callback:
            log_callback(f"처리 시작: 총 {len(rows_to_process)}개 행")
            log_callback(f"\n선택된 카테고리: {col_selection}")
        
        for i, row_idx in enumerate(rows_to_process, 1):
            try:
                current_row = df.iloc[row_idx - 2]
                
                if log_callback:
                    log_callback(f"\n=== {row_idx}행 처리 중 ===")
                
                titles = []  # 각 행마다 새로운 titles 리스트
                
                # 여러 버전 생성
                for version in range(version_count):
                    new_title, _ = create_title_combination(
                        current_row, col_selection, synonym_dict, version
                    )
                    if new_title and not new_title.startswith("ERROR"):
                        titles.append(new_title)
                        if log_callback:
                            log_callback(f"버전 {len(titles)}: {new_title}")
                
                if titles:  # 생성된 제목이 있는 경우
                    for ver, title in enumerate(titles, 1):  # 1부터 시작
                        col_name = f'상품명_{ver}'  # 열 이름으로 접근
                        if overwrite:
                            # 무조건 덮어쓰기
                            df.loc[row_idx-2, col_name] = str(title)  # 문자열로 명시적 변환
                            if model:
                                model.update_cell(row_idx-2, 12+ver-1, title)
                        else:
                            # 기존 데이터가 있으면 건드리지 않음
                            current_title = df.loc[row_idx-2, col_name]
                            if pd.isna(current_title) or current_title.strip() == '':
                                df.loc[row_idx-2, col_name] = str(title)
                                if model:
                                    model.update_cell(row_idx-2, 12+ver-1, title)
                
                if progress_callback:
                    progress_callback(i, len(rows_to_process))
                    
            except Exception as e:
                if log_callback:
                    log_callback(f"[오류] {row_idx}행 처리 실패: {str(e)}")
                continue
        
        # 디버깅: 저장 전 상태 확인
        if log_callback:
            log_callback("\n=== 저장 전 DataFrame ===")
            log_callback(f"컬럼 목록: {df.columns.tolist()}")
            log_callback(f"데이터:\n{df}")
        
        # 변경된 데이터프레임 저장
        df = df.astype(str)
        df.to_excel(file_path, sheet_name=sheet_name, index=False)
        
        # 디버깅: 저장 후 상태 확인
        wb = openpyxl.load_workbook(file_path)
        ws = wb[sheet_name]
        if log_callback:
            log_callback("\n=== 저장 후 Excel ===")
            for col in ['M', 'N', 'O']:
                col_idx = 13 + (ord(col) - ord('M'))
                val = ws.cell(row=2, column=col_idx).value
                log_callback(f"{col}열 값: {val}")
        
        wb.save(file_path)
        
        if log_callback:
            log_callback("\n완료!")
        
    except Exception as e:
        raise Exception(f"제목 생성 중 오류 발생: {str(e)}")