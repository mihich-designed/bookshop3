from django.db import models
from django.urls import reverse
from pytils.translit import slugify
from django.contrib.auth.models import AbstractUser
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import boto3
import uuid
from PIL import Image
import tempfile
import zipfile
import tempfile

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
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True, default = 'Автор')
    genre = models.ManyToManyField(Genre)
    isbn = models.CharField(null=True, verbose_name="ISBN", default='Не указан', max_length=17)

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
            self.bookpicture = BookPicture.objects.create(
                book=self, picture=f'book_covers/default_book_cover.jpg'
            )  # Создаем и связываем
        return self.bookpicture.get_picture_path()

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'page_count': self.page_count,
            'year': self.year,
            'bestseller': self.bestseller,
            'slug': self.slug,
            'description': self.description,
            'author': self.author,
            'genre': self.genre,
            'isbn': self.isbn,
        }


class User(AbstractUser):
    REQUIRED_FIELDS = ['eDjangomail', 'password']

    username = models.CharField(max_length=50, verbose_name='Логин', unique=True)
    email = models.EmailField(max_length=50, verbose_name='Электронная почта', unique=True)
    password = models.CharField(max_length=100, verbose_name='Пароль')
    phone_number = models.IntegerField(blank=True, null=True, verbose_name='Телефон', unique=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    profile_photo = models.ImageField(
        upload_to='user_profile_photo/',
        default='user_profile_photo/default_profile_photo.jpg', null=False,
    )

    def save(self, *args, **kwargs):
        if self.profile_photo:
            if self.profile_photo.name != 'user_profile_photo/default_profile_photo.jpg':
                self.profile_photo = self.preprocess_image(self.profile_photo)
        super().save(*args, **kwargs)

    def preprocess_image(self, image_field):
        # Переименовывание файла
        ext = os.path.splitext(image_field.name)[1].lower()
        filename = f'{uuid.uuid4().hex}{ext}'
        s3_key = f'user_profile_photo/{filename}'

        # Сжатие
        image = Image.open(image_field)
        image = self.optimize_image(image)

        # Сохранение во временный файл
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as temp_file:
            image.save(temp_file.name)
            temp_file_path = temp_file.name

        # Загрузка во временного файла в S3
        self.upload_to_s3(temp_file_path, s3_key)

        # Удаление временного файла
        os.remove(temp_file_path)

        return s3_key # Возвращаем путь для модели Django (это будет URL, а не локальный путь)

    def optimize_image(self, image):
        image = image.convert('RGB')  # Преобразуем в RGB
        image.thumbnail((200, 200))  # Размер в px
        return image

    def upload_to_s3(self, file_path, s3_key):
        s3 = boto3.client('s3',
                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                      endpoint_url=settings.AWS_S3_ENDPOINT_URL)
        try:
            with open(file_path, 'rb') as f:
                s3.upload_fileobj(f, settings.MEDIA_BUCKET_NAME, s3_key)
        except Exception as e:
            print(f'Ошибка загрузки файла: {e}')

    def __str__(self):
        return f'{self.username}'

    def get_user_profile_photo(self):
        return self.profile_photo.url



class Rating(models.Model):
    '''Хранит отзывы пользователя и рейтинги книги'''
    RATING = [
        (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'),
        (6, '6'), (7, '7'), (8, '8'), (9, '9'), (10, '10'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rating = models.IntegerField(null=True, blank=True, choices=RATING, verbose_name="Рейтинг",)
    feedback = models.CharField(max_length=1000, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Рейтинг {self.book}'

    def to_json(self):
        return {
            'id': self.id,
            'user': self.user,
            'book': self.book,
            'rating': self.rating,
            'feedback': self.feedback,
            'created_at': self.created_at
        }


class BookClick(models.Model):
    '''Просмотры книги'''
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    view_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.book} - {self.user}"

def get_book_cover_upload_path(instance, filename):
    '''Функция создания пути для обложки в upload_to'''
    ext = os.path.splitext(filename)[1].lower()
    filename = f'{instance.book.slug}{ext}'
    return f'book_covers/{filename}'

class BookPicture(models.Model):
    '''Обложка книги'''
    book = models.OneToOneField(Book, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to=get_book_cover_upload_path)

    def __str__(self):
        return f'Обложка для {self.book}'

    def get_picture_path(self):
        return os.path.join(settings.MEDIA_URL, self.picture.name)

def get_upload_path(instance, filename):
  '''Функция создания пути для ebook в upload_to'''
  ext = os.path.splitext(filename)[1].lower()  # Извлекаем расширение с .
  filename = f'{instance.book.slug}-{instance.file_type}{ext}'  # Изменяем имя
  if ext == '.zip':
      archive = zipfile.ZipFile(instance.ebook, 'r')
      with tempfile.TemporaryDirectory() as temp_dir: # Создание временной директории
          archive.extractall(temp_dir) # Распаковка архива во временную директорию
          file = os.listdir(temp_dir)[0] #
          os.rename(file, filename)
  return f'ebooks/{instance.book.slug}-{instance.book.id}/{filename}'

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
    ebook = models.FileField(upload_to=get_upload_path)
    file_size = models.IntegerField(null=True, blank=True) # Размер файла в килобайтах
    file_type = models.CharField(null=True, choices=BOOK_FORMATS, max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.book} в формате {self.file_type}'

    def get_absolute_url(self):
        return self.ebook.url
