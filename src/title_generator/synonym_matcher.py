"""
유의어 매칭 모듈
"""

def find_synonyms(value, synonyms_dict):
    """
    유의어 매칭 처리
    
    Args:
        value: 매칭할 원본 값
        synonyms_dict: 유의어 사전
    
    Returns:
        list: 매칭된 유의어 리스트
    """
    for dict_key, syn_list in synonyms_dict.items():
        if value.lower().strip() == dict_key.lower().strip():
            return [syn_list] if isinstance(syn_list, str) else syn_list
    return [] 