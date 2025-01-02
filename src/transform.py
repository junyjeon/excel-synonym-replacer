import pandas as pd
import openpyxl
from title_generator import create_title_combination
from openpyxl.utils.cell import get_column_letter
import time

def generate_titles(file_path, sheet_name, col_selection, synonym_dict, selected_rows, 
                   version_count, progress_callback, log_callback, model, overwrite=True):
    """
    유의어 치환으로 새로운 제목 생성
    
    Args:
        ...
        overwrite (bool): 기존 제목을 덮어쓸지 여부
    """
    try:
        wb = None
        wb_values = None
        try:
            # 수식용과 값용 워크북을 따로 열기
            wb = openpyxl.load_workbook(file_path)  # 수식 보존용
            wb_values = openpyxl.load_workbook(file_path, data_only=True)  # 값 읽기용
            
            ws = wb[sheet_name]
            ws_values = wb_values[sheet_name]

            # DataFrame은 계산된 값으로 만들기
            if model:
                df = model._df.copy()
            else:
                data = []
                headers = []
                for cell in ws[1]:  # 헤더는 수식이 없으므로 그대로
                    headers.append(cell.value)
                
                for row in ws_values.iter_rows(min_row=2):  # 데이터는 계산된 값으로
                    row_data = []
                    for cell in row:
                        value = cell.value if cell.value is not None else ''
                        row_data.append(str(value))
                    data.append(row_data)
                
                df = pd.DataFrame(data, columns=headers)

            # 상품명 열이 없으면 추가
            for ver in range(1, version_count + 1):
                col_name = f'상품명_{ver}'
                if col_name not in df.columns:
                    df[col_name] = ''

            # 디버깅: 실제 컬럼명 출력
            print("\n=== 엑셀 파일의 실제 컬럼명 ===")
            print(df.columns.tolist())

            # 필요한 컬럼 매핑 (실제 엑셀 컬럼명이 다를 수 있음)
            column_mapping = {
                '브랜드': ['브랜드', 'brand', '브랜드명'],
                '색상': ['색상', 'color', '컬러'],
                '패턴': ['패턴', 'pattern'],
                '소재': ['소재', '소재 ', 'material', '재질'],
                '카테고리': ['카테고리', 'category', '분류']
            }

            # 실제 컬럼명으로 매핑
            actual_columns = {}
            for key, possible_names in column_mapping.items():
                found = False
                # 실제 컬럼명에서 앞뒤 공백을 제거하고 비교
                for name in possible_names:
                    if any(name.strip() == col.strip() for col in df.columns):
                        # 매칭된 실제 컬럼명 찾기
                        actual_name = next(col for col in df.columns if name.strip() == col.strip())
                        actual_columns[key] = actual_name
                        found = True
                        break
                if not found:
                    raise Exception(f"'{key}' 컬럼을 찾을 수 없습니다. 가능한 이름: {possible_names}")

            # 컬럼 인덱스 계산
            col_indices = {key: df.columns.get_loc(actual_name) 
                         for key, actual_name in actual_columns.items()}

            if not selected_rows:
                selected_rows = range(2, ws.max_row + 1)

            if log_callback:
                log_callback(f"처리 시작: 총 {len(selected_rows)}개 행")

            # 각 선택된 행에 대해 처리
            for i, row_idx in enumerate(selected_rows, 1):
                try:
                    # DataFrame에서 데이터 읽기 - 매핑된 컬럼명 사용
                    current_row = pd.Series({
                        key: str(df.iloc[row_idx-2, col_indices[key]]).strip()
                        for key in column_mapping.keys()
                    })

                    # 유의어 치환으로 새 제목들 생성
                    titles = []
                    for version in range(version_count):
                        new_title, _ = create_title_combination(current_row, col_selection, synonym_dict, version)
                        if new_title and not new_title.startswith("ERROR"):
                            titles.append(new_title)

                    # M열만 수정하고 저장
                    for ver, title in enumerate(titles):
                        col_idx = 13 + ver  # M열이 13번째 열
                        if overwrite:
                            ws.cell(row=row_idx, column=col_idx, value=title)
                            if model:
                                model._df.iloc[row_idx-2, col_idx-1] = title
                                model.update_cell(row_idx-2, col_idx-1, title)
                        else:
                            old_value = ws.cell(row=row_idx, column=col_idx).value
                            if not old_value:
                                ws.cell(row=row_idx, column=col_idx, value=title)
                                if model:
                                    model._df.iloc[row_idx-2, col_idx-1] = title
                                    model.update_cell(row_idx-2, col_idx-1, title)

                    if progress_callback:
                        progress_callback(i, len(selected_rows))

                except Exception as row_error:
                    print(f"행 {row_idx} 처리 중 오류: {str(row_error)}")
                    if log_callback:
                        log_callback(f"행 {row_idx} 처리 중 오류: {str(row_error)}")
                    continue

            # 변경사항 저장
            wb.save(file_path)

        finally:
            if wb:
                wb.close()

        time.sleep(0.1)  # 파일 시스템 동기화 대기

        if log_callback:
            log_callback("\n완료!")

    except Exception as e:
        print(f"\n=== 오류 발생 ===\n{str(e)}")
        raise Exception(f"제목 생성 중 오류 발생: {str(e)}")