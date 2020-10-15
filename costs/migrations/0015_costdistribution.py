# Generated by Django 3.1.1 on 2020-10-07 13:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employee_info', '0001_initial'),
        ('costs', '0014_ad_relations'),
    ]

    operations = [
        migrations.CreateModel(
            name='CostDistribution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percentage', models.IntegerField(verbose_name='prosent')),
                ('account', models.CharField(max_length=6, verbose_name='konto')),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='distributions', to='costs.application', verbose_name='applikasjon')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employee_info.company', verbose_name='firma')),
                ('cost_center', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='employee_info.costcenter', verbose_name='ansvar')),
                ('function', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='employee_info.function', verbose_name='funksjon')),
            ],
            options={
                'unique_together': {('application', 'company', 'account', 'cost_center', 'function')},
            },
        ),
    ]
