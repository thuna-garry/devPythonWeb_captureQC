# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capture', '0012_auto_20150312_0124'),
    ]

    operations = [
        migrations.AddField(
            model_name='aqcconfig',
            name='userAgreement',
            field=models.CharField(default=b' ', max_length=2000, verbose_name=b'User Agreement'),
            preserve_default=True,
        ),
    ]
