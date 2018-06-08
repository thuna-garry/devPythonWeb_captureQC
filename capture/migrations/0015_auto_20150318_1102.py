# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capture', '0014_auto_20150317_2229'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accessprofile',
            name='stockReverse',
        ),
        migrations.AddField(
            model_name='accessprofile',
            name='stockUndo',
            field=models.BooleanField(default=False, verbose_name=b'Stock Undo-Activity'),
            preserve_default=True,
        ),
    ]
