from django.contrib import admin
from accounts.models import UserID,UserProfile,UserJobInfo

admin.site.register(UserID)
admin.site.register(UserProfile)
admin.site.register(UserJobInfo)
# Register your models here.
