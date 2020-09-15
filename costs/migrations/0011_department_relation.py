# Generated by Django 3.1 on 2020-08-13 12:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('costs', '0010_user_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='departments', to='costs.customer'),
        ),
    ]