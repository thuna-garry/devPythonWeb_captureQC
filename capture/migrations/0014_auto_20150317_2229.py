# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import capture.models


class Migration(migrations.Migration):

    dependencies = [
        ('capture', '0013_aqcconfig_useragreement'),
    ]

    operations = [
        migrations.AddField(
            model_name='accessprofile',
            name='stockReverse',
            field=models.BooleanField(default=False, verbose_name=b'Stock Reversals'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='appAdminEmail',
            field=models.CharField(max_length=50, verbose_name=b'Application E-Mail'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='appName',
            field=models.CharField(max_length=30, unique=True, serialize=False, verbose_name=b'Application Name', primary_key=True),
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
            name='batchLaborGraceTime',
            field=models.PositiveSmallIntegerField(verbose_name=b'Batch Labour Grace [sec]'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='company',
            field=models.CharField(max_length=50, verbose_name=b'Company Name'),
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
            name='dbHost',
            field=models.CharField(help_text=b'Oracle database name or IP address', max_length=30, verbose_name=b'Database Host', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='dbMode',
            field=models.CharField(max_length=20, verbose_name=b'Database Mode', choices=[(b'Dedicated', b'Dedicated'), (b'Pooled', b'Pooled')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='dbName',
            field=models.CharField(max_length=1024, verbose_name=b'Database Name'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='dbPort',
            field=models.CharField(max_length=5, verbose_name=b'Database Port', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='dbUser',
            field=models.CharField(help_text=b'Oracle username or schema name', max_length=30, verbose_name=b'Database User'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='domain',
            field=models.CharField(max_length=50, verbose_name=b'Domain'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='emailBCC',
            field=models.EmailField(max_length=50, verbose_name=b'Email BCC'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='emailFrom',
            field=models.EmailField(max_length=50, verbose_name=b'Email From'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='smtpAcct',
            field=models.CharField(max_length=50, verbose_name=b'SMTP Account'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='smtpHost',
            field=models.CharField(max_length=50, verbose_name=b'SMTP Host'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='smtpPort',
            field=models.CharField(max_length=5, verbose_name=b'SMTP Port'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='trace',
            field=capture.models.PasswordCharField(help_text=b'AdvanceQC support use only.', max_length=20, verbose_name=b'AQC Support TR', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='userAgreement',
            field=models.CharField(max_length=2000, verbose_name=b'User Agreement'),
            preserve_default=True,
        ),
    ]
