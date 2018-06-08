# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capture', '0026_auto_20150331_1415'),
    ]

    operations = [
        migrations.AddField(
            model_name='aqcconfig',
            name='stockLabel',
            field=models.ImageField(default=b'./genStockLabel.prn', help_text=b'Must be Zebra ZPL text file with replaceable tags.  Contact AdvanceQC for instructions on how to generate such a file.', verbose_name=b'Stock Label', upload_to=b''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='companyLogo',
            field=models.ImageField(default=b'./aqcWebLogo.png', upload_to=b'', verbose_name=b'Company Logo'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='defaultsprofile',
            name='idleTime',
            field=models.PositiveSmallIntegerField(default=45, help_text=b'Amount of time before an idle warning message is displayed [sec]', verbose_name=b'Idle Session [sec]'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='defaultsprofile',
            name='idleTimeOut',
            field=models.PositiveSmallIntegerField(default=15, help_text=b'Wait time after display of the idle warning message before the screen is cleared [sec]', verbose_name=b'Idle TimeOut'),
            preserve_default=True,
        ),
    ]
