# forms.py
from django import forms

# class LoginForm(forms.Form):
#     enrollment_number = forms.CharField(max_length=15)
#     dob = forms.DateField(widget=forms.SelectDateWidget(years=range(2000, 2023)))

class LoginForm(forms.Form):
    enrollment_number = forms.CharField(label="Enrollment Number", max_length=15)
    dob = forms.DateField(label="Date of Birth", widget=forms.DateInput(attrs={'type': 'date'}))
