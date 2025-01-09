from text_cleaner import clean_text
from title_generator.config import ORDERED_COLUMNS, DEFAULT_VALUES
from title_generator.preprocessor import prepare_data
from title_generator.synonym_matcher import find_synonyms
from title_generator.version_calc import calculate_version_indices
from title_generator.result_builder import generate_result

def create_title_combination(row, col_selection, synonym_dict, version_idx):
    """
    유의어 치환으로 새로운 제목 생성
    
    Args:
        row: 현재 행 데이터
        col_selection: 선택된 컬럼들
        synonym_dict: 유의어 사전
        version_idx: 버전 인덱스 (0부터 시작)
    """
    try:
        ordered_lists = []
        ordered_selections = []
        
        # 1. 데이터 전처리
        processed_data = prepare_data(row, ORDERED_COLUMNS)
        fixed_values = {}
        
        # 2. 컬럼별 유의어 처리
        for key, value in processed_data.items():
            # value가 문자열이고 비어있지 않은지 명시적으로 확인
            value_str = str(value).strip()
            if key in synonym_dict and key in col_selection and value_str:
                synonyms = find_synonyms(value_str, synonym_dict[key])
                if synonyms:
                    ordered_lists.append(synonyms)
                    ordered_selections.append(key)
                else:
                    fixed_values[key] = value_str
            else:
                fixed_values[key] = value_str
        
        # 3. 버전 인덱스 계산
        selected_indices, total_combinations = calculate_version_indices(
            ordered_lists, version_idx
        )
        
        # 4. 결과 생성
        final_text = generate_result(
            ORDERED_COLUMNS,
            ordered_selections,
            ordered_lists,
            selected_indices,
            fixed_values
        )
        
        return clean_text(final_text), total_combinations
        
    except Exception as e:
        print(f"[ERROR] create_title_combination: {str(e)}")
        return f"{DEFAULT_VALUES['error_prefix']}{str(e)}", 0 