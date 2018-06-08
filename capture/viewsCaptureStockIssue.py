"""
Copyright AdvanceQC LLC 2014,2015.  All rights reserved
"""

import re

from aqclib         import utils
from aqclib.dbUtils import dbConnection, dbQuote, dbFetchOne, dbFetchAll, dbExecute

from viewsCapture import ViewCapture, ajaxProcess


#############################################################################
# ViewCaptureStockIssue
#############################################################################
class ViewCaptureStockIssue(ViewCapture):

    @ajaxProcess
    def ajax_form(self, request, frmName, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None, bbox=None):
        fs, form = self.processInitForm(request, frmName)
        menuEntry = [ x for x in self.MENU_ITEMS if x['name'] == 'stockIssue' ][0]
        form = { 'name':  menuEntry['name']
               , 'label': menuEntry['label']
               , 'desc':  'Designate, reserve, and issue stock to work-orders and work-packages'
               , 'flds':  []
               }
        self.appendUser(request, fs, form)
        return self.processFini(request, fs, form, msgType=msgType, msg=msg)

    def createField_need(self, value=None, msgType=ViewCapture.FLD_MSG_TYPE_NONE, msg=None):
        return self.lineEdit('need', 'Remaining Need', 10, group=1, prompt="Amt still needed", value=value, msgType=msgType, msg=msg, w2cm=self.W2CM_DONT)

    def createField_reserve(self, value=None, msgType=ViewCapture.FLD_MSG_TYPE_NONE, msg=None):
        return self.lineEdit('reserve', 'Reserved', 10, group=1, prompt="Amt reserved", value=value, msgType=msgType, msg=msg, w2cm=self.W2CM_DONT)

    def createField_issue(self, value=None, msgType=ViewCapture.FLD_MSG_TYPE_NONE, msg=None):
        return self.lineEdit('issue', 'Issue', 10, group=1, prompt="Amt to issue", value=value, msgType=msgType, msg=msg, w2cm=self.W2CM_DONT)


    def gotUser(self, request, fs, form, flds, fld):
        self.fldsAppend(False, flds, self.createField_done())
        self.fldsAppend(False, flds, self.createField_woot())

    def gotWot(self, request, fs, form, flds, fld):
        self.fldsAppend(False, flds, self.createField_stock())


    @ajaxProcess
    def ajax_fld_stock(self, request, frmName, fldName=None, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, fldIdx, fld, ctrl = self.processInitFld(request, frmName, fldName)

        fs['crtlNo'] = None
        fs['ctrlId']  = None
        if re.match('[0-9]{12}$', ctrl):
            fs['ctrlNo'] = ctrl[:6]
            fs['ctrlId'] = ctrl[6:]
        elif re.match('[0-9]{1,6}[,. ][0-9]{1,6}$', ctrl):
            fs['ctrlNo'], fs['ctrlId'] = re.split('[,. ]', ctrl)
        else:
            fld['value'] = ctrl
            fld['msgType'] = self.FLD_MSG_TYPE_NOT_FOUND
            fld['msg'] = "Entry has invalid format"
            return self.processFini(request, fs, form)

        return self.getStockAndQty(request, fs, form, flds, fld, ctrl)


    def getStockAndQty(self, request, fs, form, flds, fld, ctrl, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
        q = """ select STM.stm_auto_key
                     , STM.pnm_auto_key
                     , PNM.pn
                     , PNM.description
                     , STM.qty_oh
                     , STM.qty_available
                     , decode(PNM.serialized, 'F', '', STM.serial_number)
                     , nvl(WOB.wob_auto_key, 0)   -- if zero then we'll have to insert into WOB rather than update
                     , nvl(WOB.qty_needed, 0)                           as totalNeed
                     , nvl(WOB.qty_needed, 0) - nvl(WOB.qty_issued, 0)  as remainingNeed
                     , nvl((select sum(qty_reserved) from stock_reservations where wob_auto_key = wob.wob_auto_key), 0)  as reserved
                  from stock              STM
                     , stock_reservations STR
                     , parts_master       PNM
                     , wo_bom             WOB
                 where STM.pnm_auto_key = PNM.pnm_auto_key
                   and STM.pnm_auto_key = WOB.pnm_auto_key (+)
                   and :wot_auto_key    = WOB.wot_auto_key (+)
                   and STM.ctrl_number = :ctrlNo and STM.ctrl_id = :ctrlId
                 order by WOB.wob_auto_key
            """
        row, fldNames = dbFetchOne(None, q, fs)
        if not row:
            fld['value'] = ctrl
            fld['msgType'] = self.FLD_MSG_TYPE_NOT_FOUND
            fld['msg'] = "Control number not found"
            return self.processFini(request, fs, form)
        fs['stm_auto_key'], fs['pnm_auto_key'], fs['pn'], partDesc, qtyOH, qtyAvail, serial, fs['wob_auto_key'], fs['qtyNeedTot'], fs['qtyNeed'], fs['qtyRes'] = row

        fld['value'] = ctrl
        fld['msgType'] = self.FLD_MSG_TYPE_VALID
        fld['msg'] = {True: serial, False: partDesc}[serial is not None and len(serial) > 0]
        self.fldsAppend(False, flds, self.createField_need(value=fs['qtyNeed'], msgType=self.FLD_MSG_TYPE_VALID, msg="On-hand: {}".format(qtyOH)))
        self.fldsAppend(False, flds, self.createField_reserve(value=fs['qtyRes'], msgType=self.FLD_MSG_TYPE_VALID, msg="Avail: {}".format(qtyAvail)))
        self.fldsAppend(False, flds, self.createField_issue())
        return self.processFini(request, fs, form, msgType=msgType, msg=msg)


    def reRun_getStockAndQty(self, request, fs, form, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
        idx = 0
        for f in form['flds']:
            if f['name'] == 'stock':
                break
            idx += 1
        form['flds'] = form['flds'][:idx+1]   #truncate fld array
        fld = form['flds'][idx]
        ctrl = fld['value']
        return self.getStockAndQty(request, fs, form, form['flds'], fld, ctrl, msgType=msgType, msg=msg)


    @ajaxProcess
    def ajax_fld_need(self, request, frmName, fldName=None, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, fldIdx, fld, qty = self.processInitFld(request, frmName, fldName)

        if not re.match('^\d*\.?\d*$', qty):  # doesn't allow negative numbers'
            fld['value'] = qty
            fld['msgType'] = self.FLD_MSG_TYPE_INVALID
            fld['msg'] = "Invalid number"
            return self.processFini(request, fs, form)

        self.processQtyChange(fs, qtyNeed=qty)
        lastIdx = self.getFldIndex(flds, 'stock')
        del flds[lastIdx+1:]
        #return self.reRun_getStockAndQty(request, fs, form, msgType=self.FORM_MSG_TYPE_TX_COMPLETE, msg="Qty needed updated")
        return self.processFini(request, fs, form, msgType=self.FORM_MSG_TYPE_TX_COMPLETE, msg="Qty needed updated")


    @ajaxProcess
    def ajax_fld_reserve(self, request, frmName, fldName=None, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, fldIdx, fld, qty = self.processInitFld(request, frmName, fldName)

        if not re.match('^\d*\.?\d*$', qty):  # doesn't allow negative numbers
            fld['value'] = qty
            fld['msgType'] = self.FLD_MSG_TYPE_INVALID
            fld['msg'] = "Invalid number"
            return self.processFini(request, fs, form)

        self.processQtyChange(fs, qtyRes=qty)
        lastIdx = self.getFldIndex(flds, 'stock')
        del flds[lastIdx+1:]
        #return self.reRun_getStockAndQty(request, fs, form, msgType=self.FORM_MSG_TYPE_TX_COMPLETE, msg="Stock Reserved")
        return self.processFini(request, fs, form, msgType=self.FORM_MSG_TYPE_TX_COMPLETE, msg="Stock Reserved")


    @ajaxProcess
    def ajax_fld_issue(self, request, frmName, fldName=None, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, fldIdx, fld, qty = self.processInitFld(request, frmName, fldName)

        if not re.match('^\d*\.?\d*$', qty):  # doesn't allow negative numbers
            fld['value'] = qty
            fld['msgType'] = self.FLD_MSG_TYPE_INVALID
            fld['msg'] = "Invalid number"
            return self.processFini(request, fs, form)

        self.processQtyChange(fs, qtyIss=qty)
        lastIdx = self.getFldIndex(flds, 'stock')
        del flds[lastIdx+1:]
        #return self.reRun_getStockAndQty(request, fs, form, msgType=self.FORM_MSG_TYPE_TX_COMPLETE, msg="Stock Issued")
        return self.processFini(request, fs, form, msgType=self.FORM_MSG_TYPE_TX_COMPLETE, msg="Stock Issued")


    def processQtyChange(self, fs, qtyNeed=None, qtyRes=None, qtyIss=None):
        q = """ declare
                    cur  QC_UTL_PKG.CURSOR_TYPE;
                    foo  QC_UTL_PKG.CURSOR_TYPE;
                    req_qtyNeed   number := :qtyNeed;
                    req_qtyRes    number := :qtyRes;
                    req_qtyIss    number := :qtyIss;
                    cur_qtyNeed   number;
                    cur_qtyRes    number;
                    cur_qtyIss    number;
                    l_sysur       number := :sysur_auto_key;
                    l_woo  number := :woo_auto_key;
                    l_wot  number := :wot_auto_key;
                    l_ctrlNo number := :ctrlNo;
                    l_ctrlId number := :ctrlId;
                    l_wob  number;
                    l_pnm  number;
                    l_pcc  number;
                    l_stm  number;
                    l_str  number;
                    l_stm_parent number := null;
                begin
                    aqcCaptureQC.authUserSession(:user_id);
                    -- get the part
                    select pnm_auto_key, pcc_auto_key
                      into l_pnm,        l_pcc
                      from stock
                     where ctrl_number = l_ctrlNo and ctrl_id = l_ctrlId
                       for update;
                    --
                    -- get the WOB
                    open cur for
                        select wob_auto_key, qty_needed, qty_reserved, qty_issued
                          from wo_bom
                         where pnm_auto_key = l_pnm
                           and wot_auto_key = l_wot
                         order by wob_auto_key       --yes there can be multiple wob records for same PNM and WOT!
                           for update;
                    fetch cur into l_wob, cur_qtyNeed, cur_qtyRes, cur_qtyIss;
                    if cur{percentNotFound} then
                        l_wob := NULL;
                        cur_qtyNeed := 0;
                        cur_qtyRes := 0;
                        cur_qtyIss := 0;
                    end if;
                    close cur;
                    --
                    -- change net req_qtyNeed to absolute
                    if req_qtyNeed is not null then  --we trying to change the 'net' need
                        req_qtyNeed := req_qtyNeed + cur_qtyIss;
                    end if;
                    --
                    -- figure out what needs to change
                    if req_qtyIss is not null then        --are we trying to issue
                        if req_qtyIss > cur_qtyRes then   --is issue amount larger than the actual reservation
                            req_qtyRes := req_qtyIss;
                        end if;
                    end if;
                    if req_qtyRes is not null then                     --are we trying to reserve
                        if req_qtyRes > cur_qtyNeed - cur_qtyIss then  --is reservation larger then actual remaining need
                            req_qtyNeed := req_qtyRes + cur_qtyIss;
                        end if;
                    end if;
                    if req_qtyNeed is not null then                                     --are we trying to change need
                        if req_qtyNeed - cur_qtyIss < nvl(req_qtyRes, cur_qtyRes) then  --are we requesting less than the reserved amount
                            raise_application_error( -20001, 'Cannot reduce need below reserved amount.  Change reservation first.' );
                        end if;
                    end if;
                    --
                    -- is need qty changing
                    if req_qtyNeed is not null then
                        if l_wob is not null then
                            update wo_bom
                               set qty_needed = req_qtyNeed
                                 , sysur_auto_key = l_sysur
                             where wob_auto_key = l_wob;
                        else
                            select g_wob_auto_key.nextval into l_wob from dual;
                            insert into wo_bom (
                                wob_auto_key, pnm_auto_key, pcc_auto_key, qty_needed,  wot_auto_key, woo_auto_key, manual_qty, activity,     sysur_auto_key
                            ) values (
                                l_wob,        l_pnm,        l_pcc,        req_qtyNeed, l_wot,        l_woo,        'T',        'Consumable', l_sysur
                            );
                        end if;
                    end if;
                    --
                    -- get the stm_auto_key
                    select STM.stm_auto_key
                      into l_stm
                      from stock STM
                     where STM.ctrl_number = l_ctrlNo and STM.ctrl_id = l_ctrlId
                       for update;
                    --
                    -- get current str_auto_key if it exists
                    open cur for
                        select STR.str_auto_key
                          from stock_reservations STR
                         where STR.stm_auto_key = l_stm
                           and STR.wob_auto_key = l_wob
                           for update;
                    fetch cur into l_str;
                    if cur{percentNotFound} then
                        l_str := NULL;
                    end if;
                    close cur;
                    --
                    -- is reservation qty changing
                    if req_qtyRes is not null then
                        if l_str is not null then
                            if req_qtyRes = 0 then
                                delete from stock_reservations
                                where str_auto_key = l_str;
                            else
                                update stock_reservations
                                   set qty_reserved  = req_qtyRes
                                     , sysur_auto_key = l_sysur
                                 where str_auto_key = l_str;
                            end if;
                        else
                            select g_str_auto_key.nextval into l_str from dual;
                            insert into stock_reservations (
                                str_auto_key, stm_auto_key, /*woo_auto_key,*/ wob_auto_key, qty_reserved, date_scan, sysur_auto_key
                            ) values (
                                l_str,        l_stm,        /*l_woo,       */ l_wob,        req_qtyRes,   sysdate,   l_sysur
                            );
                        end if;
                    end if;
                    --
                    -- is issue qty changing
                    if req_qtyIss is not null then
                        select min(stm_auto_key)
                          into l_stm_parent
                          from stock_reservations
                         where woo_auto_key = l_woo;
                        --
                        foo := QC_IC_PKG2.SPI_ISSUE_RESERVATION( p_str => l_str,
                                                                 p_wot => null,
                                                                 p_qty => req_qtyIss,
                                                                 p_tir => null,
                                                                 p_stm_parent => l_stm_parent,
                                                                 p_sysur_issued_to => l_sysur,
                                                                 p_commit => 'N' );
                    end if;
                    --
                    commit;
                end;
            """.format( percentNotFound = '%NOTFOUND' )
        rc = dbExecute(None, q, dict( fs.items() + dict(qtyNeed=qtyNeed, qtyRes=qtyRes, qtyIss=qtyIss).items() ))
