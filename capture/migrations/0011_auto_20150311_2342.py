# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import capture.models


class Migration(migrations.Migration):

    dependencies = [
        ('capture', '0010_auto_20150311_2155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aqcconfig',
            name='dbHost',
            field=models.CharField(default=b'oracle.yourCompany.com', max_length=30, null=True, verbose_name=b'Database Host', help_text=b'Oracle database name or IP address'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='dbPass',
            field=capture.models.PasswordCharField(help_text=b'Leave blank to keep existing password.', max_length=30, verbose_name=b'Database Password', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='dbPort',
            field=models.PositiveSmallIntegerField(default=b'1521', null=True, verbose_name=b'Database Port'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='smtpPass',
            field=capture.models.PasswordCharField(help_text=b'Leave blank to keep existing password', max_length=64, verbose_name=b'SMTP Password', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='trace',
            field=capture.models.PasswordCharField(default=b'-', help_text=b'AdvanceQC support use only.', max_length=20, verbose_name=b'AQC Support TR', blank=True),
            preserve_default=True,
        ),
    ]
