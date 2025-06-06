import requests
import xml.etree.ElementTree as ET
import sys
import os
import django

# ✅ Django 설정 초기화
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BOKMANI_Project.settings')
django.setup()

from django.conf import settings

url = "http://apis.data.go.kr/B554287/NationalWelfareInformationsV001/NationalWelfarelistV001"
service_key = "CgiK/2Ib1MAAnwFFRs6sAKrz1sOwmMAPJrMqEcEnCdq+ytCunvXYxsyzyzzPk6t96xz706kdATdeQltO6GY9iw=="

params = {
    "serviceKey": service_key,
    "callTp": "L",
    "pageNo": 1,
    "numOfRows": 10,
    "srchKeyCode": "001",
    "searchWrd": "출산",
    "age": "30",
    "onapPsbltYn": "Y",
    "orderBy": "popular"
}

if __name__ == "__main__":
    # 인자 처리
    if len(sys.argv) >= 3:
        params["age"] = sys.argv[1]
        params["searchWrd"] = sys.argv[2]
    if len(sys.argv) >= 4 and sys.argv[3]:
        params["lifeArray"] = sys.argv[3]
    if len(sys.argv) >= 5 and sys.argv[4]:
        params["trgterIndvdlArray"] = sys.argv[4]
    if len(sys.argv) >= 6 and sys.argv[5]:
        params["intrsThemaArray"] = sys.argv[5]

    response = requests.get(url, params=params)

    # 결과 저장 경로: media/api_result.txt
    output_dir = os.path.join(settings.BASE_DIR, 'media')
    os.makedirs(output_dir, exist_ok=True)
    result_path = os.path.join(output_dir, 'api_result.txt')

    if response.status_code == 200:
        try:
            root = ET.fromstring(response.text)
            items = root.findall(".//servList")

            with open(result_path, "w", encoding="utf-8") as f:
                f.write(f"조회된 복지 서비스 수: {len(items)}\n\n")

                for i, item in enumerate(items, start=1):
                    name = item.findtext("servNm")
                    summary = item.findtext("servDgst")
                    ministry = item.findtext("jurMnofNm")
                    phone = item.findtext("rprsCtadr")
                    link = item.findtext("servDtlLink")

                    f.write(f"[{i}] 📌 {name}\n")
                    f.write(f"🏛 부처: {ministry}\n")
                    f.write(f"📞 문의: {phone}\n")
                    f.write(f"📄 요약: {summary}\n")
                    f.write(f"🔗 링크: {link}\n\n")

        except Exception as e:
            with open(result_path, "w", encoding="utf-8") as f:
                f.write("❌ XML 파싱 실패: " + str(e))
    else:
        with open(result_path, "w", encoding="utf-8") as f:
            f.write(f"❌ 요청 실패\n상태 코드: {response.status_code}\n응답 일부: {response.text[:300]}")
