# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capture', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccessProfile',
            fields=[
                ('seqAccessProfile', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=75, verbose_name=b'Profile Name')),
                ('timeClock', models.BooleanField(default=False, verbose_name=b'Time clock')),
                ('labour', models.BooleanField(default=False, verbose_name=b'Single Task Labor')),
                ('labourBatch', models.BooleanField(default=False, verbose_name=b'Batched Labor')),
                ('stockIssue', models.BooleanField(default=False, verbose_name=b'Stock Issue')),
                ('woStatus', models.BooleanField(default=False, verbose_name=b'Work Order Status')),
                ('stockSearch', models.BooleanField(default=False, verbose_name=b'Stock Search')),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
    ]
