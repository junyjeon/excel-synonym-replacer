# app.py
import os
import pandas as pd
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QCheckBox, QSpinBox, QFileDialog, QTableView,
    QStatusBar, QMessageBox, QInputDialog, QProgressDialog
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex

from synonyms_manager import load_synonym_dict_from_sheets
from transform import replace_with_synonyms_in_row_v
from dataframe_model import DataFrameModel  # 별도 .py로 분리(아래 예시)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("유의어 치환기 (B~F → M열부터 다중 버전)")

        # --- 멤버 ---
        self._df = pd.DataFrame()
        self.file_path = ""
        self.synonym_dict = {}

        # --- 메인 레이아웃 ---
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

        # (2) 체크박스 영역
        opt_layout = QHBoxLayout()
        self.chk_brand = QCheckBox("브랜드")
        self.chk_color = QCheckBox("색상")
        self.chk_pattern = QCheckBox("패턴")
        self.chk_material = QCheckBox("소재")
        self.chk_category = QCheckBox("카테고리")

        opt_layout.addWidget(self.chk_brand)
        opt_layout.addWidget(self.chk_color)
        opt_layout.addWidget(self.chk_pattern)
        opt_layout.addWidget(self.chk_material)
        opt_layout.addWidget(self.chk_category)

        # 버전 스핀박스
        label_version = QLabel("버전 개수:")
        self.spin_version = QSpinBox()
        self.spin_version.setMinimum(1)
        self.spin_version.setMaximum(10)
        self.spin_version.setValue(1)  # 기본값=1
        opt_layout.addWidget(label_version)
        opt_layout.addWidget(self.spin_version)

        # 실행버튼
        self.btn_transform = QPushButton("실행 (M열부터 치환)")
        self.btn_transform.clicked.connect(self.transform_data)
        opt_layout.addWidget(self.btn_transform)
        main_layout.addLayout(opt_layout)

        # (3) 테이블뷰
        self.table_view = QTableView()
        self._model = DataFrameModel(self._df)
        self.table_view.setModel(self._model)
        main_layout.addWidget(self.table_view)

        # (4) 저장
        bottom_panel = QHBoxLayout()
        self.btn_save = QPushButton("저장")
        self.btn_save.clicked.connect(self.save_file_dialog)
        bottom_panel.addStretch(1)
        bottom_panel.addWidget(self.btn_save)
        main_layout.addLayout(bottom_panel)

        # 상태바
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

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
            self.label_file.setText(f"불러온 파일: {path} ({sheet_name})")
            self.status_bar.showMessage(f"{len(df)} 행 로드 완료")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"파일 열기 실패: {e}")

    def transform_data(self):
        if self._df.empty:
            QMessageBox.warning(self, "경고", "먼저 파일을 열어주세요.")
            return
            
        if not self.synonym_dict:
            QMessageBox.warning(self, "경고", "유의어 사전이 로드되지 않았습니다.")
            return

        # 체크된 항목 (테스트용으로 색상과 소재만)
        col_selection = []
        if self.chk_color.isChecked():    # 색상 체크
            col_selection.append("색상")
        if self.chk_material.isChecked():  # 소재 체크
            col_selection.append("소재")

        version_count = self.spin_version.value()  # 2개로 설정됨
        new_df = self._df.copy()

        # M열, N열 생성 (2개 버전)
        col_ascii_base = ord('M')
        for i in range(version_count):
            col_letter = chr(col_ascii_base + i)
            new_col = f"{col_letter}열"
            if new_col not in new_df.columns:
                new_df[new_col] = ""

        # 처음 3개 행만 처리
        test_rows = range(min(3, len(new_df)))
        
        print("\n=== 테스트 결과 ===")
        print(f"선택된 카테고리: {col_selection}")
        print(f"버전 개수: {version_count}")
        print("\n원본 -> 변환 결과:")
        
        for r in test_rows:
            row = new_df.iloc[r]
            # J열 인덱스로 접근
            orig_title = row.iloc[9] if len(row) > 9 else "제목 없음"  # J열은 10번째 열 (인덱스 9)
            print(f"\n[{r+1}번 제품]")
            print(f"원본: {orig_title}")
            
            # 버전별로 치환
            for v in range(version_count):
                col_letter = chr(col_ascii_base + v)
                new_col = f"{col_letter}열"
                new_title = replace_with_synonyms_in_row_v(
                    row, col_selection, self.synonym_dict, v
                )
                new_df.at[r, new_col] = new_title
                print(f"{col_letter}열: {new_title}")

        self._df = new_df
        self._model.setDataFrame(new_df)
        self.status_bar.showMessage("테스트 완료: 처음 3개 제품 처리됨")

    def save_file_dialog(self):
        if self._df.empty:
            QMessageBox.warning(self, "경고", "저장할 데이터가 없습니다.")
            return

        dlg = QFileDialog(self)
        dlg.setAcceptMode(QFileDialog.AcceptSave)
        dlg.setNameFilters(["Excel Files (*.xlsx)", "All Files (*)"])
        if dlg.exec():
            save_path = dlg.selectedFiles()[0]
            if save_path:
                self.save_excel_file(save_path)

    def save_excel_file(self, path: str):
        try:
            self._df.to_excel(path, index=False)
            QMessageBox.information(self, "완료", f"저장 완료: {path}")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"저장 실패: {e}")
