# Generated by Django 4.2 on 2024-12-19 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('e_app', '0003_enrollment'),
    ]

    operations = [
        migrations.AddField(
            model_name='progress',
            name='chapter',
            field=models.CharField(default='Unknown', max_length=100),
        ),
    ]
