from accounts.views import main_page  # accounts 앱에서 메인 화면을 가져와서
from django.shortcuts import render, redirect


import os
import sys
import subprocess
def home(request):
    return main_page(request)         # 메인화면을 그대로 띄움

# 복지 API 호출 view
def welfare_view(request):
    # ✅ 사용자 입력 받기
    age = request.GET.get("age", "30")
    keyword = request.GET.get("searchWrd", "출산")
    life = request.GET.get("lifeArray", "")
    target = request.GET.get("trgterIndvdlArray", "")
    interest = request.GET.get("intrsThemaArray", "")

    # ✅ central_welfare_api.py 경로
    script_path = os.path.join(os.path.dirname(__file__), 'utils', 'central_welfare_api.py')
    python_executable = sys.executable
    result_path = "C:/Users/User/Desktop/api_result.txt"  # ✅ 결과 저장 경로

    try:
        # ✅ API 실행 (출력은 파일에 저장됨)
        subprocess.run(
            [python_executable, script_path, age, keyword, life, target, interest],
            check=False
        )

        services = []

        # ✅ 결과 파일 읽기
        if os.path.exists(result_path):
            with open(result_path, "r", encoding="utf-8") as f:
                blocks = f.read().split("\n\n")
                for block in blocks:
                    if "📌" in block:
                        lines = block.strip().splitlines()
                        name = lines[0].split("📌")[1].strip() if lines else ""
                        ministry = next((line.split("부처:")[1].strip() for line in lines if "부처:" in line), "")
                        phone = next((line.split("문의:")[1].strip() for line in lines if "문의:" in line), "")
                        summary = next((line.split("요약:")[1].strip() for line in lines if "요약:" in line), "")
                        link = next((line.split("링크:")[1].strip() for line in lines if "링크:" in line), "")
                        services.append({
                            "name": name,
                            "summary": summary,
                            "ministry": ministry,
                            "phone": phone,
                            "link": link
                        })
        else:
            services = [{
                "name": "⚠ 결과 파일이 존재하지 않습니다.",
                "summary": "", "ministry": "", "phone": "", "link": "#"
            }]

    except Exception as e:
        services = [{
            "name": f"❌ 예외 발생: {e}",
            "summary": "", "ministry": "", "phone": "", "link": "#"
        }]

    return render(request, 'myapp/welfare.html', {'services': services})

