"""
Copyright AdvanceQC LLC 2014,2015.  All rights reserved
"""

import string
import random

from django.contrib import admin

from aqclib import utils
from aqclib import dbUtils

from capture.models import AqcConfig, AqcConfigForm
from capture.models import Organization
from capture.models import User
from capture.models import AccessProfile
from capture.models import DefaultsProfile
from capture.db.dbSchema import install as schemaInstall


class AqcConfigAdmin(admin.ModelAdmin):
    form = AqcConfigForm
    actions = ['reset', 'install']

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def reset(self, request, queryset):
        for aqcConfig in queryset:
            aqcConfig.appName       = utils.globalDict["application.name"]
            aqcConfig.company       = "advanceQC"
            aqcConfig.domain        = "advanceQC.com"
            aqcConfig.companyURL    = "http://www.advanceQC.com"
            #aqcConfig.companyLogo   = "./aqcWebLogo.png"
            aqcConfig.welcomeMOTD   = """<p>The use of this site is restricted to staff of Your Company.</p>""" \
                                    + """<p>Use by any other parties is strictly prohibited.</p>"""
            aqcConfig.userAgreement = """<b>Agreement</b><br>""" \
                                    + """<p>{Place staff user agreement here}</p>"""
            aqcConfig.appURL        = "http://" + utils.globalDict["application.name"] + ".advanceQC.com"
            aqcConfig.appAdminEmail = utils.globalDict["application.name"] + "@advanceQC.com"
            aqcConfig.smtpHost      = "smtp.gmail.com"
            aqcConfig.smtpPort      = "587"
            aqcConfig.smtpAcct      = utils.globalDict["application.name"] + ".advanceQC@gmail.com"
            aqcConfig.smtpPass      = "lowSecurityCredential"
            aqcConfig.emailFrom     = utils.globalDict["application.name"] + "@advanceQC.com"
            aqcConfig.emailBCC      = utils.globalDict["application.name"] + "@advanceQC.com"
            aqcConfig.dbMode        = "Dedicated"
            aqcConfig.dbName        = "tnsName - if a simple string, and host/port unspecified, or\n"  \
                                    + "sid     - if a simple string, and host/port specified, or\n"    \
                                    + "host.db.com:1521/serviceName.db.com  - if host/port unspecified, or\n"    \
                                    + "full oracle connection descriptor  - if host/port unspecified\n"
            aqcConfig.dbHost        = "" #"oracle.advanceQC.com"
            aqcConfig.dbPort        = '1521'
            aqcConfig.dbUser        = "qctl"
            aqcConfig.dbPass        = "oraPassword"
            #aqcConfig.stockLabel    = ""
            aqcConfig.whLocCheck    = False
            aqcConfig.trace         = "-"
            aqcConfig.redisSock     = "/var/run/redis/redis.captureQC.sock"
            aqcConfig.save()
        self.message_user(request, "Install default values restored")
    reset.short_description = "Reset to install defaults"


    def install(self, request, queryset):
        dbCon = dbUtils.dbConnection()
        schemaInstall(dbCon.connection)
        dbCon.close()
        self.message_user(request, "Application database objects installed for {}".format(utils.globalDict['dbUser']))
    install.short_description = "Install application database objects"


    def get_actions(self, request):
        actions = super(AqcConfigAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


class UserInline(admin.TabularInline):
    model = User
    extra = 3
    readonly_fields = ('agreedToTerms', 'lastUpdated', 'lastLoggedIn')
    exclude = ('password', 'tmpPassword')
    #actions = ['reset_password']
    fk_name = 'seqOrg'

    # def reset_password(self, request, queryset):
    #     newPass = "".join([random.choice(string.ascii_letters + string.digits) for n in xrange(8)])
    #     for user in queryset:
    #         passHash = hashlib.md5(obj.userId + newPass)[:20]
    #         user.update(password=passHash)
    #     self.message_user(request, "{0} password(s) reset to '{1}'.".format(len(queryset), passHash))
    # reset_password.short_description = "Reset Password"


class OrganizationAdmin(admin.ModelAdmin):
    inlines = [UserInline]


class UserAdmin(admin.ModelAdmin):
    readonly_fields = ('agreedToTerms', 'lastUpdated', 'lastLoggedIn')
    exclude = ('password', 'tmpPassword')
    actions = ['reset_password', 'clear_agreeToTerms']

    def reset_password(self, request, queryset):
        newPass = "".join([random.choice(string.ascii_letters + string.digits) for n in xrange(8)])
        for user in queryset:
            user.save(newPass=newPass)
        self.message_user(request, "{0} password(s) reset to '{1}'.".format(len(queryset), newPass))
    reset_password.short_description = "Reset Password"

    def clear_agreeToTerms(self, request, queryset):
        newPass = "".join([random.choice(string.ascii_letters + string.digits) for n in xrange(8)])
        for user in queryset:
            user.agreedToTerms = False
            user.save()
        self.message_user(request, "Agreement cleared for {0} user(s).".format(len(queryset), newPass))
    clear_agreeToTerms.short_description = "Clear Agreed to Terms"


admin.site.register(AqcConfig, AqcConfigAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(AccessProfile)
admin.site.register(DefaultsProfile)

