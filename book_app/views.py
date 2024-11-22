from django.shortcuts import render, redirect, HttpResponseRedirect
from .models import Book, Author, User, Rating, Genre
from . import functions
from django.db.models import F, Sum, Min, Max, Count, Avg, Value, Q
from . import forms
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse




# Create your views here.


def main_page(request):
    '''Главная страница библиотеки'''
    books = Book.objects.all()
    agg = books.aggregate(Avg('rating'), Count('id'), Min('page_count'), Max('page_count'))  # Общая агрегация
    agg_shortest_book = books.aggregate(Min('page_count'))['page_count__min']  # Агрегация по минимальному количеству страниц
    agg_longest_book = books.aggregate(Max('page_count'))['page_count__max']  # Агрегация по максимальному количеству страниц
    shortest_book = Book.objects.get(page_count=agg_shortest_book)
    longest_book = Book.objects.get(page_count=agg_longest_book)
    context = {
        'books': books,
        'agg':agg,
        'shortest_book': shortest_book,
        'longest_book': longest_book,
    }
    return render(request, 'book_app/main_page.html', context=context)

class AuthorizationView(View):
    '''Представление для авторизации пользователя'''
    def get(self, request):
        form = forms.UserAuthorizationForm()
        error_counter = 0
        return render(request, 'book_app/authorization.html', {
            'form': form,
            'error_counter': error_counter,
        })

    @csrf_exempt
    def post(self, request):
        form = forms.UserAuthorizationForm(request, data=request.POST)
        error_counter = 0 # Счетчик неудачных попыток входа
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)  # Логиним пользователя
                # return JsonResponse({'success': True})
                messages.success(request, 'Вход выполнен')
                return HttpResponseRedirect('/knizhnaya_lavka/library')  # Перенаправляем на главную страницу
        messages.error(request, 'Неверный логин или пароль')
        error_counter += 1
        # return JsonResponse({'success': False, 'error': 'Данные не прошли валидацию на сервере'})
        return render(request, 'book_app/authorization.html', {
            'form': form,
            'error_counter': error_counter,
        })

class UserAccountView(View):
    '''Переход в личный кабинет'''
    def get(self, request):
        if not request.user.is_authenticated:  # Если юзер не авторизован, (либо @login_required вначале метода)
            return redirect('user-authorization')  # его выкинет на страницу авторизации
        form = forms.UploadProfilePhotoForm(instance=request.user)
        return render(request, 'book_app/user_account.html',{
            'user': request.user, # Передаем информацию о пользователе
            'form': form,
        })

    @csrf_exempt
    def post(self, request):
        if 'logout' in request.POST:
            logout(request) # Выход из сессии
            return redirect('user-authorization')
        old_profile_photo = request.user.profile_photo
        old_profile_photo_file = old_profile_photo
        form = forms.UploadProfilePhotoForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            if not User.is_default_profile_photo(request.user): # Если фото профиля не дефолтное
                if old_profile_photo_file: # Если существует данный файл
                    if request.FILES:
                        # Удаление старого фото из хранилища
                        functions.delete_old_profile_photo(old_profile_photo_file)
                    if 'delete_photo' in request.POST:
                        # Установка дефолтного фото профиля и удаление старого
                        request.user.profile_photo = 'user_profile_photo/default_profile_photo.jpg'
                        functions.delete_old_profile_photo(old_profile_photo_file)
            form.save()
            return redirect('user-account')
            # return JsonResponse({'success':True, 'message':'Фото профиля успешно загружено'})
        # return JsonResponse({'success':False, 'message':'Ошибка, попробуйте еще раз'})
        return render(request, 'book_app/user_account.html',{
            'user': request.user,
            'form': form,
        })

class UserRegistrationView(View):
    '''Регистрация нового пользователя'''
    def get(self, request):
        form = forms.UserRegistrationForm()
        return render(request, 'book_app/registration.html', {'form':form})

    @csrf_exempt
    def post(self, request):
        form = forms.UserRegistrationForm(request.POST)
        if form.is_valid():
            # Сохранение пользователя
            user = form.save(commit=False) # Делаем сохранение не сразу
            # Установка пароля, так как form.save() не устанавливает его
            user.password = make_password(form.cleaned_data['password'])  # Хеширование пароля
            user.save()
            # return JsonResponse({'success': True})
            return redirect('user-authorization')  # Перенаправление на страницу входа
        return JsonResponse({'success': False, 'error': 'Данные не прошли валидацию на сервере'})
def show_all_books(request):
    '''
    Передает содержимое модели Book в all_books.html
    Сортирует книги по выбранным параметрам
    Обрабатывает поисковый запрос
    '''
    query = request.GET.get('q', None) # Поисковый запрос
    sorting_parameter = request.GET.get('sorting_parameter', '-rating') # Сортировка по выбранному параметру
    genre_filter = request.GET.get('genre_parameter', None) # Фильтр по жанру
    genres = Genre.objects.order_by('genre')
    functions.ebooks_downloader()
    if query: # Обработка поискового запроса
        search_results = Book.objects.filter(
            Q(title__istartswith=query.capitalize()) | Q(title__icontains=query) |
            Q(author__full_name__istartswith=query.capitalize()) | Q(author__full_name__icontains=query.capitalize())
        ).distinct().order_by('title')
    else:
        if genre_filter:
            search_results = Book.objects.filter(genre=genre_filter)
        elif sorting_parameter == '-rating':
            search_results = Book.objects.annotate(average_rating=Avg('rating__rating')
                                                   ).order_by('-average_rating') # Сортировка по рейтингу
        elif sorting_parameter == '-bookclick':
            search_results = Book.objects.annotate(view_count=Count('bookclick__book')).order_by('-view_count')
        else:
            search_results = Book.objects.order_by(sorting_parameter)
    for book in search_results:
        avg_book_rating = functions.avg_rating(request, book)
        book.average_rating = avg_book_rating
        book.rating_count = functions.rating_count(request, book) # Возвращает кол-во оценок
        book.rating_end = functions.rating_count_end(request, book) # Возвращает окончание в зависимсоти от кол-ва оцен(ок/ки/ка)
    context={
        'search_results':search_results,
        'query':query,
        'genres':genres,
    }
    return render(request, 'book_app/all_books.html', context=context)

def show_one_book(request, book_slug: str):
    '''
    - Обрабатывает результат url-запроса и ищет запись в модели Book по переданному slug
    - Проверяет в модели Rating наличие записей об оценки данной книги авторизованным пользователем
    - Если пользователь не авторизован, предлагает войти для оценки
    - Вспомогательная функция rating_chek проверяет наличие записи и обновляет рейтинг
    '''
    try:
        book = Book.objects.get(slug=book_slug)
        avg_book_rating = functions.avg_rating(request, book)
        rating_exists = False # По умолчанию
        form = forms.UserFeedbackForm()
        ratings = Rating.objects.filter(book=book)
        # book_feedbacks = [rating.feedback for rating in ratings]
        if request.user.is_authenticated:
            user = User.objects.get(username=request.user.username)
            rating_exists = Rating.objects.filter(book=book, user=user).exists()
            functions.bookclicks(request, book, user) # Проверяет просмотры книги
            functions.rating_check(request, rating_exists, book, user)
        return render(request, 'book_app/one_book.html', {
                'book': book,
                'user_authenticate': request.user.is_authenticated,
                'rating_exists': rating_exists,
                'avg_book_rating': avg_book_rating,
                'form': form,
                'ratings': ratings
            })
    except Book.DoesNotExist:
        return render(request, 'book_app/404.html', {
                'page_404': functions.transliter(book_slug)
        })

def show_all_authors(request):
    '''Представление страницы с авторами книг из библиотеки'''
    authors = Author.objects.order_by('first_name')
    context = {
        'authors': authors,
    }

    return render(request, 'book_app/all_authors.html', context=context)

def about_author(request, author_slug: str):
    try:
        author = Author.objects.get(slug=author_slug) # Ищем автора по его slug, переданному из all_authors.html
        books = author.book_set.all() # Получаем все книги, связанные с этим автором
        context = {
            'author_slug': author_slug,
            'author': author,
            'books': books,
        }
        return render(request, 'book_app/about_author.html', context=context)
    except Author.DoesNotExist:
        context={
            'page_404': functions.transliter(author_slug)
        }
        return render(request, 'book_app/404.html', context=context)

class AccountRecoveryView(View):
    '''Восстановление доступа к аккаунту, указание эл. почты'''
    def get(self, request):
        form = forms.AccountRecoveryForm()
        return render(request, 'account_recovery/account_recovery.html', {'form': form})

    @csrf_exempt
    def post(self, request):
        form = forms.AccountRecoveryForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data.get('email')
            request.session['user_email'] = user_email  # Сохранение emailа в сессии для последующего поиска
            functions.send_email_message(request)
            # return JsonResponse({'success': True, 'message': 'Успешно'})
            return redirect('reset-password')
        # Форма не прошла валидацию:
        # return JsonResponse({'success': False, 'error': 'Данные не прошли валидацию на сервере'})
        return render(request, 'account_recovery/account_recovery.html', {'form': form})

class PasswordResetView(View):
    '''Сброс пароля, ввод проверочного кода'''
    def get(self, request):
        form = forms.PasswordResetForm(request=request)
        request_new_code = request.GET.get('request_new_code', None)
        if request_new_code:
            functions.send_email_message(request)
            return JsonResponse({'success': True, 'message': 'Отправлен новый код'})
        return render(request, 'account_recovery/reset_password.html', {'form': form})

    @csrf_exempt
    def post(self, request):
        form = forms.PasswordResetForm(request.POST, request=request)
        if form.is_valid():
            # return JsonResponse({'success': True, 'message': 'Успешно'})
            return redirect('set-new-password')
        # Форма не прошла валидацию:
        # return JsonResponse({'success': False, 'error': 'Данные не прошли валидацию на сервере'})
        return render(request, 'account_recovery/reset_password.html', {
            'form': form,
        })

class SetNewPasswordView(View):
    def get(self, request):
        form = forms.SetNewPassword()
        return render(request, 'account_recovery/set_new_password.html', {'form': form})

    def post(self, request):
        form = forms.SetNewPassword(request.POST)
        clean_form = forms.SetNewPassword()
        if form.is_valid():
            user_email = request.session['user_email']
            if user_email is None:
                messages.error(request, 'Ошибка на нашей стороне. Пожалуйста, запросите новый код.')
                return redirect('account_recovery:account_recovery')
            user = User.objects.get(email=user_email)
            user.password = make_password(form.cleaned_data['new_password'])
            user.save()
            return redirect('user-authorization')
        return render(request, 'account_recovery/set_new_password.html', {'form': clean_form})


