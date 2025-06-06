import csv
from django.core.management.base import BaseCommand
from accounts.models import Location

class Command(BaseCommand):
    help = 'CSV 파일로부터 Location 데이터를 불러옵니다.'

    def handle(self, *args, **kwargs):
        with open('korean_sigungu_list.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            for row in reader:
                sido = row['sido'].strip()
                sigungu = row['sigungu'].strip()
                # town = row['town'].strip()
                Location.objects.get_or_create(sido=sido, sigungu=sigungu)
                count += 1

        self.stdout.write(self.style.SUCCESS(f'{count}개의 Location 데이터가 등록되었습니다.'))