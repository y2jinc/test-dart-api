import requests
import OpenDartReader

import os
import sys
from datetime import datetime, timedelta
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import ssl

# 인증키 얻기
#  - https://opendart.fss.or.kr/uat/uia/egovLoginUsr.do 페이지에서 신청
#  - ec4c456cb7a8044a2da714f47e01097a7b1de74c
#  - d91ab08ab1606b828a4b28efa34e833f6acda093
# 공시검색 개발가이드 : https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019001

# OpenDartReader
# https://github.com/FinanceData/OpenDartReader

ssl._create_default_https_context = ssl._create_unverified_context
dart = OpenDartReader('d91ab08ab1606b828a4b28efa34e833f6acda093')

def download_info_from_dart(start_date, end_date, filter_corp_code, filter_report_name, filter_company_name):
    report_company_name_index = 1 # 회사명
    report_name_index = 4 # 보고서명
    receipt_num_index = 5 # 접수번호

    # 종목번호로 직접 가져오는경우
    if (len(filter_corp_code) > 0):
        try:
            full_list = dart.list(corp=filter_corp_code, start=start_date, end=end_date, final=True)
        except:
            return False
    else:      
        full_list = dart.list(start=start_date, end=end_date, final=True)

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
            files = dart.attach_files(receipt_num)
            for file_path, url in files.items():
                pdf_file_name = 'document/' + file_path
                try:
                    dart.download(url, pdf_file_name)                                           
                except:
                    print("message", "다운로드 실패")
            is_find_info = True
    return is_find_info


download_info_from_dart('20241013', '20241023', '043100', '', '알파녹스')