# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capture', '0027_auto_20150331_2205'),
    ]

    operations = [
        migrations.AddField(
            model_name='aqcconfig',
            name='whLocCheck',
            field=models.BooleanField(default=False, help_text=b'Where a warehouse is specified, ensure that the location is associated with the warehouse.', verbose_name=b'Restrict Location'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='stockLabel',
            field=models.ImageField(default=b'./genStockLabel.prn', help_text=b'Must be Zebra ZPL text file with replaceable tags.  Contact AdvanceQC for help generating this file.', verbose_name=b'Stock Label', upload_to=b''),
            preserve_default=True,
        ),
    ]
