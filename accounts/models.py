from django.db import models

# 지역 정보 (먼저 정의해야 함)
class Location(models.Model):
    location_no = models.AutoField(primary_key=True)
    sido = models.CharField(max_length=100, blank=True, null=True)
    sigungu = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.sido} {self.sigungu}".strip()

# 사용자 기본 정보
class User(models.Model):
    user_no = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=100)
    user_pw = models.CharField(max_length=100)

    def __str__(self):
        return self.user_id

# 사용자 프로필 (1:1)
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    user_name = models.CharField(max_length=100, blank=True, null=True)
    user_birthdate = models.DateField(blank=True, null=True)
    user_email = models.CharField(max_length=100, blank=True, null=True)
    user_phone_no = models.CharField(max_length=100, blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)

# 사용자 직업 정보 (1:1)
class UserJobInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    user_job = models.CharField(max_length=100, blank=True, null=True)
    user_classification = models.CharField(max_length=100, blank=True, null=True)
    user_income = models.FloatField()

# 복지 제도 정보
class WelfareProgram(models.Model):
    w_no = models.AutoField(primary_key=True)
    w_name = models.CharField(max_length=100)

    def __str__(self):
        return self.w_name

# 복지 수혜 조건 (1:1)
class WelfareCriteria(models.Model):
    welfare = models.OneToOneField(WelfareProgram, on_delete=models.CASCADE, primary_key=True)
    income_eligibility = models.FloatField()
    age_eligibility = models.IntegerField(blank=True, null=True)
    classification_eligibility = models.CharField(max_length=100, blank=True, null=True)

# 복지 시행 기간 (1:1)
class WelfarePeriod(models.Model):
    welfare = models.OneToOneField(WelfareProgram, on_delete=models.CASCADE, primary_key=True)
    p_issuance = models.DateField()
    p_end = models.DateField()

# 추천 결과 (N:N with extra fields)
class RecommendationResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    welfare = models.ForeignKey(WelfareProgram, on_delete=models.CASCADE)
    match_point = models.IntegerField()
    is_eligible = models.BooleanField()

    class Meta:
        unique_together = ('user', 'welfare')
