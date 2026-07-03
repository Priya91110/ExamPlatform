from django.db import models
# Create your models here.
# models.py
from django.db import models

class Student(models.Model):
    enrollment_number = models.CharField(max_length=15, unique=True)
    dob = models.DateField()
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Question(models.Model):
    subject = models.CharField(max_length=100)
    text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    # correct_answer = models.CharField(max_length=1)  # A, B, C, or D
    ANSWER_CHOICES = [
    ('A', 'Option A'),
    ('B', 'Option B'),
    ('C', 'Option C'),
    ('D', 'Option D')]
    correct_answer = models.CharField(max_length=1, choices=ANSWER_CHOICES)


class Answer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=1, blank=True, null=True)  # A, B, C, D
   

class Result(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    score = models.IntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)








