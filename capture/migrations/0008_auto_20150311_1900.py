# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capture', '0007_aqcconfig_batchlaborgracetime'),
    ]

    operations = [
        migrations.AddField(
            model_name='aqcconfig',
            name='dbDesc',
            field=models.CharField(default=b'-', help_text=b'Must be valid JSON', max_length=500, verbose_name=b'Database Descriptor'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aqcconfig',
            name='trace',
            field=models.CharField(default=b'-', help_text=b'AdvanceQC support use only.', max_length=20, verbose_name=b'AQC Support - TR'),
            preserve_default=True,
        ),
    ]
