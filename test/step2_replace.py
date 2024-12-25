#step2_replace.py
import re
import pandas as pd

def load_synonym_dict(excel_path: str) -> dict:
    """
    original_words_with_synonyms.xlsx에서
    A열(원본단어), B열(유의어)을 읽어 {원본단어: [유의어1, 유의어2, ...]} 형태로 반환.
    """
    df = pd.read_excel(excel_path)
    # 전제: A열='원본단어', B열='유의어'
    if "원본단어" not in df.columns or "유의어" not in df.columns:
        raise ValueError("[오류] 엑셀에 '원본단어' 또는 '유의어' 컬럼이 없습니다.")

    synonym_dict = {}
    for _, row in df.iterrows():
        orig = str(row["원본단어"]).strip()
        syn_str = str(row["유의어"]).strip()  # 예: "블랙,흑색,어두운색"
        if not orig or not syn_str or syn_str.lower() in ["nan", ""]:
            continue

        # 콤마로 구분된 문자열을 리스트로 분리
        synonyms = [s.strip() for s in syn_str.split(",") if s.strip()]
        if synonyms:
            synonym_dict[orig] = synonyms

    return synonym_dict

def replace_text_with_synonyms(text: str, synonym_dict: dict) -> str:
    """
    text: "ADIDAS 검정 스트라이프 면혼방 티셔츠" 등
    synonym_dict: {"검정":["블랙","흑색"], "면혼방":["코튼믹스","코튼블렌드"], ...}

    간단히 정규식 \b(단어경계)로 치환.
    여기서는 '유의어' 중 첫 번째로만 치환.
    (원하면 랜덤/순차 로직을 추가 가능)
    """
    if not text:
        return text

    new_text = text
    for original_word, syn_list in synonym_dict.items():
        if not syn_list:
            continue
        # 첫 번째 유의어로 치환 (필요하면 랜덤.choice(syn_list))
        replacement = syn_list[0]
        pattern = r'\b' + re.escape(original_word) + r'\b'
        new_text = re.sub(pattern, replacement, new_text)

    return new_text

def main():
    # 1) 유의어 사전 로드 (1단계 결과물)
    synonym_xlsx = "original_words_with_synonyms.xlsx"
    try:
        synonym_dict = load_synonym_dict(synonym_xlsx)
        print(f"[INFO] '{synonym_xlsx}'로부터 {len(synonym_dict)}개 원본단어의 유의어를 불러왔습니다.")
    except Exception as e:
        print(f"[오류] 유의어 사전 로딩 실패: {e}")
        return

    # 2) 치환 대상 엑셀: 예) 'product_list.xlsx' (A열=브랜드, B열=상품명 등 가정)
    target_file = "product_list.xlsx"
    try:
        df_target = pd.read_excel(target_file)
    except Exception as e:
        print(f"[오류] '{target_file}' 읽기 실패: {e}")
        return

    # 상품명이 들어있는 열 이름을 확인해 주세요.
    # 예: '상품명' 컬럼이 있다고 가정
    if "상품명" not in df_target.columns:
        print("[오류] '상품명' 컬럼이 없습니다. 확인 후 수정해주세요.")
        return

    # 3) 치환 로직 적용
    #    예: 새 열 "치환결과"를 만들어 저장
    new_col = []
    for idx, row in df_target.iterrows():
        original_text = str(row["상품명"])
        replaced_text = replace_text_with_synonyms(original_text, synonym_dict)
        new_col.append(replaced_text)

    df_target["치환결과"] = new_col

    # 4) 결과 저장
    output_file = "product_list_replaced.xlsx"
    df_target.to_excel(output_file, index=False)
    print(f"[INFO] 치환 완료! '{output_file}' 파일을 확인하세요.")

if __name__ == "__main__":
    main()
