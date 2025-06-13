from django.shortcuts import render, redirect
from .models import Student
from .forms import StudentScoreForm

def input_student(request):
    if request.method == 'POST':
        form = StudentScoreForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('student_list')  # ← 자동 이동
    else:
        form = StudentScoreForm()
    return render(request, 'grade_calculator/main.html', {'form': form})

def calculate_grade(avg):
    if avg >= 90: return 'A'
    elif avg >= 80: return 'B'
    elif avg >= 70: return 'C'
    elif avg >= 60: return 'D'
    else: return 'F'


def student_list(request):
    query_id = request.GET.get('student_id', '')
    query_name = request.GET.get('name', '')

    students = Student.objects.all()
    if query_id:
        students = students.filter(student_id__icontains=query_id)
    if query_name:
        students = students.filter(name__icontains=query_name)

    student_data = []

    for student in students:
        try:
            en = float(student.en_grade)
            c = float(student.c_grade)
            py = float(student.py_grade)
        except ValueError:
            en, c, py = 0, 0, 0  # 잘못된 입력 방지용

        total = en + c + py
        avg = total / 3
        grade = calculate_grade(avg)

        student_data.append({
            'student': student,
            'total': total,
            'avg': avg,
            'grade': grade
        })

    # 등수 계산
    student_data.sort(key=lambda x: x['total'], reverse=True)
    for idx, data in enumerate(student_data):
        data['rank'] = idx + 1

    over_80_count = sum(1 for data in student_data if data['avg'] >= 80)

    return render(request, 'grade_calculator/student_list.html', {
        'students': student_data,
        'over_80_count': over_80_count,
        'query_id': query_id,
        'query_name': query_name,
    })
