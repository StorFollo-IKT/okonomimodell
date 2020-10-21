# Generated by Django 3.1.1 on 2020-10-21 09:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ad_import', '0006_manager_set_null'),
        ('costs', '0016_ad_relations'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='ip',
            field=models.GenericIPAddressField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='server',
            name='ad_object',
            field=models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='ad_import.server', verbose_name='AD'),
        ),
    ]