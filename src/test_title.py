import pandas as pd
from title_generator import create_title_combination

def test_title_generation():
    # 1. 테스트 데이터 설정
    test_row = pd.Series([
        "",         # A열
        "나이키",   # B열 (브랜드)
        "검정",     # C열 (색상)
        "",        # D열 (패턴)
        "면",      # E열 (소재)
        "티셔츠"    # F열 (카테고리)
    ])

    test_dict = {
        "브랜드": {"나이키": ["NIKE"]},
        "색상": {"검정": ["블랙", "BLACK"]},
        "소재": {"면": ["코튼", "cotton"]}
    }

    # 2. 테스트 케이스들
    test_cases = [
        {
            "name": "브랜드만 선택",
            "col_selection": ["브랜드"],
            "expected_first": "NIKE 검정 면 티셔츠"  # 브랜드-색상-소재-카테고리 순서
        },
        {
            "name": "색상만 선택",
            "col_selection": ["색상"],
            "expected_first": "나이키 블랙 면 티셔츠"  # 브랜드-색상-소재-카테고리 순서
        },
        {
            "name": "모두 선택",
            "col_selection": ["브랜드", "색상", "소재"],
            "expected_first": "NIKE 블랙 코튼 티셔츠"  # 브랜드-색상-소재-카테고리 순서
        },
        
        # 추가 케이스들
        {
            "name": "빈 값이 있는 경우",
            "col_selection": ["브랜드", "색상"],  # 패턴은 제외 (빈 값이라)
            "expected_first": "NIKE 블랙 면 티셔츠"
        },
        {
            "name": "유의어가 없는 경우",
            "col_selection": ["브랜드", "카테고리"],  # 카테고리는 유의어 없음
            "expected_first": "NIKE 검정 면 티셔츠"
        },
        {
            "name": "모든 카테고리 선택",
            "col_selection": ["브랜드", "색상", "패턴", "소재", "카테고리"],
            "expected_first": "NIKE 블랙 코튼 티셔츠"
        }
    ]

    # 3. 테스트 실행
    for case in test_cases:
        print(f"\n=== {case['name']} 테스트 ===")
        title, total = create_title_combination(
            test_row,
            case["col_selection"],
            test_dict,
            version_idx=0
        )
        print(f"기대한 첫 버전: {case['expected_first']}")
        print(f"실제 첫 버전: {title}")
        print(f"테스트 결과: {'성공' if title == case['expected_first'] else '실패'}")
        
        # 추가 버전들 확인
        print("\n다음 버전들:")
        for version in range(1, min(3, total)):
            next_title, _ = create_title_combination(
                test_row,
                case["col_selection"],
                test_dict,
                version_idx=version
            )
            print(f"버전 {version+1}: {next_title}")

if __name__ == "__main__":
    test_title_generation() 