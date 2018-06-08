# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capture', '0028_auto_20150401_1340'),
    ]

    operations = [
        migrations.AlterField(
            model_name='defaultsprofile',
            name='turnInCondition',
            field=models.CharField(default=b'AR', max_length=10, verbose_name=b'Turn-in condition code'),
            preserve_default=True,
        ),
    ]
