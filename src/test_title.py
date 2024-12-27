import pandas as pd
from title_generator import create_title_combination

# ANSI 색상 코드 추가
class Colors:
    RED = '\033[91m'      # 밝은 빨강
    GREEN = '\033[92m'    # 밝은 초록
    RESET = '\033[0m'     # 색상 초기화

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
            "name": "브랜드만 선택",  # 2개
            "col_selection": ["브랜드"],
            "expected_versions": [
                "NIKE 검정 면 티셔츠",      # version 0: (0)
                "나이키 검정 면 티셔츠",     # version 1: (1)
            ]
        },
        {
            "name": "색상만 선택",  # 3개
            "col_selection": ["색상"],
            "expected_versions": [
                "나이키 블랙 면 티셔츠",     # version 0: (0)
                "나이키 BLACK 면 티셔츠",    # version 1: (1)
                "나이키 검정 면 티셔츠",     # version 2: (2)
            ]
        },
        {
            "name": "브랜드/색상 선택",  # 2개 * 3개 = 6개 조합
            "col_selection": ["브랜드", "색상"],
            "expected_versions": [
                "NIKE 블랙 면 티셔츠",       # version 0: (0,0)
                "나이키 블랙 면 티셔츠",      # version 1: (1,0)
                "NIKE BLACK 면 티셔츠",      # version 2: (0,1)
                "나이키 BLACK 면 티셔츠",     # version 3: (1,1)
                "NIKE 검정 면 티셔츠"        # version 4: (0,2)
            ]
        },
        {
            "name": "색상/소재 동시 선택",  # 3개 * 3개 = 9개 조합
            "col_selection": ["색상", "소재"],
            "expected_versions": [
                "나이키 블랙 코튼 티셔츠",       # version 0: (0,0)
                "나이키 BLACK 코튼 티셔츠",      # version 1: (1,0)
                "나이키 검정 코튼 티셔츠",       # version 2: (2,0)
                "나이키 블랙 cotton 티셔츠",     # version 3: (0,1)
                "나이키 BLACK cotton 티셔츠"     # version 4: (1,1)
            ]
        },
        {
            "name": "브랜드/색상/소재 선택",  # 2개 * 3개 * 3개 = 18개 조합
            "col_selection": ["브랜드", "색상", "소재"],
            "expected_versions": [
                "NIKE 블랙 코튼 티셔츠",         # version 0: (0,0,0)
                "나이키 블랙 코튼 티셔츠",        # version 1: (1,0,0)
                "NIKE BLACK 코튼 티셔츠",        # version 2: (0,1,0)
                "나이키 BLACK 코튼 티셔츠",       # version 3: (1,1,0)
                "NIKE 검정 코튼 티셔츠"          # version 4: (0,2,0)
            ]
        },
        {
            "name": "유의어가 없는 경우",  # 카테고리는 유의어 없음
            "col_selection": ["브랜드", "카테고리"],
            "expected_versions": [
                "NIKE 검정 면 티셔츠",      # version 0: (0)
                "나이키 검정 면 티셔츠",     # version 1: (1)
            ]
        },
        {
            "name": "소재만 선택",  # 3개
            "col_selection": ["소재"],
            "expected_versions": [
                "나이키 검정 코튼 티셔츠",     # version 0: (0)
                "나이키 검정 cotton 티셔츠",   # version 1: (1)
                "나이키 검정 면 티셔츠",       # version 2: (2)
            ]
        },
        {
            "name": "브랜드/소재 선택",  # 2개 * 3개 = 6개
            "col_selection": ["브랜드", "소재"],
            "expected_versions": [
                "NIKE 검정 코튼 티셔츠",      # version 0: (0,0)
                "나이키 검정 코튼 티셔츠",     # version 1: (1,0)
                "NIKE 검정 cotton 티셔츠",    # version 2: (0,1)
                "나이키 검정 cotton 티셔츠",   # version 3: (1,1)
                "NIKE 검정 면 티셔츠"         # version 4: (0,2)
            ]
        },
        {
            "name": "빈 값이 있는 경우",  # 패턴은 빈 값
            "col_selection": ["브랜드", "패턴", "소재"],
            "expected_versions": [
                "NIKE 검정 코튼 티셔츠",      # version 0: (0,0)
                "나이키 검정 코튼 티셔츠",     # version 1: (1,0)
                "NIKE 검정 cotton 티셔츠",    # version 2: (0,1)
                "나이키 검정 cotton 티셔츠",   # version 3: (1,1)
                "NIKE 검정 면 티셔츠"         # version 4: (0,2)
            ]
        },
        {
            "name": "유의어가 1개인 경우",  # 카테고리는 유의어 1개
            "col_selection": ["브랜드", "카테고리"],
            "expected_versions": [
                "NIKE 검정 면 티셔츠",      # version 0: (0)
                "나이키 검정 면 티셔츠",     # version 1: (1)
            ]
        },
        {
            "name": "선택된 카테고리 없음",
            "col_selection": [],
            "expected_versions": [
                "나이키 검정 면 티셔츠"  # 원본 그대로
            ]
        },
        {
            "name": "패턴만 선택",  # 빈 값
            "col_selection": ["패턴"],
            "expected_versions": [
                "나이키 검정 면 티셔츠"  # 패턴이 빈 값이라 원본 유지
            ]
        },
        {
            "name": "카테고리만 선택",  # 유의어 없음
            "col_selection": ["카테고리"],
            "expected_versions": [
                "나이키 검정 면 티셔츠"  # 유의어가 없어서 원본 유지
            ]
        },
        {
            "name": "색상/패턴 선택",
            "col_selection": ["색상", "패턴"],
            "expected_versions": [
                "나이키 블랙 면 티셔츠",     # version 0: (0,0)
                "나이키 BLACK 면 티셔츠",    # version 1: (1,0)
                "나이키 검정 면 티셔츠"      # version 2: (2,0)
            ]
        },
        {
            "name": "색상/카테고리 선택",
            "col_selection": ["색상", "카테고리"],
            "expected_versions": [
                "나이키 블랙 면 티셔츠",     # version 0: (0)
                "나이키 BLACK 면 티셔츠",    # version 1: (1)
                "나이키 검정 면 티셔츠"      # version 2: (2)
            ]
        },
        {
            "name": "브랜드/패턴 선택",  # 패턴은 빈 값
            "col_selection": ["브랜드", "패턴"],
            "expected_versions": [
                "NIKE 검정 면 티셔츠",      # version 0: (0)
                "나이키 검정 면 티셔츠"      # version 1: (1)
            ]
        },
        {
            "name": "패턴/소재 선택",
            "col_selection": ["패턴", "소재"],
            "expected_versions": [
                "나이키 검정 코튼 티셔츠",     # version 0: (0,0)
                "나이키 검정 cotton 티셔츠",   # version 1: (0,1)
                "나이키 검정 면 티셔츠"        # version 2: (0,2)
            ]
        },
        {
            "name": "패턴/카테고리 선택",
            "col_selection": ["패턴", "카테고리"],
            "expected_versions": [
                "나이키 검정 면 티셔츠"  # 둘 다 변경 없음
            ]
        },
        {
            "name": "소재/카테고리 선택",
            "col_selection": ["소재", "카테고리"],
            "expected_versions": [
                "나이키 검정 코튼 티셔츠",     # version 0: (0)
                "나이키 검정 cotton 티셔츠",   # version 1: (1)
                "나이키 검정 면 티셔츠"        # version 2: (2)
            ]
        },
        {
            "name": "브랜드/색상/패턴 선택",  # 2 * 3 * 1
            "col_selection": ["브랜드", "색상", "패턴"],
            "expected_versions": [
                "NIKE 블랙 면 티셔츠",       # version 0: (0,0,0)
                "나이키 블랙 면 티셔츠",      # version 1: (1,0,0)
                "NIKE BLACK 면 티셔츠",      # version 2: (0,1,0)
                "나이키 BLACK 면 티셔츠",     # version 3: (1,1,0)
                "NIKE 검정 면 티셔츠"        # version 4: (0,2,0)
            ]
        },
        {
            "name": "색상/패턴/소재 선택",  # 3 * 1 * 3
            "col_selection": ["색상", "패턴", "소재"],
            "expected_versions": [
                "나이키 블랙 코튼 티셔츠",     # version 0: (0,0,0)
                "나이키 BLACK 코튼 티셔츠",    # version 1: (1,0,0)
                "나이키 검정 코튼 티셔츠",     # version 2: (2,0,0)
                "나이키 블랙 cotton 티셔츠",   # version 3: (0,0,1)
                "나이키 BLACK cotton 티셔츠"   # version 4: (1,0,1)
            ]
        },
        {
            "name": "브랜드/색상/패턴/소재 선택",  # 2 * 3 * 1 * 3
            "col_selection": ["브랜드", "색상", "패턴", "소재"],
            "expected_versions": [
                "NIKE 블랙 코튼 티셔츠",         # version 0: (0,0,0,0)
                "나이키 블랙 코튼 티셔츠",        # version 1: (1,0,0,0)
                "NIKE BLACK 코튼 티셔츠",        # version 2: (0,1,0,0)
                "나이키 BLACK 코튼 티셔츠",       # version 3: (1,1,0,0)
                "NIKE 검정 코튼 티셔츠"          # version 4: (0,2,0,0)
            ]
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
        
        expected_first = case["expected_versions"][0]
        print(f"기대한 첫 버전: {expected_first}")
        print(f"실제 첫 버전: {title}")
        success = title == expected_first
        result = f"{Colors.GREEN}성공{Colors.RESET}" if success else f"{Colors.RED}실패{Colors.RESET}"
        print(f"테스트 결과: {result}")
        
        # 가능한 모든 조합 출력
        print(f"\n총 조합 가능 개수: {total}")
        print("모든 버전:")
        for version in range(min(5, total)):
            next_title, _ = create_title_combination(
                test_row,
                case["col_selection"],
                test_dict,
                version_idx=version
            )
            print(f"버전 {version+1}: {next_title}")
            
            if version < len(case["expected_versions"]):
                expected = case["expected_versions"][version]
                print(f"기대값: {expected}")
                print(f"실제값: {next_title}")
                success = next_title == expected
                result = f"{Colors.GREEN}성공{Colors.RESET}" if success else f"{Colors.RED}실패{Colors.RESET}"
                print(f"결과: {result}")

if __name__ == "__main__":
    test_title_generation() 