from accounts.views import main_page
from django.shortcuts import render
from django.conf import settings
import os
import sys
import subprocess
def home(request):
    return main_page(request)         # 메인화면을 그대로 띄움

# 복지 API 호출 view
def search_api(request):
    # 사용자 입력 받기
    age = request.GET.get("age", "30")  # 나이 (기본: 30)     # 생년월일만 받기 때문에 변환 코드 필요
    keyword = request.GET.get("searchWrd", "출산") # 검색 키워드 (기본: 출산)
    life = request.GET.get("lifeArray", "")  # 생애주기 정보 (선택)
    target = request.GET.get("trgterIndvdlArray", "")  # 대상자 정보 (선택)
    interest = request.GET.get("intrsThemaArray", "")  # 관심주제 정보 (선택)

    #  복지 API 호출 스크립트 경로 및 실행 파일 지정
    script_path = os.path.join(os.path.dirname(__file__), 'utils', 'central_welfare_api.py')
    python_executable = sys.executable
    result_path = os.path.join(settings.BASE_DIR, 'media', 'api_result.txt')  # 결과 저장 경로

    try:
        # API 실행 (출력은 파일에 저장됨)
        subprocess.run(
            [python_executable, script_path, age, keyword, life, target, interest],
            check=False
        )

        services = []  # 화면에 보여줄 서비스 정보 리스트

        # 결과 파일 읽기
        if os.path.exists(result_path):
            with open(result_path, "r", encoding="utf-8") as f:
                blocks = f.read().split("\n\n")
                for block in blocks:
                    lines = block.strip().splitlines()
                    if len(lines) >= 6:  # 필수 정보가 충분히 있는 경우
                        name = lines[0].strip()
                        serv_id = next((line.split("서비스 ID:")[1].strip() for line in lines if "서비스 ID:" in line), "")
                        ministry = next((line.split("부처:")[1].strip() for line in lines if "부처:" in line), "")
                        phone = next((line.split("문의:")[1].strip() for line in lines if "문의:" in line), "")
                        summary = next((line.split("요약:")[1].strip() for line in lines if "요약:" in line), "")
                        link = next((line.split("링크:")[1].strip() for line in lines if "링크:" in line), "")
                        services.append({
                            "id": serv_id,
                            "name": name,
                            "summary": summary,
                            "ministry": ministry,
                            "phone": phone,
                            "link": link
                        })
        else:
            services = [{
                "name": "결과 파일이 존재하지 않습니다.",
                "summary": "", "ministry": "", "phone": "", "link": "#"
            }]

    except Exception as e:
        services = [{
            "name": f" 예외 발생: {e}",
            "summary": "", "ministry": "", "phone": "", "link": "#"
        }]

    return render(request, 'myapp/welfare.html', {'services': services})

