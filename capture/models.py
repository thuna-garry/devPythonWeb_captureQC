"""
Copyright AdvanceQC LLC 2014,2015.  All rights reserved
"""

import os
import datetime
import hashlib

from django.db import models
from django.db import connection
from django.forms import ModelForm, PasswordInput, Textarea, ChoiceField

from aqclib import utils

class AbstractModel(models.Model):
    class Meta:
        abstract = True

    def __iter__(self):
        for fn in self._meta.get_all_field_names():
            yield (fn, getattr(self, fn))

    def asDict(self, dtFormat='%Y-%m-%d %H:%M:%S'):
        d = {}
        for field,val in self:
            if type(val) is datetime.date:
                val = val.strftime(dtFormat)
            elif type(val) is datetime.datetime:
                val = val.strftime(dtFormat)
            elif isinstance(val, models.Model):
                val = self.__getattribute__(field + "_id")
            d[field] = val
        return d


class PasswordCharField(models.CharField):
    def save_form_data(self, instance, data):
        if data != u'':
            #data = instance._hashed_pwd(data)
            setattr(instance, self.name, data)


class AqcConfig(AbstractModel):
    appName = models.CharField("Application Name", max_length=30, unique=True, primary_key=True)
    company = models.CharField("Company Name", max_length=50)
    domain  = models.CharField("Domain", max_length=50)
    companyURL = models.CharField("Public URL", max_length=50)
    companyLogo = models.ImageField("Company Logo", default="./aqcWebLogo.png")
    welcomeMOTD = models.CharField("Welcome MOTD", max_length=2000, help_text='"Message of the Day" displayed on front page', default="""<p>The use of this site is restricted to staff of AdvanceQC.</p>
                                                                                                                                         <p>Use by any other parties is strictly prohibited.</p>""")
    userAgreement = models.CharField("User Agreement", max_length=2000)
    appURL = models.CharField("Application URL", max_length=50)
    appAdminEmail = models.CharField("Application E-Mail", max_length=50)
    smtpHost = models.CharField("SMTP Host", max_length=50)
    smtpPort = models.CharField("SMTP Port", max_length=5)
    smtpAcct = models.CharField("SMTP Account", max_length=50)
    smtpPass = PasswordCharField("SMTP Password", max_length=64, help_text="Leave blank to keep existing password", blank=True)
    emailFrom = models.EmailField("Email From", max_length=50)
    emailBCC = models.EmailField("Email BCC", max_length=50)
    dbMode = models.CharField("Database Mode", max_length=20, choices=(("Dedicated", "Dedicated"),("Pooled", "Pooled")), default="Dedicated" )
    dbName = models.CharField("Database Name", max_length=1024)
    dbHost = models.CharField("Database Host", max_length=30, help_text="Oracle database name or IP address", blank=True)
    dbPort = models.CharField("Database Port", max_length=5, blank=True)
    dbUser = models.CharField("Database User", max_length=30, help_text="Oracle username or schema name")
    dbPass = PasswordCharField("Database Password", max_length=30, help_text="Leave blank to keep existing password.", blank=True)
    stockLabel = models.FileField("Stock Label", help_text="Must be a Zebra ZPL text file with replaceable tags.  Contact AdvanceQC for help generating this file.", default="./genStockLabel.prn")
    whLocCheck = models.BooleanField("Restrict Location", help_text="Where a warehouse is specified, ensure that the location is associated with the warehouse.", default=False)
    trace  = PasswordCharField("Trace", max_length=20, help_text="AdvanceQC support use only: trace key.", blank=True)
    redisSock  = PasswordCharField("Redis socket", max_length=80, help_text="AdvanceQC support use only: canonical path to redis domain socket", blank=True, default="/var/run/redis/redis.captureQC.sock")
    # don't for get to update the reset values in admin.py

    class Meta:
        verbose_name="Application Configuration"
        verbose_name_plural=verbose_name
        ordering = ["appName",]

    def save(self, *args, **kwargs):
        super(AqcConfig, self).save()
        os.utime(os.path.join(utils.globalDict['path.root'], 'wsgi.py'), None)

    def __unicode__(self):  # Python 3: def __str__(self):
        return "{0}".format(self.appName)


class AqcConfigForm(ModelForm):
    class Meta:
        model = AqcConfig
        exclude = ["appName"]
        widgets = {
            "welcomeMOTD":   Textarea(),
            "userAgreement": Textarea(),
            "smtpPass":      PasswordInput(),
            "dbName":        Textarea(),
            "dbPass":        PasswordInput(),
            "trace":         PasswordInput(),
        }

    def clean(self):
        cleaned_data = super(AqcConfigForm, self).clean()
        if not cleaned_data['dbPort']:     cleaned_data['dbPort'] = ''
        if not cleaned_data['dbHost']:     cleaned_data['dbHost'] = ''
        return cleaned_data

    # #allow the next few fields to be set to anything including blank
    # def clean_smtpPass(self):
    #     print 'got here smtp'
    #     data = self.cleaned_data['smtpPass']
    #     return data
    #
    # def clean_dbPass(self):
    #     print 'got here dbpass'
    #     data = self.cleaned_data['dbPass']
    #     return data
    #
    # def clean_trace(self):
    #     print 'got here trace'
    #     data = self.cleaned_data['trace']
    #     return data


class Organization(AbstractModel):
    seqOrg = models.AutoField(primary_key=True)
    name = models.CharField('Organization Name', max_length=75, unique=True)
    enabled = models.BooleanField(default=False)
    validFrom = models.DateField('Valid From', null=True)  #if non-null then enabled
    validUntil = models.DateField('Valid To' , null=True)  #if non-null then enabled

    class Meta:
        ordering = ['name',]

    def __unicode__(self):  # Python 3: def __str__(self):
        return "{0}".format(self.name)


class AccessProfile(AbstractModel):
    seqAccessProfile = models.AutoField(primary_key=True)
    name = models.CharField('Profile Name', max_length=75, unique=True)
    timeClock   = models.BooleanField('Time clock', default=False)
    labour      = models.BooleanField('Single Task Labor', default=False)
    labourBatch = models.BooleanField('Batched Labor', default=False)
    woStatus    = models.BooleanField('Work Order Status', default=False)
    stockDemand = models.BooleanField('Stock Demand', default=False)
    stockIssue  = models.BooleanField('Stock Issue', default=False)
    stockUndo   = models.BooleanField('Stock Undo-Activity', default=False)
    stockSearch = models.BooleanField('Stock Search', default=False)
    stockTurnIn = models.BooleanField('Stock Turn-In', default=False)
    stockLabel  = models.BooleanField('Stock Label', default=False)

    class Meta:
        verbose_name="Access Profile"
        verbose_name_plural="Access Profiles"
        ordering = ['name',]

    def __unicode__(self):  # Python 3: def __str__(self):
        return "{0}".format(self.name)

    def asList(self):
        return  [ fldName for fldName in self._meta.get_all_field_names()
                    if getattr(self, fldName, False) and fldName not in ['seqAccessProfile', 'name']
                ]


class DefaultsProfile(AbstractModel):
    seqDefaultsProfile = models.AutoField(primary_key=True)
    name = models.CharField('Profile Name', max_length=75, unique=True)
    batchLaborGraceTime = models.PositiveSmallIntegerField("Batch Labour Grace [sec]", default=300)
    idleTime = models.PositiveSmallIntegerField("Idle Session [sec]", help_text="Amount of time before an idle warning message is displayed [sec]", default=45)
    idleTimeOut = models.PositiveSmallIntegerField("Idle TimeOut", help_text="Wait time after display of the idle warning message before the screen is cleared [sec]", default=15)
    turnInCondition = models.CharField('Turn-in condition code', max_length=10, default="AR")

    class Meta:
        verbose_name="Defaults Profile"
        verbose_name_plural="Defaults Profiles"
        ordering = ['name',]

    def __unicode__(self):  # Python 3: def __str__(self):
        return "{0}".format(self.name)


class UserManager(models.Manager):
    def colleagues(self, seqUser):
        cursor = connection.cursor()
        cursor.execute("""
                SELECT *
                FROM capture_user
                WHERE seqOrg = (SELECT seqOrg
                                FROM capture_user
                                WHERE seqUser = {0} )
            """.format(seqUser))
        return cursor.fetchall()

class User(AbstractModel):
    seqUser = models.AutoField(primary_key=True)
    seqOrg = models.ForeignKey(Organization, db_column='seqOrg', related_name='+')
    seqAccessProfile = models.ForeignKey(AccessProfile, db_column='seqAccessProfile', related_name='+')
    seqDefaultsProfile = models.ForeignKey(DefaultsProfile, db_column='seqDefaultsProfile', related_name='+', null=True, blank=True)
    firstName = models.CharField('First Name', max_length=35)
    lastName =  models.CharField('Last Name', max_length=35)
    userId = models.CharField('User ID', max_length=20, help_text="Must be unique for all application users")
    password = models.CharField('Password', max_length=32) #md5 hash
    tmpPassword = models.CharField('tmpPassword', null=True, max_length=46) #(yyyymmddhhmmss)(md5 hash)
    email = models.EmailField('E-Mail', max_length=50)
    phone = models.CharField('Phone Number', max_length=20)
    enabled = models.BooleanField('Enabled', default=True, help_text="Is this user account permitted to login to this application.")
    validFrom = models.DateField('Valid From', null=True, help_text="The date after which the user account is permitted to login to this application.")
    validUntil = models.DateField('Valid Until', null=True, help_text="The date after which the user account will not be permitted to login to this application.")
    admin = models.BooleanField('Is Admin', help_text="Is this user permitted to create and edit the account information of other users.", default=False)
    public = models.BooleanField('Is Public', help_text="Is this userId used to login to a shared or public workstation.", default=False)
    lastUpdated = models.DateTimeField(auto_now=True)
    lastLoggedIn = models.DateTimeField('Last Login (UTC)', null=True, default=None)
    agreedToTerms = models.BooleanField('Agreed To Terms', default=False)
    defaultUserId = models.CharField('Default UserId', max_length=12, null=True, blank=True, help_text="The default user-id for this account")
    defaultCompanyId = models.CharField('Default CompanyId', max_length=4, null=False, default='1', help_text="The Company_ID to use for this User's transactions (See Quantum's Global Settings)")
    defaultPrinter = models.CharField('Default Label Printer', max_length=16, null=True, blank=True, help_text="The name or network address of a Zebra label printer.")
    defaultWarehouse = models.CharField('Default Warehouse', max_length=15, null=True, blank=True, help_text="The warehouse name to use when specifying locations.")

    class Meta:
        verbose_name = "User Account"
        verbose_name_plural = "User Accounts"
        unique_together = ("seqOrg", "userId")
        ordering = ['lastName', 'firstName']

    def save(self, *args, **kwargs):
        if kwargs.get('newPass', ""):
            self.password = hashlib.md5(self.userId.lower() + kwargs['newPass']).hexdigest()
        super(User, self).save()

    def __unicode__(self):  # Python 3: def __str__(self):
        return "{0} ({1} {2})".format(self.userId, self.firstName, self.lastName)

    objects = UserManager()
