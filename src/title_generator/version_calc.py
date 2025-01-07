"""
버전 인덱스 계산 모듈
"""

def calculate_version_indices(ordered_lists, version_idx):
    """
    버전별 인덱스 계산
    
    Args:
        ordered_lists: 유의어 리스트들
        version_idx: 버전 인덱스
    
    Returns:
        tuple: (선택된 인덱스 리스트, 전체 조합 수)
    """
    total_combinations = 1
    for synonyms in ordered_lists:
        total_combinations *= len(synonyms)
        
    selected_indices = []
    remaining = version_idx % total_combinations if ordered_lists else 0
    
    for synonyms in ordered_lists:
        idx = remaining % len(synonyms)
        selected_indices.append(idx)
        remaining //= len(synonyms)
        
    return selected_indices, total_combinations 