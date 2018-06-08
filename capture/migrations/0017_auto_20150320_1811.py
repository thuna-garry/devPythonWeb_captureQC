# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capture', '0016_accessprofile_stockturnin'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='defaultPrinter',
            field=models.CharField(help_text=b'The name or network address of a Zebra label printer.', max_length=16, null=True, verbose_name=b'Default Label Printer'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='defaultWarehouse',
            field=models.CharField(help_text=b'The warehouse name to use when specifying locations.', max_length=15, null=True, verbose_name=b'Default Warehouse'),
            preserve_default=True,
        ),
    ]
