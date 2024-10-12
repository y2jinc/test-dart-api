import requests
from io import BytesIO
import zipfile
import json
import os
from datetime import datetime, timedelta

# 인증키 얻기
#  - https://opendart.fss.or.kr/uat/uia/egovLoginUsr.do 페이지에서 신청
#  - ec4c456cb7a8044a2da714f47e01097a7b1de74c
# 공시검색 개발가이드 : https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019001

def get_list_by_report_name(data_list: dict, filter_name: str) -> list:
  ret_dict = []
  for data in data_list:
      if data.get('report_nm').find(filter_name) >= 0:
          ret_dict.append(data)
  return ret_dict

def request_get(url, pay_load):
    res = requests.get(url,pay_load)
    # url?param1=value1 param2=value2
    url_with_params = url + '?'
    for k, v in pay_load.items():
       url_with_params += k + '=' + str(v) + ' '
    print(url_with_params)
    return res

# 오늘 날짜 구하기
today = datetime.now().strftime('%Y%m%d')

# 오늘부터 5일전 날짜 구하기
five_days_ago = (datetime.now() - timedelta(days=5)).strftime('%Y%m%d')

# 공시검색 모든 페이지 순회
# page_count : 페이지당 건수(1~100)
# bgn_de : 검색시작 접수일자(YYYYMMDD)
# end_de : 검색종료 접수일자(YYYYMMDD)
# last_reprt_at : 최종보고서만 검색여부(Y or N)
api_key = 'ec4c456cb7a8044a2da714f47e01097a7b1de74c'

print('=== 공개매수설명서 조회하기' + five_days_ago + '-' + today + ' ===')

request_list_url = 'https://opendart.fss.or.kr/api/list.json'
pay_load = {'crtfc_key': api_key, 'page_no': 1, 'page_count': 100, 'bgn_de': five_days_ago, 'end_de': today, 'last_reprt_at': 'Y'}
res = request_get(request_list_url, pay_load)

json_content = json.loads(res.content)
total_page = json_content.get('total_page')

data = json.loads(res.text)
data_list = data.get('list')

filter_name = "공개매수설명서"
result_list = get_list_by_report_name(data_list, filter_name)
for i in range(2, total_page):
    pay_load['page_no'] = i
    res = request_get(request_list_url, pay_load)
    json_data = json.loads(res.text)
    json_data_list = json_data.get('list')
    result_list += get_list_by_report_name(json_data_list, filter_name)

print('=== 문서 다운로드 ===')
# 문서 다운로드
# rcept_no : 접수번호
# corp_name : 회사명
# report_nm : 보고서명
# rcept_dt : 접수일자

request_document_url = 'https://opendart.fss.or.kr/api/document.xml'
pay_load = {'crtfc_key': api_key, 'rcept_no': ''}
for data in result_list:
    pay_load['rcept_no'] = data.get('rcept_no')
    res = request_get(request_document_url, pay_load)
    zip_file = zipfile.ZipFile(BytesIO(res.content))
    zip_file.extractall('document')    
    src_xml_file_name = 'document/' + data.get('rcept_no')+ '.xml'
    dest_xml_file_name = 'document/' + '[' + data.get('corp_name') + ']' + data.get('report_nm') + '(' + data.get('rcept_dt') + ')' + '.xml'
    os.replace(src_xml_file_name, dest_xml_file_name)
    print(dest_xml_file_name)
