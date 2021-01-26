# Generated by Django 3.1.1 on 2021-01-25 14:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('costs', '0027_workstation_cost_center_function'),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstName', models.CharField(max_length=200, verbose_name='fornavn')),
                ('lastName', models.CharField(max_length=200, verbose_name='etternavn')),
                ('ssn', models.CharField(max_length=11, verbose_name='fødselsnummer')),
                ('guid', models.CharField(max_length=36, verbose_name='GUID')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='costs.customer')),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='student',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='costs.student', verbose_name='elev'),
        ),
    ]