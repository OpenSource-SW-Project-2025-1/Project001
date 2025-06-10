import requests
import xml.etree.ElementTree as ET
import sys
import os
import django

#  Django 설정 초기화
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BOKMANI_Project.settings')
django.setup()

from django.conf import settings

# API URL 및 서비스 키 정의
base_list_url = "http://apis.data.go.kr/B554287/NationalWelfareInformationsV001/NationalWelfarelistV001"
base_detail_url = "http://apis.data.go.kr/B554287/NationalWelfareInformationsV001/NationalWelfaredetailedV001"
service_key = "CgiK/2Ib1MAAnwFFRs6sAKrz1sOwmMAPJrMqEcEnCdq+ytCunvXYxsyzyzzPk6t96xz706kdATdeQltO6GY9iw=="

params = {
    "serviceKey": service_key,  # 인증키
    "callTp": "L",  # 호출 구분 (리스트)
    "pageNo": 1,  # 페이지 번호
    "numOfRows": 3,  # 한 페이지 결과 수
    "srchKeyCode": "001",   # 검색 키 코드
    "searchWrd": "출산",   # 검색어 (예: 출산)
    "age": "30",  # 연령 (예: 30세)
    "onapPsbltYn": "Y",  # 온라인 신청 가능 여부
    "orderBy": "popular"   # 정렬 기준: 인기순
}

if __name__ == "__main__":
    # 인자 처리
    if len(sys.argv) >= 3:
        params["age"] = sys.argv[1]  # 첫 번째 인자: 나이
        params["searchWrd"] = sys.argv[2]   # 두 번째 인자: 검색어
    if len(sys.argv) >= 4 and sys.argv[3]:
        params["lifeArray"] = sys.argv[3]  # 세 번째 인자: 생애주기 배열
    if len(sys.argv) >= 5 and sys.argv[4]:
        params["trgterIndvdlArray"] = sys.argv[4]  # 네 번째 인자: 대상자 유형
    if len(sys.argv) >= 6 and sys.argv[5]:
        params["intrsThemaArray"] = sys.argv[5]  # 다섯 번째 인자: 관심주제

    # api 요청 실행
    response = requests.get(base_list_url, params=params)

    # 결과 저장 경로: media/api_result.txt
    output_dir = os.path.join(settings.BASE_DIR, 'media')
    os.makedirs(output_dir, exist_ok=True)
    result_path = os.path.join(output_dir, 'api_result.txt')

    # 응답이 성공한 경우 (status code 200)
    if response.status_code == 200:
        try:
            root = ET.fromstring(response.text)
            items = root.findall(".//servList")  # 복지 서비스 리스트 추출

            with open(result_path, "w", encoding="utf-8") as f:
                f.write(f"조회된 복지 서비스 수: {len(items)}\n\n")

                for i, item in enumerate(items, start=1):
                    # 목록에서 제공하는 항목들 추출
                    serv_id = item.findtext("servId")  # 서비스 ID
                    name = item.findtext("servNm")  # 서비스명
                    interest = item.findtext("intrsThemaArray")  # 관심주제
                    ministry = item.findtext("jurMnofNm")  # 소관 부처명
                    department = item.findtext("jurOrgNm")  # 소관 조직명
                    life_cycle = item.findtext("lifeArray")  # 생애주기
                    online_apply = item.findtext("onapPsbltYn")  # 온라인 신청 가능 여부
                    phone = item.findtext("rprsCtadr")  # 문의처
                    summary = item.findtext("servDgst")  # 서비스 요약
                    link = item.findtext("servDtlLink")  # 상세 링크
                    cycle = item.findtext("sprtCycNm")  # 지원주기
                    type = item.findtext("srvPvsnNm")  # 제공유형
                    reg_date = item.findtext("svcfrstRegTs")  # 등록일
                    household = item.findtext("trgterIndvdlArray")  # 가구유형

                    # 파일에 복지 서비스 정보 기록
                    f.write(f"{i}\n")
                    f.write(f"{serv_id}\n")
                    f.write(f"{name}\n")
                    f.write(f"{interest}\n")
                    f.write(f"{ministry}\n")
                    f.write(f"{department}\n")
                    f.write(f"{life_cycle}\n")
                    f.write(f"{online_apply}\n")
                    f.write(f"{phone}\n")
                    f.write(f"{summary}\n")
                    f.write(f"{link}\n")
                    f.write(f"{cycle}\n")
                    f.write(f"{type}\n")
                    f.write(f"{reg_date}\n")
                    f.write(f"{household}\n")

                    # 상세조회 요청
                    detail_params = {
                        "serviceKey": service_key,
                        "callTp": "D",
                        "servId": serv_id
                    }
                    detail_response = requests.get(base_detail_url, params=detail_params)

                    if detail_response.status_code == 200:
                        try:
                            detail_root = ET.fromstring(detail_response.text)
                            detail = detail_root

                            if detail is not None:
                                tgt = detail.findtext("tgtrDtlCn")  # 대상자 내용
                                crit = detail.findtext("slctCritCn")  # 선정 기준
                                benefit = detail.findtext("alwServCn")  # 급여 서비스

                                if any([tgt, crit, benefit]):
                                    f.write(f"{tgt or '정보 없음'}\n")
                                    f.write(f"{crit or '정보 없음'}\n")
                                    f.write(f"{benefit or '정보 없음'}\n")
                                else:
                                    f.write("상세정보 없음\n")
                            else:
                                f.write("상세 루트 없음\n")

                        except Exception as e:
                            f.write(f"상세 파싱 실패: {str(e)}\n")
                    else:
                        f.write(f"상세 요청 실패 (code {detail_response.status_code})\n")

                    f.write("\n")

        except Exception as e:
            # 파싱 오류 시 에러 메시지 저장
            with open(result_path, "w", encoding="utf-8") as f:
                f.write(" XML 파싱 실패: " + str(e))
    else:
        # 요청 실패 시 상태 코드 및 일부 응답 저장
        with open(result_path, "w", encoding="utf-8") as f:
            f.write(f" 요청 실패\n상태 코드: {response.status_code}\n응답 일부: {response.text[:300]}")
