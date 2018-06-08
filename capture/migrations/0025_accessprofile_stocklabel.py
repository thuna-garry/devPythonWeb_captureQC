# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capture', '0024_auto_20150328_0001'),
    ]

    operations = [
        migrations.AddField(
            model_name='accessprofile',
            name='stockLabel',
            field=models.BooleanField(default=False, verbose_name=b'Stock Label'),
            preserve_default=True,
        ),
    ]
