# Generated by Django 5.0.7 on 2024-10-29 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book_app', '0025_user_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile_photo',
            field=models.ImageField(null=True, upload_to='user_profile_photo/'),
        ),
    ]