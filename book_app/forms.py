from django import forms
from .models import User
from django.contrib.auth.forms import AuthenticationForm


class UserAuthorizationForm(AuthenticationForm):
    username = forms.CharField(label='Логин', required=True)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput, required=True)

class AccountRecoveryForm(forms.Form):
    email = forms.EmailField(label='Email')

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError(f'Пользователя с указанной почтой не существует.')

class PasswordResetForm(forms.Form):
    '''
    Переопределение инициализации для приема request
    из PasswordResetView для обработки reset_code
    в методе clean
    '''
    reset_code = forms.CharField(label='Код', required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None) # Извлекаем request и удаляем его из kwargs
        super().__init__(*args, **kwargs) # Инициализируемся без request во избежание конфликтов

    def clean(self):
         cleaned_data = super().clean()
         reset_code = cleaned_data['reset_code']
         if self.request is None:
             raise forms.ValidationError('Ошибка на нашей стороне. Пожалуйста, запросите новый код.')
             # return redirect('account-recovery')
             # return redirect('reset-password')
         elif reset_code != self.request.session['reset_code']:
             raise forms.ValidationError('Вы ввели неверный код. Пожалуйста, попробуйте снова.')

class SetNewPassword(forms.Form):
    new_password = forms.CharField(label='Новый пароль', widget=forms.PasswordInput)
    repeat_password = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        repeat_password = cleaned_data.get("repeat_password")
        if new_password != repeat_password:
            raise forms.ValidationError("Пароли не совпадают.")
        elif len(new_password) < 8:
            raise forms.ValidationError("Пароль должен содержать не менее 8 символов.")
        elif len(new_password) > 25:
            raise forms.ValidationError("Введите пароль не длиннее 25 символов.")
        return cleaned_data

class UserRegistrationForm(forms.ModelForm):
    repeat_password = forms.CharField(label="Повторите пароль", widget=forms.PasswordInput, required=True)
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'repeat_password')  # Выбираем поля
        widgets = {
            'email': forms.EmailInput(),
            'password': forms.PasswordInput(),
        } # Редактируем существующие или добавляем поля, которых нет в БД
        error_messages = {
            'username': {
                'unique': 'Этот логин уже занят.'
            },
            'email': {
                'unique': 'Пользователь с такой электронной почтой уже существует.'
            },
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        repeat_password = cleaned_data.get("repeat_password")
        if password != repeat_password:
            raise forms.ValidationError("Пароли не совпадают.")
        elif len(password) < 8:
            raise forms.ValidationError("Пароль должен содержать не менее 8 символов.")
        elif len(password) > 25:
            raise forms.ValidationError("Введите пароль не длиннее 25 символов.")
        return cleaned_data



# class UserAuthorizationForm(forms.Form):
#     username = forms.CharField(label="Логин", max_length=150, required=True)
#     password = forms.CharField(label="Пароль", widget=forms.PasswordInput, required=True)
#
#     def __init__(self, *args, **kwargs):
#         request = kwargs.pop('request', None)
#         super().__init__(*args, **kwargs)
#
#         self.request = request
#
#     def clean(self):
#         cleaned_data = super().clean()
#         username = cleaned_data.get("username")
#         password = cleaned_data.get("password")
#         # Добавьте проверку username и password здесь
#         # try:
#         #     user = User.objects.get(username=username)
#         # except User.DoesNotExists:
#         #     raise forms.ValidationError("Пользователя с таким логином не существует")
#         # if user is not None:
#         #     if password != user.password:
#         #         raise forms.ValidationError("Неверный пароль")
#
#         return cleaned_data