# Generated by Django 5.0.7 on 2024-10-06 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book_app', '0014_alter_bookpicture_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookpicture',
            name='picture',
            field=models.ImageField(default='media/book_covers/default_book_cover.jpg', null=True, upload_to='book_covers/'),
        ),
        migrations.AlterField(
            model_name='genre',
            name='genre',
            field=models.CharField(choices=[('fantastic', 'Фантастика'), ('fantasy', 'Фэнтези'), ('horrors', 'Хорроры'), ('novels', 'Романы'), ('psychology', 'Психология'), ('history', 'История'), ('detectives', 'Детективы'), ('russian_classics', 'Отечественная класика'), ('foreign_classics', 'Зарубежная класика'), ('biography', 'Биография'), ('self_development', 'Саморазвитие'), ('prose', 'Проза'), ('business', 'Бизнес'), ('drama', 'Драма'), ('dystopia', 'Антиутопия'), ('adventures', 'Приключения')], default='', max_length=50),
        ),
    ]
