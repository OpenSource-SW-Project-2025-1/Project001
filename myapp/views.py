from accounts.views import main_page  # accounts 앱에서 메인 화면을 가져와서
def home(request):
    return main_page(request)         # 메인화면을 그대로 띄움
# 회원가입 시 중복확인버튼 클릭 시 기존 사용자 데이터 불러오는 코드 만들어주세요