import pandas as pd
import openpyxl
from title_generator import create_title_combination
from openpyxl.utils.cell import get_column_letter
import time

def generate_titles(file_path, sheet_name, col_selection, synonym_dict, selected_rows, 
                   version_count, progress_callback, log_callback, model, overwrite=True):
    """유의어 치환으로 새로운 제목 생성"""
    try:
        wb = None
        try:
            # 수식용 워크북 열기
            wb = openpyxl.load_workbook(file_path)
            ws = wb[sheet_name]

            # DataFrame은 모델에서 가져오기
            if model:
                df = model._df.copy()
            else:
                raise Exception("모델이 없습니다.")

            # 상품명 열이 없으면 추가 (모든 버전에 대해)
            for ver in range(1, version_count + 1):
                col_name = f'상품명_{ver}'
                if col_name not in df.columns:
                    df[col_name] = ''

            # 실제 컬럼명 매핑 (체크된 항목만)
            actual_columns = {}
            for key in col_selection:  # 체크된 항목만 처리
                possible_names = {
                    '브랜드': ['브랜드', 'brand', '브랜드명'],
                    '색상': ['색상', 'color', '컬러'],
                    '패턴': ['패턴', 'pattern'],
                    '소재': ['소재', '소재 ', 'material', '재질'],
                    '카테고리': ['카테고리', 'category', '분류']
                }.get(key, [key])

                # 실제 컬럼 찾기 (없으면 스킵)
                for name in possible_names:
                    if any(col.strip() == name.strip() for col in df.columns):
                        actual_name = next(col for col in df.columns if col.strip() == name.strip())
                        actual_columns[key] = actual_name
                        break

            if not selected_rows:
                selected_rows = range(2, len(df) + 2)

            if log_callback:
                log_callback(f"처리 시작: 총 {len(selected_rows)}개 행")

            # 각 선택된 행에 대해 처리
            for i, row_idx in enumerate(selected_rows, 1):
                try:
                    # DataFrame에서 데이터 읽기 (매핑된 컬럼만)
                    current_row = {}
                    for key, col_name in actual_columns.items():
                        value = str(df.iloc[row_idx-2][col_name]).strip()
                        current_row[key] = value

                    # 유의어 치환으로 새 제목들 생성
                    titles = []
                    for version in range(version_count):
                        new_title, _ = create_title_combination(
                            pd.Series(current_row), 
                            col_selection, 
                            synonym_dict, 
                            version
                        )
                        if new_title and not new_title.startswith("ERROR"):
                            titles.append(new_title)

                    # 제목 열 업데이트 (모든 버전)
                    for ver, title in enumerate(titles, 1):
                        col_name = f'상품명_{ver}'
                        if overwrite or not df.iloc[row_idx-2][col_name]:
                            df.iloc[row_idx-2, df.columns.get_loc(col_name)] = title
                            if model:
                                model.update_cell(row_idx-2, df.columns.get_loc(col_name), title)

                    if progress_callback:
                        progress_callback(i, len(selected_rows))

                except Exception as row_error:
                    print(f"행 {row_idx} 처리 중 오류: {str(row_error)}")
                    if log_callback:
                        log_callback(f"행 {row_idx} 처리 중 오류: {str(row_error)}")
                    continue

            # 변경사항 저장
            df.to_excel(file_path, index=False)

        finally:
            if wb:
                wb.close()

        if log_callback:
            log_callback("\n완료!")

    except Exception as e:
        print(f"\n=== 오류 발생 ===\n{str(e)}")
        raise Exception(f"제목 생성 중 오류 발생: {str(e)}")