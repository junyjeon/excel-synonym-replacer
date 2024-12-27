import pandas as pd
from title_generator import create_title_combination

# ANSI 색상 코드 추가
class Colors:
    RED = '\033[91m'      # 밝은 빨강
    GREEN = '\033[92m'    # 밝은 초록
    RESET = '\033[0m'     # 색상 초기화

def test_title_generation():
    # 1. 기본 테스트 데이터 설정
    default_row = pd.Series([
        "",         # A열
        "나이키",   # B열 (브랜드)
        "검정",     # C열 (색상)
        "무지",     # D열 (패턴)
        "면",      # E열 (소재)
        "티셔츠"    # F열 (카테고리)
    ])

    test_dict = {
        "브랜드": {
            "나이키": ["NIKE"],
            "US폴로아센": ["U.S. Polo Assn."],
            "더엣지": ["THE EDGE"]
        },
        "색상": {
            "검정": ["진검정", "흑색", "검정색"]
        },
        "패턴": {
            "무지": ["단색", "솔리드", "기본"],
            "스트라이프": ["줄무늬", "선무늬", "라인"],
            "도트무늬": ["땡땡이", "물방울", "폴카"]
        },
        "소재": {
            "면": ["코튼", "목화", "순면"],
            "마혼방": ["리넨믹스", "린넨블렌드", "리넨혼합"],
            "폴리에스터": ["폴리", "폴리에스테르", "폴리섬유"]
        },
        "카테고리": {
            "티셔츠": ["티", "반팔티", "반소매"]
        }
    }

    # 2. 테스트 케이스들
    test_cases = [
        {
            "name": "브랜드만 선택",
            "col_selection": ["브랜드"],
            "expected_versions": [
                "NIKE 검정 면 티셔츠"
            ]
        },
        {
            "name": "색상만 선택",
            "col_selection": ["색상"],
            "expected_versions": [
                "나이키 진검정 면 티셔츠",   # 원본: "나이키 검정 면 티셔츠"
                "나이키 흑색 면 티셔츠",     # 색상만 변환
                "나이키 검정색 면 티셔츠"
            ]
        },
        {
            "name": "소재만 선택",
            "col_selection": ["소재"],
            "expected_versions": [
                "나이키 검정 코튼 티셔츠",
                "나이키 검정 목화 티셔츠",
                "나이키 검정 순면 티셔츠"
            ]
        },
        {
            "name": "패턴만 선택",
            "col_selection": ["패턴"],
            "expected_versions": [
                "나이키 검정 면 티셔츠"  # 무지는 제거되므로 패턴 없이
            ]
        },
        {
            "name": "카테고리만 선택",
            "col_selection": ["카테고리"],
            "expected_versions": [
                "나이키 검정 면 티",
                "나이키 검정 면 반팔티",
                "나이키 검정 면 반소매"
            ]
        },
        
        # 2. 두 카테고리 조합
        {
            "name": "브랜드/색상 선택",
            "col_selection": ["브랜드", "색상"],
            "expected_versions": [
                "NIKE 진검정 면 티셔츠",
                "NIKE 흑색 면 티셔츠",
                "NIKE 검정색 면 티셔츠"
            ]
        },
        {
            "name": "브랜드/소재 선택",
            "col_selection": ["브랜드", "소재"],
            "expected_versions": [
                "NIKE 검정 코튼 티셔츠",
                "NIKE 검정 목화 티셔츠",
                "NIKE 검정 순면 티셔츠"
            ]
        },
        {
            "name": "색상/소재 선택",
            "col_selection": ["색상", "소재"],
            "expected_versions": [
                "나이키 진검정 코튼 티셔츠",      # (진검정, 코튼)
                "나이키 흑색 코튼 티셔츠",        # (흑색, 코튼)
                "나이키 검정색 코튼 티셔츠",      # (검정색, 코튼)
                "나이키 진검정 목화 티셔츠",      # (진검정, 목화)
                "나이키 흑색 목화 티셔츠",        # (흑색, 목화)
                "나이키 검정색 목화 티셔츠",      # (검정색, 목화)
                "나이키 진검정 순면 티셔츠",      # (진검정, 순면)
                "나이키 흑색 순면 티셔츠",        # (흑색, 순면)
                "나이키 검정색 순면 티셔츠"       # (검정색, 순면)
            ]
        },
        
        # 3. 세 카테고리 조합
        {
            "name": "브랜드/색상/소재 선택",
            "col_selection": ["브랜드", "색상", "소재"],
            "expected_versions": [
                "NIKE 진검정 코튼 티셔츠",
                "NIKE 흑색 코튼 티셔츠",
                "NIKE 검정색 코튼 티셔츠",
                "NIKE 진검정 목화 티셔츠",
                "NIKE 흑색 목화 티셔츠",
                "NIKE 검정색 목화 티셔츠",
                "NIKE 진검정 순면 티셔츠",
                "NIKE 흑색 순면 티셔츠",
                "NIKE 검정색 순면 티셔츠"
            ]
        },
        
        # 4. 특수 케이스
        {
            "name": "선택된 카테고리 없음",
            "col_selection": [],
            "expected_versions": [
                "나이키 검정 면 티셔츠"  # 원본 유지
            ]
        },
        {
            "name": "빈 값이 있는 경우",
            "col_selection": ["브랜드", "패턴", "소재"],
            "expected_versions": [
                "NIKE 검정 코튼 티셔츠",
                "NIKE 검정 목화 티셔츠",
                "NIKE 검정 순면 티셔츠"
            ]
        },
        {
            "name": "유의어가 없는 경우",
            "col_selection": ["브랜드", "카테고리"],
            "expected_versions": [
                "NIKE 검정 면 티",
                "NIKE 검정 면 반팔티",
                "NIKE 검정 면 반소매"
            ]
        },
        {
            "name": "패턴만 선택",
            "col_selection": ["패턴"],
            "expected_versions": [
                "나이키 검정 면 티셔츠"  # 무지는 제거되므로 패턴 없이
            ]
        },
        {
            "name": "카테고리만 선택",
            "col_selection": ["카테고리"],
            "expected_versions": [
                "나이키 검정 면 티",
                "나이키 검정 면 반팔티",
                "나이키 검정 면 반소매"
            ]
        },
        {
            "name": "브랜드/패턴/카테고리 선택",
            "col_selection": ["브랜드", "패턴", "카테고리"],
            "expected_versions": [
                "NIKE 검정 면 티",        # 무지는 제거되므로 패턴 없이
                "NIKE 검정 면 반팔티",    # 카테고리만 변경
                "NIKE 검정 면 반소매"
            ]
        },
        {
            "name": "브랜드 매칭 테스트",
            "col_selection": ["브랜드"],
            "test_row": pd.Series([
                "", "더엣지", "검정", "무지", "면", "티셔츠"
            ]),
            "expected_versions": [
                "THE EDGE 검정 면 티셔츠"
            ]
        },
        {
            "name": "폴리 제거 테스트",
            "col_selection": ["소재"],
            "test_row": pd.Series([
                "", "나이키", "검정", "무지", "폴리", "티셔츠"
            ]),
            "expected_versions": [
                "나이키 검정 티셔츠"
            ]
        }
    ]

    # 3. 테스트 실행
    for case in test_cases:
        print(f"\n=== {case['name']} ===")
        print(f"선택된 카테고리: {', '.join(case['col_selection'])}")
        
        # test_row가 없으면 default_row 사용
        current_row = case.get("test_row", default_row)
        
        # 원본 값 출력
        original = " ".join([
            str(current_row[1]),  # 브랜드
            str(current_row[2]),  # 색상
            str(current_row[4]),  # 소재
            str(current_row[5])   # 카테고리
        ])
        print(f"원본: {original}")
        
        title, total = create_title_combination(
            current_row,
            case["col_selection"],
            test_dict,
            version_idx=0
        )
        
        print(f"기대하는 버전 수: {len(case['expected_versions'])}")
        print(f"실제 생성된 버전 수: {total}")
        
        expected_first = case["expected_versions"][0]
        print(f"\n기대한 첫 버전: {expected_first}")
        print(f"실제 첫 버전: {title}")
        success = title == expected_first
        result = f"{Colors.GREEN}성공{Colors.RESET}" if success else f"{Colors.RED}실패{Colors.RESET}"
        print(f"테스트 결과: {result}")
        
        # 가능한 모든 조합 출력
        print("\n모든 버전:")
        for version in range(min(5, total)):
            print(f"버전 {version+1}:")
            
            next_title, _ = create_title_combination(
                current_row,
                case["col_selection"],
                test_dict,
                version_idx=version
            )
            
            if version < len(case["expected_versions"]):
                expected = case["expected_versions"][version]
                print(f"기대값: {expected}")
                print(f"실제값: {next_title}")
                success = next_title == expected
                result = f"{Colors.GREEN}성공{Colors.RESET}" if success else f"{Colors.RED}실패{Colors.RESET}"
                print(f"결과: {result}\n")

if __name__ == "__main__":
    test_title_generation() 