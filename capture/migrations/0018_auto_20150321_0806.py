# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capture', '0017_auto_20150320_1811'),
    ]

    operations = [
        migrations.CreateModel(
            name='DefaultsProfile',
            fields=[
                ('seqDefaultsProfile', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=75, verbose_name=b'Profile Name')),
                ('turnInCondition', models.CharField(unique=True, max_length=10, verbose_name=b'Turn-in condition code')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Defaults Profile',
                'verbose_name_plural': 'Defaults Profiles',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='user',
            name='seqDefaultsProfile',
            field=models.ForeignKey(related_name='+', db_column=b'seqDefaultsProfile', to='capture.DefaultsProfile', null=True),
            preserve_default=True,
        ),
    ]
