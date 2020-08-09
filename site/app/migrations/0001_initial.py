# Generated by Django 3.0.7 on 2020-08-09 04:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AppSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('file', models.FileField(upload_to='files')),
            ],
            options={
                'verbose_name': 'Settings',
                'verbose_name_plural': 'Settings',
                'abstract': False,
            },
        ),
    ]
