# Generated by Django 5.1 on 2024-08-30 10:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_userreg_reset_token_userreg_token_created_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='passwordresettoken',
            name='user',
        ),
        migrations.DeleteModel(
            name='Userlog',
        ),
        migrations.DeleteModel(
            name='PasswordResetToken',
        ),
        migrations.DeleteModel(
            name='Userreg',
        ),
    ]
