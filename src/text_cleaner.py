import re

def clean_text(text: str) -> str:
    """특수문자와 불필요한 단어 제거"""
    patterns = [
        r'\s*\[[^\]]+\]',  # [S], [없음] 등 대괄호 내용
        r'\^+',            # ^ 기호
        r'&+',             # & 기호
        r'폴리\b',         # 폴리 (단어 끝)
        r'\b무지\b',       # 무지 (단어)
        r'\b패턴\b',       # 패턴 (단어)
        r'\(.*?\)',        # (in&out) 등 괄호 내용
    ]
    
    result = text
    for pattern in patterns:
        result = re.sub(pattern, '', result)
    
    return ' '.join(result.split()).strip() 