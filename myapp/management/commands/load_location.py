import csv
from django.core.management.base import BaseCommand
from accounts.models import Location

class Command(BaseCommand):
    help = 'Load location data from CSV'

    def handle(self, *args, **kwargs):
        with open('korean_sigungu_list.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                Location.objects.get_or_create(
                    sido=row['시도'].strip(),
                    sigungu=row['시군구'].strip()
                )
        self.stdout.write(self.style.SUCCESS('✅ Location data loaded successfully.'))