# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capture', '0009_auto_20150311_2120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aqcconfig',
            name='dbName',
            field=models.CharField(default=b'tnsName - if a simple string, and host/port unspecified, or\nsid     - if a simple string, and host/port specified, or\nhost.db.com:1521/serviceName.db.com  - if host/port unspecified, or\nfull oracle connection descriptor  - if host/port unspecified', max_length=1024, verbose_name=b'Database Name'),
            preserve_default=True,
        ),
    ]
