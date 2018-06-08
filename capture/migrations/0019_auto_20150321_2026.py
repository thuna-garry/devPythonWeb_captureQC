# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capture', '0018_auto_20150321_0806'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='defaultUserId',
            field=models.CharField(help_text=b'The default quantum user-id for this account', max_length=12, null=True, verbose_name=b'Default UserId', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='defaultPrinter',
            field=models.CharField(help_text=b'The name or network address of a Zebra label printer.', max_length=16, null=True, verbose_name=b'Default Label Printer', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='defaultWarehouse',
            field=models.CharField(help_text=b'The warehouse name to use when specifying locations.', max_length=15, null=True, verbose_name=b'Default Warehouse', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='seqDefaultsProfile',
            field=models.ForeignKey(related_name='+', db_column=b'seqDefaultsProfile', blank=True, to='capture.DefaultsProfile', null=True),
            preserve_default=True,
        ),
    ]
