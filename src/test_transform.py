import pandas as pd
import openpyxl
from transform import generate_titles
import os

def test_generate_titles():
    # 1. 테스트용 엑셀 파일 생성
    test_df = pd.DataFrame({
        'A': ['', '', ''],
        'B': ['아디다스', 'US폴로아센', '더엣지'],
        'C': ['블랙', '네이비', '스카이블루'],
        'D': ['무지', '스트라이프', '도트무늬'],
        'E': ['면', '폴리', '마혼방'],
        'F': ['맨투맨', '맨투맨티', '니트카라티'],
    }, dtype=str)  # 모든 열을 문자열로 설정

    # 유의어 열 추가
    for ver in range(1, 4):
        test_df[f'유의어_{ver}'] = ''

    test_df = test_df.astype(str)  # 전체 DataFrame을 문자열로 변환
    
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
            "블랙": ["진검정", "흑색", "검정색"],
            "네이비": ["곤색", "남색", "짙은파랑"],
            "스카이블루": ["하늘색", "연파랑", "옅랑"]
        },
        "패턴": {
            "스트라이프": ["줄무늬", "선무늬", "라인"],
            "도트무늬": ["땡땡이", "물방울", "폴카"]
        },
        "소재": {
            "면": ["코튼", "목화", "순면"],
            "마혼방": ["리넨믹스", "린넨블렌드", "리넨혼합"]
        }
    }
    
    test_cases = [
        {
            "name": "첫 행 - 브랜드/색상/소재",
            "row": 2,
            "col_selection": ["브랜드", "색상", "소재"],
            "expected": {
                "M": "ADIDAS 진검정 코튼 맨투맨",      # version 0
                "N": "ADIDAS 흑색 코튼 맨투맨",       # version 1
                "O": "ADIDAS 검정색 코튼 맨투맨"      # version 2
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
                file_path=test_file,
                sheet_name="Sheet1",
                col_selection=case["col_selection"],
                synonym_dict=test_dict,
                selected_rows=[case["row"]],
                version_count=3,
                progress_callback=None,
                log_callback=print,
                model=None,
                overwrite=True
            )
            
            # 결과 검증
            result_df = pd.read_excel(test_file)  # 먼저 DataFrame으로 읽기
            
            for col, expected in case["expected"].items():
                col_name = f'유의어_{ord(col) - ord("M") + 1}'  # M -> 유의어_1
                actual = result_df[col_name].iloc[case["row"]-2]  # 0-based index
                print(f"{col}열 ({col_name}) 검증:")
                print(f"기대값: {expected}")
                print(f"실제값: {actual}")
                assert actual == expected, f"{col}열 값이 일치하지 않습니다"
            
            print("테스트 성공!")
            
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == "__main__":
    test_generate_titles() 