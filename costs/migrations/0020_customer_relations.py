# Generated by Django 3.1.1 on 2020-10-22 15:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employee_info', '0001_initial'),
        ('ad_import', '0006_manager_set_null'),
        ('costs', '0019_application_sector'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='employee_info.company', verbose_name='Firma'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='ad_directories',
            field=models.ManyToManyField(blank=True, to='ad_import.Directory'),
        ),
    ]
