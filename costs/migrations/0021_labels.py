# Generated by Django 3.1.1 on 2020-10-28 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('costs', '0020_customer_relations'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='costdistribution',
            options={'verbose_name': 'kostnadsfordeling', 'verbose_name_plural': 'kostnadsfordelinger'},
        ),
        migrations.AlterField(
            model_name='application',
            name='external_cost',
            field=models.IntegerField(default=0, verbose_name='Konsulentkostnad per år'),
        ),
        migrations.AlterField(
            model_name='application',
            name='licence_cost',
            field=models.IntegerField(default=0, verbose_name='Lisenskostnad per år'),
        ),
    ]
