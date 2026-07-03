from django.contrib import admin
from . models import Student, Question, Result

# Register your models here.
class StudentAdmin(admin.ModelAdmin):
    model = Student 
    fields = ['enrollment_number','dob','name']

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['subject', 'text', 'correct_answer']
    fields = ['subject', 'text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']


class ResultAdmin(admin.ModelAdmin):  # Fixed class name and typo
    model = Result
    list_display = ['student', 'score', 'submitted_at']  # Fixed 'list_diplay' to 'list_display'
    readonly_fields = ['submitted_at']
    search_fields = ['student__name', 'student__enrollment_number']
    list_filter = ['submitted_at', 'score']


admin.site.register(Student, StudentAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Result, ResultAdmin)