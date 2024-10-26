from django.db import models
from django.urls import reverse
from pytils.translit import slugify
from django.contrib.auth.models import AbstractUser
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os


# Create your models here.

class Author(models.Model):
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    full_name = models.CharField(max_length= 150, verbose_name='Полное имя')
    slug = models.SlugField(default='', blank=True)
    description = models.CharField(max_length=500, default='Описание будет добавлено позже', verbose_name="Описание")

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def get_url(self):
        return reverse('author-info', args=[self.slug])
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'
    def save(self, *args, **kwargs):
        self.slug = f'{slugify(self.first_name)}_{slugify(self.last_name)}'
        # self.full_name = self.get_full_name()
        super(Author, self).save(*args, **kwargs)
class Genre(models.Model):
    '''Жанры книги'''
    GENRES = [
        ('fantastic', 'Фантастика'),
        ('fantasy', 'Фэнтези'),
        ('horrors', 'Хорроры'),
        ('novels', 'Романы'),
        ('psychology', 'Психология'),
        ('history', 'История'),
        ('detectives', 'Детективы'),
        ('russian_classics', 'Отечественная класика'),
        ('foreign_classics', 'Зарубежная класика'),
        ('biography', 'Биография'),
        ('self_development', 'Саморазвитие'),
        ('prose', 'Проза'),
        ('business', 'Бизнес'),
        ('drama', 'Драма'),
        ('dystopia', 'Антиутопия'),
        ('adventures', 'Приключения'),
    ]
    genre = models.CharField(max_length=50, choices=GENRES, default='')

    def __str__(self):
        return f'{self.genre}'

class Book(models.Model):
    F = 'F'
    E = 'E'
    D = 'D'
    BOOK_FORMATS = [ (F, 'FB2'), (E, 'EPUB'), (D, 'DOC'),]

    title = models.CharField(max_length=70, verbose_name="Название")
    page_count = models.IntegerField(null=True, verbose_name="Страницы")
    year = models.IntegerField(null=True, verbose_name="Год публикации")
    bestseller = models.BooleanField(null=True, verbose_name="Бестселлер")
    slug = models.SlugField(default='', blank=True)
    description = models.CharField(max_length=500, default='Описание будет добавлено позже', verbose_name="Описание")
    format = models.CharField(max_length=1, choices=BOOK_FORMATS, default=F, verbose_name="Формат")
    author = models.ForeignKey(Author, on_delete=models.PROTECT, null=True, default = 'Автор')
    genre = models.ManyToManyField(Genre)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Book, self).save(*args, **kwargs)

    def get_url(self):
        return reverse('book-info', args=[self.slug])

    def __str__(self):
        return f'«{self.title}»'

    def get_cover(self):
        try:
            self.bookpicture
        except BookPicture.DoesNotExist:
            self.bookpicture = BookPicture.objects.create(book=self, picture='book_covers/default_book_cover.jpg')  # Создаем и связываем
        return self.bookpicture.picture.url

class User(AbstractUser):
    REQUIRED_FIELDS = ['eDjangomail', 'password']

    username = models.CharField(max_length=50, verbose_name='Логин', unique=True)
    email = models.EmailField(max_length=50, verbose_name='Электронная почта', unique=True)
    password = models.CharField(max_length=50, verbose_name='Пароль')
    phone_number = models.IntegerField(blank=True, null=True, verbose_name='Телефон', unique=True)

    def __str__(self):
        return f'Логин: {self.username}'


class Rating(models.Model):
    '''Рейтинг книги'''
    RATING = [
        (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'),
        (6, '6'), (7, '7'), (8, '8'), (9, '9'), (10, '10'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rating = models.IntegerField(null=True, blank=True, choices=RATING, verbose_name="Рейтинг",)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Рейтинг {self.book}'


class BookClick(models.Model):
    '''Просмотры книги'''
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    view_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.book} - {self.user}"

class BookPicture(models.Model):
    '''Обложка книги'''
    book = models.OneToOneField(Book, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='book_covers/')

    def __str__(self):
        return f'Обложка для {self.book}'

# Настройка хранилища для электронных книг
ebook_storage = FileSystemStorage(location='content/ebooks') # Указываем путь к папке

def get_upload_path(instance, filename):
  '''Функция для создания пути для файла в upload_to'''
  return f'{instance.book.slug}/{filename}'

class EBookFile(models.Model):
    '''Хранит электронные книги'''
    F = 'F'
    E = 'E'
    D = 'D'
    P = 'P'
    T = 'T'
    R = 'R'

    BOOK_FORMATS = [
        (F, 'FB2'), (E, 'EPUB'), (D, 'DOC'),
        (P, 'PDF'), (T, 'TXT'), (R, 'RTF'),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    ebook = models.FileField(upload_to=get_upload_path, storage=ebook_storage)
    file_size = models.IntegerField(null=True, blank=True) # Размер файла в килобайтах
    file_type = models.CharField(null=True, choices=BOOK_FORMATS, max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.book} в формате {self.file_type}'

    def get_absolute_url(self):
        # В self.ebook.name делим и берем последнее, тк возвращает ebooks/filename.filetype
        return f'content/ebooks/{self.book.slug}/{self.ebook.name.split('/')[-1]}'

