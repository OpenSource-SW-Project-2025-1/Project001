from django.db import models

class Student(models.Model):
    student_id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    en_grade = models.CharField(max_length=100)
    c_grade = models.CharField(max_length=100)
    py_grade = models.CharField(max_length=100)
