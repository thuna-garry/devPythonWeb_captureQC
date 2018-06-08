# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capture', '0003_auto_20150306_1900'),
    ]

    operations = [
        migrations.CreateModel(
            name='AqcConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('appName', models.CharField(unique=True, max_length=30, verbose_name=b'Application Name')),
                ('company', models.CharField(max_length=50, verbose_name=b'Company Name')),
                ('domain', models.CharField(max_length=50, verbose_name=b'Domain')),
                ('companyURL', models.CharField(max_length=50, verbose_name=b'Domain')),
                ('companyLogo', models.ImageField(upload_to=b'', verbose_name=b'Company Logo')),
                ('appURL', models.CharField(max_length=50, verbose_name=b'Domain')),
                ('appAdminEmail', models.CharField(max_length=50, verbose_name=b'Domain')),
                ('smtpHost', models.CharField(max_length=50, verbose_name=b'SMTP Host')),
                ('smtpPort', models.PositiveSmallIntegerField(verbose_name=b'SMTP Port')),
                ('smtpAcct', models.CharField(max_length=50, verbose_name=b'SMTP Account')),
                ('smtpPass', models.CharField(max_length=50, verbose_name=b'SMTP Password')),
                ('emailFrom', models.EmailField(max_length=50, verbose_name=b'Email From')),
                ('emailBCC', models.EmailField(max_length=50, verbose_name=b'Email From')),
            ],
            options={
                'ordering': ['appName'],
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='user',
            name='seqAccessProfile',
            field=models.ForeignKey(related_name='+', db_column=b'seqAccessProfile', to='capture.AccessProfile'),
            preserve_default=True,
        ),
    ]
