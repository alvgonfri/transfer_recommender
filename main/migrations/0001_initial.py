# Generated by Django 5.0 on 2023-12-27 17:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('market_value', models.FloatField()),
                ('average_age', models.FloatField()),
                ('foreigner_percentage', models.FloatField()),
                ('goalkeepers', models.IntegerField()),
                ('defenders', models.IntegerField()),
                ('midfielders', models.IntegerField()),
                ('forwards', models.IntegerField()),
                ('logoURL', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('age', models.IntegerField()),
                ('nationality', models.CharField(max_length=100)),
                ('position', models.CharField(max_length=100)),
                ('market_value', models.FloatField()),
                ('photoURL', models.CharField(max_length=200)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.team')),
            ],
        ),
    ]
