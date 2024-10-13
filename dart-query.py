import requests
from datetime import datetime, timedelta
import OpenDartReader
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic

# 오늘 날짜 구하기
end_date = datetime.now().strftime('%Y%m%d')

# 오늘부터 5일전 날짜 구하기
start_date = (datetime.now() - timedelta(days=20)).strftime('%Y%m%d')

api_key = 'ec4c456cb7a8044a2da714f47e01097a7b1de74c'

def download_info(filter_corp_code, filter_report_name, filter_company_name):
    report_company_name_index = 1 # 보고서명
    report_name_index = 4 # 보고서명
    receipt_num_index = 5 # 접수번호
    # 종목번호로 직접 가져오는경우
    if (len(filter_corp_code) > 0):
      full_list = dart.list(corp='088980', final=True)
    else:
      # 일주일간의 공시목록을 가져온다
      full_list = dart.list(start=start_date, end=end_date, final=True)

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
        files = dart.attach_files(receipt_num)
        for file_path, url in files.items():
          pdf_file_name = 'document/' + file_path
          dart.download(url, pdf_file_name)

dart = OpenDartReader(api_key)
# 다운로드 받는 사이트에서 연결실패 처리되서 아래의 요청을 먼저 보낸다. User-Agent 값을 먼저보내서 정상적인 유저임을 알림.
# res = requests.get('http://dart.fss.or.kr/dsaf001/main.do',
#                    headers={"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/)"})

form = uic.loadUiType("dart_search.ui")[0]

# 화면구성이 저장되어 있는 form을 이용한 메인 윈도우 만들기
# form에 저장되어 있는 속성 및 메소드를 모두 상속
# setupUi() 메소드를 통해서 form의 속성 및 메소드를 설정
class App(QMainWindow, form) :
    def __init__(self):
        super().__init__()
        self.setGeometry(300, 300, 800, 480)
        self.setupUi(self)
        self.setWindowTitle("DRY") # 제목 표시줄 
        self.DownloadButton.clicked.connect(self.downloadClicked)        

    def downloadClicked(self):
        corp_code = self.CorpCodeTextEdit.toPlainText()
        report_name = self.ReportNameTextEdit.toPlainText()
        company_name = self.CompanyNameTextEdit.toPlainText()        
        download_info(corp_code, report_name, company_name)
        QMessageBox.about(self, "message", "다운로드 완료")
        
app = QApplication(sys.argv)
window = App()
window.show()
sys.exit(app.exec_())