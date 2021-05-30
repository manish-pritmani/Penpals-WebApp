from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .utils import LANGUAGE_CHOICES
from .models import Profile


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'password']


class ProfileEditForm(forms.ModelForm):
    first = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    speaks = forms.MultipleChoiceField(choices=LANGUAGE_CHOICES,
                                       widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    is_learning = forms.MultipleChoiceField(label="Currently Learning", choices=LANGUAGE_CHOICES,
                                            widget=forms.SelectMultiple(attrs={'class': 'form-control'}))

    def from_values_to_labels(self, method):
        list_labels = [label for values, label in LANGUAGE_CHOICES if values in self[method].value()]
        # here the self[method].value() function will give the value of selected choices
        languages = ','.join(list_labels)
        return languages

    class Meta:
        model = Profile
        fields = ['first', 'last', 'speaks', 'is_learning', 'photo']


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label="Password", help_text="at least 8 characters",
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).count() > 0:
            raise forms.ValidationError('Email Already Exist.')
        return data
