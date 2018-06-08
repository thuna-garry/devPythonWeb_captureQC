# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capture', '0023_auto_20150327_2351'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aqcconfig',
            name='idleTime',
            field=models.PositiveSmallIntegerField(default=45, help_text=b'Amount of time before an idle warning message is displayed [sec]', verbose_name=b'Inactive'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='idleTimeOut',
            field=models.PositiveSmallIntegerField(default=15, help_text=b'Wait time after display of the idle warning message before the screen is cleared [sec]', verbose_name=b'TimeOut'),
            preserve_default=True,
        ),
    ]
