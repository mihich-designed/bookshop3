# Generated by Django 5.0.7 on 2024-10-05 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book_app', '0012_delete_bookgenrerelation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='slug',
            field=models.SlugField(default=''),
        ),
        migrations.AlterField(
            model_name='book',
            name='slug',
            field=models.SlugField(default=''),
        ),
    ]