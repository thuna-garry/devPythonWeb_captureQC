"""
Copyright AdvanceQC LLC 2014,2015.  All rights reserved
"""

import re
import datetime
import calendar

from django.core.urlresolvers import reverse

from aqclib         import utils
from aqclib.dbUtils import dbConnection, dbQuote, dbFetchOne, dbFetchAll, dbExecute
from aqclib.dbUtils import ServerDbError

from viewUtils    import jsonRedirect
from viewsCapture import ViewCapture, ajaxProcess


#############################################################################
# ViewCaptureStockTurnIn
#############################################################################
class ViewCaptureStockTurnIn(ViewCapture):

    @ajaxProcess
    def ajax_form(self, request, frmName, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None, bbox=None):
        fs, form = self.processInitForm(request, frmName)
        menuEntry = [ x for x in self.MENU_ITEMS if x['name'] == 'stockTurnIn' ][0]
        form = { 'name':  menuEntry['name']
               , 'label': menuEntry['label']
               , 'desc':  'Receive parts into inventory via a work-order.'
               , 'flds':  []
               }
        self.appendUser(request, fs, form)
        return self.processFini(request, fs, form, msgType=msgType, msg=msg)

    def createField_warehouse(self, value=None, listItems={}, msgType=ViewCapture.FLD_MSG_TYPE_NONE, msg=None):
        return self.lookup('warehouse', 'Warehouse', 10, value=value, listItems=listItems, msgType=msgType, msg=msg, group=1)

    def createField_location(self, value=None, msgType=ViewCapture.FLD_MSG_TYPE_NONE, msg=None):
        return self.lineEdit('location', 'Location', 10, value=value, msgType=msgType, msg=msg, group=1)

    def createField_unitCost(self, value=None, msgType=ViewCapture.FLD_MSG_TYPE_NONE, msg=None):
        return self.lineEdit('unitCost', 'Unit Cost', 10, value=value, msgType=msgType, msg=msg, group=2)

    def createField_serial(self, value=None, msgType=ViewCapture.FLD_MSG_TYPE_NONE, msg=None):
        return self.lineEdit('serial', 'Serial', 40, size=12, value=value, msgType=msgType, msg=msg, group=2)

    def createField_qty(self, value=None, msgType=ViewCapture.FLD_MSG_TYPE_NONE, msg=None):
        return self.lineEdit('qty', 'Qty', 10, value=value, msgType=msgType, msg=msg, group=2)

    def createField_expiry(self, value=None, msgType=ViewCapture.FLD_MSG_TYPE_NONE, msg=None):
        if not value:
            n = datetime.datetime.today()
            value = dict( y=n.year, m=n.month, d=n.day )
        return self.dateEdit('expiry', 'Expiry', value=value, msgType=msgType, msg=msg, group=2)

    def createField_notes(self, value=None, msgType=ViewCapture.FLD_MSG_TYPE_NONE, msg=None):
        return self.textEdit('notes', 'Notes', 2000, prompt="Stock notes", value=value, msgType=msgType, msg=msg, group=2)

    def createField_save(self, msgType=ViewCapture.FLD_MSG_TYPE_NONE, msg=None):
        return self.action('save', 'Save', icon='fa-save', msgType=msgType, msg=msg, group=2)


    def gotUser(self, request, fs, form, flds, fld):
        self.fldsAppend(False, flds, self.createField_done())
        self.fldsAppend(False, flds, self.createField_woot())


    def gotWot(self, request, fs, form, flds, fld):
        self.fldsAppend(False, flds, self.createField_part())


    def gotPart(self, request, fs, form, flds, fld):
        self.appendConditionCode(request, fs, form)


    def gotConditionCode(self, request, fs, form, flds, fld):
        self.appendWarehouse(request, fs, form)


    # @ajaxProcess
    # def ajax_fld_part(self, request, frmName, fldName=None, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
    #     fs, form, flds, fldIdx, fld, part = self.processInitFld(request, frmName, fldName)
    #
    #     self.generic_fld_part(request, fs, form, flds, fld, part)
    #     if fs['pnm_auto_key']:
    #         self.appendConditionCode(request, fs, flds)
    #     return self.processFini(request, fs, form, msgType=msgType, msg=msg)


    # def appendConditionCode(self, request, fs, flds):
    #     fs['pcc_auto_key'] = None
    #
    #     listItems = self.get_partConditionCodes(fs)
    #     defCondCode = request.session['defaultsProfile'].get('turnInCondition')
    #     defCondDesc = ""
    #     if defCondCode:    #see if we can find the auto_key for the default
    #         for item in listItems:
    #             if item['code'].upper() == defCondCode.upper():
    #                 fs['pcc_auto_key'] = item['seq']
    #                 defCondCode = item['code']
    #                 defCondDesc = item['desc']
    #                 break
    #     self.fldsAppend(False, flds, self.createField_condition(value=defCondCode, listItems=listItems, msgType=self.FLD_MSG_TYPE_VALID, msg=defCondDesc))
    #     if fs['pcc_auto_key']:
    #         self.appendWarehouse(request, fs, flds)
    #
    #
    # @ajaxProcess
    # def ajax_fld_condition(self, request, frmName, fldName=None, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
    #     fs, form, flds, fldIdx, fld, condCode = self.processInitFld(request, frmName, fldName)
    #
    #     fs['pcc_auto_key'] = None
    #     listItem = None
    #     for rec in fld['listItems']:
    #         if condCode.upper() == rec['code'].upper():
    #             listItem = rec
    #             break
    #
    #     if not listItem:
    #         fld['value'] = condCode
    #         fld['msgType'] = self.FLD_MSG_TYPE_NOT_FOUND
    #         fld['msg'] = "Condition code not found"
    #         return self.processFini(request, fs, form, msgType=msgType, msg=msg)
    #     fs['pcc_auto_key'] = listItem['seq']
    #
    #     fld['value'] = listItem['code']
    #     fld['msgType'] = self.FLD_MSG_TYPE_VALID
    #     fld['msg'] = listItem['desc']
    #     self.appendWarehouse(request, fs, flds)
    #     return self.processFini(request, fs, form, msgType=msgType, msg=msg)


    def appendWarehouse(self, request, fs, form):
        flds = form['flds']
        fs['whs_auto_key'] = None

        listItems = self.get_getWarehouseCodes(fs)
        defWarehouseCode = request.session['conUser'].get('defaultWarehouse')
        defWarehouseDesc = ""
        if defWarehouseCode:    #see if we can find the auto_key for the default
            for item in listItems:
                if item['code'].upper() == defWarehouseCode.upper():
                    fs['whs_auto_key'] = item['seq']
                    defWarehouseCode = item['code']
                    defWarehouseDesc = item['desc']
                    break
        self.fldsAppend(False, flds, self.createField_warehouse(value=defWarehouseCode, listItems=listItems, msgType=self.FLD_MSG_TYPE_VALID, msg=defWarehouseDesc))
        self.fldsAppend(False, flds, self.createField_location())


    @ajaxProcess
    def ajax_fld_warehouse(self, request, frmName, fldName=None, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, fldIdx, fld, whCode = self.processInitFld(request, frmName, fldName)

        fs['whs_auto_key'] = None
        fs['loc_auto_key'] = None
        flds[fldIdx+0]['value'] = "";  flds[fldIdx+0]['msgType'] = self.FLD_MSG_TYPE_NONE; flds[fldIdx+0]['msg'] = "";
        flds[fldIdx+1]['value'] = "";  flds[fldIdx+1]['msgType'] = self.FLD_MSG_TYPE_NONE; flds[fldIdx+1]['msg'] = "";

        if whCode.strip():
            q = """ select whs_auto_key     as "seq"
                         , warehouse_code   as "code"
                         , description      as "desc"
                     from warehouse
                    where upper(warehouse_code) = upper(:whCode)
                """
            row, fldNames = dbFetchOne(None, q, dict(whCode=whCode))
            if not row:
                fld['value'] = whCode
                fld['msgType'] = self.FLD_MSG_TYPE_NOT_FOUND
                fld['msg'] = "Warehouse code not found"
                return self.processFini(request, fs, form)
            fs['whs_auto_key'], code, desc = row

            fld['value'] = code
            fld['msgType'] = self.FLD_MSG_TYPE_VALID
            fld['msg'] = desc
        return self.processFini(request, fs, form, msgType=msgType, msg=msg)


    @ajaxProcess
    def ajax_fld_location(self, request, frmName, fldName=None, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, fldIdx, fld, locCode = self.processInitFld(request, frmName, fldName)

        fs['loc_auto_key'] = None
        if fs['whs_auto_key'] and utils.globalDict['whLocCheck']:
            q = """ select LOC.loc_auto_key     as "seq"
                         , LOC.location_code    as "code"
                         , LOC.description      as "desc"
                     from location             LOC
                        , warehouse_locations  WLC
                    where WLC.loc_auto_key = LOC.loc_auto_key
                      and WLC.whs_auto_key = :whs_auto_key
                      and upper(location_code) = upper(:locCode)
                """
        else:
            q = """ select loc_auto_key     as "seq"
                         , location_code    as "code"
                         , description      as "desc"
                     from location
                    where upper(location_code) = upper(:locCode)
                """
        row, fldNames = dbFetchOne(None, q, dict(fs.items() + dict(locCode=locCode).items()))
        if not row:
            fld['value'] = locCode
            fld['msgType'] = self.FLD_MSG_TYPE_NOT_FOUND
            fld['msg'] = "Location code not found"
            return self.processFini(request, fs, form)
        fs['loc_auto_key'], code, desc = row

        fld['value'] = code
        fld['msgType'] = self.FLD_MSG_TYPE_VALID
        fld['msg'] = desc
        self.appendUnitCost(request, fs, flds)
        return self.processFini(request, fs, form, msgType=msgType, msg=msg)


    def appendUnitCost(self, request, fs, flds):
        fs['unitCost'] = '{:.2f}'.format(float(fs['coreVal']))

        fld = self.fldsAppend(False, flds, self.createField_unitCost())
        fld['value'] = fs['unitCost']
        fld['msgType'] = self.FLD_MSG_TYPE_NONE
        fld['msg'] = fs['uomCode']

        self.appendSerial(request, fs, flds)
        self.showSave(flds)


    @ajaxProcess
    def ajax_fld_unitCost(self, request, frmName, fldName=None, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, fldIdx, fld, unitCost = self.processInitFld(request, frmName, fldName)

        if not re.match(r'^(\d*[.])?\d+$', unitCost):
            fld['value'] = unitCost
            fld['msgType'] = self.FLD_MSG_TYPE_INVALID
            fld['msg'] = 'Invalid number'
            self.showSave(flds)
            return self.processFini(request, fs, form)

        fs['unitCost'] = "{:.2f}".format(float(unitCost))
        fld['value'] = fs['unitCost']
        fld['msgType'] = self.FLD_MSG_TYPE_NONE
        fld['msg'] = fs['uomCode']
        self.showSave(flds)
        return self.processFini(request, fs, form, msgType=msgType, msg=msg)


    def appendSerial(self, request, fs, flds):
        fs['serial'] = None
        if fs['serialized'] == 'T':
            self.fldsAppend(False, flds, self.createField_serial())
        self.appendExpiry(request, fs, flds)
        self.showSave(flds)


    @ajaxProcess
    def ajax_fld_serial(self, request, frmName, fldName=None, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, fldIdx, fld, serial = self.processInitFld(request, frmName, fldName)

        if not re.match(r'^\w[,.\w:/-]*$', serial):
            fld['value'] = serial
            fld['msgType'] = self.FLD_MSG_TYPE_INVALID
            fld['msg'] = 'Invalid format'
            self.showSave(flds)
            return self.processFini(request, fs, form)

        fs['serial'] = serial
        fld['value'] = serial
        fld['msgType'] = self.FLD_MSG_TYPE_VALID
        fld['msg'] = ""
        self.showSave(flds)
        return self.processFini(request, fs, form, msgType=msgType, msg=msg)


    def appendExpiry(self, request, fs, flds):
        fs['expiry'] = None
        if fs['shelfLife'] == 'T':
            fld = self.fldsAppend(False, flds, self.createField_expiry())
            if not fld['value']:
                n = datetime.datetime.today()
                fld['value'] = dict( y=n.year, m=n.month, d=n.day )
                fs['expiry'] = "{:04d}-{:02d}-{:02d}".format(n.year, n.month, n.day)
        self.appendQty(request, fs, flds)
        self.showSave(flds)


    @ajaxProcess
    def ajax_fld_expiry(self, request, frmName, fldName=None, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, fldIdx, fld, data = self.processInitFld(request, frmName, fldName)

        y = fld['value']['y'];  m = fld['value']['m'];  d = fld['value']['d']
        if data.startswith('y'): y = int(data[1:])
        if data.startswith('m'): m = int(data[1:])
        if data.startswith('d'): d = int(data[1:])
        expDate = "{:04d}-{:02d}-{:02d}".format(y,m,d)
        if expDate < datetime.datetime.today().strftime('%Y-%m-%d'):
            fld['value'] = dict(y=y, m=m, d=d)
            fld['msgType'] = self.FLD_MSG_TYPE_INVALID
            fld['msg'] = 'Cannot be past'
            self.showSave(flds)
            return self.processFini(request, fs, form)

        fs['expiry'] = expDate
        fld['value'] = dict(y=y, m=m, d=d)
        fld['msgType'] = self.FLD_MSG_TYPE_VALID
        fld['msg'] = ""
        self.showSave(flds)
        return self.processFini(request, fs, form, msgType=msgType, msg=msg)


    def appendQty(self, request, fs, flds):
        fs['qty'] = 1
        if fs['serialized'] == 'F':
            self.fldsAppend(False, flds, self.createField_qty(value=1, msgType=self.FLD_MSG_TYPE_NONE, msg=fs['uomCode']))
        self.appendNotes(request, fs, flds)
        self.showSave(flds)


    @ajaxProcess
    def ajax_fld_qty(self, request, frmName, fldName=None, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, fldIdx, fld, qty = self.processInitFld(request, frmName, fldName)

        if not re.match(r'^(\d*[.])?\d+$', qty.strip()):
            fld['value'] = qty
            fld['msgType'] = self.FLD_MSG_TYPE_INVALID
            fld['msg'] = 'Invalid quantity'
            self.showSave(flds)
            return self.processFini(request, fs, form)

        fs['qty'] = float(qty)
        fld['value'] = fs['qty']
        fld['msgType'] = self.FLD_MSG_TYPE_NONE
        fld['msg'] = fs['uomCode']
        self.showSave(flds)
        return self.processFini(request, fs, form, msgType=msgType, msg=msg)


    def appendNotes(self, request, fs, flds):
        fs['notes'] = ""
        self.fldsAppend(False, flds, self.createField_notes(value="", msgType=self.FLD_MSG_TYPE_NONE))  #msgTypes are used to determine if 'save' should be shown
        self.showSave(flds)


    @ajaxProcess
    def ajax_fld_notes(self, request, frmName, fldName=None, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, fldIdx, fld, notes = self.processInitFld(request, frmName, fldName)
        fs['notes'] = notes
        fld['value'] = notes
        return self.processFini(request, fs, form, msgType=msgType, msg=msg)


    def showSave(self, flds):
        okayToShow = True
        for fld in flds:
            if fld['group'] == 2:
                okayToShow = okayToShow and (fld['msgType'] >= 0)
        if okayToShow:
            self.fldsAppend(False, flds, self.createField_save())
        else:
            self.fldsRemove(flds, 'save')


    @ajaxProcess
    def ajax_fld_save(self, request, frmName, fldName=None, msgType=ViewCapture.FORM_MSG_TYPE_NONE, msg=None):
        fs, form, flds, fldIdx, fld, data = self.processInitFld(request, frmName, fldName)

        # create bind vars for optional fields
        if not 'expiry' in fs: fs['expiry'] = None
        if not 'serial' in fs: fs['serial'] = None

        # manually get the next stm_auto_key
        q = """ select g_stm_auto_key.nextval
                  from dual
            """
        row, fldNames = dbFetchOne(None, q, fs)
        nextStm, = row

        q = """ declare
                    cur             QC_UTL_PKG.CURSOR_TYPE;
                    l_bos_initial   number;
                    l_wob           number;
                    l_stm           number := {nextStm};
                    l_ctrlNo        number;
                    l_ctrlId        number;
                    l_cnc           number;
                    l_syscm         number;
                    l_gl_trans_link number;
                begin
                    aqcCaptureQC.authUserSession(:user_id);
                    --
                    select bos_initial into l_bos_initial from wo_control;
                    --
                    insert into wo_bom ( wob_auto_key,            woo_auto_key,  pnm_auto_key,  sysur_auto_key,  pcc_auto_key, qty_needed, activity,  cond_level,  wot_auto_key,  unit_price, requisition, extra_part, rework_flag, accumulation, inspect_status, priority, entry_date, sysur_requested, bos_auto_key,  req_verification, tech_record )
                        values         ( g_wob_auto_key.nextval, :woo_auto_key, :pnm_auto_key, :sysur_auto_key, :pcc_auto_key, :qty,       'Turn-In', 0,          :wot_auto_key, :unitCost,   'T',         'F',        'F',         'F',          'None',         0,        sysdate,    :sysur_auto_key, l_bos_initial, 'F',              'F'         )
                        returning wob_auto_key into l_wob;
                    --
                    -- see if woo has already had parts turned in, and if so use the same ctrlNo and next ctrlId
                    open cur for
                        select STM.ctrl_number
                             , max(STM.ctrl_id) + 1
                          from stock        STM
                             , stock_ti     STI
                             , wo_bom       WOB
                             , wo_operation WOO
                         where WOO.woo_auto_key = WOB.woo_auto_key and
                               WOB.wob_auto_key = STI.wob_auto_key and
                               STI.stm_auto_key = STM.stm_auto_key and
                               STI.ti_type = 'T' and
                               WOO.woo_auto_key = :woo_auto_key
                         group by WOO.woo_auto_key
                                , STM.ctrl_number;
                    fetch cur into l_ctrlNo, l_ctrlId;
                    if cur{percentNotFound} then
                        select g_stm_ctrl_number.nextval, 1
                          into l_ctrlNo, l_ctrlId
                          from dual;
                    end if;
                    close cur;
                    --
                    select min(cnc_auto_key)   into l_cnc   from consignment_codes;
                    select min(syscm_auto_key) into l_syscm from sys_companies;
                    --
                    insert into stock (  stm_auto_key,  pnm_auto_key, cmp_auto_key,  pcc_auto_key, ifc_auto_key,  loc_auto_key,  whs_auto_key,    cnc_auto_key, cts_auto_key,  sysur_auto_key,  ctrl_number, ctrl_id,  rec_date, receiver_number,  unit_price,  qty_oh,  qty_adj,  adj_cost, syscm_auto_key,   rec_tran_id,          stc_auto_key,       series_number,         series_id, stock_audit, ic_udn_001, ic_udn_002, ic_udn_003, ic_udn_004, ic_udn_005, ic_udn_006, ic_udn_007, ic_udn_008, ic_udn_009, ic_udn_010, turnin_rec,  serial_number,  exp_date,                        notes   )
                        values        (  l_stm,        :pnm_auto_key, l_syscm,      :pcc_auto_key, null,         :loc_auto_key, :whs_auto_key,  l_cnc,          null,         :sysur_auto_key,  l_ctrlNo,    l_ctrlId, sysdate,  :si_number,       :unitCost,  :qty,    :qty,     :unitCost, 1,              g_rec_tran_id.nextval,  null,         g_stm_series_number.nextval, 1,         'F',         0,          0,          0,          0,          0,          0,          0,          0,          0,          0,          'T',        :serial,         to_date(:expiry, 'yyyy-mm-dd'), :notes   )
                        returning stm_auto_key into l_stm;
                    --
                    select g_gl_trans_link.nextval into l_gl_trans_link from dual;
                    --
                    insert into stock_ti (  sti_auto_key,           stm_auto_key,   wob_auto_key,  qty, tran_date, ti_type,   gl_trans_link  )
                        values           (g_sti_auto_key.nextval, l_stm,          l_wob,          :qty, sysdate,   'T',     l_gl_trans_link  );
                    --
                    cur := QC_GL_PKG.SPI_SI_GL2( p_gl_trans_link => l_gl_trans_link
                                               , p_commit        => 'N'
                                               );
                    --
                    commit;
                end;
            """.format( nextStm = nextStm
                      , percentNotFound = '%NOTFOUND'
                      )
        rc = dbExecute(None, q, fs)

        request.session['stock.stmAutoKey'] = nextStm
        uri = reverse('capture:stockLabel', kwargs=dict(frmName='stockLabel')) + '.html'
        return jsonRedirect(dict(redirectTo=uri), 'Printing...')


    #--------------------------------------------------
    #- convenience routines
    #--------------------------------------------------
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


    def get_getWarehouseCodes(self, fs):
        q = """ select whs_auto_key     as "seq"
                     , warehouse_code   as "code"
                     , description      as "desc"
                 from warehouse
                order by sequence
            """
        recs, fldNames = dbFetchAll(None, q, fs, asDict=True)
        if not recs:
            raise ServerDbError("AQC-0001", "No part warehouse codes were found.  Please relay this message to a system administrator.")
        return recs
