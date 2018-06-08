"""
Copyright AdvanceQC LLC 2014,2015.  All rights reserved
"""

import os
import random
import string
import hashlib
import re
import logging
import time
from datetime import datetime, timedelta, date

import smtplib
from email.mime.multipart  import MIMEMultipart
from email.mime.text       import MIMEText
from email.mime.image      import MIMEImage

from django                   import forms
from django.http              import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts         import render, get_object_or_404, get_list_or_404
from django.utils.safestring  import mark_safe
from django.core.urlresolvers import reverse

from aqclib         import utils
from aqclib.dbUtils import dbConnection, dbQuote, dbFetchOne, dbFetchAll, dbExecute

from models import User
from viewUtils    import viewSecurity, navStackModify, jsonDump
from viewsCapture import ViewCapture


#############################################################################
# very basic/core views
#############################################################################
def sessionErr(request, msg=None):
    return render(request, 'session/sessionErr.html', dict(frmName='sessionErr', msg=msg))


#############################################################################
# views
#############################################################################
def welcome(request):
    return render(request, 'session/welcome.html')


class LoginForm(forms.Form):
    userId   = forms.CharField(max_length=35, label="User-ID")
    password = forms.CharField(max_length=20, label="Password", widget=forms.PasswordInput())

    def clean_userId(self):
        val = self.cleaned_data['userId']
        if not val.isalnum:
            raise forms.ValidationError('Please enter a proper UserID')
        return val


def login(request):
    if request.method == 'POST': # If the form has been submitted...
        form = LoginForm(request.POST) # A form bound to the POST data
        if form.is_valid():
            userId   = form.cleaned_data['userId']
            password = form.cleaned_data['password']

            # is there a user with the given password
            users = User.objects.filter(userId=userId.lower())
            for user in users:
                if hashlib.md5(user.userId.lower() + password).hexdigest() == user.password:
                    break
                if user.tmpPassword:
                    if hashlib.md5(user.userId.lower() + password).hexdigest() == user.tmpPassword[14:]:
                        now = datetime.now().strftime("%Y%m%d%H%M%S")
                        if now < user.tmpPassword[:14]:
                            break
            else:
                msg = """<p>Could not authenticate: {0} </p>
                         <p>If you would like a
                           temporary password,
                           one can be sent to the e-mail address set in your preferences.</p>
                         <a href="{1}" data-role="button" data-mini="true" data-inline="True">Temporary Password...</a>
                      """.format(userId, reverse('capture:resetPassword'))
                form._errors['__all__'] = form.error_class([mark_safe(msg)])
                form._errors['password'] = form.error_class([mark_safe('<span style="font-color: blue;">Check caps lock.<span>')])
                return render(request, 'session/login.html', dict(frmName='login', form=form))
            conUser = user
            conOrg = user.seqOrg

            def accountNotEnabled():
                form._errors['__all__'] = form.error_class([mark_safe('User account not authorized at this time')])
                return render(request, 'session/login.html', dict(frmName='login', form=form))

            # is the org enabled
            now = date.today()
            if not conOrg.enabled:
                return accountNotEnabled()
            if conOrg.validFrom is None or now < conOrg.validFrom:
                return accountNotEnabled()
            if conOrg.validUntil is None or now > conOrg.validUntil:
                return accountNotEnabled()

            # is the user enabled
            if not conUser.enabled:
                return accountNotEnabled()
            if conUser.validFrom is None or now < conUser.validFrom:
                return accountNotEnabled()
            if conUser.validUntil is None or now > conUser.validUntil:
                return accountNotEnabled()

            # okay we're in... create new session
            request.session.flush()

            # stuff timeZone offset into the session
            request.session['tzOffset'] = request.POST.get('tzOffset')
            if (request.session['tzOffset'] is None):   #use server timezone offset
                request.session['tzOffset'] = -time.altzone/60

            # stuff conUser into the session
            conUser.lastLoggedIn = datetime.now()
            conUser.save()
            request.session['conUser']         = conUser.asDict()
            try:
                request.session['accessList']      = conUser.seqAccessProfile.asList()
            except AttributeError, e:
                form._errors['__all__'] = form.error_class([mark_safe('Account has not be provided with an access list.  Login denied.')])
                return render(request, 'session/login.html', dict(frmName='login', form=form))
            try:
                request.session['defaultsProfile'] = conUser.seqDefaultsProfile.asDict()
            except AttributeError, e:
                form._errors['__all__'] = form.error_class([mark_safe('Account has not be provided with a defaults profile.  Login denied.')])
                return render(request, 'session/login.html', dict(frmName='login', form=form))

            # where to now
            if not conUser.agreedToTerms:
                return HttpResponseRedirect( reverse('capture:userAgreement') )
            #elif 'interceptedUri' in request.session:
            #    #we were re-directed here, now lets redirect back to the original requested uri
            #    revString, args, kwargs = request.session['interceptedUri']
            #    return HttpResponseRedirect( reverse(revString, args=args, kwargs=kwargs) )
            return HttpResponseRedirect( reverse('capture:menu') )
    else:
        form = LoginForm() # An unbound form
    return render(request, 'session/login.html', dict(frmName='login', form=form))


class ResetPasswordForm(forms.Form):
    email = forms.CharField(max_length=35, label="E-Mail")

    def clean_email(self):
        val = self.cleaned_data['email']
        if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", val):
            raise forms.ValidationError('Please enter a proper E-mail address')
        return val


def resetPassword(request):
    if request.method == 'POST': # If the form has been submitted...
        form = ResetPasswordForm(request.POST) # A form bound to the POST data
        if form.is_valid():
            email = form.cleaned_data['email']

            # is there a user with this email
            users = User.objects.filter(email__iexact=email)
            for user in users:
                newPass = "".join([random.choice(string.ascii_letters + string.digits) for n in xrange(8)])
                user.tmpPassword = (datetime.now() + timedelta(hours=4)).strftime("%Y%m%d%H%M%S") + hashlib.md5(user.userId.lower() + newPass).hexdigest()
                user.save()

                try:
                    # send email Create message container - the correct MIME type is multipart/alternative.
                    msg = MIMEMultipart('alternative')
                    msg['From'] = utils.globalDict['emailFrom']
                    msg['To'] = user.email
                    msg['Subject'] = "{} @ {}: Password Reset".format(utils.globalDict['appName'], utils.globalDict['company'])

                    text = """
                        Your {provider} {appName} password has been changed.

                            userId:   {userId}
                            password: {newPass}

                        Please login and and change your password from the 'profile' page as this
                        password is temporary, and it will expire in a few hours.

                        Thank-you
                            {provider}
                    """.format(provider = utils.globalDict['company'],
                               appName = utils.globalDict['appName'],
                               userId = user.userId,
                               newPass = newPass,
                               portalAddress = utils.globalDict['appURL'],
                               domain = utils.globalDict['domain'],
                              )
                    html = """
                        <html>
                            <head>
                                <style>
                                    td {{
                                        border: 0px solid black;
                                        border-collapse: collapse;
                                        padding-right: 15px;
                                    }}
                                    table {{
                                        padding-left: 20px;
                                    }}
                                </style>
                            </head>
                            <body>
                                <p>
                                    Your {provider} {appName} password has been changed.
                                </p>
                                <br>
                                    <table>
                                        <tr> <td>userId:</td>            <td><b>{userId}</b></td>   </tr>
                                        <tr> <td>password:</td>          <td><b>{newPass}</b></td>  </tr>
                                    </table>
                                <br>
                                <p>
                                    Please login and change your password from the 'profile' page as this
                                    password is temporary, and it will expire in a few hours.
                                </p>
                                <br>
                                <p>
                                    Thank-you,
                                </p>
                                <a href="{webAddress}"><img src="cid:companyLogo.img"></a><br>
                            </body>
                        </html>
                    """.format(provider = utils.globalDict['company'],
                               appName = utils.globalDict['appName'],
                               userId = user.userId,
                               newPass = newPass,
                               portalAddress = utils.globalDict['appURL'],
                               domain = utils.globalDict['domain'],
                               webAddress = utils.globalDict['companyURL'],
                              )
                    # Attach parts into message container.
                    # According to RFC 2046, the last part of a multipart message, in this case
                    # the HTML message, is best and preferred.
                    msg.attach(MIMEText(text, 'plain'))
                    msg.attach(MIMEText(html, 'html'))
                    try:
                        with open(os.path.join(utils.globalDict['path.mediaRoot'], utils.globalDict['companyLogo']), 'rb') as fp:
                            img = MIMEImage(fp.read())
                            img.add_header('Content-ID', "companyLogo.img")
                            msg.attach(img)
                    except IOError as e:
                        pass

                    # send the mail
                    s = smtplib.SMTP(utils.globalDict['smtpHost'], int(utils.globalDict['smtpPort']))
                    s.ehlo()
                    s.starttls()
                    s.login(utils.globalDict['smtpAcct'], utils.globalDict['smtpPass'])
                    s.sendmail(msg['From'], [msg['To']],                    msg.as_string())
                    #s.sendmail(msg['From'], [utils.globalDict['emailBCC']], msg.as_string())
                    s.quit()

                except Exception, exc:
                    logging.exception(exc)
                break
            else:
                msg = 'No user with this e-mail is registered.'
                form._errors['__all__'] = form.error_class([mark_safe(msg)])
                return render(request, 'session/resetPassword.html', dict(frmName='resetPassword', form=form))
            return HttpResponseRedirect( reverse('capture:login') )
    else:
        form = ResetPasswordForm() # An unbound form
    return render(request, 'session/resetPassword.html', dict(frmName='resetPassword', form=form,))


def logout(request):
    request.session.flush()
    return HttpResponseRedirect( reverse('capture:welcome') )


@viewSecurity('capture:userAgreement')
def userAgreement(request):
    conUser = get_object_or_404(User, seqUser=request.session['conUser']['seqUser'])
    if request.method == 'POST': # If the form has been submitted...
        agree = request.POST.get("agree", "")
        if agree == 'Agree':
            conUser.agreedToTerms = True
            conUser.save()
            return HttpResponseRedirect( reverse('capture:menu') )
        else:
            return HttpResponseRedirect( reverse('capture:welcome') )
    else:
        return render(request, 'session/userAgreement.html', dict(userAgreement = utils.globalDict['userAgreement'].splitlines()))

@viewSecurity('capture:menu')
def menu(request):
    navStackModify(request.session, 'Menu', reverse('capture:menu'))
    conUser = get_object_or_404(User, seqUser=request.session['conUser']['seqUser'])
    accessList = request.session['accessList']
    pages = []
    for item in ViewCapture.MENU_ITEMS:
        if item['name'] in accessList:
            pages.append(dict( name     = item['name']
                             , label    = item['label']
                             , template = item['html']
                             , org      = conUser.seqOrg.name  ))
    return render(request, 'capture/pageMenu.html', dict( frmName='menu', pages=pages, ))


@viewSecurity('capture:about')
def about(request):
    navStackModify(request.session, 'About', reverse('capture:about'))

    q = """ select APP.version
                 , APP.installedOn
                 , to_char(LIC.expiry, 'yyyy-mm-dd')
              from aqcApplication APP
                 , aqcLicense     LIC
             where APP.seqApplication = LIC.seqApplication
               and APP.application = :appName
               and LIC.schema = upper(:dbUser) """
    row, fldNames = dbFetchOne(None, q, dict( appName = utils.globalDict['appName']
                                            , dbUser = utils.globalDict['dbUser']
                                            ))

    return render(request, 'session/about.html', dict( frmName = 'about',
                                                       version     = utils.globalDict['application.version'],
                                                       installedOn = row[1],
                                                       expiresOn   = row[2],
                                                     ))


