# Generated by Django 2.0.3 on 2018-04-05 06:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('picManager', '0003_auto_20180403_2208'),
    ]

    operations = [
        migrations.AddField(
            model_name='picentry',
            name='owner',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
    ]
