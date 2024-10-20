import requests
import OpenDartReader

import os
import sys
from datetime import datetime, timedelta
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic

# 인증키 얻기
#  - https://opendart.fss.or.kr/uat/uia/egovLoginUsr.do 페이지에서 신청
#  - ec4c456cb7a8044a2da714f47e01097a7b1de74c
# 공시검색 개발가이드 : https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019001

# OpenDartReader
# https://github.com/FinanceData/OpenDartReader

# UI 로드
ui_form = uic.loadUiType("dart_query.ui")[0]

class App(QMainWindow, ui_form) :
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("DART") # 제목 표시줄 
        self.start_date = ''
        self.end_date = ''
        self.api_key = 'ec4c456cb7a8044a2da714f47e01097a7b1de74c'

        self.init_directory()
        self.init_ui()
         
        try:
            self.connect_open_dart_reader()
        except:
            QMessageBox.about(self, "error", f"Dart 연결 실패")
            sys.exit()

    def init_directory(self):
        doc_dir = 'document'
        if not os.path.exists(doc_dir):
            os.makedirs(doc_dir)

    def init_ui(self):
        # 키 / 마우스 바인드
        self.ConfirmButton.clicked.connect(self.confirmClicked)
        self.CorpCodeTextEdit.returnPressed.connect(self.on_enter)
        self.ReportNameTextEdit.returnPressed.connect(self.on_enter)
        self.CompanyNameTextEdit.returnPressed.connect(self.on_enter)

        # 포커스 안가게 함.
        self.startDateEdit.setFocusPolicy(Qt.ClickFocus)
        self.endDateEdit.setFocusPolicy(Qt.ClickFocus)
        self.ConfirmButton.setFocusPolicy(Qt.NoFocus)

        # 기본적으로 종목코드 입력난에 포커스 지정.
        self.CorpCodeTextEdit.setFocus();                

        # 초기날짜는 오늘 부터 20일 부터 한다.
        today_date = QDateTime.currentDateTime()
        start_date = today_date .addDays(-10)
        self.startDateEdit.setDateTime(start_date)
        self.endDateEdit.setDateTime(QDateTime.currentDateTime())

    def connect_open_dart_reader(self):        
        self.dart = OpenDartReader(self.api_key)

    def on_enter(self):
        self.download_info()

    def confirmClicked(self):
        self.download_info()

    def download_info(self):
        corp_code = self.CorpCodeTextEdit.displayText()
        report_name = self.ReportNameTextEdit.displayText()
        company_name = self.CompanyNameTextEdit.displayText()
        start_date = self.startDateEdit.date().toString("yyyyMMdd")
        end_date = self.endDateEdit.date().toString("yyyyMMdd")

        return_value = self.download_info_from_dart(start_date, end_date, corp_code, report_name, company_name)
        display_start_date = self.startDateEdit.date().toString("yyyy-MM-dd")
        display_end_date = self.endDateEdit.date().toString("yyyy-MM-dd")
        if return_value == True:        
            QMessageBox.about(self, "message", f"다운로드 완료")
        else:
            QMessageBox.about(self, "message", f"정보를 찾지 못했습니다")

    def download_info_from_dart(self, start_date, end_date, filter_corp_code, filter_report_name, filter_company_name):
        report_company_name_index = 1 # 회사명
        report_name_index = 4 # 보고서명
        receipt_num_index = 5 # 접수번호

        # 종목번호로 직접 가져오는경우
        if (len(filter_corp_code) > 0):
            try:
                full_list = self.dart.list(corp=filter_corp_code, start=start_date, end=end_date, final=True)
            except:
                return False
        else:      
            full_list = self.dart.list(start=start_date, end=end_date, final=True)

        if len(full_list.values) == 0:
            return False

        is_find_info = False
        for info in full_list.values:
            company_name = str(info[report_company_name_index])
            report_name = str(info[report_name_index])
            receipt_num = str(info[receipt_num_index])
            check_report_name = True
            check_company_name = True
            if (len(filter_report_name) > 0 and report_name.find(filter_report_name) == -1):
                check_report_name = False
            if (len(filter_company_name) > 0 and company_name.find(filter_company_name) == -1):
                check_company_name = False
            if (check_report_name and check_company_name):
                files = self.dart.attach_files(receipt_num)
                for file_path, url in files.items():
                    pdf_file_name = 'document/' + file_path
                    self.dart.download(url, pdf_file_name)
                    is_find_info = True
        return is_find_info
        
app = QApplication(sys.argv)
window = App()
window.show()
sys.exit(app.exec_())