# Generated by Django 5.0.7 on 2024-10-04 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book_app', '0010_book_genre'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='top_100',
        ),
        migrations.AddField(
            model_name='book',
            name='bestseller',
            field=models.BooleanField(null=True, verbose_name='Бестселлер'),
        ),
    ]
