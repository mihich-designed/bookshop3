from transliterate import translit
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import User, Rating, BookClick
from .forms import UserFeedbackForm
from django.db.models import F, Sum, Min, Max, Count, Avg, Value
from django.db.models.functions import Round
from django.utils.crypto import get_random_string
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
import webbrowser

def transliter(slug: str):
    '''Транслит переданного url-запроса в кириллицу для обработки ошибки 404'''
    transliteration = translit(slug, 'ru').capitalize().replace('-', ' ')
    return transliteration

def rating_check(request, rating_exists, book, user):
    '''Проверка наличия оценки книги пользователем за одну сессию'''
    if request.method == 'POST':  # Проверяем метод запроса
        form = UserFeedback(request.POST)
        if form.is_valid():
            user_rating = form.cleaned_data.get('rating', None)  # Проверяем существование ключа 'rating'
            user_feedback = form.cleaned_data.get('feedback', None)
            if user_rating:
                if not rating_exists:  # Проверяем существование оценки данной книги данным пользователем
                    rating = Rating(book=book, user=user, rating=user_rating, feedback=user_feedback)
                    rating.save()

def avg_rating(request, book):
    try:
        book_rating = Rating.objects.filter(book=book)
        avg_book_rating = book_rating.aggregate(average_rating=Round(Avg('rating'), 1))['average_rating']
    except Rating.DoesNotExist:
        avg_book_rating = 'нет оценок'
    return avg_book_rating

def rating_count(request, book):
    try:
        book_rating = Rating.objects.filter(book=book)
        rating_count = book_rating.aggregate(Count('rating'))
    except Rating.DoesNotExist:
        rating_count = 0
    return rating_count

def bookclicks(request, book, user):
    # Проверяем, существует ли запись для этой книги и пользователя
    book_view, created = BookClick.objects.get_or_create(book=book, user=user)
    # Если запись создана (это первый просмотр для этого пользователя)
    if created:
        # Увеличиваем счетчик просмотров на 1
        book_view.view_count = F('view_count') + 1
        book_view.save()

def send_email_message(request):
    '''
    Отправляет на почту код восстановления
    Возвращает код восстановления
    '''
    reset_code = get_random_string(length=6)
    request.session['reset_code'] = reset_code # Сохранение кода в сессии для последующей проверки
    html_message = render_to_string('email_messages/reset_code_email_message.html', {
        'reset_code': reset_code
    })
    email_message = EmailMessage(
        subject='Восстановление пароля',
        body=html_message,
        from_email='awesome.knizhnaya@yandex.ru',
        to=[request.session['user_email']],
    )
    email_message.content_subtype = 'html'
    email_message.body = html_message
    email_message.send(fail_silently=False)
    return reset_code

def users_data_verification(login, email, password, repeat_password):
    try:
        User.objects.get(login=login)
        existing_login = True # Флаг существующий логин
        return existing_login
    except User.DoesNotExist: # Такого логина еще не существует, идем дальше
        try:
            User.objects.get(email=email)
            existing_email = True  # Флаг существующий емаил
            return existing_email
        except User.DoesNotExist:
            if password != repeat_password:
                password_mismatch = True
                return password_mismatch
    success = True
    return success

def rating_count_end(request, book):
    book_rating_count = rating_count(request, book) # Словарь {'rating__count': 3}
    # Преобразуем rating_count в строку, чтобы взять последний символ и обратно в число
    last_digit = int(str(book_rating_count['rating__count'])[-1])
    if last_digit == 0 or (5<=last_digit<=9) or (10<=book_rating_count['rating__count']<=20):
        end = 'ок'
    elif 2<=last_digit<=4:
        end = 'ки'
    elif last_digit == 1:
        end = 'ка'
    return end

def ebooks_downloared():
    webbrowser.open('https://royallib.com/book/fitsdgerald_frensis/velikiy_getsbi.html')

