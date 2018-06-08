# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capture', '0015_auto_20150318_1102'),
    ]

    operations = [
        migrations.AddField(
            model_name='accessprofile',
            name='stockTurnIn',
            field=models.BooleanField(default=False, verbose_name=b'Stock Turn-In'),
            preserve_default=True,
        ),
    ]
