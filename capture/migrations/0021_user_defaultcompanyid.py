# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capture', '0020_auto_20150327_1354'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='defaultCompanyID',
            field=models.CharField(default=b'1', help_text=b"The Company_ID to use for this User's transactions (See Quantum's Global Settings)", max_length=4, verbose_name=b'Default CompanyId'),
            preserve_default=True,
        ),
    ]
