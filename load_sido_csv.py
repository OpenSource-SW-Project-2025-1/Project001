import csv
from accounts.models import Sido

def run():
    with open('korean_sido_list.csv', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # 헤더 건너뜀

        for row in reader:
            Sido.objects.get_or_create(name=row[0])
