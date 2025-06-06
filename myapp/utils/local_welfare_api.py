import subprocess
import os
import sys
import django

#  Django 설정 초기화
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BOKMANI_Project.settings')
django.setup()
from django.conf import settings

#  기본 파라미터 설정
query = {
    "pageNo": "1",
    "numOfRows": "10",
    "lifeArray": "007",
    "trgterIndvdlArray": "020",
    "intrsThemaArray": "080",
    "age": "30",
    "ctpvNm": "서울특별시",
    "sggNm": "강남구",
    "srchKeyCode": "001",
    "searchWrd": "출산",
    "arrgOrd": "002"
}

#  인자 처리
if len(sys.argv) >= 3:
    query["searchWrd"] = sys.argv[1]
    query["lifeArray"] = sys.argv[2]
if len(sys.argv) >= 4:
    query["trgterIndvdlArray"] = sys.argv[3]
if len(sys.argv) >= 5:
    query["intrsThemaArray"] = sys.argv[4]
if len(sys.argv) >= 6:
    query["age"] = sys.argv[5]
if len(sys.argv) >= 7:
    query["ctpvNm"] = sys.argv[6]
if len(sys.argv) >= 8:
    query["sggNm"] = sys.argv[7]

#  URL 직접 구성 (인코딩된 인증키 포함)
encoded_key = "CgiK%2F2Ib1MAAnwFFRs6sAKrz1sOwmMAPJrMqEcEnCdq%2BytCunvXYxsyzyzzPk6t96xz706kdATdeQltO6GY9iw%3D%3D"
base_url = "https://apis.data.go.kr/B554287/LocalGovernmentWelfareInformations/LcgvWelfarelist"
query_string = "&".join([f"{key}={value}" for key, value in query.items()])
full_url = f"{base_url}?serviceKey={encoded_key}&{query_string}"

#  결과 파일 경로
output_dir = os.path.join(settings.BASE_DIR, "media")
os.makedirs(output_dir, exist_ok=True)
result_path = os.path.join(output_dir, "local_api_result.txt")

#  curl 명령 실행 (SSL 우회)
try:
    result = subprocess.run(["curl", full_url], capture_output=True, text=True, timeout=15)
    if result.returncode == 0:
        with open(result_path, "w", encoding="utf-8") as f:
            f.write(result.stdout)
    else:
        with open(result_path, "w", encoding="utf-8") as f:
            f.write(" curl 호출 실패\n")
            f.write(result.stderr)
except Exception as e:
    with open(result_path, "w", encoding="utf-8") as f:
        f.write(" subprocess 오류 발생: " + str(e))
