# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('seqOrg', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=75, verbose_name=b'Organization Name')),
                ('enabled', models.BooleanField(default=False)),
                ('validFrom', models.DateField(null=True, verbose_name=b'Valid From')),
                ('validUntil', models.DateField(null=True, verbose_name=b'Valid To')),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('seqUser', models.AutoField(serialize=False, primary_key=True)),
                ('firstName', models.CharField(max_length=35, verbose_name=b'First Name')),
                ('lastName', models.CharField(max_length=35, verbose_name=b'Last Name')),
                ('userId', models.CharField(help_text=b'Must be unique for all your portal users', max_length=20, verbose_name=b'User ID')),
                ('password', models.CharField(max_length=32, verbose_name=b'Password')),
                ('tmpPassword', models.CharField(max_length=46, null=True, verbose_name=b'tmpPassword')),
                ('email', models.EmailField(max_length=50, verbose_name=b'E-Mail')),
                ('phone', models.CharField(max_length=20, verbose_name=b'Phone Number')),
                ('enabled', models.BooleanField(default=True, help_text=b'Is this user account permitted to login to this portal.', verbose_name=b'Enabled')),
                ('validFrom', models.DateField(help_text=b'The date after which the user account is permitted to login to this portal.', null=True, verbose_name=b'Valid From')),
                ('validUntil', models.DateField(help_text=b'The date after which the user account will not be permitted to login to this portal.', null=True, verbose_name=b'Valid Until')),
                ('admin', models.BooleanField(default=False, help_text=b'Is this user permitted to create and edit the account information of other users.', verbose_name=b'Is Admin')),
                ('public', models.BooleanField(default=False, help_text=b'Is this userId used to login to a shared or public workstation.', verbose_name=b'Is Public')),
                ('lastUpdated', models.DateTimeField(auto_now=True)),
                ('lastLoggedIn', models.DateTimeField(default=None, null=True, verbose_name=b'Last Login (UTC)')),
                ('agreedToTerms', models.BooleanField(default=False, verbose_name=b'Agreed To Terms')),
                ('seqOrg', models.ForeignKey(related_name='+', db_column=b'seqOrg', to='capture.Organization')),
            ],
            options={
                'ordering': ['lastName', 'firstName'],
                'verbose_name': 'User Account',
                'verbose_name_plural': 'User Accounts',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='user',
            unique_together=set([('seqOrg', 'userId')]),
        ),
    ]
