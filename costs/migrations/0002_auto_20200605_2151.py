# Generated by Django 2.2.12 on 2020-06-05 21:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('costs', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='external_cost',
            field=models.IntegerField(default=0, verbose_name='Konsulentkostnad'),
        ),
        migrations.AlterField(
            model_name='application',
            name='internal_hours',
            field=models.IntegerField(default=0, verbose_name='Applikasjonsdrift timer pr mnd'),
        ),
        migrations.AlterField(
            model_name='application',
            name='licence_cost',
            field=models.IntegerField(default=0, verbose_name='Lisenskostnad'),
        ),
    ]