from django import forms
from PitchAndSlope.core.models import Document
from django.core.exceptions import ValidationError
from PitchAndSlope.core.models import PortalUser

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('description', 'document', )
 
class CustomUserCreationForm(forms.Form):
    userId = forms.CharField(label='Username', min_length=8, max_length=150)
    firstName = forms.CharField(label='First Name', max_length=100)
    lastName = forms.CharField(label='Last Name', max_length=100)
    email = forms.EmailField(label='Email Id')
    password = forms.CharField(label='Enter password', widget=forms.PasswordInput)
    password1 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)
 
    def clean_username(self):
        userId = self.cleaned_data['userId'].lower()
        r = PortalUser.objects.filter(userId=userId)
        if r.count():
            raise  ValidationError("Username already exists")
        return userId
 
    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        r = PortalUser.objects.filter(email=email)
        if r.count():
            raise  ValidationError("Email already exists")
        return email
 
    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password1 = self.cleaned_data.get('password1')
 
        if password and password1 and password != password1:
            raise ValidationError("Password don't match")
 
        return password1
     
    def save(self, commit=True):
        user = PortalUser()
        user.userId=self.clean_username()
        user.firstName=self.cleaned_data['firstName']
        user.lastName=self.cleaned_data['lastName']
        user.email=self.clean_email()
        user.password=self.clean_password2()
        user.save()
        return user