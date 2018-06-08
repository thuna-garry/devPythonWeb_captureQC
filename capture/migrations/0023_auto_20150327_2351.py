# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capture', '0022_auto_20150327_1607'),
    ]

    operations = [
        migrations.AddField(
            model_name='aqcconfig',
            name='idleTime',
            field=models.PositiveSmallIntegerField(default=45, verbose_name=b'Amount of time before an idle warning message is displayed [sec]'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aqcconfig',
            name='idleTimeOut',
            field=models.PositiveSmallIntegerField(default=15, verbose_name=b'Wait time after display of the idle warning message before the screen is cleared [sec]'),
            preserve_default=True,
        ),
    ]
