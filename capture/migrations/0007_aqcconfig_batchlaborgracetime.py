# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capture', '0006_auto_20150311_1441'),
    ]

    operations = [
        migrations.AddField(
            model_name='aqcconfig',
            name='batchLaborGraceTime',
            field=models.PositiveSmallIntegerField(default=300, verbose_name=b'Batch Labour Grace [sec]'),
            preserve_default=True,
        ),
    ]
