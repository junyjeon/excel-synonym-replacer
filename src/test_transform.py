import pandas as pd
import openpyxl
from transform import generate_titles
import os

def test_generate_titles():
    # 1. 테스트용 엑셀 파일 생성
    test_df = pd.DataFrame({
        'A': ['', '', ''],
        'B': ['아디다스', 'US폴로아센', '더엣지'],     # 브랜드
        'C': ['블랙', '네이비', '스카이블루'],         # 색상
        'D': ['무지', '스트라이프', '도트무늬'],       # 패턴
        'E': ['면', '폴리', '마혼방'],                # 소재
        'F': ['맨투맨', '맨투맨티', '니트카라티']      # 카테고리
    })
    
    test_file = "test_data.xlsx"
    test_df.to_excel(test_file, index=False)
    
    # 2. 실제 유의어 사전
    test_dict = {
        "브랜드": {
            "아디다스": ["ADIDAS"],
            "US폴로아센": ["U.S. Polo Assn."],
            "더엣지": ["THE EDGE"]
        },
        "색상": {
            "블랙": ["BLACK", "검정색"],
            "네이비": ["NAVY", "곤색"],
            "스카이블루": ["SKYBLUE", "하늘색"]
        },
        "패턴": {
            "스트라이프": ["줄무늬", "선무늬", "라인"],
            "도트무늬": ["땡땡이", "물방울", "폴카"]
        },
        "소재": {
            "면": ["코튼", "목화", "면직물"],
            "마혼방": ["리넨믹스", "린넨블렌드", "리넨혼합"]
        }
    }
    
    test_cases = [
        {
            "name": "첫 행 - 브랜드/색상/소재",
            "row": 2,
            "col_selection": ["브랜드", "색상", "소재"],
            "expected": {
                "M": "ADIDAS BLACK 코튼 맨투맨",      # version 0
                "N": "ADIDAS BLACK 목화 맨투맨",      # version 1
                "O": "ADIDAS BLACK 면직물 맨투맨"     # version 2
            }
        },
        {
            "name": "두 번째 행 - 패턴 포함",
            "row": 3,
            "col_selection": ["브랜드", "패턴"],
            "expected": {
                "M": "U.S. Polo Assn. 네이비 줄무늬 맨투맨티",
                "N": "U.S. Polo Assn. 네이비 선무늬 맨투맨티",
                "O": "U.S. Polo Assn. 네이비 라인 맨투맨티"
            }
        }
    ]
    
    try:
        for case in test_cases:
            print(f"\n=== {case['name']} 테스트 ===")
            
            generate_titles(
                excel_path=test_file,
                sheet_name="Sheet1",
                col_selection=case["col_selection"],
                synonym_dict=test_dict,
                selected_rows=[case["row"]],
                num_versions=3,
                overwrite=True
            )
            
            # 결과 검증
            wb = openpyxl.load_workbook(test_file)
            ws = wb["Sheet1"]
            
            for col, expected in case["expected"].items():
                col_idx = ord(col) - ord('A') + 1
                actual = ws.cell(row=case["row"], column=col_idx).value
                print(f"{col}열 검증:")
                print(f"기대값: {expected}")
                print(f"실제값: {actual}")
                assert actual == expected, f"{col}열 값이 일치하지 않습니다"
            
            print("테스트 성공!")
            
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == "__main__":
    test_generate_titles() 