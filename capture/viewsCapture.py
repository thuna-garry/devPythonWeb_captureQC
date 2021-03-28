"""
Copyright AdvanceQC LLC 2014,2015.  All rights reserved
"""

import logging
import re
import json
import traceback

from django.views.generic     import View
from django.shortcuts         import render
from django.http              import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.core.urlresolvers import reverse
from django.utils.cache       import patch_cache_control
from django.utils.safestring  import mark_safe

from aqclib         import utils
from aqclib.dbUtils import dbConnection, dbQuote, dbFetchOne, dbFetchAll, dbExecute
from aqclib.dbUtils import ServerDbError

from viewUtils import jsonResponse, emptyJsonResponse,  jsonRedirect, jsonErrorResponse
from viewUtils import SessionError

RE_BIND_PARM = re.compile(':\w+')


#############################################################################
# decorators
#############################################################################
def ajaxProcess(f):
    def wrapped_f(self, request, frmName, *args, **kwargs):
        if frmName in request.session['accessList']:
            return f(self, request, frmName, *args, **kwargs)
        respData = {'errCode':'AQC-0001', 'errMsg': 'Access not permitted', 'errTitle': 'Security Violation'}
        return jsonErrorResponse(respData, 'Access not permitted')
    return wrapped_f


#############################################################################
# ViewCapture: base capture form
#############################################################################
class ViewCapture(View):

    MENU_ITEMS = [  #remember that the name here must exist as a field in the AccessProfile model
            {'name': 'timeClock',    'label': 'Time-Clock',              'html': 'capture/pageTimeClock.html'},
            {'name': 'labour',       'label': 'Labor: Single-Task',      'html': 'capture/pageLaborSingleTask.html'},
            {'name': 'labourBatch',  'label': 'Labor: Batched',          'html': 'capture/pageLaborBatch.html'},
            {'name': 'woStatus',     'label': 'Work-Order Status',       'html': 'capture/pageWorkOrderStatus.html'},
            {'name': 'stockIssue',   'label': 'Stock Issue',             'html': 'capture/pageForm.html'},
            {'name': 'stockDemand',  'label': 'Stock Demand',            'html': 'capture/pageForm.html'},
            {'name': 'stockUndo',    'label': 'Stock Undo-Activity',     'html': 'capture/pageStockUndo.html'},
            {'name': 'stockSearch',  'label': 'Stock Search',            'html': 'capture/pageStockSearch.html'},
            {'name': 'stockTurnIn',  'label': 'Stock Turn-In',           'html': 'capture/pageForm.html'},
            {'name': 'stockLabel',   'label': 'Stock Print Label',       'html': 'capture/pageForm.html'},
        ]

    FLD_MSG_TYPE_NONE = 0
    FLD_MSG_TYPE_ERROR = -1
    FLD_MSG_TYPE_INVALID = -2
    FLD_MSG_TYPE_NOT_FOUND = -3
    FLD_MSG_TYPE_VALID = 2

    W2CM_DONT = 0        #when to clear message
    W2CM_ON_CHANGE = 1   #when to clear message
    W2CM_GOT_FOCUS = 2
    W2CM_EDIT_DONE = 3

    FORM_MSG_TYPE_NONE = 0
    FORM_MSG_TYPE_ERROR = -1
    FORM_MSG_TYPE_CRITICAL = -2
    FORM_MSG_TYPE_WARNING = -3
    FORM_MSG_TYPE_TX_COMPLETE = 1

    def get(self, request, frmName, target=None):
        return self.post(request, frmName, target=target)

    def post(self, request, frmName, target=None):
        try:
            if not request.session.get('conUser'):
                raise SessionError("Session invalid or expired.")
            if request.path_info.endswith(('.html', '.html/')):
                template = [ item['html'] for item in self.MENU_ITEMS if item['name'] == frmName ][0]
                request.session['referer'] = request.META['HTTP_REFERER']  #stash reference from initial page load
                response = render(request, template, dict( frmName=frmName, pages=self.MENU_ITEMS ))
                response['Pragma'] = 'no-cache'
                response['Expires'] = '0'
                patch_cache_control(response, no_cache=True, no_store=True, must_revalidate=True, max_age=0)
                return response
            if not target:
                return getattr(self, 'ajax_form')(request, frmName)
            elif target.startswith('fld_'):
                rc = getattr(self, 'ajax_' + target)(request, frmName, target[4:])
                return rc
            else:
                return getattr(self, 'ajax_' + target)(request, frmName)

        except SessionError as e:
            if 'application/json' in request.META['HTTP_ACCEPT']:
                return jsonErrorResponse(dict(redirectTo=reverse('capture:sessionErr')), e.message)
            else:
                return HttpResponseRedirect( reverse('capture:sessionErr') )

        except ServerDbError as e:
            trace = [ x for x in e.message.split('\n') ]
            oraErr, oraMsg = trace[0].split(': ')
            msg = "Database error occurred while processing form ({}/{})\n{}"
            #logging.debug(msg, exc_info=True)
            if 'application/json' in request.META['HTTP_ACCEPT']:
                return jsonErrorResponse(dict(errTitle=e.errTitle, errMsg=oraMsg), msg.format(frmName, target, e.message))
            else:
                request.session['systemError'] = dict(msg=msg.format(frmName, target, oraMsg), trace=trace)
                return HttpResponseRedirect( reverse('capture:systemErr') )

        except Exception as e:
            msg = "AQC-0003: Exception while processing form ({}/{})".format(frmName, target)
            logging.debug(msg, exc_info=True)
            request.session['systemError'] = dict(msg=msg, trace=traceback.format_exc())
            if 'application/json' in request.META['HTTP_ACCEPT']:
                return jsonErrorResponse(dict(redirectTo=reverse('capture:systemErr')), msg)
            else:
                return HttpResponseRedirect( reverse('capture:systemErr') )


    def ajax_form(self, request, frmName=None, fldName=None):
        """ this exists only to provide a view signature for reverse URL lookups
            and should/will never actually be called """
        logging.error("Received disallowed request")
        return emptyJsonResponse()


    #---------------------------------------------------
    # session utilities
    #---------------------------------------------------
    def processInitForm(self, request, frmName):
        fs   = {}   #request.session.get("fs_"   + frmName, {})
        form = None #request.session.get("form_" + frmName, {})
        fs['loggedInUser'] = request.session['conUser']['userId']
        fs['appName'] = utils.globalDict['appName']
        return fs, form

    def processInit(self, request, frmName):
        fs   = request.session.get("fs_"   + frmName, {})
        form = request.session.get("form_" + frmName, {})
        flds = form['flds']
        return fs, form, flds, json.loads(request.body)

    def processInitFld(self, request, frmName, fldName):
        fs, form, flds, reqBody = self.processInit(request, frmName)
        fldIdx = self.getFldIndex(flds, fldName)
        fld = flds[fldIdx]
        if (   ( not flds[fldIdx].get('group') )
            or (     len(flds)-1 > fldIdx
                 and flds[fldIdx+1].get('group', 0) != flds[fldIdx].get('group', 0)
              )
           ):
            del flds[fldIdx+1:]
        return fs, form, flds, fldIdx, fld, reqBody['value']

    def processFini(self, request, fs, form, payload=None, msgType=FORM_MSG_TYPE_NONE, msg=None, bbox=None):
        request.session["form_" + form['name']] = form
        request.session["fs_"   + form['name']] = fs
        if payload is not None:
            return jsonResponse([payload, msgType, msg, bbox])
        else:
            return jsonResponse([form,    msgType, msg, bbox])


    #---------------------------------------------------
    # field utilities
    #---------------------------------------------------
    def field(self, variety, name, label, value=None, msg=None, msgType=None, enabled=True, group=None, w2cm=W2CM_ON_CHANGE):
        fld = dict()
        fld['type'] = variety
        fld['name'] = name
        fld['label'] = label
        fld['value'] = value
        fld['msg'] = msg
        fld['msgType'] = msgType
        fld['w2cm'] = w2cm
        fld['enabled'] = enabled
        fld['group'] = group
        return fld

    def display(self, name, label, value=None, msg=None, msgType=FLD_MSG_TYPE_NONE, enabled=True, group=None):
        fld = self.field('display', name, label, value=value, msg=msg, msgType=msgType, enabled=enabled, group=group)
        return fld

    def lineEdit(self, name, label, length=12, size=None, prompt=None, value=None, msg=None, msgType=FLD_MSG_TYPE_NONE, enabled=True, group=None, w2cm=W2CM_ON_CHANGE):
        fld = self.field('lineEdit', name, label, value=value, msg=msg, msgType=msgType, enabled=enabled, group=group, w2cm=w2cm)
        fld['length'] = length
        fld['size'] = size if size else length
        fld['prompt'] = prompt
        if not prompt:
            fld['prompt'] = "Enter {}".format(label)
        return fld

    def textEdit(self, name, label, length=12, prompt=None, value=None, msg=None, msgType=FLD_MSG_TYPE_NONE, enabled=True, group=None, w2cm=W2CM_ON_CHANGE):
        fld = self.field('textEdit', name, label, value=value, msg=msg, msgType=msgType, enabled=enabled, group=group, w2cm=w2cm)
        fld['length'] = length
        fld['prompt'] = prompt
        if not prompt:
            fld['prompt'] = "Enter {}".format(label)
        return fld

    def dateEdit(self, name, label, value=None, msg=None, msgType=FLD_MSG_TYPE_NONE, enabled=True, group=None, w2cm=W2CM_ON_CHANGE):
        fld = self.field('dateEdit', name, label, value=value, msg=msg, msgType=msgType, enabled=enabled, group=group, w2cm=w2cm)
        return fld

    def lookup(self, name, label, length=8, size=None, prompt=None, value=None, multi=0, listItems=[], msg=None, msgType=FLD_MSG_TYPE_NONE, enabled=True, group=None, w2cm=W2CM_ON_CHANGE):
        fld = self.lineEdit(name, label, length, size=size, prompt=prompt, value=value, msg=msg, msgType=msgType, enabled=enabled, group=group, w2cm=w2cm)
        fld['type'] = 'lookup'
        fld['multi'] = multi
        fld['listItems'] = listItems
        return fld

    def listView(self, name, label, listItems=[], value=None, msg=None, msgType=FLD_MSG_TYPE_NONE, enabled=True, group=None):
        fld = self.field('listView', name, label, value=value, msg=msg, msgType=msgType, enabled=enabled, group=group)
        fld['listItems'] = listItems
        return fld

    def action(self, name, label, icon="", value="", msg=None, msgType=FLD_MSG_TYPE_NONE, enabled=True, group=None, w2cm=W2CM_ON_CHANGE):
        fld = self.field('action', name, label, value=value, msg=msg, msgType=msgType, enabled=enabled, group=group, w2cm=w2cm)
        fld['icon'] = icon
        return fld


    def getFldIndex(self, flds, fldName):
        i = 0
        for f in flds:
            if f['name'] == fldName:
                return i
            else:
                i += 1


    def fldsAppend(self, replace, flds, fld):
        idx = self.getFldIndex(flds, fld['name'])
        if idx:
            if replace:
                flds[idx] = fld
            return flds[idx]
        else:
            flds.append(fld)
            return fld

    def fldsRemove(self, flds, name):
        idx = self.getFldIndex(flds, name)
        if idx >= 0:

            del flds[idx]

#---------------------------------------------------
# generic fields and field operations   User
#---------------------------------------------------
    def createField_userId(self, value=None, msgType=FLD_MSG_TYPE_NONE, msg=None, group=None):
        return self.lineEdit('userId', 'Staff Id', 8, value=value, msgType=msgType, msg=msg, group=group)


    def appendUser(self, request, fs, form, msgType=FLD_MSG_TYPE_NONE, msg=None, group=None):
        flds = form['flds']
        fs['sysur_auto_key'] = None
        fld = self.fldsAppend(False, flds, self.createField_userId(msgType=msgType, msg=msg, group=group))

        defUserId = request.session['conUser'].get('defaultUserId')
        if not defUserId:
            return

        self.generic_fld_userId(request, fs, form, flds, fld, defUserId)
        if fs['sysur_auto_key']:
            self.gotUser(request, fs, form, flds, fld)


    def generic_fld_userId(self, request, fs, form, flds, fld, user_id):
        # get basic parameters for the scanned user
        fs['sysur_auto_key'] = None
        fs['user_id'] = user_id
        fs['company_id'] = request.session['conUser'].get('defaultCompanyId', 1)

        q = """ select SYSUR.sysur_auto_key, SYSUR.user_id, SYSUR.employee_code, SYSUR.last_name, SYSUR.first_name
                     , TAH.tah_auto_key, nvl(TAH.auto_lunch, 'F')
                     , SYSUR.wo_flag, SYSUR.mo_flag, SYSUR.wok_auto_key, WOK.description
                  from sys_users        SYSUR
                     , sys_companies    SYSCM
                     , ta_shift_header  TAH
                     , wo_skills        WOK
                 where SYSUR.tah_auto_key = TAH.tah_auto_key (+)
                   and SYSUR.wok_auto_key = WOK.wok_auto_key (+)
                   and SYSUR.user_id = :user_id
                   and SYSUR.archived = 'F'
                   and SYSCM.company_id = :company_id
            """
        row, fldNames = dbFetchOne(None, q, fs)
        if not row:
            fld['value'] = ""
            fld['msgType'] = self.FLD_MSG_TYPE_NOT_FOUND
            fld['msg'] = "User/Company not found"
            return None

        fs['sysur_auto_key'], fs['user_id'], fs['employee_code'], last_name, first_name \
            , fs['tah_auto_key'], fs['autoLunch'] \
            , fs['wo_flag'], fs['mo_flag'], fs['wok_auto_key'], fs['wokDesc'] = row

        displayName = utils.nvl(fs['employee_code'], "(user name not provided)").strip()
        first_name = utils.nvl(first_name, "").strip()
        last_name = utils.nvl(last_name, "").strip()
        if len(first_name) and len(last_name):
             displayName = " ".join((first_name, last_name))

        fld['value'] = user_id
        fld['msgType'] = self.FLD_MSG_TYPE_VALID
        fld['msg'] = displayName
        return fs['sysur_auto_key']


    @ajaxProcess
    def ajax_fld_userId(self, request, frmName, fldName=None, msgType=FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, fldIdx, fld, user_id = self.processInitFld(request, frmName, fldName)

        self.generic_fld_userId(request, fs, form, flds, fld, user_id)
        if fs['sysur_auto_key']:
            self.gotUser(request, fs, form, flds, fld)
        return self.processFini(request, fs, form, msgType=msgType, msg=msg)


#---------------------------------------------------
# generic fields and field operations   WOOT
#---------------------------------------------------
    def createField_woot(self, value=None, msgType=FLD_MSG_TYPE_NONE, msg=None, group=None):
        return self.lineEdit('woot', 'Work Order', 12, prompt="W/O or Task", value=value, msgType=msgType, msg=msg, group=group)


    def generic_fld_woot(self, request, fs, form, flds, fld, woot):
        fs['woo_auto_key'] = None
        fs['wot_auto_key'] = None
        fs['si_number'] = None

        # could be a task capture
        if re.match('[0-9]+[SCsc]$', woot):
            wot_auto_key = woot[:-1]
            q = """ select WOT.woo_auto_key
                         , WOT.wot_auto_key
                         , WOT.sequence
                         , WTM.description
                         , nvl(WOS.description,   'Pending')
                      from wo_task          WOT
                         , wo_task_master   WTM
                         , wo_status        WOS
                     where WOT.wtm_auto_key = WTM.wtm_auto_key  -- all tasks have a masters
                       and WOT.wos_auto_key = WOS.wos_auto_key (+)
                       and WOT.wot_auto_key = :wot_auto_key
                """
            row, fldNames = dbFetchOne(None, q, dict(wot_auto_key = wot_auto_key))
            if row:
                fs['woo_auto_key'], fs['wot_auto_key'], sequence, wot_desc, wot_status = row

        # get the work order
        if fs.get('woo_auto_key') is None:
            wClause = "and upper(WOO.si_number) = upper(:woot)"
        else:
            wClause = "and WOO.woo_auto_key = :woo_auto_key"
        q = """ select WOO.woo_auto_key
                     , WOO.si_number
                     , WOO.open_flag
                     , PNM.pn
                     , PNM.description
                     , nvl(WOS.description, 'Pending')
                  from wo_operation     WOO
                     , parts_master     PNM
                     , wo_status        WOS
                 where WOO.pnm_auto_key = PNM.pnm_auto_key (+)
                   and WOO.wos_auto_key = WOS.wos_auto_key (+)
                   {wClause}
            """.format(wClause=wClause)
        row, fldNames = dbFetchOne(None, q, dict(fs.items() + dict(woot=woot).items()))
        if row:
            fs['woo_auto_key'], fs['si_number'], openFlag, pnum, pdesc, woo_status = row

        if not fs['woo_auto_key']:
            fld['value'] = woot
            fld['msgType'] = self.FLD_MSG_TYPE_NOT_FOUND
            fld['msg'] = "No work-order found"
            return None, None
        else:
            if openFlag == 'F':
                fld['value'] = woot
                fld['msgType'] = self.FLD_MSG_TYPE_NOT_FOUND
                fld['msg'] = "Work-order closed"
                return None, None

        fld['value'] = fs['si_number']
        fld['msgType'] = self.FLD_MSG_TYPE_VALID
        fld['msg'] = "{}  [{}]".format(pnum, woo_status)

        fld = self.fldsAppend(False, flds, self.createField_task())
        if fs['wot_auto_key']:
            fld['value'] = sequence
            fld['msgType'] = self.FLD_MSG_TYPE_VALID
            fld['msg'] = "{}  [{}]".format(wot_desc, wot_status)
        return fs['woo_auto_key'], fs['wot_auto_key']


    @ajaxProcess
    def ajax_fld_woot(self, request, frmName, fldName=None, msgType=FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, fldIdx, fld, woot = self.processInitFld(request, frmName, fldName)

        woo, wot = self.generic_fld_woot(request, fs, form, flds, fld, woot)
        if wot:
            self.gotWot(request, fs, form, flds, fld)
        return self.processFini(request, fs, form, msgType=msgType, msg=msg)


#---------------------------------------------------
# generic fields and field operations  task
#---------------------------------------------------
    def createField_task(self, value=None, msgType=FLD_MSG_TYPE_NONE, msg=None, group=None):
        return self.lineEdit('task', 'Task', 10, value=value, msgType=msgType, msg=msg, group=group)


    def generic_fld_task(self, request, fs, form, flds, fld, task):
        fs['wot_auto_key'] = None

        if re.match('[0-9]+[SCsc]$', task):
            wClause = " and WOT.wot_auto_key = {}".format(task[:-1])
        elif re.match('[0-9]+$', task):
            wClause = " and WOT.woo_auto_key = :woo_auto_key" \
                      " and WOT.sequence = {}".format(task)
        else:
            fld['value'] = task
            fld['msgType'] = self.FLD_MSG_TYPE_NOT_FOUND
            fld['msg'] = "Entry has invalid format"
            return None

        q = """
                select WOT.woo_auto_key
                     , WOT.wot_auto_key
                     , WOT.sequence
                     , WTM.description
                     , nvl(WOS.description,   'Pending')
                  from wo_task          WOT
                     , wo_task_master   WTM
                     , wo_status        WOS
                 where WOT.wtm_auto_key = WTM.wtm_auto_key  -- all tasks have a masters
                   and WOT.wos_auto_key = WOS.wos_auto_key (+)
                   {wClause}
            """.format(wClause=wClause)
        row, fldNames = dbFetchOne(None, q, fs)
        if not row:
            fld['value'] = task
            fld['msgType'] = self.FLD_MSG_TYPE_NOT_FOUND
            fld['msg'] = "No task found"
            return None

        fs['woo_auto_key'], fs['wot_auto_key'], sequence, wot_desc, wot_status = row
        fld['value'] = sequence
        fld['msgType'] = self.FLD_MSG_TYPE_VALID
        fld['msg'] = "{}  [{}]".format(wot_desc, wot_status)
        return fs['wot_auto_key']


    @ajaxProcess
    def ajax_fld_task(self, request, frmName, fldName=None, msgType=FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, fldIdx, fld, task = self.processInitFld(request, frmName, fldName)

        self.generic_fld_task(request, fs, form, flds, fld, task)
        if fs['wot_auto_key']:
            self.gotWot(request, fs, form, flds, fld)
        return self.processFini(request, fs, form, msgType=msgType, msg=msg)


#---------------------------------------------------
# generic fields and field operations  stock
#---------------------------------------------------
    def createField_stock(self, value=None, msgType=FLD_MSG_TYPE_NONE, msg=None, group=None):
        return self.lineEdit('stock', 'Stock', 16, prompt="Stock Control Number", value=value, msgType=msgType, msg=msg, group=group)

    #only use if retrieving stock from the session context "stock.stmAutoKey"
    def appendStock(self, request, fs, form, msgType=FLD_MSG_TYPE_NONE, msg=None, group=None):
        flds = form['flds']
        fs['stm_auto_key'] = None
        fld = self.fldsAppend(False, flds, self.createField_stock(msgType=msgType, msg=msg, group=group))

        sessStm = request.session.get('stock.stmAutoKey')
        if not sessStm:
            return

        self.generic_fld_stock(request, fs, form, flds, fld, stm=sessStm)
        if fs['stm_auto_key']:
            del request.session['stock.stmAutoKey']   #clear passed values out of session
            self.gotStock(request, fs, form, flds, fld)


    def generic_fld_stock(self, request, fs, form, flds, fld, ctrl=None, stm=None):
        fs['stm_auto_key'] = None
        fs['crtlNo'] = None
        fs['ctrlId'] = None

        if stm:
            fs['stm_auto_key'] = stm
            wClause = """ and STM.stm_auto_key = :stm_auto_key """
        else:
            if re.match('[0-9]{12}$', ctrl):
                fs['ctrlNo'] = ctrl[:6]
                fs['ctrlId'] = ctrl[6:]
            elif re.match('[0-9]{1,6}[,. ][0-9]{1,6}$', ctrl):
                fs['ctrlNo'], fs['ctrlId'] = re.split('[,. ]', ctrl)
            else:
                fld['value'] = ctrl
                fld['msgType'] = self.FLD_MSG_TYPE_NOT_FOUND
                fld['msg'] = "Entry has invalid format"
                return None
            wClause = """ and STM.ctrl_number = :ctrlNo
                          and STM.ctrl_id     = :ctrlId """

        q = """ select STM.stm_auto_key
                     , STM.pnm_auto_key
                     , STM.ctrl_number
                     , STM.ctrl_id
                     , PNM.pn
                     , PNM.description
                     , STM.qty_oh
                     , STM.qty_available
                     , decode(PNM.serialized, 'F', '', STM.serial_number)
                     , nvl(PCC.condition_code, '-')
                  from stock                STM
                     , parts_master         PNM
                     , part_condition_codes PCC
                 where STM.pnm_auto_key = PNM.pnm_auto_key
                   and STM.pcc_auto_key = PCC.pcc_auto_key (+)
                   {wClause}
            """.format(wClause = wClause)
        row, fldNames = dbFetchOne(None, q, fs)
        if not row:
            fld['value'] = ctrl
            fld['msgType'] = self.FLD_MSG_TYPE_NOT_FOUND
            fld['msg'] = "Control number not found"
            return  None
        fs['stm_auto_key'], pnm_auto_key, fs['ctrlNo'], fs['ctrlId'], pn, partDesc, qtyOH, qtyAvail, serial, condCode = row

        fld['value'] = {True: ctrl, False: "{}.{}".format(fs['ctrlNo'], fs['ctrlId'])}[ctrl is not None]
        fld['msgType'] = self.FLD_MSG_TYPE_VALID
        fld['msg'] = '{} [{}]'.format( pn, {True: serial, False: condCode}[serial is not None and len(serial) > 0] )
        return fs['stm_auto_key']


    @ajaxProcess
    def ajax_fld_stock(self, request, frmName, fldName=None, msgType=FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, fldIdx, fld, ctrl = self.processInitFld(request, frmName, fldName)

        self.generic_fld_stock(request, fs, form, flds, fld, ctrl)
        if fs['stm_auto_key']:
            self.gotStock(request, fs, form, flds, fld)
        return self.processFini(request, fs, form, msgType=msgType, msg=msg)


#---------------------------------------------------
# generic fields and field operations  part
#---------------------------------------------------
    def createField_part(self, value=None, msgType=FLD_MSG_TYPE_NONE, msg=None, group=None):
        return self.lineEdit('part', 'Part', length=40, size=12, prompt="Part or Control", value=value, msgType=msgType, msg=msg, group=group)


    def generic_fld_part(self, request, fs, form, flds, fld, part):
        fs['pnm_auto_key'] = None
        fs['condCode'] = None   #might as well get PCC if user supplies a stock ctrlNo/Id

        # is it a control No/Id
        whereClause = None
        ctrlNo = None; ctrlId = None
        if re.match('[0-9]{12}$', part):
            ctrlNo = part[:6]
            ctrlId = part[6:]
        elif re.match('[0-9]{1,6}[,. ][0-9]{1,6}$', part):
            ctrlNo, ctrlId = re.split('[,. ]', part)

        if ctrlNo and ctrlId:
            q = """ select STM.pnm_auto_key
                         , nvl(PCC.condition_code, '-')
                      from stock STM
                         , part_condition_codes PCC
                     where STM.ctrl_number = :ctrlNo
                       and STM.pcc_auto_key = PCC.pcc_auto_key (+)
                       and STM.ctrl_id = :ctrlId  """
            row, fldNames = dbFetchOne(None, q, dict(ctrlNo=ctrlNo, ctrlId=ctrlId))
            if row:
                fs['pnm_auto_key'], fs['condCode'] = row
                whereClause = "PNM.pnm_auto_key = :pnm_auto_key"

        if not whereClause:
            whereClause = "rowNum = 1 "
            if re.match('[0-9]+$', part):    # it's all numeric
                whereClause += " and PNM.pn_stripped = '{0}' ".format(part)
            elif re.search('[\w]', part):      # it has at least one alphanumeric character
                whereClause += " and upper(PNM.pn_stripped) = upper('{0}') ".format(re.sub('[\W_]+', '', part))

        q = """ select PNM.pnm_auto_key                    as "pnm_auto_key"
                     , PNM.pn                              as "pn"
                     , PNM.description                     as "desc"
                     , nvl(PNM.serialized, 'F')            as "serialized"
                     , to_char(nvl(PNM.def_core_value, 0)) as "coreVal"
                     , nvl(PNM.shelf_life, 'F')            as "shelfLife"
                     , nvl(UOM.uom_code, 'EA')             as "uomCode"
                  from parts_master        PNM
                     , uom_codes           UOM
                  where PNM.uom_auto_key = UOM.uom_auto_key (+)
                    and ({whereClause})
            """.format(whereClause=whereClause)
        row, fldNames = dbFetchOne(None, q, fs)
        if not row:
            fld['value'] = part
            fld['msgType'] = self.FLD_MSG_TYPE_NOT_FOUND
            fld['msg'] = "Part not found"
            return None
        fs['pnm_auto_key'], partNum, partDesc, fs['serialized'], fs['coreVal'], fs['shelfLife'], fs['uomCode'] = row

        fld['value'] = partNum
        fld['msgType'] = self.FLD_MSG_TYPE_VALID
        fld['msg'] = partDesc
        return fs['pnm_auto_key']


    @ajaxProcess
    def ajax_fld_part(self, request, frmName, fldName=None, msgType=FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, fldIdx, fld, part = self.processInitFld(request, frmName, fldName)

        self.generic_fld_part(request, fs, form, flds, fld, part)
        if fs['pnm_auto_key']:
            self.gotPart(request, fs, form, flds, fld)
        return self.processFini(request, fs, form, msgType=msgType, msg=msg)


#---------------------------------------------------
# generic fields and field operations  conditionCode
#---------------------------------------------------
    def createField_conditionCode(self, value=None, listItems={}, msgType=FLD_MSG_TYPE_NONE, msg=None, group=None):
        return self.lookup('conditionCode', 'Condition', 10, prompt="Code", value=value, listItems=listItems, msgType=msgType, msg=msg)


    def appendConditionCode(self, request, fs, form, msgType=FLD_MSG_TYPE_NONE, msg=None, group=None):
        flds = form['flds']
        fs['pcc_auto_key'] = None
        fld = self.fldsAppend(False, flds, self.createField_conditionCode(listItems=self.get_partConditionCodes(fs), msgType=msgType, msg=msg, group=group))

        # a condCode may have been stuffed in the fs when an earlier field used a stock ctrlNo/Id
        if fs.get('condCode'):
            defCondCode = fs.get('condCode')
            del fs['condCode']
        else:
            defCondCode = request.session['defaultsProfile'].get('turnInCondition')
        if not defCondCode:
            return

        self.generic_fld_conditionCode(request, fs, form, flds, fld, defCondCode)
        if fs['pcc_auto_key']:
            self.gotConditionCode(request, fs, form, flds, fld)


    def generic_fld_conditionCode(self, request, fs, form, flds, fld, condCode):
        fs['pcc_auto_key'] = None

        listItem = None
        for rec in fld['listItems']:
            if condCode.upper() == rec['code'].upper():
                listItem = rec
                break

        if not listItem:
            fld['value'] = condCode
            fld['msgType'] = self.FLD_MSG_TYPE_NOT_FOUND
            fld['msg'] = "Condition code not found"
            return None
        fs['pcc_auto_key'] = listItem['seq']

        fld['value'] = listItem['code']
        fld['msgType'] = self.FLD_MSG_TYPE_VALID
        fld['msg'] = listItem['desc']
        return fs['pcc_auto_key']


    @ajaxProcess
    def ajax_fld_conditionCode(self, request, frmName, fldName=None, msgType=FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, fldIdx, fld, condCode = self.processInitFld(request, frmName, fldName)

        self.generic_fld_conditionCode(request, fs, form, flds, fld, condCode)
        if fs['pcc_auto_key']:
            self.gotConditionCode(request, fs, form, flds, fld)
        return self.processFini(request, fs, form, msgType=msgType, msg=msg)


    def get_partConditionCodes(self, fs):
        q = """ select pcc_auto_key     as "seq"
                     , condition_code   as "code"
                     , description      as "desc"
                 from part_condition_codes
                order by sequence
            """
        recs, fldNames = dbFetchAll(None, q, fs, asDict=True)
        if not recs:
            raise ServerDbError("AQC-0001", "No part condition codes were found.  Please relay this message to a system administrator.")
        return recs


#---------------------------------------------------
# generic fields and field operations  actions
#---------------------------------------------------
    def createField_restart(self, value="", msgType=FLD_MSG_TYPE_NONE, msg=None, group=None):
        return self.action('restart', 'Restart', icon='fa-refresh', value=value, msgType=msgType, msg=msg, group=group)

    def createField_done(self, value="", msgType=FLD_MSG_TYPE_NONE, msg=None, group=None):
        return self.action('done', 'Done', icon='fa-check-square-o', value=value, msgType=msgType, msg=msg, group=group)

    @ajaxProcess
    def ajax_fld_restart(self, request, frmName, fldName=None, msgType=FORM_MSG_TYPE_NONE, msg=None):
        uri = re.match('(.*)/', request.path).group(1)
        return jsonRedirect(dict(redirectTo=uri + '.html'), 'User requested "Restart"')

    @ajaxProcess
    def ajax_fld_done(self, request, frmName, fldName=None, msgType=FORM_MSG_TYPE_NONE, msg=None):
        uri = re.match('(.*)/', request.path).group(1)
        return jsonRedirect(dict(redirectTo=uri + '.html'), 'User done')
        #return jsonErrorResponse(dict(redirectTo=reverse('capture:menu')), 'User requested "Done"')


#---------------------------------------------------
# generic fields and field operations  misc
#---------------------------------------------------
    def createField_print(self, msgType=FLD_MSG_TYPE_NONE, msg=None, group=None):
        return self.action('print', 'Print', value="", icon='fa-print', msgType=msgType, msg=msg, group=group)

