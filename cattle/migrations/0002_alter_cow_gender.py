# Generated by Django 4.2.23 on 2025-07-08 05:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cattle', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cow',
            name='gender',
            field=models.CharField(choices=[('male', 'オス'), ('female', 'メス'), ('castrated', '去勢')], default='female', max_length=10),
        ),
    ]
