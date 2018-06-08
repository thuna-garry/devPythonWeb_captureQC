"""
Copyright AdvanceQC LLC 2014,2015.  All rights reserved
"""

import os
import re
import socket
import string

from aqclib         import utils
from aqclib.dbUtils import dbConnection, dbQuote, dbFetchOne, dbFetchAll, dbExecute

from viewUtils    import jsonRedirect
from viewsCapture import ViewCapture, ajaxProcess


#############################################################################
# ViewCaptureStockLabel
#############################################################################
class ViewCaptureStockLabel(ViewCapture):

    @ajaxProcess
    def ajax_form(self, request, frmName, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None, bbox=None):
        fs, form = self.processInitForm(request, frmName)
        menuEntry = [ x for x in self.MENU_ITEMS if x['name'] == 'stockLabel' ][0]
        form = { 'name':  menuEntry['name']
               , 'label': menuEntry['label']
               , 'desc':  'Receive parts into inventory via a work-order.'
               , 'flds':  []
               }
        self.appendStock(request, fs, form)
        return self.processFini(request, fs, form, msgType=msgType, msg=msg)

    def createField_printer(self, value=None, msgType=ViewCapture.FLD_MSG_TYPE_NONE, msg=None):
        return self.lineEdit('printer', 'Printer', length=40, size=10, value=value, msgType=msgType, msg=msg)

    def createField_copies(self, msgType=ViewCapture.FLD_MSG_TYPE_NONE, msg=None):
        return self.lineEdit('copies', 'Copies', 5, value=1, msgType=msgType, msg=msg)


    def gotStock(self, request, fs, form, flds, fld):
        self.fldsAppend(False, flds, self.createField_done())
        self.appendPrinter(request, fs, form)


    def appendPrinter(self, request, fs, form):
        flds = form['flds']
        fld = self.fldsAppend(False, flds, self.createField_printer())

        fs['printerIp'] = None
        defPrinter = request.session['conUser'].get('defaultPrinter')
        if not defPrinter:
            return

        self.check_printer(request, fs, form, flds, fld, defPrinter)
        if fs['printerIp']:
            self.gotPrinter(request, fs, form, flds, fld)


    def check_printer(self, request, fs, form, flds, fld, printer=None):
        fs['printerIp'] = None
        host = None
        ip = None
        fldMsg = "{}"
        try:
            if re.match("^(?:(?:25[0-5]|2[0-4][0-9]|[:01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", printer):
                ip = '.'.join([ str(int(x)) for x in printer.split('.') ])  #strip leading zeros
                host = socket.gethostbyaddr(ip)[0]
                fldMsg = fldMsg.format(host)
            else:
                host = printer
                ip = socket.gethostbyname(host)
                fldMsg = fldMsg.format(ip)
        except socket.gaierror as e:
            fld['value'] = printer
            fld['msgType'] = self.FLD_MSG_TYPE_INVALID
            fld['msg'] = "Invalid name or addr"
            return None

        fs['printerIp'] = ip
        fld['value'] = printer
        fld['msgType'] = self.FLD_MSG_TYPE_VALID
        fld['msg'] = fldMsg
        return fs['printerIp']


    @ajaxProcess
    def ajax_fld_printer(self, request, frmName, fldName=None, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, fldIdx, fld, printer = self.processInitFld(request, frmName, fldName)

        if self.check_printer(request, fs, form, flds, fld, printer):
            self.gotPrinter(request, fs, form, flds, fld)
        return self.processFini(request, fs, form, msgType=msgType, msg=msg)


    def gotPrinter(self, request, fs, form, flds, fld):
        self.fldsAppend(False, flds, self.createField_copies())
        self.fldsAppend(False, flds, self.createField_print())


    @ajaxProcess
    def ajax_fld_copies(self, request, frmName, fldName=None, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, fldIdx, fld, copies = self.processInitFld(request, frmName, fldName)

        try:
            fld['value'] = abs(int(float(copies)))
        except ValueError:
            fld['value'] = copies
            fld['msgType'] = self.FLD_MSG_TYPE_NOT_FOUND
            fld['msg'] = "Not a valid number"
            return self.processFini(request, fs, form, msgType=msgType, msg=msg)

        self.fldsAppend(False, flds, self.createField_print())
        return self.processFini(request, fs, form, msgType=msgType, msg=msg)


    @ajaxProcess
    def ajax_fld_print(self, request, frmName, fldName=None, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, fldIdx, fld, data = self.processInitFld(request, frmName, fldName)

        # get the label details
        q = """ select STM.ctrl_number                       as "ctrlNo"
                     , STM.ctrl_id                           as "ctrlId"
                     , STM.qty_oh                            as "qty"
                     , STM.serial_number                     as "serial"
                     , STM.exp_date                          as "expire"
                     , STM.receiver_number                   as "receiver"
                     , to_char(STM.rec_date, 'yyyy-mm-dd')   as "received"
                     , PNM.pn                                as "partNo"
                     , PNM.description                       as "partDesc"
                     , nvl(PCC.condition_code, '')           as "cond"
                     , nvl(WHS.warehouse_code, '')           as "wh"
                     , nvl(LOC.location_code, '')            as "loc"
                     , nvl(POH.po_number, '')                as "po"
                     , nvl(UOM.uom_code, '')                 as "uom"
                  from stock                  STM
                     , parts_master           PNM
                     , part_condition_codes   PCC
                     , warehouse              WHS
                     , location               LOC
                     , uom_codes              UOM
                     , po_detail              POD
                     , po_header              POH
                 where STM.pnm_auto_key = PNM.pnm_auto_key
                   and STM.pcc_auto_key = PCC.pcc_auto_key (+)
                   and STM.whs_auto_key = WHS.whs_auto_key (+)
                   and STM.loc_auto_key = LOC.loc_auto_key (+)
                   and PNM.uom_auto_key = UOM.uom_auto_key (+)
                   and STM.pod_auto_key = POD.pod_auto_key (+)
                   and POD.poh_auto_key = POH.poh_auto_key (+)
                   and STM.stm_auto_key = :stm_auto_key
            """
        rec, fldNames = dbFetchOne(None, q, fs, asDict=True)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # open socket to printer:9100
            s.connect( (fs['printerIp'], 9100) )

            # loop through for each copy
            copies = flds[self.getFldIndex(flds, 'copies')]['value']
            fname = os.path.join(utils.globalDict['path.mediaRoot'], utils.globalDict['stockLabel'])
            for count in range(copies):
                with open(fname, 'r+') as f:
                    foundStart = False
                    for line in f:
                        if not foundStart:
                            if not line.startswith('^XA'):
                                continue
                            foundStart = True

                        # do substitutions
                        if line.startswith('^'):
                            line = line.replace('*000000000000*', "*{:06d}{:06d}*".format(rec['ctrlNo'], rec['ctrlId']) )
                            line = line.replace('[ctrlNo]',   str(rec['ctrlNo']))
                            line = line.replace('[ctrlId]',   str(rec['ctrlId']))
                            line = line.replace('[partNo]',   str(rec['partNo']))
                            line = line.replace('[partDesc]', str(rec['partDesc']))
                            line = line.replace('[cond]',     str(rec['cond']))
                            line = line.replace('[serial]',   str(rec['serial']))
                            line = line.replace('[expire]',   str(rec['expire']))
                            line = line.replace('[po]',       str(rec['po']))
                            line = line.replace('[receiver]', str(rec['receiver']))
                            line = line.replace('[received]', str(rec['received']))
                            line = line.replace('[wh]',       str(rec['wh']))
                            line = line.replace('[loc]',      str(rec['loc']))
                            line = line.replace('[uom]',      str(rec['uom']))
                            line = line.replace('*qty*',      "*{}*".format(rec['qty']) )

                        # write to printer socket
                        s.send(line)

        except IOError as e:
            return self.processFini(request, fs, form, msgType=ViewCapture.FORM_MSG_TYPE_WARNING, msg="Print operation failed")
        finally:
            s.close()
        return self.processFini(request, fs, form, msgType=ViewCapture.FORM_MSG_TYPE_TX_COMPLETE, msg="Label Sent")


    @ajaxProcess
    def ajax_fld_done(self, request, frmName, fldName=None, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
        uri = re.match('(.*)/', request.path).group(1)
        return jsonRedirect(dict(redirectTo=request.session['referer']), 'User done')
