from django.shortcuts import render, redirect
from .models import Student, Subject, Score
from .forms import StudentScoreForm

def input_student(request):
    if request.method == 'POST':
        form = StudentScoreForm(request.POST)
        if form.is_valid():
            sid = form.cleaned_data['student_id']
            name = form.cleaned_data['name']
            scores = {
                'English': form.cleaned_data['english'],
                'C Language': form.cleaned_data['c_language'],
                'Python': form.cleaned_data['python']
            }

            # 학생 생성 또는 불러오기
            student, created = Student.objects.get_or_create(student_id=sid, defaults={'name': name})

            # 과목과 점수 저장
            for subject_name, value in scores.items():
                subject, _ = Subject.objects.get_or_create(name=subject_name)
                Score.objects.create(student=student, subject=subject, score=value)

            return redirect('student_list')  # 입력 후 목록 페이지로 이동

    else:
        form = StudentScoreForm()
    return render(request, 'grade_calculator/input_form.html', {'form': form})


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
        scores = Score.objects.filter(student=student)
        total = sum(s.score for s in scores)
        avg = total / scores.count() if scores.exists() else 0
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


def calculate_grade(avg):
    if avg >= 90: return 'A'
    elif avg >= 80: return 'B'
    elif avg >= 70: return 'C'
    elif avg >= 60: return 'D'
    else: return 'F'
