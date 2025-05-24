from accounts.views import main_page  # accounts 앱에서 메인 화면을 가져와서
def home(request):
    return main_page(request)         # 메인화면을 그대로 띄움
