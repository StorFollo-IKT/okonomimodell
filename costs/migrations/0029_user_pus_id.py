# Generated by Django 3.1.1 on 2021-01-25 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('costs', '0028_student'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='pus_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='PureService ID'),
        ),
    ]
