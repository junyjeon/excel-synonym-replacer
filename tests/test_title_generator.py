"""
유의어 치환 타이틀 생성기 테스트
"""
import pytest
import sys
from pathlib import Path

# src 디렉토리를 Python 경로에 추가
sys.path.append(str(Path(__file__).parent.parent))

from src.title_generator import create_title_combination
from src.title_generator.config import ORDERED_COLUMNS
import pandas as pd

def test_brand_synonym_matching():
    """브랜드 유의어 치환 테스트"""
    
    # 실제 유의어 사전과 동일한 형식
    test_synonyms = {
        '브랜드': {
            'LAB': ['랩', 'LAB', '랩코리아'],
            'THE EDGE': ['더엣지', 'THEEDGE', '디엣지'],
            'NBA': ['엔비에이', 'N.B.A', '엔바'],
            'ADIDAS': ['아디다스', 'adidas', '아디다스코리아'],
            'adidas Originals': ['아디다스오리지널', 'ADIDAS ORIGINALS', '아디다스오리지날스'],
            'Patagonia': ['파타고니아', 'PATAGONIA'],
            'U.S. Polo Assn.': ['US폴로아센', 'US POLO', '유에스폴로'],
            '8SECONDS': ['에잇세컨즈', '8세컨즈', '에잇세컨드'],
            'WHO.A.U': ['후아유', 'WHOAU', '후아유진']
        },
        '색상': {
            '블랙': ['검정색', '흑색', '먹색'],
            '네이비': ['곤색', '감청색', '남색']
        },
        '카테고리': {
            '맨투맨': ['맨투맨', '스웨트셔츠', '크루넥'],
            '셔츠': ['셔츠', '남방', '남방셔츠']
        }
    }
    
    # 다양한 테스트 케이스
    test_cases = [
        # 1. 기본 매칭
        {
            'row': pd.Series({'브랜드': 'LAB', '색상': '네이비', '카테고리': '셔츠'}),
            'expected': '랩 곤색 셔츠'
        },
        # 2. 대소문자 구분 없는 매칭
        {
            'row': pd.Series({'브랜드': 'lab', '색상': '네이비', '카테고리': '셔츠'}),
            'expected': '랩 곤색 셔츠'
        },
        # 3. 공백 있는 브랜드
        {
            'row': pd.Series({'브랜드': 'adidas Originals', '색상': '블랙', '카테고리': '맨투맨'}),
            'expected': '아디다스오리지널 검정색 맨투맨'
        },
        # 4. 특수문자 포함
        {
            'row': pd.Series({'브랜드': 'U.S. Polo Assn.', '색상': '네이비', '카테고리': '셔츠'}),
            'expected': 'US폴로아센 곤색 셔츠'
        },
        # 5. 숫자 포함
        {
            'row': pd.Series({'브랜드': '8SECONDS', '색상': '블랙', '카테고리': '맨투맨'}),
            'expected': '에잇세컨즈 검정색 맨투맨'
        },
        # 6. 앞뒤 공백 있는 경우
        {
            'row': pd.Series({'브랜드': ' NBA ', '색상': '블랙', '카테고리': '맨투맨'}),
            'expected': '엔비에이 검정색 맨투맨'
        },
        # 7. 원본 형태와 다른 표기
        {
            'row': pd.Series({'브랜드': 'adidas originals', '색상': '블랙', '카테고리': '맨투맨'}),
            'expected': '아디다스오리지널 검정색 맨투맨'
        }
    ]
    
    # 모든 컬럼 선택
    col_selection = ['브랜드', '색상', '패턴', '소재', '카테고리']
    
    # 각 케이스 테스트
    for case in test_cases:
        result, _ = create_title_combination(
            row=case['row'],
            col_selection=col_selection,
            synonym_dict=test_synonyms,
            version_idx=0
        )
        assert result == case['expected'], f"Expected '{case['expected']}' but got '{result}'"

def test_multiple_versions():
    """여러 버전 생성 테스트"""
    test_row = pd.Series({
        '브랜드': 'NBA',
        '색상': '블랙',
        '카테고리': '맨투맨'
    })
    
    test_synonyms = {
        '브랜드': {
            'NBA': ['엔비에이', 'N.B.A', '엔바']
        },
        '색상': {
            '블랙': ['검정색', '흑색', '먹색']
        },
        '카테고리': {
            '맨투맨': ['맨투맨', '스웨트셔츠', '크루넥']
        }
    }
    
    col_selection = ['브랜드', '색상', '패턴', '소재', '카테고리']
    
    # 순차적 조합 테스트 (브랜드가 먼저 변경)
    expected_versions = [
        '엔비에이 검정색 맨투맨',      # version 0 (0,0,0)
        'N.B.A 검정색 맨투맨',        # version 1 (1,0,0)
        '엔바 검정색 맨투맨',         # version 2 (2,0,0)
        '엔비에이 흑색 맨투맨',        # version 3 (0,1,0)
        'N.B.A 흑색 맨투맨',         # version 4 (1,1,0)
    ]
    
    for idx, expected in enumerate(expected_versions):
        result, _ = create_title_combination(
            row=test_row,
            col_selection=col_selection,
            synonym_dict=test_synonyms,
            version_idx=idx
        )
        assert result == expected, f"Version {idx}: Expected '{expected}' but got '{result}'"

def test_no_brand_in_dict():
    """사전에 없는 브랜드 처리 테스트"""
    test_row = pd.Series({
        '브랜드': '없는브랜드',
        '색상': '블랙',
        '카테고리': '맨투맨'
    })
    
    test_synonyms = {
        '브랜드': {
            'NBA': ['엔비에이']
        },
        '색상': {
            '블랙': ['검정색', '흑색', '먹색']
        },
        '카테고리': {
            '맨투맨': ['맨투맨', '스웨트셔츠', '크루넥']
        }
    }
    
    col_selection = ['브랜드', '색상', '패턴', '소재', '카테고리']
    
    result, _ = create_title_combination(
        row=test_row,
        col_selection=col_selection,
        synonym_dict=test_synonyms,
        version_idx=0
    )
    
    # 사전에 없는 브랜드는 원본 유지
    assert result == '없는브랜드 검정색 맨투맨'

def test_brand_not_replaced_when_unchecked():
    """체크하지 않은 브랜드가 치환되지 않는지 테스트"""
    # 테스트 데이터 준비
    row = {
        '브랜드': 'Nike',
        '색상': '블랙',
        '패턴': '단색',
        '소재': '면',
        '카테고리': '상의'
    }
    
    # 색상만 선택한 경우의 유의어 사전
    synonym_dict = {
        '브랜드': {'Nike': ['나이키', '나익']},
        '색상': {'블랙': ['검정', '검은색']}
    }
    
    # 색상만 선택
    col_selection = ['색상']
    
    # 실행
    result, _ = create_title_combination(row, col_selection, synonym_dict, 0)
    
    # 검증
    assert 'Nike' in result  # 브랜드는 원본 유지
    assert '검정' in result or '검은색' in result  # 색상은 치환됨
    assert 'Nike 검정' in result or 'Nike 검은색' in result

def test_material_preserved_when_not_selected():
    """체크하지 않은 소재가 누락되지 않고 보존되는지 테스트"""
    # 테스트 데이터 준비
    row = {
        '브랜드': 'Nike',
        '색상': '블랙',
        '패턴': '단색',
        '소재': '면',
        '카테고리': '상의'
    }
    
    # 색상과 카테고리만 있는 유의어 사전
    synonym_dict = {
        '색상': {'블랙': ['검정', '검은색']},
        '카테고리': {'상의': ['티셔츠', '상의류']}
    }
    
    # 색상과 카테고리만 선택
    col_selection = ['색상', '카테고리']
    
    # 실행
    result, _ = create_title_combination(row, col_selection, synonym_dict, 0)
    
    # 검증
    assert '면' in result  # 소재가 보존됨
    assert 'Nike' in result  # 브랜드도 보존됨
    assert '검정' in result or '검은색' in result  # 색상은 치환됨
    assert '티셔츠' in result or '상의류' in result  # 카테고리는 치환됨

def test_empty_material_handled_correctly():
    """소재가 비어있는 경우 올바르게 처리되는지 테스트"""
    # 테스트 데이터 준비
    row = {
        '브랜드': 'Nike',
        '색상': '블랙',
        '패턴': '단색',
        '소재': '',  # 빈 소재
        '카테고리': '상의'
    }
    
    synonym_dict = {
        '색상': {'블랙': ['검정', '검은색']},
        '카테고리': {'상의': ['티셔츠', '상의류']}
    }
    
    col_selection = ['색상', '카테고리']
    
    # 실행
    result, _ = create_title_combination(row, col_selection, synonym_dict, 0)
    
    # 검증
    assert 'Nike' in result  # 브랜드 보존
    assert '검정' in result or '검은색' in result  # 색상 치환
    assert '티셔츠' in result or '상의류' in result  # 카테고리 치환
    assert '  ' not in result  # 불필요한 공백이 없어야 함

def test_missing_material_handled_correctly():
    """소재 컬럼이 없는 경우 올바르게 처리되는지 테스트"""
    # 테스트 데이터 준비 - 소재 컬럼 없음
    row = {
        '브랜드': 'Nike',
        '색상': '블랙',
        '패턴': '단색',
        '카테고리': '상의'
    }
    
    synonym_dict = {
        '색상': {'블랙': ['검정', '검은색']},
        '카테고리': {'상의': ['티셔츠', '상의류']}
    }
    
    col_selection = ['색상', '카테고리']
    
    # 실행
    result, _ = create_title_combination(row, col_selection, synonym_dict, 0)
    
    # 검증
    assert 'Nike' in result  # 브랜드 보존
    assert '검정' in result or '검은색' in result  # 색상 치환
    assert '티셔츠' in result or '상의류' in result  # 카테고리 치환
    assert '  ' not in result  # 불필요한 공백이 없어야 함

def test_partial_synonym_dict():
    """일부 컬럼만 유의어 사전에 있는 경우 테스트"""
    row = {
        '브랜드': 'Nike',
        '색상': '블랙',
        '패턴': '단색',
        '소재': '면',
        '카테고리': '상의'
    }
    
    # 일부 컬럼만 있는 유의어 사전
    partial_dict = {
        '색상': {'블랙': ['검정']},
        # 브랜드, 패턴, 소재, 카테고리는 누락
    }
    
    # 모든 컬럼 선택
    col_selection = ORDERED_COLUMNS
    
    # 실행
    result, _ = create_title_combination(row, col_selection, partial_dict, 0)
    
    # 검증
    assert 'Nike' in result, "누락된 사전의 브랜드가 유지되지 않음"
    assert '검정' in result, "존재하는 사전의 색상이 치환되지 않음"
    assert '단색' in result, "누락된 사전의 패턴이 유지되지 않음"
    assert '면' in result, "누락된 사전의 소재가 유지되지 않음"
    assert '상의' in result, "누락된 사전의 카테고리가 유지되지 않음"

def test_version_index_range():
    """버전 인덱스 범위 테스트"""
    row = {
        '브랜드': 'Nike',
        '색상': '블랙'
    }
    
    synonym_dict = {
        '색상': {'블랙': ['검정', '흑색', '먹색']}  # 3가지 유의어
    }
    
    col_selection = ['색상']
    
    # 정상 범위 테스트
    for i in range(5):  # 0~4 테스트
        result, total = create_title_combination(row, col_selection, synonym_dict, i)
        assert total == 3, f"전체 조합 수가 잘못됨: {total}"
        assert result.split()[0] == 'Nike', "브랜드가 변경됨"
        assert result.split()[1] in ['검정', '흑색', '먹색'], f"잘못된 색상: {result}"

    # 매우 큰 인덱스 테스트 (순환되어야 함)
    result, _ = create_title_combination(row, col_selection, synonym_dict, 1000)
    assert result.split()[1] in ['검정', '흑색', '먹색'], "큰 인덱스에서 순환이 잘못됨"

def test_case_sensitivity():
    """대소문자 구분 없이 매칭되는지 테스트"""
    test_cases = [
        {'input': 'NIKE', 'expected': '나이키'},
        {'input': 'nike', 'expected': '나이키'},
        {'input': 'NiKe', 'expected': '나이키'},
        {'input': 'BLACK', 'expected': '검정'},
        {'input': 'black', 'expected': '검정'},
        {'input': 'BlAcK', 'expected': '검정'}
    ]
    
    synonym_dict = {
        '브랜드': {'nike': ['나이키']},
        '색상': {'black': ['검정']}
    }
    
    for case in test_cases:
        # 브랜드 테스트
        row = {'브랜드': case['input']}
        result, _ = create_title_combination(
            row, ['브랜드'], synonym_dict, 0
        )
        if '나이키' in case['expected']:
            assert case['expected'] in result, f"브랜드 대소문자 매칭 실패: {case['input']}"
            
        # 색상 테스트
        row = {'색상': case['input']}
        result, _ = create_title_combination(
            row, ['색상'], synonym_dict, 0
        )
        if '검정' in case['expected']:
            assert case['expected'] in result, f"색상 대소문자 매칭 실패: {case['input']}"

def test_invalid_synonym_dict():
    """잘못된 형식의 유의어 사전이 에러를 발생시키는지 테스트"""
    row = {
        '브랜드': 'Nike',
        '색상': '블랙'
    }
    
    # 잘못된 형식의 유의어 사전
    invalid_dict = {
        '브랜드': 'Nike',  # 딕셔너리가 아닌 문자열
        '색상': {'블랙': ['검정']}
    }
    
    col_selection = ['브랜드']  # 브랜드만 선택
    
    # 실행
    result, _ = create_title_combination(row, col_selection, invalid_dict, 0)
    
    # 검증 - 잘못된 형식은 에러를 반환해야 함
    assert result.startswith("ERROR:"), "잘못된 사전 형식이 에러를 발생시키지 않음"
    assert "'str' object has no attribute 'items'" in result, "문자열 값에 대한 구체적 에러 메시지 누락"

def test_empty_values():
    """빈 값 처리 테스트"""
    # 다양한 형태의 빈 값
    empty_values = ['', ' ', None, '  ', '\t', '\n']
    
    for empty_value in empty_values:
        row = {
            '브랜드': 'Nike',
            '색상': empty_value,
            '카테고리': '상의'
        }
        
        synonym_dict = {
            '색상': {'블랙': ['검정']},
            '카테고리': {'상의': ['티셔츠']}
        }
        
        col_selection = ['브랜드', '색상', '카테고리']
        
        # 실행
        result, _ = create_title_combination(row, col_selection, synonym_dict, 0)
        
        # 검증
        assert 'Nike' in result, "브랜드가 누락됨"
        assert '티셔츠' in result, "카테고리가 치환되지 않음"
        assert '  ' not in result, "불필요한 공백이 있음"
        assert result.count(' ') <= 2, f"잘못된 공백 처리: {result}"

if __name__ == '__main__':
    pytest.main([__file__]) 