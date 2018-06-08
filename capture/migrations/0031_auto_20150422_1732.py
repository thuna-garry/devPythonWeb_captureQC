# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import capture.models


class Migration(migrations.Migration):

    dependencies = [
        ('capture', '0030_auto_20150406_1446'),
    ]

    operations = [
        migrations.AddField(
            model_name='aqcconfig',
            name='redisSock',
            field=capture.models.PasswordCharField(default=b'/var/run/redis/redis.captureQC.sock', help_text=b'AdvanceQC support use only: canonical path to redis domain socket', max_length=80, verbose_name=b'Redis socket', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='trace',
            field=capture.models.PasswordCharField(help_text=b'AdvanceQC support use only: trace key.', max_length=20, verbose_name=b'Trace', blank=True),
            preserve_default=True,
        ),
    ]
