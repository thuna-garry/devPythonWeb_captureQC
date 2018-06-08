# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capture', '0011_auto_20150311_2342'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aqcconfig',
            name='dbHost',
            field=models.CharField(default=b'oracle.yourCompany.com', help_text=b'Oracle database name or IP address', max_length=30, verbose_name=b'Database Host', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='dbPort',
            field=models.CharField(default=b'1521', max_length=5, verbose_name=b'Database Port', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='smtpPort',
            field=models.CharField(default=b'587', max_length=5, verbose_name=b'SMTP Port'),
            preserve_default=True,
        ),
    ]
