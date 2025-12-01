from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Электронная почта')
    avatar = forms.ImageField(required=True, label='Аватар', help_text='Обязательное поле')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': 'Имя пользователя',
            'email': 'Электронная почта',
            'password1': 'Пароль',
            'password2': 'Подтверждение пароля',
        }

    def save(self, commit=True):
        # Сохраняем пользователя
        user = super().save(commit=commit)

        # Получаем загруженный аватар
        avatar = self.cleaned_data.get('avatar')

        # Создаем профиль с аватаром
        UserProfile.objects.create(user=user, avatar=avatar)

        return user


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(label='Электронная почта')

    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            'username': 'Имя пользователя',
            'email': 'Электронная почта',
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'birth_date']
        labels = {
            'avatar': 'Аватар',
            'bio': 'О себе',
            'birth_date': 'Дата рождения',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].required = True