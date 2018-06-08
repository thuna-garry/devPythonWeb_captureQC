# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capture', '0021_user_defaultcompanyid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='defaultCompanyID',
            new_name='defaultCompanyId',
        ),
    ]
