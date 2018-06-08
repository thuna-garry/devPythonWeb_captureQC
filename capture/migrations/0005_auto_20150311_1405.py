# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capture', '0004_auto_20150311_1334'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='aqcconfig',
            options={'ordering': ['appName'], 'verbose_name': 'Application Configuration', 'verbose_name_plural': 'Application Configuration'},
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='appAdminEmail',
            field=models.CharField(max_length=50, verbose_name=b'Application E-Mail'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='appURL',
            field=models.CharField(max_length=50, verbose_name=b'Application URL'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='companyURL',
            field=models.CharField(max_length=50, verbose_name=b'Public URL'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='emailBCC',
            field=models.EmailField(max_length=50, verbose_name=b'Email BCC'),
            preserve_default=True,
        ),
    ]
