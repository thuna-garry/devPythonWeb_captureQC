# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capture', '0019_auto_20150321_2026'),
    ]

    operations = [
        migrations.AddField(
            model_name='aqcconfig',
            name='welcomeMOTD',
            field=models.CharField(help_text=b'"Message of the Day" displayed on front page', max_length=2000, null=True, verbose_name=b'Welcom MOTD', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='defaultUserId',
            field=models.CharField(help_text=b'The default user-id for this account', max_length=12, null=True, verbose_name=b'Default UserId', blank=True),
            preserve_default=True,
        ),
    ]
