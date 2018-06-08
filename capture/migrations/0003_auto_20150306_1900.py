# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capture', '0002_accessprofile'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='accessprofile',
            options={'ordering': ['name'], 'verbose_name': 'Access Profile', 'verbose_name_plural': 'Access Profiles'},
        ),
        migrations.AddField(
            model_name='user',
            name='seqAccessProfile',
            field=models.ForeignKey(related_name='+', db_column=b'seqAccessProfile', default=1, to='capture.AccessProfile'),
            preserve_default=True,
        ),
    ]
