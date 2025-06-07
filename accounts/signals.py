import csv
import os
from django.conf import settings
from .models import Location

def load_location_data(sender, **kwargs):
    csv_path = os.path.join(settings.BASE_DIR, 'korean_sigungu_list.csv')

    if not os.path.exists(csv_path):
        print(f"⚠️ CSV 파일이 존재하지 않습니다: {csv_path}")
        return

    with open(csv_path, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0
        for row in reader:
            sido = row['sido'].strip()
            sigungu = row['sigungu'].strip()

            _, created = Location.objects.get_or_create(sido=sido, sigungu=sigungu)
            if created:
                count += 1

    print(f"✅ Location 데이터 {count}개 자동 로딩 완료")