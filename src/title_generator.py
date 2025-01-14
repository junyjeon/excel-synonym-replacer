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
        
        # # [DEBUG] 전처리된 데이터 확인
        # print(f"[DEBUG] processed_data: {processed_data}")
        
        # 2. 컬럼별 유의어 처리
        for key, value in processed_data.items():
            value_str = str(value).strip()
            
            # # [DEBUG] 각 키-값 확인
            # print(f"[DEBUG] key={key}, value_str='{value_str}'")
            
            if key in synonym_dict and key in col_selection and value_str:
                synonyms = find_synonyms(value_str, synonym_dict[key])
                
                # # [DEBUG] 치환 후보(synonyms) 확인
                # print(f"[DEBUG] synonyms for '{value_str}': {synonyms}")
                
                if synonyms:
                    ordered_lists.append(synonyms)
                    ordered_selections.append(key)
                else:
                    fixed_values[key] = value_str
            else:
                # [DEBUG] 치환 대상이 아니거나, 빈 문자열일 때
                if key not in synonym_dict:
                    print(f"[DEBUG] '{key}' not in synonym_dict keys")
                if key not in col_selection:
                    print(f"[DEBUG] '{key}' not in col_selection")
                if not value_str:
                    print("[DEBUG] value_str is empty or None")
                
                fixed_values[key] = value_str
        
        # # [DEBUG] fixed_values, ordered_lists 확인
        # print(f"[DEBUG] fixed_values: {fixed_values}")
        # print(f"[DEBUG] ordered_lists: {ordered_lists}")
        # print(f"[DEBUG] ordered_selections: {ordered_selections}")
        
        # 3. 버전 인덱스 계산
        selected_indices, total_combinations = calculate_version_indices(
            ordered_lists, version_idx
        )
        
        # # [DEBUG] 버전별 인덱스, 전체 조합 수
        # print(f"[DEBUG] selected_indices: {selected_indices}")
        # print(f"[DEBUG] total_combinations: {total_combinations}")
        
        # 4. 결과 생성
        final_text = generate_result(
            ORDERED_COLUMNS,
            ordered_selections,
            ordered_lists,
            selected_indices,
            fixed_values
        )
        
        # # [DEBUG] 최종 생성된 텍스트
        # print(f"[DEBUG] final_text: '{final_text}'")
        
        return clean_text(final_text), total_combinations
        
    except Exception as e:
        print(f"[ERROR] create_title_combination: {str(e)}")
        return f"{DEFAULT_VALUES['error_prefix']}{str(e)}", 0
