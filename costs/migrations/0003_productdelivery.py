# Generated by Django 2.2.12 on 2020-06-19 15:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('costs', '0002_auto_20200605_2151'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductDelivery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(verbose_name='Antall')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='deliveries', to='costs.Customer', verbose_name='Kunde')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='deliveries', to='costs.Product', verbose_name='Tjeneste')),
                ('sector', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='deliveries', to='costs.Sector', verbose_name='Sektor')),
            ],
            options={
                'verbose_name': 'tjenesteleveranse',
                'verbose_name_plural': 'tjenesteleveranser',
                'unique_together': {('customer', 'product')},
            },
        ),
    ]
