# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capture', '0025_accessprofile_stocklabel'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='aqcconfig',
            name='batchLaborGraceTime',
        ),
        migrations.RemoveField(
            model_name='aqcconfig',
            name='idleTime',
        ),
        migrations.RemoveField(
            model_name='aqcconfig',
            name='idleTimeOut',
        ),
        migrations.AddField(
            model_name='defaultsprofile',
            name='batchLaborGraceTime',
            field=models.PositiveSmallIntegerField(default=300, verbose_name=b'Batch Labour Grace [sec]'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='defaultsprofile',
            name='idleTime',
            field=models.PositiveSmallIntegerField(default=45, help_text=b'Amount of time before an idle warning message is displayed [sec]', verbose_name=b'Inactive'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='defaultsprofile',
            name='idleTimeOut',
            field=models.PositiveSmallIntegerField(default=15, help_text=b'Wait time after display of the idle warning message before the screen is cleared [sec]', verbose_name=b'TimeOut'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='welcomeMOTD',
            field=models.CharField(help_text=b'"Message of the Day" displayed on front page', max_length=2000, null=True, verbose_name=b'Welcome MOTD', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='defaultsprofile',
            name='turnInCondition',
            field=models.CharField(default=b'AR', unique=True, max_length=10, verbose_name=b'Turn-in condition code'),
            preserve_default=True,
        ),
    ]
