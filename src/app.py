# app.py
import os
# 운영체제별 플랫폼 자동 설정
import platform
if platform.system() == "Windows":
    os.environ["QT_QPA_PLATFORM"] = "windows"
elif platform.system() == "Linux":
    os.environ["QT_QPA_PLATFORM"] = "xcb"
import pandas as pd
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QCheckBox, QSpinBox, QFileDialog, QTableView,
    QStatusBar, QMessageBox, QInputDialog, QProgressDialog, QHeaderView,
    QTextEdit
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtWidgets import QApplication
import json
import os.path

from synonyms_manager import load_synonym_dict_from_sheets
from transform import generate_titles
from dataframe_model import DataFrameModel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("유의어 치환기")

        # --- 멤버 변수 초기화 ---
        self._df = pd.DataFrame()
        self.file_path = ""
        self.synonym_dict = {}
        self.current_sheet = ""
        self.settings_file = "settings.json"
        self.last_directory = ""  # 추가: 초기값 설정

        # --- UI 초기화 ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # (1) 상단: 파일 열기
        top_panel = QHBoxLayout()
        self.label_file = QLabel("불러온 파일: (없음)")
        self.btn_open = QPushButton("파일 열기")
        self.btn_open.clicked.connect(self.open_file_dialog)
        top_panel.addWidget(self.label_file)
        top_panel.addWidget(self.btn_open)
        main_layout.addLayout(top_panel)

        # (2) 체크박스 영역 수정
        opt_layout = QHBoxLayout()

        # 왼크박스 객체들 먼저 생성
        self.chk_brand = QCheckBox("브랜드")
        self.chk_color = QCheckBox("색상")
        self.chk_pattern = QCheckBox("패턴")
        self.chk_material = QCheckBox("소재")
        self.chk_category = QCheckBox("카테고리")

        # 왼쪽: 카테고리 체크박스들
        category_group = QHBoxLayout()
        category_group.addWidget(self.chk_brand)
        category_group.addWidget(self.chk_color)
        category_group.addWidget(self.chk_pattern)
        category_group.addWidget(self.chk_material)
        category_group.addWidget(self.chk_category)
        opt_layout.addLayout(category_group)

        # 중앙: 구분선
        opt_layout.addWidget(QLabel(" | "))  # 공백 추가

        # 오른쪽: 설정 그룹
        settings_group = QHBoxLayout()

        # 버전 개수 입력
        version_layout = QHBoxLayout()
        label_version = QLabel("버전:")
        self.spin_version = QSpinBox()
        self.spin_version.setMinimum(1)
        self.spin_version.setMaximum(10)
        self.spin_version.setValue(1)
        self.spin_version.setFixedWidth(50)  # 너비 고정
        version_layout.addWidget(label_version)
        version_layout.addWidget(self.spin_version)
        settings_group.addLayout(version_layout)

        # 덮어쓰기 체크박스
        self.chk_overwrite = QCheckBox("덮어쓰기")
        self.chk_overwrite.setChecked(True)  # 기본값 = 덮어쓰기
        settings_group.addWidget(self.chk_overwrite)

        # 실행 버튼
        self.btn_transform = QPushButton("실행")
        self.btn_transform.clicked.connect(self.transform_data)  # 이벤트 핸들러 연결 추가
        settings_group.addWidget(self.btn_transform)

        opt_layout.addLayout(settings_group)
        main_layout.addLayout(opt_layout)

        # 테이블뷰 안내 레이블
        table_guide = QLabel(
            "※ 행 선택 방법:\n"
            "  - 단일 행 선택: 행 클릭\n"
            "  - 연속 선택: Shift + 클릭\n"
            "  - 개별 선택: Ctrl + 클릭"
        )
        table_guide.setStyleSheet("color: #666666;")  # 회색으로 표시
        main_layout.addWidget(table_guide)

        # (3) 테이블뷰
        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.ExtendedSelection)
        self.table_view.setEditTriggers(QTableView.NoEditTriggers)
        
        # 모델 먼저 설정
        self._model = DataFrameModel()
        self._model.setDataFrame(pd.DataFrame())
        self.table_view.setModel(self._model)
        
        # 그 다음 헤더 설정
        header = self.table_view.horizontalHeader()
        header.setStretchLastSection(True)
        
        # 기본 열 크기 설정
        for i in range(header.count()):
            if i < 5:  # 처음 5개 열
                header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
            else:  # 나머지 열
                header.setSectionResizeMode(i, QHeaderView.Interactive)
                header.setDefaultSectionSize(100)  # 기본 너비 설정
        
        # 행 설정
        self.table_view.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table_view.verticalHeader().setDefaultSectionSize(25)
        
        # 선택 변경 이벤트 연결
        self.table_view.selectionModel().selectionChanged.connect(self.on_selection_changed)

        # 테이블뷰 크기 정책 설정
        self.table_view.setMinimumHeight(400)  # 테이블 최소 높이 설정
        main_layout.addWidget(self.table_view)

        # 로그 텍스트 영역 크기 조정
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(100)  # 로그창 최대 높이 제한
        main_layout.addWidget(self.log_text)

        # 저장 관련 코드 제거
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # 설정 로드는 모든 초기화가 끝난 후에
        try:
            self.loadSettings()
        except Exception as e:
            print(f"설정 로드 실패: {str(e)}")

    def open_file_dialog(self):
        dlg = QFileDialog(self)
        dlg.setNameFilters(["Excel Files (*.xlsx *.xls)", "All Files (*)"])
        if dlg.exec():
            selected_file = dlg.selectedFiles()[0]
            if selected_file:
                # 엑셀 파일 로드
                self.load_excel_file(selected_file)
                
                # 같은 파일에서 유의어 사전 시트들 로드
                try:
                    self.synonym_dict = load_synonym_dict_from_sheets(selected_file)
                    if self.synonym_dict:
                        self.status_bar.showMessage(f"유의어 사전 로드 완료: {len(self.synonym_dict)}개 단어")
                    else:
                        QMessageBox.warning(self, "경고", "유의어 사전 시트(브랜드,색상,패턴,소재,카테고리)를 찾을 수 없습니다.")
                except Exception as e:
                    QMessageBox.warning(self, "경고", f"유의어 사전 로드 실패: {str(e)}")

    def load_excel_file(self, path: str):
        try:
            wb = pd.ExcelFile(path)
            if len(wb.sheet_names) > 1:
                sheet_name, ok = QInputDialog.getItem(
                    self,
                    "시트 선택",
                    "처리할 시트를 선택하세요:",
                    wb.sheet_names,
                    0,  # 기본값 = 첫번째 시트
                    False  # 수정 불가
                )
                if not ok:
                    return
            else:
                sheet_name = wb.sheet_names[0]
            
            df = pd.read_excel(path, sheet_name=sheet_name)
            self._df = df
            self._model.setDataFrame(df)
            self.file_path = path
            self.current_sheet = sheet_name  # 시트 이름 저장
            self.label_file.setText(f"불러온 파일: {path} ({sheet_name})")
            self.status_bar.showMessage(f"{len(df)} 행 로드 완료")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"파일 열기 실패: {e}")

    def transform_data(self):
        try:
            # 기본 검증
            if self._df.empty:
                QMessageBox.warning(self, "경고", "먼저 파일을 열어주세요.")
                return
            
            if not self.synonym_dict:
                QMessageBox.warning(self, "경고", "유의어 사전이 로드되지 않았습니다.")
                return
            
            # 선택된 카테고리 확인
            col_selection = []
            if self.chk_brand.isChecked(): col_selection.append("브랜드")
            if self.chk_color.isChecked(): col_selection.append("색상")
            if self.chk_pattern.isChecked(): col_selection.append("패턴")
            if self.chk_material.isChecked(): col_selection.append("소재")
            if self.chk_category.isChecked(): col_selection.append("카테고리")
            
            if not col_selection:
                QMessageBox.warning(self, "경고", "하나 이상의 카테고리를 선택해주세요.")
                return
            
            # 선택된 행 확인
            selected_rows = []
            for idx in self.table_view.selectionModel().selectedRows():
                row_num = idx.row() + 2  # 여기를 수정
                selected_rows.append(row_num)
            
            if not selected_rows:
                QMessageBox.warning(self, "경고", "행을 선택해주세요.")
                return
            
            # 진행 상태 표시
            progress = QProgressDialog("처리 중...", "취소", 0, len(selected_rows), self)
            progress.setWindowModality(Qt.WindowModal)
            
            def update_progress(current, total):
                progress.setValue(current)
            
            # 로그창 초기화
            self.log_text.clear()
            
            def update_log(text):
                self.log_text.append(text)
                self.log_text.verticalScrollBar().setValue(
                    self.log_text.verticalScrollBar().maximum()
                )  # 자동 스크롤
            
            # 선택된 행 출력을 로그창으로 이동
            update_log(f"선택된 행: {', '.join(map(str, selected_rows))}")
            
            # 유의어 치환 실행
            generate_titles(
                self.file_path,
                self.current_sheet,
                col_selection,
                self.synonym_dict,
                selected_rows,
                self.spin_version.value(),
                update_progress,
                update_log,
                self._model
            )
        except Exception as e:
            QMessageBox.critical(self, "오류", f"제목 생성 중 오류 발생: {str(e)}")

    def on_selection_changed(self, selected, deselected):
        rows = self.table_view.selectionModel().selectedRows()
        if rows:
            self.status_bar.showMessage(f"{len(rows)}개 행 선택됨")

    def loadSettings(self):
        """설정 파일 로드"""
        if not os.path.exists(self.settings_file):
            return
        
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            # 체크박스 매핑 수정 - 초기화 이후에 매핑
            self.checkbox_mapping = {
                'brand': self.chk_brand,
                'color': self.chk_color,
                'pattern': self.chk_pattern,
                'material': self.chk_material,
                'category': self.chk_category
            }
            
            # 체크박스 상태 복원
            for key, checkbox in self.checkbox_mapping.items():
                if key in settings:
                    checkbox.setChecked(settings[key])
            
            # 버전 수 복원
            if 'versions' in settings:
                self.spin_version.setValue(settings['versions'])
            
            # 최근 파일 경로 복원
            self.last_directory = settings.get('last_directory', '')
            
        except Exception as e:
            print(f"설정 로드 중 오류 발생: {str(e)}")

    def saveSettings(self):
        """설정 저장"""
        settings = {
            'brand': self.chk_brand.isChecked(),
            'color': self.chk_color.isChecked(),
            'pattern': self.chk_pattern.isChecked(),
            'material': self.chk_material.isChecked(),
            'category': self.chk_category.isChecked(),
            'versions': self.spin_version.value(),
            'last_directory': os.path.dirname(self.file_path) if self.file_path else ''
        }
        
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"설정 저장 중 오류 발생: {str(e)}")

    def closeEvent(self, event):
        """프로그램 종료 시 설정 저장"""
        self.saveSettings()
        super().closeEvent(event)

