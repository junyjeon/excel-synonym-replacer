import re

def clean_text(text: str) -> str:
    """특수문자와 불필요한 단어 제거 및 텍스트 정규화"""
    
    # 1. 제거할 패턴 정의
    patterns = [
        # 괄호 및 내용
        r'\s*\[[^\]]*\]',     # [S], [없음] 등 대괄호와 내용
        r'\([^)]*\)',         # (in&out) 등 소괄호와 내용
        
        # 특수문자
        r'[\^&,]+',           # ^, &, , (쉼표까지 추가)
        
        # 불필요한 단어 (단어 경계 처리)
        r'\b(폴리|무지|패턴|없음|제거|유니섹스)\b',  # "체크" 제거하지 않음
        
        # 공백 정리
        r'\s{2,}',            # 두 개 이상의 공백을 하나로
        r'^\s+|\s+$'          # 앞뒤 공백
    ]
    
    # 2. 패턴 순차 적용
    result = text
    for pattern in patterns:
        result = re.sub(pattern, ' ', result)
    
    # 3. 최종 정리
    result = ' '.join(result.split())
    
    return result.strip()


def test_clean_text():
    """텍스트 정제 함수 테스트"""
    test_cases = [
        (
            "나이키 [S] 블랙 ^^ 면 & 티셔츠",
            "나이키 블랙 면 티셔츠"
        ),
        (
            "아디다스  폴리  무지  패턴  (2023)",
            "아디다스 티셔츠"
        ),
        (
            "  유니클로   [없음]   코튼  ",
            "유니클로 코튼"
        )
    ]
    
    for input_text, expected in test_cases:
        result = clean_text(input_text)
        assert result == expected, f"\n입력: {input_text}\n기대: {expected}\n실제: {result}" 