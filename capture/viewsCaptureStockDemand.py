"""
Copyright AdvanceQC LLC 2014,2015.  All rights reserved
"""

import re

from aqclib         import utils
from aqclib.dbUtils import dbConnection, dbQuote, dbFetchOne, dbFetchAll, dbExecute

from viewsCapture import ViewCapture, ajaxProcess


#############################################################################
# ViewCaptureStockDemand
#############################################################################
class ViewCaptureStockDemand(ViewCapture):

    @ajaxProcess
    def ajax_form(self, request, frmName, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None, bbox=None):
        fs, form = self.processInitForm(request, frmName)
        menuEntry = [ x for x in self.MENU_ITEMS if x['name'] == 'stockDemand' ][0]
        form = { 'name':  menuEntry['name']
               , 'label': menuEntry['label']
               , 'desc':  'Add or edit part demands for a work-order'
               , 'flds':  []
               }
        self.appendUser(request, fs, form)
        return self.processFini(request, fs, form, msgType=msgType, msg=msg)

    def createField_wobInfo(self, value=None, msgType=ViewCapture.FLD_MSG_TYPE_NONE, msg=None):
         return self.display('wobInfo', '', value=value, msgType=msgType, msg=msg)

    def createField_need(self, value=None, msgType=ViewCapture.FLD_MSG_TYPE_NONE, msg=None):
        return self.lineEdit('need', 'Total Need', 10, group=1, prompt="Amt needed", value=value, msgType=msgType, msg=msg, w2cm=self.W2CM_DONT)


    def gotUser(self, request, fs, form, flds, fld):
        self.fldsAppend(False, flds, self.createField_done())
        self.fldsAppend(False, flds, self.createField_woot())


    def gotWot(self, request, fs, form, flds, fld):
        self.fldsAppend(False, flds, self.createField_part())


    def gotPart(self, request, fs, form, flds, fld):
        self.appendConditionCode(request, fs, form)


    def gotConditionCode(self, request, fs, form, flds, fld):
        self.appendWobInfo(request, fs, form)
        self.fldsAppend(False, flds, self.createField_need(msgType=self.FLD_MSG_TYPE_NONE, msg=fs['uomCode']))


    def appendWobInfo(self, request, fs, form):
        flds = form['flds']
        fld = self.fldsAppend(False, flds, self.createField_wobInfo())

        #lets get some useful data
        q = """ select nvl((select sum(qty_oh)
                              from stock
                             where pnm_auto_key = :pnm_auto_key
                               and pcc_auto_key = :pcc_auto_key
                           ), 0)                                                        as "qtyOH"
                     , nvl((select sum(qty_available)
                              from stock
                             where pnm_auto_key = :pnm_auto_key
                               and pcc_auto_key = :pcc_auto_key
                           ), 0)                                                        as "qtyAvail"
                     , nvl(WOB.qty_needed, 0)                                           as "totalNeed"
                     , nvl(WOB.qty_needed, 0) - nvl(WOB.qty_issued, 0)                  as "remainingNeed"
                     , nvl((select sum(qty_reserved)
                              from stock_reservations
                             where wob_auto_key = WOB.wob_auto_key
                           ), 0)                                                        as "reserved"
                     , nvl((SELECT sum( CASE WHEN STI.ti_type = 'I' THEN STI.qty END)
                              FROM stock_ti STI
                             WHERE STI.wob_auto_key = WOB.wob_auto_key
                           ), 0)                                                        as "issued"
                     , nvl((SELECT sum( CASE WHEN STI.ti_type = 'T' THEN STI.qty END)
                              FROM stock_ti STI
                             WHERE STI.wob_auto_key = WOB.wob_auto_key
                           ), 0)                                                        as "turnedIn"
                  from dual
                     , wo_bom  WOB
                 where dual.dummy != WOB.activity (+)  --force one rec
                   and :pnm_auto_key = WOB.pnm_auto_key (+)
                   and :pcc_auto_key = WOB.pcc_auto_key (+)
                   and :wot_auto_key = WOB.wot_auto_key (+)
            """
        row, fldNames = dbFetchOne(None, q, fs)
        if not row:
            fld['value'] = ""
            fld['msgType'] = self.FLD_MSG_TYPE_ERROR
            fld['msg'] = "Error: could not retrieve BOM stats."
            return
        qtyOH, qtyAvail, totalNeed, remainingNeed, reserved, issued, turnedIn = row

        fld['value'] = """ On-Hand=<b>{qtyOH}</b> &nbsp;&nbsp;
                           Reserved=<b>{reserved}</b> &nbsp;&nbsp;
                           Available=<b>{qtyAvail}</b>
                           <br>
                           Need=<b>{totalNeed}</b> &nbsp;&nbsp;
                           Issued=<b>{issued}</b> &nbsp;&nbsp;
                           TurnedIn=<b>{turnedIn}</b>
                       """.format( qtyOH=qtyOH
                                 , qtyAvail=qtyAvail
                                 , totalNeed=totalNeed
                                 , reserved=reserved
                                 , issued=issued
                                 , turnedIn=turnedIn
                                 )
        fld['msgType'] = self.FLD_MSG_TYPE_NONE
        fld['msg'] = ""
        return


    @ajaxProcess
    def ajax_fld_need(self, request, frmName, fldName=None, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, fldIdx, fld, qty = self.processInitFld(request, frmName, fldName)

        if not re.match('^\d*\.?\d*$', qty):  # doesn't allow negative numbers'
            fld['value'] = qty
            fld['msgType'] = self.FLD_MSG_TYPE_INVALID
            fld['msg'] = "Invalid number"
            return self.processFini(request, fs, form)

        self.processQtyChange(fs, qty)
        lastIdx = self.getFldIndex(flds, 'part')
        del flds[lastIdx+1:]
        return self.processFini(request, fs, form, msgType=self.FORM_MSG_TYPE_TX_COMPLETE, msg="Qty needed updated")


    def processQtyChange(self, fs, qtyNeed):
        q = """ declare
                    cur  QC_UTL_PKG.CURSOR_TYPE;
                    req_qtyNeed   number := :qtyNeed;
                    l_sysur       number := :sysur_auto_key;
                    l_woo  number := :woo_auto_key;
                    l_wot  number := :wot_auto_key;
                    l_pnm  number := :pnm_auto_key;
                    l_pcc  number := :pcc_auto_key;
                    l_wob  number;
                begin
                    aqcCaptureQC.authUserSession(:user_id);
                    --
                    -- get the WOB
                    open cur for
                        select wob_auto_key
                          from wo_bom
                         where pnm_auto_key = l_pnm
                           and wot_auto_key = l_wot
                         order by wob_auto_key       --yes there can be multiple wob records for same PNM and WOT!
                           for update;
                    fetch cur into l_wob;
                    if cur{percentNotFound} then
                        l_wob := NULL;
                    end if;
                    close cur;
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
                    commit;
                end;
            """.format( percentNotFound = '%NOTFOUND' )
        rc = dbExecute(None, q, dict( fs.items() + dict(qtyNeed=qtyNeed).items() ))
