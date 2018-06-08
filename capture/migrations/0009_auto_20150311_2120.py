# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capture', '0008_auto_20150311_1900'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='aqcconfig',
            name='dbDesc',
        ),
        migrations.AddField(
            model_name='aqcconfig',
            name='dbHost',
            field=models.CharField(default=b'oracle.yourCompany.com', help_text=b'Oracle database name or IP address', max_length=30, verbose_name=b'Database Host'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aqcconfig',
            name='dbMode',
            field=models.CharField(default=b'Dedicated', max_length=20, verbose_name=b'Database Mode', choices=[(b'Dedicated', b'Dedicated'), (b'Pooled', b'Pooled')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aqcconfig',
            name='dbName',
            field=models.CharField(default=b'tnsName - if a simple string, and host/port unspecified, or\nsid     - if a simple string, and host/port specified, or\nhost.db.com:1521/serviceName.db.com  -if host/port unspecified', max_length=1024, verbose_name=b'Database Name'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aqcconfig',
            name='dbPass',
            field=models.CharField(default=b'password', help_text=b'Oracle password', max_length=30, verbose_name=b'Database Password'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aqcconfig',
            name='dbPort',
            field=models.PositiveSmallIntegerField(default=b'1521', verbose_name=b'Database Port'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aqcconfig',
            name='dbUser',
            field=models.CharField(default=b'qctl', help_text=b'Oracle username or schema name', max_length=30, verbose_name=b'Database User'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='appAdminEmail',
            field=models.CharField(default=b'CaptureQC@yourCompany.com', max_length=50, verbose_name=b'Application E-Mail'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='appName',
            field=models.CharField(primary_key=True, default=b'CaptureQC', serialize=False, max_length=30, unique=True, verbose_name=b'Application Name'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='appURL',
            field=models.CharField(default=b'CaptureQC.yourCompany.com', max_length=50, verbose_name=b'Application URL'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='company',
            field=models.CharField(default=b'Your Company', max_length=50, verbose_name=b'Company Name'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='companyURL',
            field=models.CharField(default=b'www.yourCompany.com', max_length=50, verbose_name=b'Public URL'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='domain',
            field=models.CharField(default=b'yourCompany.com', max_length=50, verbose_name=b'Domain'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='emailBCC',
            field=models.EmailField(default=b'CaptureQC@yourCompany.com', max_length=50, verbose_name=b'Email BCC'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='emailFrom',
            field=models.EmailField(default=b'CaptureQC@yourCompany.com', max_length=50, verbose_name=b'Email From'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='smtpAcct',
            field=models.CharField(default=b'test.user@gmail.com', max_length=50, verbose_name=b'SMTP Account'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='smtpHost',
            field=models.CharField(default=b'smtp.gmail.com', max_length=50, verbose_name=b'SMTP Host'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='smtpPort',
            field=models.PositiveSmallIntegerField(default=b'587', verbose_name=b'SMTP Port'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='trace',
            field=models.CharField(default=b'-', help_text=b'AdvanceQC support use only.', max_length=20, verbose_name=b'AQC Support TR', blank=True),
            preserve_default=True,
        ),
    ]
