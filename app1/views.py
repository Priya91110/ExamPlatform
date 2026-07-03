from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from .forms import LoginForm
from .models import Student
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Student, Question, Answer, Result
import csv
from django.contrib.auth.decorators import login_required, user_passes_test


# Create your views here.
def index(request):
    return render(request, "app1/index.html")

def login_view(request):
    form = LoginForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            enrollment_number = form.cleaned_data['enrollment_number']
            dob = form.cleaned_data['dob']

            try:
                student = Student.objects.get(enrollment_number=enrollment_number, dob=dob)
                # Store student in session
                request.session['student_id'] = student.id
                messages.success(request, f"Welcome, {student.name}!")
                return redirect('instructions')  # Change this to your exam dashboard route
            except Student.DoesNotExist:
                messages.error(request, "Invalid enrollment number or date of birth.")
    
    return render(request, 'app1/login.html', {'form': form})


def instructions_view(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('login')

    student = Student.objects.get(id=student_id)
    return render(request, 'app1/instructions.html', {'student_name': student.name})


def logout_view(request):
    # Logout user and flush the session data
    request.session.flush()  # Clears all session data
    return redirect('login')  # Redirect to login page


    # student_id = request.session.get('student_id')
    # if not student_id:
    #     return redirect('login')
    # prevent resubmit the test
    # if Result.objects.filter(student=student).exists():
    #     return redirect('thank_you')
  

def start_exam_view(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('login')

    student = Student.objects.get(id=student_id)

    if request.method == 'POST':
        if 'test' in request.POST:
            selected_test = request.POST.get('test', '').strip().lower()
            request.session['selected_test'] = selected_test
            request.session.modified = True

            if 'start_time' not in request.session:
                start_time = datetime.now()
                end_time = start_time + timedelta(minutes=10)
                request.session['start_time'] = start_time.isoformat()
                request.session['end_time'] = end_time.isoformat()
                request.session.modified = True
                print("✅ Start Time Set:", request.session['start_time'])
                print("✅ End Time Set:", request.session['end_time'])

            return redirect('start_exam')

    selected_test = request.session.get('selected_test')
    if not selected_test:
        return redirect('instructions')

    questions = Question.objects.filter(subject__iexact=selected_test)

    # Convert session strings to datetime objects
    start_time_str = request.session.get('start_time')
    end_time_str = request.session.get('end_time')
    start_time = datetime.fromisoformat(start_time_str) if start_time_str else None
    end_time = datetime.fromisoformat(end_time_str) if end_time_str else None

    return render(request, 'app1/start_exam.html', {
        'questions': questions,
        'start_time': start_time,
        'end_time': end_time
    })



def submit_exam_view(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('login')

    student = Student.objects.get(id=student_id)

    selected_test = request.session.get('selected_test')
    if not selected_test:
        messages.error(request, "No exam subject selected. Please start the exam again.")
        return redirect('instructions')

    questions = Question.objects.filter(subject__iexact=selected_test)
    if not questions.exists():
        messages.error(request, "No questions found for the selected exam.")
        return redirect('instructions')

    if request.method != 'POST':
        return redirect('start_exam')

    attempted = 0
    correct_answers = 0

    for question in questions:
        answer_value = request.POST.get(f'question_{question.id}')
        if answer_value:
            selected_answer = answer_value.strip().upper()
            Answer.objects.update_or_create(
                student=student,
                question=question,
                defaults={'selected_answer': selected_answer}
            )
            attempted += 1
            if selected_answer == question.correct_answer.strip().upper():
                correct_answers += 1
        else:
            Answer.objects.update_or_create(
                student=student,
                question=question,
                defaults={'selected_answer': None}
            )

    total_questions = questions.count()
    wrong_answers = attempted - correct_answers
    percentage = (correct_answers / total_questions) * 100 if total_questions else 0

    Result.objects.update_or_create(
        student=student,
        defaults={'score': correct_answers, 'submitted_at': timezone.now()}
    )

    request.session.pop('start_time', None)
    request.session.pop('end_time', None)

    request.session['result_data'] = {
        'score': correct_answers,
        'correct': correct_answers,
        'wrong': wrong_answers,
        'attempted': attempted,
        'total': total_questions,
        'percentage': round(percentage, 2)
    }
    request.session.modified = True

    return redirect('thank_you')


def thank_you_view(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('login')

    student = Student.objects.get(id=student_id)
    result = Result.objects.get(student=student)
    result_data = request.session.get('result_data')

    if not result_data:
        selected_test = request.session.get('selected_test')
        if selected_test:
            answers = Answer.objects.filter(student=student, question__subject__iexact=selected_test)
            total = Question.objects.filter(subject__iexact=selected_test).count()
        else:
            answers = Answer.objects.filter(student=student)
            total = answers.count()

        attempted = answers.exclude(selected_answer__isnull=True).exclude(selected_answer__exact='').count()
        correct_answers = sum(
            1 for answer in answers
            if answer.selected_answer and answer.selected_answer.strip().upper() == answer.question.correct_answer.strip().upper()
        )
        wrong_answers = attempted - correct_answers
        percentage = (correct_answers / total) * 100 if total else 0

        result_data = {
            'score': correct_answers,
            'correct': correct_answers,
            'wrong': wrong_answers,
            'attempted': attempted,
            'total': total,
            'percentage': round(percentage, 2)
        }
        request.session['result_data'] = result_data
        request.session.modified = True

    return render(request, 'app1/thank_you.html', {
        'student_name': student.name,
        'result_data': result_data,
        'score': result.score
    })


@staff_member_required
def upload_questions_view(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        subject = request.POST.get('subject')

        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file.')
            return redirect('upload_questions')

        try:
            # Decode and read the CSV file
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)

            # Delete existing questions for the selected subject
            Question.objects.filter(subject__iexact=subject).delete()

            # Create new questions from CSV
            for row in reader:
                Question.objects.create(
                    subject=subject,
                    text=row['text'],
                    option_a=row['option_a'],
                    option_b=row['option_b'],
                    option_c=row['option_c'],
                    option_d=row['option_d'],
                    correct_answer=row['correct_answer'].strip().upper()
                )

            messages.success(request, f'Questions for subject "{subject}" uploaded successfully!')
            return redirect('home')

        except Exception as e:
            messages.error(request, f"Error processing file: {e}")
            return redirect('upload_questions')

    return render(request, 'app1/upload_questions.html')




