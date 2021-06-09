# Generated by Django 3.2.3 on 2021-06-07 23:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dynamica_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('start', models.TimeField()),
                ('end', models.TimeField()),
                ('year', models.IntegerField()),
                ('month', models.IntegerField()),
                ('day', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Music',
            fields=[
                ('name', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('number_of_parts', models.IntegerField()),
            ],
        ),
    ]
