# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capture', '0005_auto_20150311_1405'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='aqcconfig',
            name='id',
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='appName',
            field=models.CharField(max_length=30, unique=True, serialize=False, verbose_name=b'Application Name', primary_key=True),
            preserve_default=True,
        ),
    ]
