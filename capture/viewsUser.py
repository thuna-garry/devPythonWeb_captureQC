"""
Copyright AdvanceQC LLC 2014,2015.  All rights reserved
"""

import json
import sys
import logging

from django                   import forms
from django.forms.extras.widgets import SelectDateWidget
from django.shortcuts         import render
from django.shortcuts         import get_object_or_404, get_list_or_404
from django.core.urlresolvers import reverse
from django.http              import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.utils.safestring  import mark_safe

from viewUtils import *
from models import *


#############################################################################
# views
#############################################################################
class UserForm(forms.ModelForm):
    pass1 = forms.CharField(label='Password',         max_length=32, widget=forms.PasswordInput(), required=False)
    pass2 = forms.CharField(label='Password Confirm', max_length=32, widget=forms.PasswordInput(), required=False)

    class Meta:
        model = User
        fields = ['firstName', 'lastName', 'userId', 'pass1', 'pass2',
                  'email', 'phone', 'enabled', 'validFrom', 'validUntil', 'admin']
        widgets = {
            'validFrom': SelectDateWidget(),
            'validUntil': SelectDateWidget(),
        }

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs) # Call to ModelForm constructor
        for f in self.fields:
            if isinstance(self.fields[f], forms.fields.CharField):
                self.fields[f].widget.attrs['style'] = "width:{0}em;".format(int(self.fields[f].widget.attrs['maxlength']) / 2)
            if isinstance(self.fields[f], forms.fields.EmailField):
                self.fields[f].widget.attrs['style'] = "width:{0}em;".format(int(self.fields[f].widget.attrs['maxlength']) / 2)
            #print type(self.fields[f])

    def clean_uid(self):
        uid = self.cleaned_data['uid']
        if not uid.isalnum:
            raise forms.ValidationError('Please enter a proper UserID')
        return uid

    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        pass1 = cleaned_data['pass1']
        pass2 = cleaned_data['pass2']
        if pass1 or pass2:
            if pass1 != pass2:
                self._errors["__all__"] = 'Password and its confirmation do not match.'
                self._errors["pass1"] = 'Password Error'
                self._errors["pass2"] = 'Password Error'
        if not self.instance.seqUser and not pass1:
            self._errors["pass1"] = self.error_class(['This field is required.'])
            self._errors["pass2"] = self.error_class(['This field is required.'])
        return cleaned_data


class ProfileForm(UserForm):
    userId = forms.CharField(label='User ID', max_length=20, widget=forms.TextInput(attrs={'readonly':'readonly'}))
    class Meta(UserForm.Meta):
        fields = ['userId', 'firstName', 'lastName', 'pass1', 'pass2', 'email', 'phone', 'defaultUserId', 'defaultPrinter', 'defaultWarehouse']


@viewSecurity('capture:profile')
def profile(request):
    navStackModify(request.session, 'Profile', reverse('capture:profile'))
    modUser = get_object_or_404(User, seqUser=request.session['conUser']['seqUser'])
    print "in profile"
    if request.method == 'POST': # If the form has been submitted...
        print "in post"
        form = ProfileForm(request.POST, instance=modUser) # A form bound to the POST data
        if form.is_valid():
            print "form is valid"
            modUser = form.save(commit=False)
            pass1 = form.cleaned_data['pass1']
            if pass1:
                print "pass1 is non null"
                modUser.save(newPass=pass1)
            else:
                modUser.save()
            # put changes in session
            request.session['conUser'] = modUser.asDict()
            return HttpResponseRedirect( reverse('capture:menu') )
    else:
        if modUser.public:
            return HttpResponseRedirect( reverse('capture:sessionErr') )
        form = ProfileForm(instance=modUser) # An unbound form
    return render(request, 'users/profile.html', dict( frmName='profile', form=form ))

