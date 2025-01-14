import pytest
from PySide6.QtWidgets import QApplication, QCheckBox
from PySide6.QtCore import Qt
import pandas as pd
from app import MainWindow
import tempfile
import time

@pytest.fixture(scope="session")
def app():
    return QApplication.instance() or QApplication([])

@pytest.fixture
def main_window(app):
    """MainWindow 인스턴스를 생성하는 fixture"""
    window = MainWindow()
    return window

@pytest.fixture
def overwrite_checkbox(app):
    checkbox = QCheckBox("덮어쓰기")
    checkbox.setChecked(True)  # 기본값 True로 설정
    return checkbox

def test_checkbox_initial_state(overwrite_checkbox):
    """체크박스 초기 상태 테스트"""
    assert overwrite_checkbox.text() == "덮어쓰기"
    assert overwrite_checkbox.isChecked() == True

def test_checkbox_toggle(overwrite_checkbox):
    """체크박스 토글 기능 테스트"""
    initial_state = overwrite_checkbox.isChecked()
    overwrite_checkbox.click()
    assert overwrite_checkbox.isChecked() != initial_state
    
    # 다시 클릭
    overwrite_checkbox.click()
    assert overwrite_checkbox.isChecked() == initial_state

def test_checkbox_disabled_state(overwrite_checkbox):
    """체크박스 비활성화 상태 테스트"""
    overwrite_checkbox.setEnabled(False)
    assert not overwrite_checkbox.isEnabled()
    
    # 비활성화 상태에서 클릭해도 상태가 변경되지 않아야 함
    initial_state = overwrite_checkbox.isChecked()
    overwrite_checkbox.click()
    assert overwrite_checkbox.isChecked() == initial_state

def test_checkbox_programmatic_change(overwrite_checkbox):
    """프로그래밍 방식의 상태 변경 테스트"""
    overwrite_checkbox.setChecked(False)
    assert not overwrite_checkbox.isChecked()
    
    overwrite_checkbox.setChecked(True)
    assert overwrite_checkbox.isChecked()

def test_checkbox_signal(overwrite_checkbox, qtbot):
    """체크박스 시그널 발생 테스트"""
    # 시그널 감지를 위한 카운터
    signal_received = False
    
    def on_state_changed(state):
        nonlocal signal_received
        signal_received = True
    
    # stateChanged 시그널에 슬롯 연결
    overwrite_checkbox.stateChanged.connect(on_state_changed)
    
    # 시그널 발생 확인을 위한 대기 설정
    with qtbot.wait_signals([overwrite_checkbox.stateChanged], timeout=1000):
        # 체크박스 상태 변경
        overwrite_checkbox.setChecked(not overwrite_checkbox.isChecked())
    
    # 시그널이 발생했는지 확인
    assert signal_received 

def test_transform_with_overwrite(main_window, qtbot):
    window = main_window
    qtbot.addWidget(window)
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        df = pd.DataFrame({
            '브랜드': ['테스트 브랜드'],
            '색상': ['빨강'],
            '패턴': ['무지'],
            '소재': ['면'],
            '카테고리': ['의류'],
            '상품명_1': ['기존 제목']
        })
        df.to_excel(tmp.name, index=False)
        
        # 파일 로드
        window.load_excel_file(tmp.name)
        
        # 유의어 사전 설정
        window.synonym_dict = {
            '브랜드': {'테스트 브랜드': ['변경된브랜드']},
            '색상': {'빨강': ['레드']}
        }
        
        # 버전 수 설정
        window.spin_version.setValue(1)
        
        # 체크박스 설정
        window.chk_brand.setChecked(True)
        window.chk_color.setChecked(True)
        window.chk_overwrite.setChecked(True)
        
        # 행 선택
        window.table_view.selectRow(0)
        
        # 변환 실행
        window.transform_data()
        time.sleep(0.1)
        
        # 결과 확인
        result_df = pd.read_excel(tmp.name)
        print(f"변환된 내용: {result_df['상품명_1'].iloc[0]}")
        assert result_df['상품명_1'].iloc[0] != '기존 제목'
        assert '변경된브랜드' in result_df['상품명_1'].iloc[0]
        assert '레드' in result_df['상품명_1'].iloc[0]

def test_transform_without_overwrite(main_window, qtbot):
    """덮어쓰기 옵션이 해제된 데이터 변환 테스트"""
    window = main_window
    qtbot.addWidget(window)
    
    # 임시 파일 생성
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        # 테스트 데이터를 파일로 저장 (M열에 기존 데이터)
        df = pd.DataFrame({
            '유의어': ['테스트 상품'],
            '브랜드': ['테스트 브랜드'],
            '색상': ['빨강'],
            '패턴': ['무지'],
            '소재': ['면'],
            '카테고리': ['의류'],
            '상품명_1': ['기존 제목']  # M열에 기존 데이터
        })
        df.to_excel(tmp.name, index=False)
        
        # 파일 경로 설정
        window.file_path = tmp.name
        window.current_sheet = 'Sheet1'
        
        # 데이터프레임 설정
        window._df = df
        window._model.setDataFrame(df)
        
        # 덮어쓰기 해제
        window.chk_overwrite.setChecked(False)
        
        # 카테고리 선택
        window.chk_brand.setChecked(True)
        window.chk_color.setChecked(True)
        
        # 행 선택
        window.table_view.selectRow(0)
        
        # 변환 실행
        window.transform_data()
        
        # 파일 시스템 동기화 대기
        time.sleep(0.1)
        
        # 결과 확인 - 파일에서 다시 읽어서 확인
        result_df = pd.read_excel(tmp.name)
        print(f"M열 내용: {result_df['상품명_1'].iloc[0]}")
        # M열의 기존 내용이 유지되는지 확인
        assert result_df['상품명_1'].iloc[0] == '기존 제목' 

def test_transform_with_overwrite_detailed(main_window, qtbot):
    """덮어쓰기 모드의 상세 동작 테스트"""
    window = main_window
    qtbot.addWidget(window)
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        # 1. 더 다양한 테스트 데이터
        df = pd.DataFrame({
            '유의어': ['테스트 상품'],
            '브랜드': ['테스트 브랜드'],
            '색상': ['빨강'],
            '패턴': ['무지'],
            '소재': ['면'],
            '카테고리': ['의류'],
            '상품명_1': ['기존 제목'],
            '상품명_2': ['기존 버전2'],  # 두 번째 버전 열도 추가
            '상품명_3': ['기존 버전3']   # 세 번째 버전 열도 추가
        })
        df.to_excel(tmp.name, index=False)
        
        # 2. 더 복잡한 유의어 사전
        window.synonym_dict = {
            '브랜드': {
                '테스트 브랜드': ['변경된브랜드', '새브랜드'],  # 여러 유의어
                '다른브랜드': ['other']  # 미사용 유의어
            },
            '색상': {
                '빨강': ['레드', '크림슨'],  # 여러 유의어
                '파랑': ['블루']  # 미사용 유의어
            }
        }
        
        # 3. 파일 및 모델 설정
        window.file_path = tmp.name
        window.current_sheet = 'Sheet1'
        window._df = df.copy()
        window._model.setDataFrame(window._df)
        
        # 4. 다양한 설정 조합 테스트
        test_cases = [
            {
                'overwrite': True,
                'version_count': 3,
                'selections': ['브랜드', '색상']
            },
            {
                'overwrite': True,
                'version_count': 1,
                'selections': ['브랜드']
            }
        ]
        
        for case in test_cases:
            print(f"\n=== 테스트 케이스: {case} ===")
            
            # 설정 적용
            window.chk_overwrite.setChecked(case['overwrite'])
            window.spin_version.setValue(case['version_count'])
            
            # 카테고리 선택 초기화
            window.chk_brand.setChecked(False)
            window.chk_color.setChecked(False)
            
            # 선택된 카테고리만 체크
            for sel in case['selections']:
                if sel == '브랜드':
                    window.chk_brand.setChecked(True)
                elif sel == '색상':
                    window.chk_color.setChecked(True)
            
            # 행 선택
            window.table_view.selectRow(0)
            
            # 변환 실행
            window.transform_data()
            
            # 파일 시스템 동기화 대기
            time.sleep(0.1)
            
            # 결과 검증
            result_df = pd.read_excel(tmp.name)
            
            print("\n결과 데이터:")
            print(f"컬럼 목록: {result_df.columns.tolist()}")
            
            # 각 버전 열 확인
            for ver in range(1, case['version_count'] + 1):
                col_name = f'상품명_{ver}'
                content = result_df[col_name].iloc[0]
                print(f"{col_name}: '{content}'")
                
                if case['overwrite']:
                    # 덮어쓰기 모드: 새로운 내용으로 변경되었는지 확인
                    assert content != f'기존 버전{ver}', f"{col_name}이 덮어써지지 않음"
                    
                    # 선택된 카테고리의 유의어가 포함되었는지 확인
                    if '브랜드' in case['selections']:
                        assert any(word in content for word in ['변경된브랜드', '새브랜드']), \
                            f"{col_name}에 브랜드 유의어가 없음"
                    if '색상' in case['selections']:
                        assert any(word in content for word in ['레드', '크림슨']), \
                            f"{col_name}에 색상 유의어가 없음"
                else:
                    # 일반 모드: 기존 내용이 유지되는지 확인
                    assert content == f'기존 버전{ver}' if ver > 1 else '기존 제목', \
                        f"{col_name}의 기존 내용이 변경됨"

def test_transform_edge_cases(main_window, qtbot):
    """엣지 케이스 테스트"""
    window = main_window
    qtbot.addWidget(window)
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        # 1. 특수한 데이터 케이스
        df = pd.DataFrame({
            '유의어': [''],  # 빈 상품명
            '브랜드': ['없는브랜드'],  # 사전에 없는 브랜드
            '색상': ['  빨강  '],  # 앞뒤 공백
            '패턴': ['무지'],
            '소재': ['면'],
            '카테고리': ['의류'],
            '상품명_1': ['기존 제목']
        }, dtype=str)
        df.to_excel(tmp.name, index=False)
        
        # 2. 기본 설정
        window.file_path = tmp.name
        window.current_sheet = 'Sheet1'
        window._df = df.copy()
        window._model.setDataFrame(window._df)
        
        # 유의어 사전 설정 추가
        window.synonym_dict = {
            '브랜드': {
                '테스트브랜드': ['변경된브랜드']  # 없는브랜드는 사전에 없음
            },
            '색상': {
                '빨강': ['레드', '크림슨']  # 공백 처리 테스트용
            }
        }
        
        # 3. 엣지 케이스 테스트
        window.chk_overwrite.setChecked(True)
        window.chk_brand.setChecked(True)
        window.chk_color.setChecked(True)
        window.table_view.selectRow(0)
        
        # 4. 변환 실행
        window.transform_data()
        
        # 파일 시스템 동기화 대기
        time.sleep(0.1)
        
        # 5. 결과 검증
        result_df = pd.read_excel(tmp.name)
        content = result_df['상품명_1'].iloc[0]
        
        print("\n=== 엣지 케이스 결과 ===")
        print(f"변환된 내용: '{content}'")
        
        # 사전에 없는 브랜드는 원본값 유지
        assert '없는브랜드' in content, "사전에 없는 브랜드 처리 실패"
        # 공백이 제거된 색상의 유의어 확인
        assert '레드' in content, "공백 처리된 색상의 유의어 변환 실패" 