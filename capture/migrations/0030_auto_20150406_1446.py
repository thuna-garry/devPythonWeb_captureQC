# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capture', '0029_auto_20150401_2106'),
    ]

    operations = [
        migrations.AddField(
            model_name='accessprofile',
            name='stockDemand',
            field=models.BooleanField(default=False, verbose_name=b'Stock Demand'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='dbMode',
            field=models.CharField(default=b'Dedicated', max_length=20, verbose_name=b'Database Mode', choices=[(b'Dedicated', b'Dedicated'), (b'Pooled', b'Pooled')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='stockLabel',
            field=models.FileField(default=b'./genStockLabel.prn', help_text=b'Must be a Zebra ZPL text file with replaceable tags.  Contact AdvanceQC for help generating this file.', verbose_name=b'Stock Label', upload_to=b''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='aqcconfig',
            name='welcomeMOTD',
            field=models.CharField(default=b'<p>The use of this site is restricted to staff of AdvanceQC.</p>\n                                                                                                                                         <p>Use by any other parties is strictly prohibited.</p>', help_text=b'"Message of the Day" displayed on front page', max_length=2000, verbose_name=b'Welcome MOTD'),
            preserve_default=True,
        ),
    ]
