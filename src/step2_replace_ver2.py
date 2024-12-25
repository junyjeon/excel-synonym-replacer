import pandas as pd
from itertools import product

def read_excel_sheets():
    # 엑셀 파일 경로 지정
    excel_path = '/home/jun/12_Desember/pyside6-excel-renamer/src/제목생성+1.1.xlsx'
    
    try:
        # 각 시트를 다른 데이터프레임으로 읽기
        df_color = pd.read_excel(excel_path, sheet_name='색상')
        df_pattern = pd.read_excel(excel_path, sheet_name='패턴')
        df_material = pd.read_excel(excel_path, sheet_name='소재')
        
        # 각 열의 첫 번째 값을 기준으로 리스트 생성
        colors = df_color.iloc[:, 0].dropna().tolist()
        patterns = df_pattern.iloc[:, 0].dropna().tolist()
        materials = df_material.iloc[:, 0].dropna().tolist()
        
        # 모든 조합 생성
        combinations = list(product(colors, patterns, materials))
        
        # 결과 출력
        print("\n=== 모든 가능한 조합 ===")
        print(f"총 {len(combinations)}개의 조합이 생성되었습니다.\n")
        
        for i, (color, pattern, material) in enumerate(combinations, 1):
            print(f"조합 {i:3d}: {color}-{pattern}-{material}")
        
        return df_color, df_pattern, df_material, combinations
    
    except FileNotFoundError:
        print("파일을 찾을 수 없습니다.")
        return None, None, None, None
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        return None, None, None, None

if __name__ == "__main__":
    color_df, pattern_df, material_df, all_combinations = read_excel_sheets()

# def read_excel_file():
#     # 엑셀 파일 경로 지정
#     excel_path = '/home/jun/12_Desember/pyside6-excel-renamer/src/제목생성+1.1.xlsx'
    
#     try:
#         # 엑셀 파일 읽기
#         df = pd.read_excel(excel_path)
        
#         # 데이터 출력
#         print("엑셀 파일 내용:")
#         print(df)
        
#         return df
    
#     except FileNotFoundError:
#         print("파일을 찾을 수 없습니다.")
#         return None
#     except Exception as e:
#         print(f"오류 발생: {str(e)}")
#         return None