from django.contrib import admin, messages
from .models import Book, Author, User, Rating, BookClick, BookPicture, Genre, EBookFile
from django.db.models import QuerySet, Q




class PageCountFilter(admin.SimpleListFilter):
    '''Фильтр по размеру книги'''
    title = 'Размер книги'
    parameter_name = 'page_count'

    def lookups(self, request, model_admin):
        return [
            ('<200', 'Маленькие (поясни за маленкость)'), # self.value в queryset
            ('200-500', 'Средние'),
            ('>=500', 'Большие'),
        ]
    def queryset(self, request, queryset):
        if self.value() == '<200':
            return queryset.filter(page_count__lt=200)
        elif self.value() == '200-500':
            return queryset.filter(Q(page_count__gte=200), Q(page_count__lt=500))
        elif self.value() == '>=500':
            return queryset.filter(page_count__gte=500)

class BookAdmin(admin.ModelAdmin):


    list_display = ['title', 'author', 'year', 'format',] # Настройка отображения колонок модели в админке
    list_editable = ['year', 'format'] # Выбор данных для редакции
    ordering= ['-rating'] # Сортировка
    list_per_page = 8 # Кол-во записей на странице
    actions = ['set_fb2', 'set_epub',] # Регистрация действия
    search_fields = ['title__iregex'] # Поиск по названию книги, регистр кириллицы учитывается, поэтому применяем __iregex
    list_filter = ['format', 'bestseller', PageCountFilter] # Ну это фильтры епта


    # Вычисляемое поле для админки, показывает суммарный рейтинг книги:
    # @admin.display(ordering='rating', description='Суммарный рейтинг')
    # def total_rating(self, book: Book):
    #     return round(book.rating * book.rating_count, 1)

    # Действие об изменение формата выбранных книг
    @admin.action(description='Установить формат FB2')
    def set_fb2(self, request, queryset: QuerySet):
        queryset.update(format=Book.F)

    # Действие об изменение формата выбранных книг
    @admin.action(description='Установить формат EPUB')
    def set_epub(self, request, queryset: QuerySet):
        updates_count = queryset.update(format=Book.E)
        self.message_user(
            request,
            f'Было обновлено {updates_count} записей',
            level=messages.INFO # Меняет цвет сообщения
        )
class BookPictureAdmin(admin.ModelAdmin):
    '''Исключает отображение записей из моделей, связанных с Book'''
    raw_id_fields = ('book',)

class EBookFileAdmin(admin.ModelAdmin):
    '''Исключает отображение записей из моделей, связанных с Book'''
    raw_id_fields = ('book',)

admin.site.register(Author)
admin.site.register(Book, BookAdmin)
admin.site.register(User)
admin.site.register(Rating)
admin.site.register(BookClick)
admin.site.register(BookPicture, BookPictureAdmin)
admin.site.register(Genre)
admin.site.register(EBookFile, EBookFileAdmin)

